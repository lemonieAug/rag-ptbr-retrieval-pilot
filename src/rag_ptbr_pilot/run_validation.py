"""Bind saved results to the benchmark, corpus and configuration that produced them."""

from .config import config_to_dict
from .errors import ConfigError
from .io_utils import load_json
from .manifest import hash_json, sha256_file, sha256_text
from .persistence import load_frozen_corpus


def benchmark_hashes(cfg):
    return {name: sha256_file(cfg.resolve(path)) for name, path in {
        "questions_hash": cfg.paths.questions_path,
        "evidence_groups_hash": cfg.paths.evidence_groups_path,
    }.items()}


def validate_run(cfg, run_dir, questions, qrels):
    if not questions:
        raise ConfigError("Nenhuma pergunta aprovada; resultados oficiais exigem revisão humana.")
    chunks, corpus = load_frozen_corpus(cfg)
    path = run_dir / "run_manifest.json"
    if not path.exists():
        raise ConfigError("Manifesto da execução ausente; não é seguro reutilizar resultados.")
    saved = load_json(path)
    revision_file = cfg.resolve(cfg.models.cache_dir) / "revisions.json"
    revisions = load_json(revision_file).get("revisions", {}) if revision_file.exists() else {}
    prompt_path = cfg.resolve(cfg.generation.prompt_template)
    expected = {
        "config_hash": hash_json(config_to_dict(cfg)),
        "corpus_version": corpus.corpus_version,
        "qrels_hash": hash_json([q.model_dump(mode="json") for q in qrels]),
        "prompts_hash": sha256_text(prompt_path.read_text(encoding="utf-8")) if prompt_path.exists() else "",
        "model_revisions": revisions,
        **benchmark_hashes(cfg),
    }
    for key, value in expected.items():
        if saved.get(key) != value:
            raise ConfigError(f"Execução incompatível: {key} mudou ou está ausente; execute retrieve novamente.")
    if saved.get("run_id") != run_dir.name:
        raise ConfigError("run_id incompatível com o diretório de resultados.")
    from .retrieval import build_matrix, select_matrix
    selected = select_matrix(build_matrix(cfg.effective_embeddings()),
                             cfg.experiments.select, cfg.experiments.include_reranker)
    config_ids = {s.config_id for s in selected}
    actual = {p.stem for p in (run_dir / "rankings").glob("*.jsonl")}
    if set(saved.get("configurations", [])) != config_ids or actual != config_ids:
        raise ConfigError("Rankings incompletos ou incompatíveis com a matriz da execução.")
    from .io_utils import load_jsonl
    approved_ids = {q.question_id for q in questions}
    for cid in sorted(config_ids):
        ranking_path = run_dir / "rankings" / f"{cid}.jsonl"
        if saved.get("ranking_hashes", {}).get(ranking_path.name) != sha256_file(ranking_path):
            raise ConfigError(f"Ranking alterado ou hash ausente: {cid}.")
        rows = load_jsonl(ranking_path)
        if ({r.get("query_id") for r in rows} != approved_ids
                or len(rows) != len(approved_ids)
                or any(r.get("config_id") != cid for r in rows)):
            raise ConfigError(f"Perguntas/configuração incompatíveis no ranking {cid}.")
        from .retrieval.results import QueryRetrieval
        valid_ids = {c.chunk_id for c in chunks}
        for row in rows:
            try:
                parsed = QueryRetrieval.from_dict(row)
                for stage in (parsed.bm25, parsed.dense, parsed.rrf_union, parsed.rrf_topn,
                              parsed.candidates_to_rerank, parsed.final):
                    ids = [c.chunk_id for c in stage]
                    if len(set(ids)) != len(ids) or not set(ids) <= valid_ids:
                        raise ValueError("IDs de chunks inválidos no ranking")
            except (KeyError, TypeError, ValueError) as exc:
                raise ConfigError(f"Ranking inválido em {cid}: {exc}") from exc
    return saved
