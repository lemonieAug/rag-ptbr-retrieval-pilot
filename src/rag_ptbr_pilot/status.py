"""Consolidated local readiness; checks artifacts without loading model weights."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from .adapters.local import local_checkpoint
from .adapters.specs import get_embedding_spec
from .benchmark.audit import audit_gold, review_counts
from .benchmark.loaders import load_questions
from .config import load_config
from .corpus_reference import REFERENCE_PATH, assert_official_corpus
from .errors import PilotError
from .io_utils import load_json
from .persistence import load_frozen_corpus
from .retrieval.matrix import build_matrix


def checkpoint_available(checkpoint: str, cache_dir: Path,
                         revisions_path: Path | None = None) -> dict:
    """Inspect required local files and all declared shards; no HF/torch imports."""
    try:
        snapshot = Path(local_checkpoint(checkpoint, cache_dir, revisions_path))
        required = [snapshot / "config.json"]
        if not any((snapshot / p).is_file() for p in ("tokenizer.json", "tokenizer.model", "spiece.model")):
            raise ValueError("tokenizer ausente")
        indexes = [p for p in (snapshot / "model.safetensors.index.json",
                               snapshot / "pytorch_model.bin.index.json") if p.exists()]
        if indexes:
            shards = set(load_json(indexes[0]).get("weight_map", {}).values())
            if not shards:
                raise ValueError("manifesto de pesos vazio")
            required.extend(snapshot / shard for shard in shards)
        else:
            weights = [p for p in (snapshot / "model.safetensors", snapshot / "pytorch_model.bin") if p.exists()]
            if not weights:
                raise ValueError("pesos ausentes")
            required.extend(weights)
        if any(not p.is_file() or not p.stat().st_size for p in required):
            raise ValueError("arquivo obrigatório ausente ou vazio")
        return {"status": "available", "revision": snapshot.name}
    except (PilotError, OSError, ValueError, KeyError, TypeError) as exc:
        return {"status": "unavailable", "reason": str(exc)}


def collect_status(cfg) -> dict:
    # Reuse the retrieval loaders so an existing but incompatible index is rejected.
    from .cli import _load_bm25, _load_dense_index
    from .indexing import LexicalNormalizer

    result = {"corpus": {}, "models": {}, "indexes": {}}
    reasons = []
    try:
        chunks, manifest = load_frozen_corpus(cfg)
        if cfg.resolve(REFERENCE_PATH).is_file():
            assert_official_corpus(cfg, manifest)
        result["corpus"] = {"documents": len(manifest.doc_ids), "chunks": len(chunks),
                            "frozen": manifest.frozen, "corpus_version": manifest.corpus_version,
                            "status": "valid"}
    except (PilotError, OSError, ValueError, KeyError, TypeError) as exc:
        manifest = None
        result["corpus"] = {"status": "invalid", "reason": str(exc)}
        reasons.append("CORPUS_INVALID")
    for name in cfg.effective_embeddings() + ["reranker"]:
        checkpoint = cfg.models.reranker.checkpoint if name == "reranker" else get_embedding_spec(name).checkpoint
        result["models"][name] = checkpoint_available(
            checkpoint, cfg.resolve(cfg.models.cache_dir), cfg.resolve(cfg.models.revisions_path))
    if any(m["status"] != "available" for m in result["models"].values()):
        reasons.append("LOCAL_MODELS_UNAVAILABLE")
    for name in ["bm25"] + cfg.effective_embeddings():
        if manifest is None:
            result["indexes"][name] = {"status": "unverified", "reason": "corpus inválido"}
            continue
        try:
            if name == "bm25":
                index = _load_bm25(cfg, chunks, LexicalNormalizer(cfg.retrieval.lexical), manifest.corpus_version)
                result["indexes"][name] = {"status": "valid", "documents": index.n_docs, "fingerprint": index.fingerprint}
            else:
                index = _load_dense_index(cfg, name, manifest.corpus_version)
                result["indexes"][name] = {"status": "valid", "shape": list(index.matrix.shape),
                                            "dimension": index.dimension, "fingerprint": index.fingerprint}
            del index
        except (PilotError, OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            result["indexes"][name] = {"status": "invalid", "reason": str(exc)}
    if any(i["status"] != "valid" for i in result["indexes"].values()):
        reasons.append("INDEXES_UNAVAILABLE_OR_INVALID")
    try:
        if manifest is None:
            counts = review_counts(load_questions(cfg.resolve(cfg.paths.questions_path)))
            result["benchmark"] = {
                **counts, "status": "pending_corpus",
                "validation": {"valid": None, "errors": [], "warning_counts": {}},
            }
            reasons.append("BENCHMARK_PENDING_CORPUS")
        else:
            gold = audit_gold(cfg)
            result["benchmark"] = gold
            if not gold["validation"]["valid"]:
                reasons.append("BENCHMARK_STRUCTURAL_ERRORS")
            if gold["draft_ready"] + gold["draft_pending"] or not gold["approved"]:
                reasons.append("HUMAN_GOLD_REVIEW_REQUIRED")
    except (PilotError, OSError, ValueError, KeyError, TypeError) as exc:
        result["benchmark"] = {"status": "invalid", "reason": str(exc)}
        reasons.append("BENCHMARK_STRUCTURAL_ERRORS")
    result["experiment"] = {
        "configurations": len(build_matrix(cfg.effective_embeddings())),
        "ready_for_retrieval": not reasons, "reasons": reasons,
        "readiness_scope": "complete benchmark; drafts require human decisions",
    }
    return result


def cmd_status(args) -> None:
    result = collect_status(load_config(args.config))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Full warnings remain available in JSON; the terminal overview stays short.
        validation = result.get("benchmark", {}).get("validation")
        if validation:
            result["benchmark"]["validation"] = {
                "errors": validation["errors"], "warning_counts": validation["warning_counts"]}
        print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False))


def register_status_parser(subparsers) -> None:
    parser = subparsers.add_parser("status", help="Verifica corpus, modelos locais, índices e gold sem carregar modelos.")
    parser.add_argument("-c", "--config", default=None)
    parser.add_argument("--json", action="store_true", help="Inclui inventário e validação completos em JSON.")
    parser.set_defaults(handler=cmd_status)
