"""Adaptadores de modelos: embeddings, reranker e specs.

Importar este módulo NÃO carrega torch/transformers (imports sob demanda).
"""

from __future__ import annotations

from ..config import AppConfig
from .base import EmbeddingAdapter, RerankerAdapter
from .embeddings import build_embedding_adapter
from .reranker import build_reranker
from .specs import (
    DEFAULT_TASK_INSTRUCTION,
    EMBEDDING_SPECS,
    GENERATOR_SPEC,
    RERANKER_SPEC,
    EmbeddingSpec,
    RerankerSpec,
)

__all__ = [
    "EmbeddingAdapter",
    "RerankerAdapter",
    "EmbeddingSpec",
    "RerankerSpec",
    "EMBEDDING_SPECS",
    "RERANKER_SPEC",
    "GENERATOR_SPEC",
    "DEFAULT_TASK_INSTRUCTION",
    "get_embedding_adapter",
    "get_reranker_adapter",
]


def get_embedding_adapter(name: str, cfg: AppConfig) -> EmbeddingAdapter:
    dtype = getattr(cfg.models.dtype, name, None)
    return build_embedding_adapter(
        name,
        cache_dir=cfg.resolve(cfg.models.cache_dir),
        device=cfg.models.device,
        dtype=dtype,
    )


def get_reranker_adapter(cfg: AppConfig) -> RerankerAdapter:
    return build_reranker(
        cache_dir=cfg.resolve(cfg.models.cache_dir),
        device=cfg.models.reranker.device,
        dtype=cfg.models.reranker.dtype,
        max_length=cfg.models.reranker.max_length,
    )
