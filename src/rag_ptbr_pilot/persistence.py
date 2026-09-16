"""Persistência de chunks, manifesto e artefatos (leitura/escrita)."""

from __future__ import annotations

from pathlib import Path

from .io_utils import load_json, load_jsonl, save_json, save_jsonl
from .schemas import ChunkRecord, CorpusManifest


def save_chunks(path: str | Path, chunks: list[ChunkRecord]) -> None:
    save_jsonl(path, [c.model_dump(mode="json") for c in chunks])


def load_chunks(path: str | Path) -> list[ChunkRecord]:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Chunks não encontrados: {path}. Rode primeiro: rag-ptbr chunk."
        )
    return [ChunkRecord.model_validate(d) for d in load_jsonl(path)]


def save_manifest(path: str | Path, manifest: CorpusManifest) -> None:
    save_json(path, manifest.model_dump(mode="json"))


def load_manifest(path: str | Path) -> CorpusManifest:
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Manifesto do corpus não encontrado: {path}. Rode: rag-ptbr chunk."
        )
    return CorpusManifest.model_validate(load_json(path))
