"""Benchmark: carregamento, validação e separação gold/entrada."""

from .leakage import (
    GOLD_FIELDS,
    assert_no_leakage,
    check_leakage,
    retrieval_query,
)
from .loaders import (
    load_articles,
    load_evidence_groups,
    load_qrels,
    load_questions,
)
from .validation import ValidationReport, validate_benchmark

__all__ = [
    "GOLD_FIELDS",
    "ValidationReport",
    "assert_no_leakage",
    "check_leakage",
    "load_articles",
    "load_evidence_groups",
    "load_qrels",
    "load_questions",
    "retrieval_query",
    "validate_benchmark",
]
