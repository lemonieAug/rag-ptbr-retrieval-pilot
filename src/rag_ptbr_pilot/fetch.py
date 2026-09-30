"""Etapa EXPLÍCITA de obtenção de modelos (única que baixa checkpoints).

Nenhuma outra etapa baixa modelos silenciosamente: os adaptadores carregam
com ``local_files_only=True`` e falham com instrução útil se o artefato faltar.

``rag-ptbr prepare-models`` baixa os embeddings ativos (config: colibri,
qwen_embedding, e5 — todos de acesso livre) + o reranker para o cache local e
grava as revisões reais em ``artifacts/models/revisions.json`` (para o
manifesto de execução).
"""

from __future__ import annotations

from pathlib import Path

from .adapters.specs import EMBEDDING_SPECS, RERANKER_SPEC
from .config import AppConfig
from .errors import ConfigError
from .io_utils import save_json
from .model_revisions import pinned_revisions


def fetch_models(cfg: AppConfig) -> dict:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError(
            "huggingface-hub não instalado. Instale: pip install -e '.[models]'"
        ) from exc

    cache_dir = str(cfg.resolve(cfg.models.cache_dir))
    repos = [spec.checkpoint for spec in EMBEDDING_SPECS.values()]
    repos.append(RERANKER_SPEC.checkpoint)

    pins = pinned_revisions(cfg.resolve(cfg.models.revisions_path))
    revisions: dict[str, str] = {}
    for repo in repos:
        revision = pins[repo]
        print(f"[prepare-models] Baixando {repo}@{revision} -> {cache_dir}")
        snapshot = Path(snapshot_download(repo_id=repo, revision=revision, cache_dir=cache_dir))
        expected_parent = "models--" + repo.replace("/", "--")
        if (snapshot.name != revision or snapshot.parent.name != "snapshots"
                or snapshot.parent.parent.name != expected_parent or not snapshot.is_dir()):
            raise ConfigError(f"Snapshot incompatível para {repo}: {snapshot}; esperado {revision}.")
        revisions[repo] = revision

    out_path = cfg.resolve(cfg.models.cache_dir) / "revisions.json"
    save_json(out_path, {"revisions": revisions})
    from .status import checkpoint_available
    for repo in repos:
        state = checkpoint_available(repo, cfg.resolve(cfg.models.cache_dir),
                                     cfg.resolve(cfg.models.revisions_path))
        if state["status"] != "available":
            raise ConfigError(f"Snapshot incompleto para {repo}: {state['reason']}")
    return revisions
