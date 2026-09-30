"""Inventory ignored artifacts without treating their absence as repository damage."""

from __future__ import annotations

import argparse
from pathlib import Path

from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.corpus_reference import (
    assert_official_corpus, load_reference, source_issues,
)
from rag_ptbr_pilot.errors import PilotError
from rag_ptbr_pilot.status import collect_status


def inventory(cfg) -> dict[str, tuple[str, str]]:
    status = collect_status(cfg)
    rows: dict[str, tuple[str, str]] = {}
    source_files = ("pyproject.toml", "configs/default.yaml", "configs/model_revisions.yaml",
                    "configs/corpus_reference.yaml", "src/rag_ptbr_pilot/cli.py")
    missing_code = [p for p in source_files if not cfg.resolve(p).is_file()]
    rows["SOURCE CODE"] = ("MISSING", ", ".join(missing_code)) if missing_code else ("READY", "")
    try:
        reference = load_reference(cfg)
    except PilotError:
        reference = None
    missing_corpus = [p for p in (cfg.paths.chunks_path, cfg.paths.corpus_manifest_path)
                      if not cfg.resolve(p).is_file()]

    gold = status.get("benchmark", {})
    if gold.get("validation", {}).get("valid") and gold.get("approved", 0) > 0 and not (gold.get("draft_ready", 0) + gold.get("draft_pending", 0)):
        rows["BENCHMARK"] = ("READY", f"{gold['approved']} aprovadas; {gold.get('rejected', 0)} rejeitadas")
    elif (gold.get("status") == "pending_corpus"
          and gold.get("approved", 0) > 0
          and not (gold.get("draft_ready", 0) + gold.get("draft_pending", 0))
          and all(cfg.resolve(p).is_file() for p in
                  (cfg.paths.questions_path, cfg.paths.qrels_path, cfg.paths.evidence_groups_path))):
        rows["BENCHMARK"] = ("READY", "arquivos presentes; validação cruzada aguarda corpus compatível")
    elif all(cfg.resolve(p).exists() for p in (cfg.paths.questions_path, cfg.paths.qrels_path, cfg.paths.evidence_groups_path)):
        rows["BENCHMARK"] = ("INCOMPATIBLE", "gold incompleto ou validação falhou")
    else:
        paths = (cfg.paths.questions_path, cfg.paths.qrels_path, cfg.paths.evidence_groups_path)
        rows["BENCHMARK"] = ("MISSING", ", ".join(p for p in paths if not cfg.resolve(p).exists()))

    for title, kind in (("RAW PDFs", "pdf"), ("EXTRACTED DATA", "markdown")):
        if reference is None:
            rows[title] = ("MISSING", "configs/corpus_reference.yaml")
            continue
        missing, incompatible = source_issues(cfg, reference, kind)
        detail = "; ".join(filter(None, (
            "ausentes: " + ", ".join(missing) if missing else "",
            "hash divergente: " + ", ".join(incompatible) if incompatible else "")))
        rows[title] = ("MISSING", detail) if missing else (
            ("INCOMPATIBLE", detail) if incompatible else
            ("READY", f"{len(reference['documents'])} documentos"))

    if missing_corpus:
        rows["FROZEN CORPUS"] = ("MISSING", ", ".join(missing_corpus))
    elif status["corpus"].get("status") != "valid":
        rows["FROZEN CORPUS"] = ("INCOMPATIBLE", status["corpus"].get("reason", ""))
    else:
        from types import SimpleNamespace
        try:
            assert_official_corpus(cfg, SimpleNamespace(
                corpus_version=status["corpus"]["corpus_version"]))
        except PilotError as exc:
            rows["FROZEN CORPUS"] = ("INCOMPATIBLE", str(exc))
        else:
            rows["FROZEN CORPUS"] = ("READY", status["corpus"]["corpus_version"])

    models = status["models"]
    unavailable = [name for name, item in models.items() if item["status"] != "available"]
    incompatible = [name for name in unavailable if "incompatível" in models[name].get("reason", "").lower()]
    if unavailable:
        from rag_ptbr_pilot.adapters.specs import get_embedding_spec, RERANKER_SPEC
        from rag_ptbr_pilot.model_revisions import pinned_revisions
        try:
            pins = pinned_revisions(cfg.resolve(cfg.models.revisions_path))
        except PilotError:
            pins = {}
        paths = []
        for name in unavailable:
            repo = RERANKER_SPEC.checkpoint if name == "reranker" else get_embedding_spec(name).checkpoint
            paths.append(f"{cfg.models.cache_dir}/models--{repo.replace('/', '--')}/snapshots/{pins.get(repo, '<REVISION>')}")
        rows["MODELS"] = ("INCOMPATIBLE" if incompatible else "MISSING",
                          f"{cfg.models.cache_dir}/revisions.json; " + ", ".join(paths))
    else:
        rows["MODELS"] = ("READY", f"{len(models)} snapshots pinados")
    indexes = status["indexes"]
    bad = [name for name, item in indexes.items() if item["status"] != "valid"]
    if bad:
        base = f"{cfg.reporting.artifacts_dir}/indexes"
        paths = ([f"{base}/bm25.json"] if "bm25" in bad else [])
        for name in bad:
            if name != "bm25":
                paths.extend((f"{base}/dense_{name}/meta.json",
                              f"{base}/dense_{name}/matrix.npy"))
        missing_paths = [p for p in paths if not cfg.resolve(p).is_file()]
        detail = ", ".join(missing_paths or paths)
        rows["INDEXES"] = ("MISSING" if missing_paths else "INCOMPATIBLE", detail)
    else:
        rows["INDEXES"] = ("READY", f"{len(indexes)} índices compatíveis")
    result_dir = cfg.resolve(cfg.reporting.results_dir)
    run_dirs = [p for p in result_dir.glob("run-*") if (p / "run_manifest.json").is_file()] if result_dir.exists() else []
    rows["RESULTS"] = ("READY", f"{len(run_dirs)} run(s)") if run_dirs else (
        "MISSING", f"{cfg.reporting.results_dir}/<RUN_ID>/run_manifest.json")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true", help="Bloqueia a execução oficial se faltar gold, corpus ou modelos.")
    parser.add_argument("--require-canonical-sources", action="store_true",
                        help="Exige PDFs canônicos e Markdown revisado antes de reconstruir o corpus.")
    args = parser.parse_args()
    rows = inventory(load_config())
    for name, (state, detail) in rows.items():
        print(f"{name}: {state}" + (f" — {detail}" if detail else ""))
    if args.require_ready and any(rows[name][0] != "READY" for name in ("SOURCE CODE", "BENCHMARK", "FROZEN CORPUS", "MODELS")):
        return 2
    if args.require_canonical_sources and any(rows[name][0] != "READY" for name in ("RAW PDFs", "EXTRACTED DATA")):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
