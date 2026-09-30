"""Resolve pinned checkpoints without consulting a remote registry."""

from pathlib import Path

from ..errors import MissingArtifactError
from ..io_utils import load_json
from ..model_revisions import pinned_revisions
from .specs import EMBEDDING_SPECS, RERANKER_SPEC


def local_checkpoint(checkpoint: str, cache_dir: str | Path | None,
                     revisions_path: str | Path | None = None) -> str:
    if cache_dir is None:
        raise MissingArtifactError("Cache local e revisions.json são obrigatórios; rode prepare-models.")
    root = Path(cache_dir)
    manifest = root / "revisions.json"
    revisions = load_json(manifest).get("revisions", {}) if manifest.exists() else {}
    revision = revisions.get(checkpoint)
    if not revision:
        raise MissingArtifactError(f"Revisão local não registrada para {checkpoint}; rode prepare-models.")
    known = {spec.checkpoint for spec in EMBEDDING_SPECS.values()} | {RERANKER_SPEC.checkpoint}
    if checkpoint in known:
        pins = pinned_revisions(revisions_path or "configs/model_revisions.yaml")
        if revision != pins[checkpoint]:
            raise MissingArtifactError(
                f"Revisão local incompatível para {checkpoint}: {revision}; esperado {pins[checkpoint]}. "
                "Rode prepare-models."
            )
    snapshot = root / ("models--" + checkpoint.replace("/", "--")) / "snapshots" / revision
    if not snapshot.is_dir():
        raise MissingArtifactError(f"Snapshot fixado ausente: {snapshot}; rode prepare-models.")
    return str(snapshot)
