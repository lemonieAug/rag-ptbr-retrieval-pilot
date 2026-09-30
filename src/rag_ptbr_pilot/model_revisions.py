"""Versioned Hugging Face snapshot identities for the scientific run."""

from __future__ import annotations

import re
from pathlib import Path

from .adapters.specs import EMBEDDING_SPECS, RERANKER_SPEC
from .errors import ConfigError
from .io_utils import load_yaml

DEFAULT_REVISIONS_PATH = "configs/model_revisions.yaml"


def pinned_revisions(path: str | Path = DEFAULT_REVISIONS_PATH) -> dict[str, str]:
    try:
        raw = load_yaml(path)
    except OSError as exc:
        raise ConfigError(f"Arquivo de revisões pinadas ausente ou inacessível: {path}") from exc
    entries = raw.get("models", {}) if isinstance(raw, dict) else {}
    expected = {name: spec.checkpoint for name, spec in EMBEDDING_SPECS.items()}
    expected["reranker"] = RERANKER_SPEC.checkpoint
    if not isinstance(entries, dict) or set(entries) != set(expected):
        raise ConfigError("model_revisions.yaml deve declarar exatamente os quatro modelos do piloto.")
    pins = {}
    for name, checkpoint in expected.items():
        entry = entries[name]
        if not isinstance(entry, dict) or entry.get("checkpoint") != checkpoint:
            raise ConfigError(f"Checkpoint pinado incompatível para {name}.")
        revision = entry.get("revision")
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ConfigError(f"Revisão SHA inválida para {name}.")
        pins[checkpoint] = revision
    return pins


def validate_local_revisions(revisions: dict, pins: dict[str, str]) -> None:
    for checkpoint, expected in pins.items():
        if revisions.get(checkpoint) != expected:
            raise ConfigError(
                f"Revisão incompatível ou ausente para {checkpoint}: "
                f"esperada {expected}, encontrada {revisions.get(checkpoint)!r}. "
                "Rode rag-ptbr prepare-models."
            )
