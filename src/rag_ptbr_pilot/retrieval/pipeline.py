"""Pipeline de recuperação controlada (sem acesso a qrels/gold).

Executa as variantes da matriz: BM25, Densa e Híbrida (RRF), com ou sem o
reranker. A variante com reranker recebe EXATAMENTE os mesmos N candidatos da
variante sem reranker correspondente (o reranker só reordena, nunca adiciona).

Registra as listas originais, a união RRF, os candidatos enviados ao reranker e
o ranking final — para medir cobertura antes/depois da seleção top-N.
"""

from __future__ import annotations

from ..adapters.base import EmbeddingAdapter, RerankerAdapter
from ..config import RetrievalConfig
from ..indexing.dense import DenseIndex
from ..indexing.hybrid import rrf_fuse
from ..indexing.lexical import BM25Index, LexicalNormalizer
from ..schemas import ChunkRecord
from ..timing import Timer
from .matrix import ConfigSpec
from .results import QueryRetrieval, RankedChunk


def _ranked(items: list[tuple[str, float]], kind: str) -> list[RankedChunk]:
    out: list[RankedChunk] = []
    for i, (chunk_id, score) in enumerate(items, start=1):
        rc = RankedChunk(chunk_id=chunk_id, score=score, rank=i)
        if kind == "bm25":
            rc.bm25_rank = i
        elif kind == "dense":
            rc.dense_rank = i
        out.append(rc)
    return out


class RetrievalRunner:
    def __init__(self, retrieval_cfg: RetrievalConfig,
                 chunk_by_id: dict[str, ChunkRecord],
                 bm25_index: BM25Index,
                 normalizer: LexicalNormalizer,
                 dense_indices: dict[str, DenseIndex],
                 embedding_adapters: dict[str, EmbeddingAdapter],
                 reranker: RerankerAdapter | None = None) -> None:
        self.cfg = retrieval_cfg
        self.chunk_by_id = chunk_by_id
        self.bm25_index = bm25_index
        self.normalizer = normalizer
        self.dense_indices = dense_indices
        self.embedding_adapters = embedding_adapters
        self.reranker = reranker
        self._qcache: dict[tuple[str, str], object] = {}

    def _bm25(self, query_text: str, top_n: int) -> list[RankedChunk]:
        items = self.bm25_index.search(query_text, self.normalizer, top_n)
        return _ranked(items, "bm25")

    def _dense(self, embedding: str, query_id: str, query_text: str,
               top_n: int) -> list[RankedChunk]:
        qvec = self._encode_query(embedding, query_id, query_text)
        items = self.dense_indices[embedding].search(qvec, top_n)
        return _ranked(items, "dense")

    def _encode_query(self, embedding: str, query_id: str, query_text: str):
        key = (embedding, query_id)
        if key not in self._qcache:
            self._qcache[key] = self.embedding_adapters[embedding].encode_queries([query_text])[0]
        return self._qcache[key]

    def _fuse(self, bm25: list[RankedChunk], dense: list[RankedChunk],
              top_n: int) -> tuple[list[RankedChunk], list[RankedChunk]]:
        rrf = self.cfg.rrf
        bm25_pairs = [(c.chunk_id, c.score if c.score is not None else 0.0) for c in bm25]
        dense_pairs = [(c.chunk_id, c.score if c.score is not None else 0.0) for c in dense]
        fused = rrf_fuse(bm25_pairs, dense_pairs, c=rrf.c,
                         weight_bm25=rrf.weight_bm25, weight_dense=rrf.weight_dense)

        bm25_rank = {c.chunk_id: c.bm25_rank for c in bm25}
        dense_rank = {c.chunk_id: c.dense_rank for c in dense}
        union: list[RankedChunk] = []
        for i, (chunk_id, score) in enumerate(fused, start=1):
            rc = RankedChunk(chunk_id=chunk_id, rrf_score=score, rank=i)
            rc.bm25_rank = bm25_rank.get(chunk_id)
            rc.dense_rank = dense_rank.get(chunk_id)
            union.append(rc)
        return union, union[:top_n]

    def run_query(self, query_id: str, query_text: str,
                  spec: ConfigSpec) -> QueryRetrieval:
        top_n = self.cfg.top_n
        qr = QueryRetrieval(
            query_id=query_id,
            config_id=spec.config_id,
            initial_retrieval=spec.initial_retrieval,
            embedding=spec.embedding,
            rerank=spec.rerank,
        )

        bm25: list[RankedChunk] = []
        dense: list[RankedChunk] = []
        base: list[RankedChunk] = []

        if spec.initial_retrieval in ("bm25", "hybrid"):
            t = Timer()
            bm25 = self._bm25(query_text, top_n)
            qr.bm25 = bm25
            qr.timings["bm25"] = t.stop(sync=False)
        if spec.initial_retrieval in ("dense", "hybrid"):
            assert spec.embedding is not None
            t = Timer()
            dense = self._dense(spec.embedding, query_id, query_text, top_n)
            qr.dense = dense
            qr.timings["dense"] = t.stop()

        if spec.initial_retrieval == "hybrid":
            t = Timer()
            union, topk = self._fuse(bm25, dense, top_n)
            qr.rrf_union = union
            qr.rrf_topn = topk
            qr.timings["rrf"] = t.stop(sync=False)
            base = topk
        elif spec.initial_retrieval == "bm25":
            base = bm25
        else:
            base = dense

        qr.n_available = len(base)

        if spec.rerank:
            qr.candidates_to_rerank = list(base)
            assert self.reranker is not None, "reranker não carregado"
            docs = [self.chunk_by_id[c.chunk_id].text for c in base]
            t = Timer()
            scores = self.reranker.score(query_text, docs)
            qr.timings["rerank"] = t.stop()
            ranked = sorted(zip(base, scores),
                            key=lambda x: (-x[1], x[0].chunk_id))
            final: list[RankedChunk] = []
            for i, (rc, score) in enumerate(ranked, start=1):
                new_rc = RankedChunk(
                    chunk_id=rc.chunk_id, score=score, rank=i,
                    bm25_rank=rc.bm25_rank, dense_rank=rc.dense_rank,
                    rrf_score=rc.rrf_score, rerank_score=score,
                )
                final.append(new_rc)
            qr.final = final
        else:
            qr.final = base

        return qr
