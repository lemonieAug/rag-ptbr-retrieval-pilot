"""Etapa EXPLÍCITA de obtenção de modelos (única que baixa checkpoints).

Nenhuma outra etapa baixa modelos silenciosamente: os adaptadores carregam
com ``local_files_only=True`` e falham com instrução útil se o artefato faltar.

``rag-ptbr prepare-models`` baixa os 4 embeddings + o reranker para o cache
local e grava as revisões reais em ``artifacts/models/revisions.json`` (para o
manifesto de execução). O EmbeddingGemma é gated e exige ``HF_TOKEN``.
"""

from __future__ import annotations

from .adapters.specs import EMBEDDING_SPECS, RERANKER_SPEC
from .config import AppConfig
from .io_utils import save_json


def fetch_models(cfg: AppConfig) -> dict:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError(
            "huggingface-hub não instalado. Instale: pip install -e '.[models]'"
        ) from exc

    cache_dir = str(cfg.resolve(cfg.models.cache_dir))
    embeddings = cfg.effective_embeddings()
    repos = [EMBEDDING_SPECS[e].checkpoint for e in embeddings]
    repos.append(RERANKER_SPEC.checkpoint)

    revisions: dict[str, str | None] = {}
    for repo in repos:
        print(f"[prepare-models] Baixando {repo} -> {cache_dir}")
        snapshot_download(repo_id=repo, cache_dir=cache_dir)
        revisions[repo] = _resolve_revision(repo)

    out_path = cfg.resolve(cfg.models.cache_dir) / "revisions.json"
    save_json(out_path, {"revisions": revisions})
    return revisions


def _resolve_revision(repo: str) -> str | None:
    try:
        from huggingface_hub import HfApi

        return HfApi().model_info(repo).sha
    except Exception:
        return None
