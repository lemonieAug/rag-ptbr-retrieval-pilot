"""Fingerprints de cache e invalidação de índices/embeddings.

Cada artefato derivado (índice BM25, índice denso) guarda um ``fingerprint``.
Na carga, o fingerprint é recalculado a partir do estado atual (corpus, modelo,
dimensão, parâmetros); se divergir, o cache é considerado incompatível e deve
ser reconstruído — NUNCA reutilizado silenciosamente.
"""

from __future__ import annotations

from ..manifest import hash_json


def bm25_fingerprint(corpus_version: str, k1: float, b: float,
                     lexical_config: dict) -> str:
    return hash_json({
        "kind": "bm25",
        "corpus_version": corpus_version,
        "k1": k1,
        "b": b,
        "lexical": lexical_config,
    })


def dense_fingerprint(corpus_version: str, embedding_name: str, checkpoint: str,
                      revision: str | None, dimension: int) -> str:
    return hash_json({
        "kind": "dense",
        "corpus_version": corpus_version,
        "embedding_name": embedding_name,
        "checkpoint": checkpoint,
        "revision": revision,
        "dimension": dimension,
    })


def ensure_compatible(stored: str, expected: str, what: str) -> None:
    """Levanta se o fingerprint armazenado não confere com o esperado."""
    if stored != expected:
        raise RuntimeError(
            f"Cache incompatível para {what}: o corpus, o modelo, a dimensão ou "
            f"os parâmetros mudaram. Reconstrua o índice (rag-ptbr index)."
        )
