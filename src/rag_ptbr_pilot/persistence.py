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


def load_frozen_corpus(cfg):
    """Check the actual chunk content before trusting a manifest fingerprint."""
    from .chunking.chunker import compute_corpus_version
    from .errors import ConfigError

    missing = [str(cfg.resolve(path)) for path in
               (cfg.paths.chunks_path, cfg.paths.corpus_manifest_path)
               if not cfg.resolve(path).is_file()]
    if missing:
        raise ConfigError(
            "Corpus auditado ausente: " + ", ".join(missing) +
            ". Transfira os arquivos congelados para os caminhos esperados."
        )
    chunks = load_chunks(cfg.resolve(cfg.paths.chunks_path))
    manifest = load_manifest(cfg.resolve(cfg.paths.corpus_manifest_path))
    actual = compute_corpus_version(chunks)
    if (not manifest.frozen or len(chunks) != manifest.chunk_count
            or actual != manifest.corpus_version
            or actual != manifest.hashes.get("chunks")
            or sorted({c.doc_id for c in chunks}) != sorted(manifest.doc_ids)
            or len({c.chunk_id for c in chunks}) != len(chunks)
            or any(not c.text.strip() for c in chunks)):
        raise ConfigError("Corpus congelado incompatível com o manifesto; restaure a versão verificada.")
    return chunks, manifest
