"""Igualdade dos candidatos antes/depois do reranking.

A variante COM reranker deve receber EXATAMENTE os mesmos N candidatos da
variante SEM reranker correspondente; o reranker apenas reordena (permutação),
não adiciona nem remove documentos.
"""

import numpy as np

from rag_ptbr_pilot.config import RetrievalConfig
from rag_ptbr_pilot.indexing.lexical import BM25Index, LexicalNormalizer
from rag_ptbr_pilot.retrieval.matrix import ConfigSpec
from rag_ptbr_pilot.retrieval.pipeline import RetrievalRunner
from rag_ptbr_pilot.schemas import ChunkRecord


def _chunk(cid, text):
    return ChunkRecord(chunk_id=cid, doc_id="d", block_id=cid, text=text,
                       token_count_ref=10, char_count=len(text))


class FakeDenseIndex:
    def __init__(self, ranked):
        self.ranked = ranked

    def search(self, qvec, top_n):
        return list(self.ranked[:top_n])


class FakeEmbedding:
    def encode_queries(self, texts):
        return np.zeros((len(texts), 3), dtype=np.float32)


class FakeReranker:
    def score(self, query, documents):
        # Reverte a ordem (apenas reordena).
        return [float(len(documents) - i) for i in range(len(documents))]


def _build_runner():
    chunks = [_chunk(f"c{i}", f"documento {i} sobre anemia ferropriva em crianças")
              for i in range(10)]
    bm25 = BM25Index(k1=1.2, b=0.75)
    bm25.build(chunks, LexicalNormalizer())
    dense = FakeDenseIndex([(f"c{i}", float(10 - i)) for i in range(10)])
    runner = RetrievalRunner(
        RetrievalConfig(),
        {c.chunk_id: c for c in chunks},
        bm25,
        LexicalNormalizer(),
        {"e5": dense},
        {"e5": FakeEmbedding()},
        FakeReranker(),
    )
    return runner


def _assert_same_candidates(runner, base_spec, rerank_spec):
    base = runner.run_query("q1", "anemia ferropriva", base_spec)
    rerank = runner.run_query("q1", "anemia ferropriva", rerank_spec)
    base_ids = [c.chunk_id for c in base.final]
    cand_ids = [c.chunk_id for c in rerank.candidates_to_rerank]
    final_ids = [c.chunk_id for c in rerank.final]
    assert cand_ids == base_ids  # mesmos N candidatos, mesma ordem
    assert set(final_ids) == set(cand_ids)  # reranker só reordena
    assert len(final_ids) == len(cand_ids)


def test_bm25_rerank_candidates_equal_bm25_final():
    runner = _build_runner()
    _assert_same_candidates(
        runner,
        ConfigSpec("bm25", "bm25", None, False),
        ConfigSpec("bm25_rerank", "bm25", None, True),
    )


def test_dense_rerank_candidates_equal_dense_final():
    runner = _build_runner()
    _assert_same_candidates(
        runner,
        ConfigSpec("dense_e5", "dense", "e5", False),
        ConfigSpec("dense_e5_rerank", "dense", "e5", True),
    )


def test_hybrid_rerank_candidates_equal_hybrid_final():
    runner = _build_runner()
    _assert_same_candidates(
        runner,
        ConfigSpec("hybrid_e5", "hybrid", "e5", False),
        ConfigSpec("hybrid_e5_rerank", "hybrid", "e5", True),
    )
