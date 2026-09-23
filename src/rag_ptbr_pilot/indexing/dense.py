"""Índice denso em NumPy (busca exata por cosseno).

Vetores são normalizados (norma L2 = 1), então cosseno = produto interno. Sem
banco vetorial: o corpus é pequeno e a busca exata em NumPy é suficiente.

O índice é persistido como ``matrix.npy`` + ``meta.json``, com ``fingerprint``
que invalida o cache quando corpus/modelo/dimensão mudam.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..io_utils import load_json, save_json


@dataclass
class DenseIndex:
    embedding_name: str
    checkpoint: str
    revision: str | None
    dimension: int
    chunk_ids: list[str] = field(default_factory=list)
    matrix: np.ndarray | None = None
    fingerprint: str = ""
    encoding_config: dict | None = None

    def search(self, query_vector: np.ndarray,
               top_n: int) -> list[tuple[str, float]]:
        if self.matrix is None:
            raise RuntimeError("Índice denso não carregado")
        q = np.asarray(query_vector, dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-12)
        scores = (self.matrix @ q).astype(np.float64)
        scored = list(zip(self.chunk_ids, scores.tolist()))
        scored.sort(key=lambda kv: (-kv[1], kv[0]))
        return scored[:top_n]

    def to_meta(self) -> dict:
        return {
            "embedding_name": self.embedding_name,
            "checkpoint": self.checkpoint,
            "revision": self.revision,
            "dimension": self.dimension,
            "chunk_ids": self.chunk_ids,
            "fingerprint": self.fingerprint,
            "encoding_config": self.encoding_config,
        }

    @classmethod
    def from_meta(cls, meta: dict, matrix: np.ndarray) -> "DenseIndex":
        return cls(
            embedding_name=meta["embedding_name"],
            checkpoint=meta["checkpoint"],
            revision=meta.get("revision"),
            dimension=meta["dimension"],
            chunk_ids=meta["chunk_ids"],
            matrix=matrix,
            fingerprint=meta.get("fingerprint", ""),
            encoding_config=meta.get("encoding_config"),
        )

    def save(self, out_dir: str | Path) -> None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        np.save(out_dir / "matrix.npy", self.matrix.astype(np.float32))
        save_json(out_dir / "meta.json", self.to_meta())

    @classmethod
    def load(cls, out_dir: str | Path) -> "DenseIndex":
        out_dir = Path(out_dir)
        meta = load_json(out_dir / "meta.json")
        try:
            matrix = np.load(out_dir / "matrix.npy", allow_pickle=False)
        except EOFError as exc:
            raise ValueError(f"Índice denso corrompido: {out_dir}") from exc
        if (not np.issubdtype(matrix.dtype, np.floating)
                or matrix.ndim != 2
                or matrix.shape != (len(meta["chunk_ids"]), meta["dimension"])
                or len(set(meta["chunk_ids"])) != len(meta["chunk_ids"])
                or not np.isfinite(matrix).all()
                or not np.allclose(np.linalg.norm(matrix, axis=1), 1.0, atol=1e-3)):
            raise ValueError(f"Índice denso corrompido: {out_dir}")
        return cls.from_meta(meta, matrix)
