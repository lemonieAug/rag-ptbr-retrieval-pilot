"""Índices e estratégias de recuperação (BM25, densa, híbrida RRF)."""

from .dense import DenseIndex
from .hybrid import rrf_fuse
from .lexical import BM25Index, LexicalNormalizer
from .store import (
    bm25_fingerprint,
    dense_fingerprint,
    ensure_compatible,
)

__all__ = [
    "BM25Index",
    "DenseIndex",
    "LexicalNormalizer",
    "rrf_fuse",
    "bm25_fingerprint",
    "dense_fingerprint",
    "ensure_compatible",
]
