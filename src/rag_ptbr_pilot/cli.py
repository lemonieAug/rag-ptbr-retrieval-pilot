"""Interface de linha de comando (CLI).

Importar este módulo (ou o pacote) NÃO carrega modelos nem inicia downloads.
Modelos são carregados apenas pelos comandos que os usam (``index``, ``retrieve``,
``generate``), sempre a partir de cache local, com falha instruída se ausentes.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

from . import __version__
from .benchmark import (
    assert_no_leakage,
    load_articles,
    load_evidence_groups,
    load_qrels,
    load_questions,
    retrieval_query,
    validate_benchmark,
)
from .config import AppConfig, config_to_dict, load_config
from .errors import ConfigError, PilotError
from .indexing import (
    BM25Index,
    DenseIndex,
    LexicalNormalizer,
    bm25_fingerprint,
    dense_fingerprint,
    ensure_compatible,
)
from .io_utils import load_json, save_json, save_jsonl, save_text
from .manifest import RunManifest, hash_json, sha256_text, short_hash, timestamp_iso
from .persistence import load_chunks, load_manifest, save_chunks, save_manifest
from .retrieval import (
    RetrievalRunner,
    build_matrix,
    select_matrix,
    standard_comparisons,
)
from .retrieval.results import QueryRetrieval
from .schemas import ReviewStatus
from .chunking import build_chunks, build_corpus_manifest
from .chunking.token_validation import TokenValidationReport
from .reporting import build_qrel_index, evaluate_config, paired_delta, render_report

STAGES_SUMMARY = "rankings"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _approved(questions):
    return [q for q in questions if q.review_status == ReviewStatus.approved]


def _new_run_id(corpus_version: str) -> str:
    stamp = timestamp_iso().replace(":", "").replace("-", "")
    return f"run-{stamp}-{short_hash(corpus_version, 8)}"


def _latest_run_id(results_dir: Path) -> str | None:
    if not results_dir.exists():
        return None
    runs = sorted(p.name for p in results_dir.iterdir() if p.is_dir() and p.name.startswith("run-"))
    return runs[-1] if runs else None


def _collect_environment() -> dict:
    import platform

    env = {"python_version": platform.python_version(), "platform": platform.platform()}
    libs = ["torch", "transformers", "sentence-transformers", "numpy", "pydantic",
            "PyYAML", "pdfplumber", "pypdf", "requests", "huggingface-hub"]
    versions: dict[str, str | None] = {}
    try:
        from importlib.metadata import PackageNotFoundError, version
        for lib in libs:
            try:
                versions[lib] = version(lib)
            except PackageNotFoundError:
                versions[lib] = None
    except Exception:
        pass
    env["library_versions"] = versions
    gpu: dict = {}
    try:
        import torch

        gpu["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            gpu["device_name"] = torch.cuda.get_device_name(0)
            gpu["device_count"] = torch.cuda.device_count()
    except Exception:
        gpu["cuda_available"] = None
    env["gpu"] = gpu
    return env


def _load_revisions(cfg: AppConfig) -> dict:
    p = cfg.resolve(cfg.models.cache_dir) / "revisions.json"
    if p.exists():
        return load_json(p).get("revisions", {})
    return {}


def _load_bm25(cfg: AppConfig, chunks, normalizer, corpus_version: str) -> BM25Index:
    idx_path = cfg.resolve(cfg.reporting.artifacts_dir) / "indexes" / "bm25.json"
    if not idx_path.exists():
        raise ConfigError(f"Índice BM25 não encontrado: {idx_path}. Rode: rag-ptbr index.")
    idx = BM25Index.from_dict(load_json(idx_path))
    expected = bm25_fingerprint(
        corpus_version, cfg.retrieval.bm25.k1, cfg.retrieval.bm25.b,
        cfg.retrieval.lexical.model_dump(mode="json"),
    )
    ensure_compatible(idx.fingerprint, expected, "bm25")
    idx.rebuild_terms(chunks, normalizer)
    return idx


def _load_dense_index(cfg: AppConfig, embedding: str, corpus_version: str) -> DenseIndex:
    from .adapters.specs import get_embedding_spec

    spec = get_embedding_spec(embedding)
    d = cfg.resolve(cfg.reporting.artifacts_dir) / "indexes" / f"dense_{embedding}"
    if not (d / "meta.json").exists():
        raise ConfigError(f"Índice denso de {embedding} não encontrado: {d}. Rode: rag-ptbr index.")
    idx = DenseIndex.load(d)
    revision = _load_revisions(cfg).get(spec.checkpoint)
    expected = dense_fingerprint(
        corpus_version, embedding, spec.checkpoint, revision, idx.dimension,
    )
    ensure_compatible(idx.fingerprint, expected, f"dense_{embedding}")
    return idx


def _merge_reports(reports: list[TokenValidationReport]) -> TokenValidationReport:
    merged = TokenValidationReport()
    if reports:
        merged.binding_model = reports[0].binding_model
        merged.binding_limit = reports[0].binding_limit
    for r in reports:
        merged.subdivided_blocks.extend(r.subdivided_blocks)
        merged.overflow_remaining.extend(r.overflow_remaining)
        for model, info in r.per_model.items():
            cur = merged.per_model.setdefault(model, {"limit": info.get("limit"),
                                                      "limit_known": info.get("limit_known"),
                                                      "overflow_chunks": 0})
            cur["overflow_chunks"] += info.get("overflow_chunks", 0)
    return merged


def _load_query_results(path: Path) -> list[QueryRetrieval]:
    from .io_utils import load_jsonl

    return [QueryRetrieval.from_dict(d) for d in load_jsonl(path)]


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------


def cmd_matrix(args) -> None:
    cfg = load_config(args.config)
    embeddings = cfg.effective_embeddings()
    specs = build_matrix(embeddings)
    selected = select_matrix(specs, cfg.experiments.select, cfg.experiments.include_reranker)
    print(f"Matriz experimental ({len(specs)} configurações, embeddings={embeddings}):")
    for s in specs:
        mark = "*" if s in selected else " "
        emb = s.embedding or "-"
        print(f" {mark} {s.config_id:<28} initial={s.initial_retrieval:<7} emb={emb:<16} rerank={s.rerank}")
    print(f"\n{len(selected)} configuração(ões) selecionada(s) (subset em experiments.select).")


def cmd_validate(args) -> None:
    cfg = load_config(args.config)
    articles = load_articles(cfg.resolve(cfg.paths.metadata_path))
    questions = load_questions(cfg.resolve(cfg.paths.questions_path))
    qrels = load_qrels(cfg.resolve(cfg.paths.qrels_path))
    groups = load_evidence_groups(cfg.resolve(cfg.paths.evidence_groups_path))

    chunks = []
    chunks_path = cfg.resolve(cfg.paths.chunks_path)
    if chunks_path.exists():
        chunks = load_chunks(chunks_path)

    report = validate_benchmark(articles, questions, qrels, groups, chunks)
    print(f"Artigos: {len(articles)} | Perguntas: {len(questions)} | "
          f"Qrels: {len(qrels)} | Grupos: {len(groups)} | Chunks: {len(chunks)}")
    print(f"Erros: {len(report.errors)} | Avisos: {len(report.warnings)}")
    for e in report.errors:
        print(f"  [ERRO] {e}")
    for w in report.warnings:
        print(f"  [aviso] {w}")
    if not report.valid:
        sys.exit(1)


def cmd_extract(args) -> None:
    from .ingest import extract_article

    cfg = load_config(args.config)
    articles = load_articles(cfg.resolve(cfg.paths.metadata_path))
    out_dir = cfg.resolve(cfg.paths.extracted_dir)
    for meta in articles:
        summary = extract_article(cfg.articles_dir(), meta, out_dir)
        print(f"[ok] {meta.doc_id}: {summary['num_pages']} páginas, "
              f"{summary['tables_count']} tabelas -> {summary['markdown_path']}")
        for w in summary["warnings"]:
            print(f"  [aviso] {w}")
        for r in summary["review_items"]:
            print(f"  [revisar] {r}")


def cmd_chunk(args) -> None:
    from .adapters.specs import get_embedding_spec
    from .manifest import sha256_text

    cfg = load_config(args.config)
    articles = load_articles(cfg.resolve(cfg.paths.metadata_path))
    specs = [get_embedding_spec(e) for e in cfg.effective_embeddings()]
    cache_dir = str(cfg.resolve(cfg.models.cache_dir))
    extracted_dir = cfg.resolve(cfg.paths.extracted_dir)

    all_chunks = []
    doc_hashes: dict[str, dict] = {}
    reports: list[TokenValidationReport] = []

    for meta in articles:
        md_path = extracted_dir / f"{meta.doc_id}.md"
        if not md_path.exists():
            raise ConfigError(f"Markdown não encontrado: {md_path}. Rode: rag-ptbr extract.")
        md_text = md_path.read_text(encoding="utf-8")
        result = build_chunks(md_text, meta.doc_id, cfg.chunking, specs, cache_dir)
        all_chunks.extend(result.chunks)
        reports.append(result.report)

        prov_path = extracted_dir / f"{meta.doc_id}.provenance.json"
        prov = load_json(prov_path) if prov_path.exists() else {}
        doc_hashes[meta.doc_id] = {
            "pdf_sha256": prov.get("pdf_sha256"),
            "md_sha256": sha256_text(md_text),
        }

    merged = _merge_reports(reports)
    manifest = build_corpus_manifest(all_chunks, doc_hashes, cfg.chunking, merged)

    save_chunks(cfg.resolve(cfg.paths.chunks_path), all_chunks)
    save_manifest(cfg.resolve(cfg.paths.corpus_manifest_path), manifest)
    print(f"[ok] {len(all_chunks)} chunks congelados (corpus {manifest.corpus_version}).")
    print(f"  binding: {merged.binding_model} (limite {merged.binding_limit})")
    print(f"  blocos subdivididos: {len(merged.subdivided_blocks)}")
    if merged.overflow_remaining:
        print(f"  [revisar] overflow restante: {len(merged.overflow_remaining)} chunk(s)")


def cmd_prepare_models(args) -> None:
    from .fetch import fetch_models

    cfg = load_config(args.config)
    revisions = fetch_models(cfg)
    print("[ok] Modelos obtidos. Revisões resolvidas:")
    for repo, rev in revisions.items():
        print(f"  {repo}: {rev}")


def cmd_index(args) -> None:
    from .adapters import get_embedding_adapter

    cfg = load_config(args.config)
    chunks = load_chunks(cfg.resolve(cfg.paths.chunks_path))
    manifest = load_manifest(cfg.resolve(cfg.paths.corpus_manifest_path))
    corpus_version = manifest.corpus_version
    normalizer = LexicalNormalizer(cfg.retrieval.lexical)

    indexes_dir = cfg.resolve(cfg.reporting.artifacts_dir) / "indexes"
    indexes_dir.mkdir(parents=True, exist_ok=True)

    # BM25
    bm25 = BM25Index(k1=cfg.retrieval.bm25.k1, b=cfg.retrieval.bm25.b)
    bm25.build(chunks, normalizer)
    bm25.fingerprint = bm25_fingerprint(
        corpus_version, cfg.retrieval.bm25.k1, cfg.retrieval.bm25.b,
        cfg.retrieval.lexical.model_dump(mode="json"),
    )
    save_json(indexes_dir / "bm25.json", bm25.to_dict())
    print("[ok] Índice BM25 construído.")

    # Densa (por embedding, em etapas, liberando recursos)
    revisions = _load_revisions(cfg)
    for embedding in cfg.effective_embeddings():
        adapter = get_embedding_adapter(embedding, cfg)
        print(f"[index] codificando documentos com {embedding} ...")
        adapter.load()
        try:
            matrix = adapter.encode_documents([c.text for c in chunks])
            revision = revisions.get(adapter.checkpoint)
            dense = DenseIndex(
                embedding_name=embedding,
                checkpoint=adapter.checkpoint,
                revision=revision,
                dimension=adapter.dimension,
                chunk_ids=[c.chunk_id for c in chunks],
                matrix=matrix,
            )
            dense.fingerprint = dense_fingerprint(
                corpus_version, embedding, adapter.checkpoint, revision, adapter.dimension,
            )
            dense.save(indexes_dir / f"dense_{embedding}")
            print(f"[ok] Índice denso de {embedding} (dim={adapter.dimension}).")
        finally:
            adapter.unload()


def cmd_retrieve(args) -> None:
    from .adapters import get_embedding_adapter, get_reranker_adapter

    cfg = load_config(args.config)
    chunks = load_chunks(cfg.resolve(cfg.paths.chunks_path))
    manifest = load_manifest(cfg.resolve(cfg.paths.corpus_manifest_path))
    chunk_by_id = {c.chunk_id: c for c in chunks}
    normalizer = LexicalNormalizer(cfg.retrieval.lexical)

    questions = load_questions(cfg.resolve(cfg.paths.questions_path))
    approved = _approved(questions)
    if not approved:
        raise ConfigError("Nenhuma pergunta aprovada para recuperação (review_status=approved).")

    matrix = build_matrix(cfg.effective_embeddings())
    selected = select_matrix(matrix, cfg.experiments.select, cfg.experiments.include_reranker)

    needed_embeddings = {s.embedding for s in selected if s.embedding}
    bm25 = _load_bm25(cfg, chunks, normalizer, manifest.corpus_version)
    dense_indices = {e: _load_dense_index(cfg, e, manifest.corpus_version) for e in needed_embeddings}
    adapters = {e: get_embedding_adapter(e, cfg) for e in needed_embeddings}
    for adapter in adapters.values():
        adapter.load()

    reranker = None
    if any(s.rerank for s in selected):
        reranker = get_reranker_adapter(cfg)
        reranker.load()

    runner = RetrievalRunner(cfg.retrieval, chunk_by_id, bm25, normalizer,
                             dense_indices, adapters, reranker)

    run_id = _new_run_id(manifest.corpus_version)
    rankings_dir = cfg.resolve(cfg.reporting.results_dir) / run_id / "rankings"
    rankings_dir.mkdir(parents=True, exist_ok=True)

    for spec in selected:
        results = []
        for q in approved:
            query_text = retrieval_query(q)
            assert_no_leakage(query_text, q)
            results.append(runner.run_query(q.question_id, query_text, spec))
        save_jsonl(rankings_dir / f"{spec.config_id}.jsonl",
                   [r.to_dict() for r in results])
        print(f"[ok] {spec.config_id}: {len(results)} consultas -> "
              f"{rankings_dir / (spec.config_id + '.jsonl')}")

    # Manifesto de execução
    qrels = load_qrels(cfg.resolve(cfg.paths.qrels_path))
    prompts_hash = ""
    prompt_path = cfg.resolve(cfg.generation.prompt_template)
    if prompt_path.exists():
        prompts_hash = sha256_text(prompt_path.read_text(encoding="utf-8"))
    env = _collect_environment()
    manifest_run = RunManifest(
        run_id=run_id,
        config_hash=hash_json(config_to_dict(cfg)),
        corpus_version=manifest.corpus_version,
        prompts_hash=prompts_hash,
        qrels_hash=hash_json([q.model_dump(mode="json") for q in qrels]),
        model_revisions=_load_revisions(cfg),
        package_version=__version__,
        library_versions=env.get("library_versions", {}),
        python_version=env.get("python_version", ""),
        hardware=env.get("gpu", {}),
        seed=cfg.experiments.seed,
        parameters={"top_n": cfg.retrieval.top_n,
                    "bm25": cfg.retrieval.bm25.model_dump(mode="json"),
                    "rrf": cfg.retrieval.rrf.model_dump(mode="json")},
        configurations=[s.config_id for s in selected],
    )
    save_json(cfg.resolve(cfg.reporting.results_dir) / run_id / "run_manifest.json",
              manifest_run.to_dict())
    print(f"\nRun ID: {run_id}")


def cmd_evaluate(args) -> None:
    cfg = load_config(args.config)
    questions = _approved(load_questions(cfg.resolve(cfg.paths.questions_path)))
    qrels = load_qrels(cfg.resolve(cfg.paths.qrels_path))
    groups = load_evidence_groups(cfg.resolve(cfg.paths.evidence_groups_path))
    relevant, relevance = build_qrel_index(qrels)
    groups_by_q: dict = defaultdict(list)
    for g in groups:
        groups_by_q[g.question_id].append(g)
    questions_by_id = {q.question_id: q for q in questions}

    run_id = args.run_id or _latest_run_id(cfg.resolve(cfg.reporting.results_dir))
    if run_id is None:
        raise ConfigError("Nenhuma execução encontrada. Rode: rag-ptbr retrieve.")
    run_dir = cfg.resolve(cfg.reporting.results_dir) / run_id
    rankings_dir = run_dir / "rankings"

    k_values = cfg.metrics.k_values
    summaries: dict[str, dict] = {}
    metrics_dir = run_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    for rpath in sorted(rankings_dir.glob("*.jsonl")):
        config_id = rpath.stem
        qrs = _load_query_results(rpath)
        qr_by_qid = {qr.query_id: qr for qr in qrs if qr.query_id in questions_by_id}
        summary = evaluate_config(qr_by_qid, relevant, relevance, groups_by_q,
                                  questions_by_id, k_values)
        summaries[config_id] = summary
        save_json(metrics_dir / f"{config_id}.json", summary)

    save_json(run_dir / "metrics_summary.json",
              {cid: {"means": s["means"], "group_coverage": s["group_coverage"],
                     "n_questions_evaluated": s["n_questions_evaluated"]}
               for cid, s in summaries.items()})

    comparisons = standard_comparisons(cfg.effective_embeddings())
    deltas = []
    for comp in comparisons:
        sa, sb = summaries.get(comp.a), summaries.get(comp.b)
        if sa is None or sb is None:
            continue
        d = paired_delta(sa, sb, cfg.metrics.primary)
        deltas.append({"label": comp.label, "a": comp.a, "b": comp.b, **d})
    save_json(run_dir / "comparison.json", deltas)

    run_manifest = load_json(run_dir / "run_manifest.json") if (run_dir / "run_manifest.json").exists() else {}
    manifest = RunManifest(run_id=run_id)
    for k, v in run_manifest.items():
        if hasattr(manifest, k):
            setattr(manifest, k, v)

    report_md = render_report(run_id, summaries, comparisons, manifest,
                              cfg.metrics.primary, k_values)
    save_text(run_dir / "report.md", report_md)
    print(f"[ok] Métricas e relatório em {run_dir}/")
    print(f"  relatório: {run_dir / 'report.md'}")


def cmd_generate(args) -> None:
    from .generation import OllamaClient, assemble_context
    from .generation.human_eval import build_human_eval_rows, write_human_eval_csv

    cfg = load_config(args.config)
    chunks = load_chunks(cfg.resolve(cfg.paths.chunks_path))
    chunk_by_id = {c.chunk_id: c for c in chunks}
    questions = _approved(load_questions(cfg.resolve(cfg.paths.questions_path)))
    questions_by_id = {q.question_id: q for q in questions}

    run_id = args.run_id or _latest_run_id(cfg.resolve(cfg.reporting.results_dir))
    if run_id is None:
        raise ConfigError("Nenhuma execução encontrada. Rode: rag-ptbr retrieve.")
    run_dir = cfg.resolve(cfg.reporting.results_dir) / run_id
    rankings_dir = run_dir / "rankings"

    template_path = cfg.resolve(cfg.generation.prompt_template)
    template = template_path.read_text(encoding="utf-8")

    gen = cfg.models.generator
    host = os.environ.get("OLLAMA_HOST") or gen.host
    client = OllamaClient(
        host=host, model=gen.model, temperature=gen.temperature,
        seed=gen.seed, num_ctx=gen.num_ctx, reasoning=gen.reasoning,
        tag=gen.tag, digest=gen.digest,
    )

    config_ids = [args.config_id] if args.config_id else [p.stem for p in sorted(rankings_dir.glob("*.jsonl"))]
    generations = []
    for config_id in config_ids:
        qrs = _load_query_results(rankings_dir / f"{config_id}.jsonl")
        for qr in qrs:
            if qr.query_id not in questions_by_id:
                continue
            qtext = questions_by_id[qr.query_id].text
            prompt_empty = template.format(query=qtext, context="")
            asm = assemble_context(
                qr.final_ids(), chunk_by_id,
                top_k=cfg.generation.top_k_context,
                context_budget_tokens=cfg.generation.context_budget_tokens,
                prompt_text=prompt_empty,
                response_reserve_tokens=cfg.generation.response_reserve_tokens,
                model_num_ctx=gen.num_ctx,
            )
            final_prompt = template.format(query=qtext, context=asm.context_text)
            g = client.generate(qr.query_id, config_id, final_prompt)
            g.context_included = asm.included_chunk_ids
            g.context_text = asm.context_text
            # Anexa metadados de montagem no resultado (via parâmetros).
            g.parameters["context_assembly"] = asm.to_dict()
            generations.append(g)

    gen_dir = run_dir / "generation"
    gen_dir.mkdir(parents=True, exist_ok=True)
    save_jsonl(gen_dir / "generations.jsonl", [g.to_dict() for g in generations])

    rows, mapping = build_human_eval_rows(
        [g for g in generations],
        questions_by_id,
        cfg.generation.human_eval_shuffle_seed,
    )
    write_human_eval_csv(rows, mapping, gen_dir / "human_eval.csv",
                         gen_dir / "blind_mapping.json")
    print(f"[ok] {len(generations)} respostas geradas em {gen_dir}/")
    print(f"  avaliação humana: {gen_dir / 'human_eval.csv'}")


def cmd_report(args) -> None:
    cfg = load_config(args.config)
    run_id = args.run_id or _latest_run_id(cfg.resolve(cfg.reporting.results_dir))
    if run_id is None:
        raise ConfigError("Nenhuma execução encontrada. Rode: rag-ptbr retrieve.")
    run_dir = cfg.resolve(cfg.reporting.results_dir) / run_id
    report_path = run_dir / "report.md"
    if report_path.exists():
        print(report_path.read_text(encoding="utf-8"))
    else:
        print("Relatório não encontrado. Rode: rag-ptbr evaluate.")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def _add_config(p) -> None:
    p.add_argument("-c", "--config", default=None,
                   help="Caminho do YAML de configuração (default: configs/default.yaml)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag-ptbr",
        description="Piloto de retrieval para RAG em artigos científicos em PT-BR.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("matrix", help="Mostra a matriz experimental e a seleção.")
    _add_config(p)
    p.set_defaults(handler=cmd_matrix)

    p = sub.add_parser("validate", help="Valida metadados/perguntas/qrels/grupos (sem modelos).")
    _add_config(p)
    p.set_defaults(handler=cmd_validate)

    p = sub.add_parser("extract", help="Extrai PDFs -> Markdown + proveniência.")
    _add_config(p)
    p.set_defaults(handler=cmd_extract)

    p = sub.add_parser("chunk", help="Gera e congela os chunks (valida tokens).")
    _add_config(p)
    p.set_defaults(handler=cmd_chunk)

    p = sub.add_parser("prepare-models", help="Baixa os checkpoints explicitamente.")
    _add_config(p)
    p.set_defaults(handler=cmd_prepare_models)

    p = sub.add_parser("index", help="Constrói BM25 + índices densos.")
    _add_config(p)
    p.set_defaults(handler=cmd_index)

    p = sub.add_parser("retrieve", help="Executa as configurações da matriz.")
    _add_config(p)
    p.set_defaults(handler=cmd_retrieve)

    p = sub.add_parser("evaluate", help="Calcula métricas e gera relatório.")
    _add_config(p)
    p.add_argument("--run-id", default=None, help="ID da execução (default: mais recente).")
    p.set_defaults(handler=cmd_evaluate)

    p = sub.add_parser("generate", help="Geração opcional via Ollama (Qwen3 14B).")
    _add_config(p)
    p.add_argument("--run-id", default=None, help="ID da execução (default: mais recente).")
    p.add_argument("--config-id", dest="config_id", default=None,
                   help="Configuração específica (default: todas com ranking).")
    p.set_defaults(handler=cmd_generate)

    p = sub.add_parser("report", help="Imprime o relatório existente.")
    _add_config(p)
    p.add_argument("--run-id", default=None, help="ID da execução (default: mais recente).")
    p.set_defaults(handler=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.handler(args)
    except PilotError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
