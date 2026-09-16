"""Testes das métricas de ranking e seus casos extremos."""

import math

import pytest

from rag_ptbr_pilot.errors import NoGoldError
from rag_ptbr_pilot.metrics.ranking import (
    hit_at_k,
    mrr_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def test_recall_denominator_is_total_relevant():
    ranked = ["a", "b", "c", "d"]
    relevant = {"b", "d"}  # total = 2
    assert recall_at_k(ranked, relevant, 2) == pytest.approx(0.5)  # só "b"
    assert recall_at_k(ranked, relevant, 4) == pytest.approx(1.0)


def test_hit_is_not_recall():
    ranked = ["a", "b"]
    relevant = {"b"}
    assert hit_at_k(ranked, relevant, 1) == 0.0
    assert hit_at_k(ranked, relevant, 2) == 1.0
    # recall@1 = 0 (b está fora), mas hit@2=1: hit mede presença, recall mede cobertura
    assert recall_at_k(ranked, relevant, 1) == 0.0


def test_mrr_first_relevant_position():
    ranked = ["x", "a", "y"]
    relevant = {"a"}
    assert mrr_at_k(ranked, relevant, 10) == pytest.approx(0.5)
    assert mrr_at_k(["a"], {"b"}, 10) == 0.0  # ausente -> zero


def test_precision_denominator_when_fewer_than_k():
    ranked = ["a", "b"]
    relevant = {"a"}
    # denominador = min(k, len(ranked)) = 2
    assert precision_at_k(ranked, relevant, 5) == pytest.approx(0.5)


def test_ndcg_binary_with_idcg_from_annotation():
    # 1 relevante na posição 1 -> DCG = IDCG = 1/log2(2) -> nDCG = 1
    assert ndcg_at_k(["a", "b"], {"a": 1}, 2) == pytest.approx(1.0)
    # relevante na posição 2 -> nDCG = (1/log2(3)) / (1/log2(2))
    expected = (1.0 / math.log2(3)) / (1.0 / math.log2(2))
    assert ndcg_at_k(["x", "a"], {"a": 1}, 2) == pytest.approx(expected)


def test_ndcg_never_built_from_retrieved_only():
    # Mesmo ranking, mas com um relevante anotado FORA do ranking não recuperado:
    # IDCG deve considerar todos os relevantes anotados (2), não só os recuperados.
    ranked = ["a"]
    relevance = {"a": 1, "z": 1}  # "z" é relevante e não foi recuperado
    dcg = 1.0 / math.log2(2)
    idcg = (1.0 / math.log2(2)) + (1.0 / math.log2(3))
    assert ndcg_at_k(ranked, relevance, 2) == pytest.approx(dcg / idcg)


def test_no_gold_blocks_instead_of_zero():
    with pytest.raises(NoGoldError):
        recall_at_k(["a"], set(), 5)
    with pytest.raises(NoGoldError):
        ndcg_at_k(["a"], {}, 5)
    with pytest.raises(NoGoldError):
        hit_at_k(["a"], set(), 5)
