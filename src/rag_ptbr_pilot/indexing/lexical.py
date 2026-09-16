"""Normalização lexical (Unicode/PT-BR) e BM25 local.

Normalização IDÊNTICA para documentos e consultas. Sem stemming, sem remoção de
acentos, sem stopwords (evitar ablações adicionais). Acentos são preservados;
Unicode é normalizado via NFKC para consistência.

BM25: k1 = 1.2, b = 0.75 (defaults registrados e configuráveis).
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field

from ..config import LexicalConfig
from ..schemas import ChunkRecord


class LexicalNormalizer:
    """Normaliza e tokeniza textos de forma fixa e determinística."""

    def __init__(self, config: LexicalConfig | None = None) -> None:
        cfg = config or LexicalConfig()
        self.lowercase = cfg.lowercase
        self.strip_accents = cfg.strip_accents
        self.unicode_nfkc = cfg.unicode_nfkc
        self.token_pattern = cfg.token_pattern

    def normalize(self, text: str) -> str:
        if self.unicode_nfkc:
            text = unicodedata.normalize("NFKC", text)
        if self.lowercase:
            text = text.lower()
        # strip_accents é FALSO por padrão (decisão metodológica).
        return text

    def tokenize(self, text: str) -> list[str]:
        norm = self.normalize(text)
        return re.findall(self.token_pattern, norm, re.UNICODE)


@dataclass
class BM25Index:
    """Índice BM25 em memória, serializável para JSON."""

    k1: float = 1.2
    b: float = 0.75
    chunk_ids: list[str] = field(default_factory=list)
    doc_lengths: dict[str, int] = field(default_factory=dict)
    doc_terms: dict[str, list[str]] = field(default_factory=dict)
    df: dict[str, int] = field(default_factory=dict)
    avgdl: float = 0.0
    n_docs: int = 0
    fingerprint: str = ""

    def build(self, chunks: list[ChunkRecord], normalizer: LexicalNormalizer) -> None:
        self.chunk_ids = []
        self.doc_lengths = {}
        self.doc_terms = {}
        self.df = {}
        for c in chunks:
            terms = normalizer.tokenize(c.text)
            self.chunk_ids.append(c.chunk_id)
            self.doc_lengths[c.chunk_id] = len(terms)
            self.doc_terms[c.chunk_id] = terms
            for t in set(terms):
                self.df[t] = self.df.get(t, 0) + 1
        self.n_docs = len(self.chunk_ids)
        total = sum(self.doc_lengths.values())
        self.avgdl = total / self.n_docs if self.n_docs else 0.0

    def _idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query: str, normalizer: LexicalNormalizer,
               top_n: int) -> list[tuple[str, float]]:
        qterms = normalizer.tokenize(query)
        scores: dict[str, float] = {}
        for term in qterms:
            idf = self._idf(term)
            if idf == 0.0:
                continue
            for cid in self.chunk_ids:
                tf = self.doc_terms[cid].count(term)
                if tf == 0:
                    continue
                dl = self.doc_lengths[cid]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[cid] = scores.get(cid, 0.0) + idf * (tf * (self.k1 + 1)) / denom
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_n]

    def to_dict(self) -> dict:
        return {
            "k1": self.k1,
            "b": self.b,
            "chunk_ids": self.chunk_ids,
            "doc_lengths": self.doc_lengths,
            "df": self.df,
            "avgdl": self.avgdl,
            "n_docs": self.n_docs,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BM25Index":
        idx = cls(
            k1=data["k1"],
            b=data["b"],
            chunk_ids=data["chunk_ids"],
            doc_lengths=data["doc_lengths"],
            df=data["df"],
            avgdl=data["avgdl"],
            n_docs=data["n_docs"],
        )
        idx.fingerprint = data.get("fingerprint", "")
        # Reconstrói doc_terms (não serializado, para manter o arquivo enxuto).
        idx.doc_terms = {}
        return idx

    def rebuild_terms(self, chunks: list[ChunkRecord],
                      normalizer: LexicalNormalizer) -> None:
        by_id = {c.chunk_id: c for c in chunks}
        self.doc_terms = {
            cid: normalizer.tokenize(by_id[cid].text)
            for cid in self.chunk_ids if cid in by_id
        }
