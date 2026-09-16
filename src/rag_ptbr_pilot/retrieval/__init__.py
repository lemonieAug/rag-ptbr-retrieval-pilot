"""Recuperação e reranking controlados."""

from .matrix import (
    Comparison,
    ConfigSpec,
    base_config_id,
    build_matrix,
    select_matrix,
    standard_comparisons,
)
from .pipeline import RetrievalRunner
from .results import QueryRetrieval, RankedChunk

__all__ = [
    "Comparison",
    "ConfigSpec",
    "QueryRetrieval",
    "RankedChunk",
    "RetrievalRunner",
    "base_config_id",
    "build_matrix",
    "select_matrix",
    "standard_comparisons",
]
