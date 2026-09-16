"""Testes de RRF: ranks (1-based), soma de contribuições, dedup e desempate."""

import pytest

from rag_ptbr_pilot.indexing.hybrid import rrf_fuse


def test_rrf_accumulates_contributions_and_orders():
    bm25 = [("a", 5.0), ("b", 4.0)]
    dense = [("b", 9.0), ("c", 8.0)]
    out = rrf_fuse(bm25, dense, c=60.0, weight_bm25=1.0, weight_dense=1.0)
    scores = dict(out)
    assert scores["a"] == pytest.approx(1 / 61.0)
    assert scores["c"] == pytest.approx(1 / 62.0)
    assert scores["b"] == pytest.approx(1 / 62.0 + 1 / 61.0)
    # b (acumulado) > a (1/61) > c (1/62)
    assert [cid for cid, _ in out] == ["b", "a", "c"]


def test_rrf_dedup_by_chunk_id():
    # chunk "a" aparece nas duas listas: não pode aparecer duplicado.
    bm25 = [("a", 1.0)]
    dense = [("a", 2.0)]
    out = rrf_fuse(bm25, dense, c=60.0)
    ids = [cid for cid, _ in out]
    assert ids == ["a"]
    assert dict(out)["a"] == pytest.approx(1 / 61.0 + 1 / 61.0)


def test_rrf_deterministic_tiebreak():
    # Contribuições iguais -> desempate determinístico por chunk_id.
    bm25 = [("x", 1.0)]
    dense = [("y", 1.0)]
    out = rrf_fuse(bm25, dense, c=60.0)
    assert out == [("x", 1 / 61.0), ("y", 1 / 61.0)]


def test_rrf_ranks_start_at_one():
    # rank 1 -> contribuição 1/(c+1), nunca 1/(c+0).
    out = rrf_fuse([("a", 0.0)], [], c=60.0)
    assert dict(out)["a"] == pytest.approx(1 / 61.0)


def test_rrf_weights():
    bm25 = [("a", 1.0)]
    dense = [("b", 1.0)]
    out = rrf_fuse(bm25, dense, c=60.0, weight_bm25=2.0, weight_dense=0.5)
    scores = dict(out)
    assert scores["a"] == pytest.approx(2.0 / 61.0)
    assert scores["b"] == pytest.approx(0.5 / 61.0)
