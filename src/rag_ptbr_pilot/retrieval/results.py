"""Estruturas de resultado da recuperação (serializáveis, sem qrels).

O pipeline de recuperação NÃO recebe qrels/gold — registra apenas as listas
ranqueadas e as coberturas de candidatos são calculadas depois, na avaliação.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class RankedChunk:
    """Um chunk ranqueado com scores/ranks de proveniência preservados."""

    chunk_id: str
    score: float | None = None
    rank: int | None = None
    bm25_rank: int | None = None
    dense_rank: int | None = None
    rrf_score: float | None = None
    rerank_score: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RankedChunk":
        fields = {"chunk_id", "score", "rank", "bm25_rank", "dense_rank",
                  "rrf_score", "rerank_score"}
        return cls(**{k: v for k, v in d.items() if k in fields})


@dataclass
class QueryRetrieval:
    """Resultado de uma consulta sob uma configuração."""

    query_id: str
    config_id: str
    initial_retrieval: str
    embedding: str | None
    rerank: bool
    bm25: list[RankedChunk] = field(default_factory=list)
    dense: list[RankedChunk] = field(default_factory=list)
    rrf_union: list[RankedChunk] = field(default_factory=list)
    rrf_topn: list[RankedChunk] = field(default_factory=list)
    candidates_to_rerank: list[RankedChunk] = field(default_factory=list)
    final: list[RankedChunk] = field(default_factory=list)
    n_available: int = 0          # nº de chunks usados quando < N
    timings: dict = field(default_factory=dict)

    def final_ids(self) -> list[str]:
        return [c.chunk_id for c in self.final]

    def stage_ids(self, stage: str) -> list[str]:
        mapping = {
            "bm25": self.bm25,
            "dense": self.dense,
            "rrf_union": self.rrf_union,
            "rrf_topn": self.rrf_topn,
            "to_rerank": self.candidates_to_rerank,
            "final": self.final,
        }
        return [c.chunk_id for c in mapping.get(stage, [])]

    def to_dict(self) -> dict:
        return {
            "query_id": self.query_id,
            "config_id": self.config_id,
            "initial_retrieval": self.initial_retrieval,
            "embedding": self.embedding,
            "rerank": self.rerank,
            "n_available": self.n_available,
            "timings": self.timings,
            "bm25": [c.to_dict() for c in self.bm25],
            "dense": [c.to_dict() for c in self.dense],
            "rrf_union": [c.to_dict() for c in self.rrf_union],
            "rrf_topn": [c.to_dict() for c in self.rrf_topn],
            "candidates_to_rerank": [c.to_dict() for c in self.candidates_to_rerank],
            "final": [c.to_dict() for c in self.final],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "QueryRetrieval":
        return cls(
            query_id=d["query_id"],
            config_id=d["config_id"],
            initial_retrieval=d["initial_retrieval"],
            embedding=d.get("embedding"),
            rerank=d.get("rerank", False),
            bm25=[RankedChunk.from_dict(x) for x in d.get("bm25", [])],
            dense=[RankedChunk.from_dict(x) for x in d.get("dense", [])],
            rrf_union=[RankedChunk.from_dict(x) for x in d.get("rrf_union", [])],
            rrf_topn=[RankedChunk.from_dict(x) for x in d.get("rrf_topn", [])],
            candidates_to_rerank=[RankedChunk.from_dict(x) for x in d.get("candidates_to_rerank", [])],
            final=[RankedChunk.from_dict(x) for x in d.get("final", [])],
            n_available=d.get("n_available", 0),
            timings=d.get("timings", {}),
        )
