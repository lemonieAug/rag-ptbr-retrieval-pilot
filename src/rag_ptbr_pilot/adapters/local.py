"""Resolve pinned checkpoints without consulting a remote registry."""

from pathlib import Path

from ..errors import MissingArtifactError
from ..io_utils import load_json


def local_checkpoint(checkpoint: str, cache_dir: str | Path | None) -> str:
    if cache_dir is None:
        raise MissingArtifactError("Cache local e revisions.json são obrigatórios; rode prepare-models.")
    root = Path(cache_dir)
    manifest = root / "revisions.json"
    revisions = load_json(manifest).get("revisions", {}) if manifest.exists() else {}
    revision = revisions.get(checkpoint)
    if not revision:
        raise MissingArtifactError(f"Revisão local não registrada para {checkpoint}; rode prepare-models.")
    snapshot = root / ("models--" + checkpoint.replace("/", "--")) / "snapshots" / revision
    if not snapshot.is_dir():
        raise MissingArtifactError(f"Snapshot fixado ausente: {snapshot}; rode prepare-models.")
    return str(snapshot)
