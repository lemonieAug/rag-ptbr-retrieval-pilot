"""Métricas, análise de cobertura e erros."""

from .coverage import (
    all_groups_covered,
    group_coverage,
    recall_in_set,
    required_groups,
)
from .ranking import (
    compute_metrics,
    dcg_at_k,
    hit_at_k,
    idcg_at_k,
    mrr_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)

__all__ = [
    "all_groups_covered",
    "compute_metrics",
    "dcg_at_k",
    "group_coverage",
    "hit_at_k",
    "idcg_at_k",
    "mrr_at_k",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "recall_in_set",
    "required_groups",
]
