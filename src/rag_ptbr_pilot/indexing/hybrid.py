"""Fusão híbrida BM25 + Dense via Reciprocal Rank Fusion (RRF).

Não soma scores brutos (BM25 e cosseno têm escalas diferentes). Em vez disso:

1. Recebe o top-N de cada recuperador (ranks iniciados em 1).
2. Une por ``chunk_id``, acumulando contribuições quando o chunk aparece nas duas
   listas: ``contribuição = peso / (c + rank)``.
3. Ordena com desempate determinístico (score decrescente, depois chunk_id).

A seleção dos top-N da fusão acontece no pipeline (e sua cobertura é medida
antes e depois — pode excluir evidências).
"""

from __future__ import annotations


def rrf_fuse(bm25_ranked: list[tuple[str, float]],
             dense_ranked: list[tuple[str, float]],
             c: float = 60.0,
             weight_bm25: float = 1.0,
             weight_dense: float = 1.0) -> list[tuple[str, float]]:
    """Funde duas listas ranqueadas via RRF (ranks 1-based).

    Retorna pares ``(chunk_id, rrf_score)`` ordenados, com IDs deduplicados e
    contribuições acumuladas.
    """
    contributions: dict[str, float] = {}
    for rank, (chunk_id, _score) in enumerate(bm25_ranked, start=1):
        contributions[chunk_id] = contributions.get(chunk_id, 0.0) + weight_bm25 / (c + rank)
    for rank, (chunk_id, _score) in enumerate(dense_ranked, start=1):
        contributions[chunk_id] = contributions.get(chunk_id, 0.0) + weight_dense / (c + rank)

    ranked = sorted(contributions.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked
