"""Métricas de ordenamento e cobertura (definições e casos extremos).

Definições (protocolo, seção de avaliação):

- ``Recall@k`` = relevantes no top-k / TOTAL de chunks relevantes anotados.
- ``Hit@k`` = 1 se há pelo menos um relevante no top-k (NÃO é sinônimo de Recall).
- ``MRR@10`` = 1/posição do primeiro relevante até a posição 10; 0 se ausente.
- ``nDCG@k`` = DCG/IDCG com qrels BINÁRIOS; IDCG é construído com a relevância
  anotada (todos os relevantes primeiro), nunca só com os candidatos recuperados.
- ``Precision@k`` = relevantes no top-k / min(k, nº de resultados) — denominador
  explícito quando há menos de k resultados.

Uma pergunta sem gold válido é BLOQUEADA (``NoGoldError``), não recebe zero.
"""

from __future__ import annotations

import math

from ..errors import NoGoldError


def _require_relevant(relevant_ids: set[str]) -> None:
    if not relevant_ids:
        raise NoGoldError(
            "pergunta sem gold válido (nenhum chunk relevante anotado); "
            "avaliação bloqueada, não zerada."
        )


def recall_at_k(ranked_ids: list[str], relevant_ids: set[str], k: int) -> float:
    _require_relevant(relevant_ids)
    hits = sum(1 for cid in ranked_ids[:k] if cid in relevant_ids)
    return hits / len(relevant_ids)


def hit_at_k(ranked_ids: list[str], relevant_ids: set[str], k: int) -> float:
    _require_relevant(relevant_ids)
    return 1.0 if any(cid in relevant_ids for cid in ranked_ids[:k]) else 0.0


def mrr_at_k(ranked_ids: list[str], relevant_ids: set[str], k: int) -> float:
    _require_relevant(relevant_ids)
    for i, cid in enumerate(ranked_ids[:k], start=1):
        if cid in relevant_ids:
            return 1.0 / i
    return 0.0


def precision_at_k(ranked_ids: list[str], relevant_ids: set[str], k: int) -> float:
    denom = min(k, len(ranked_ids))  # denominador explícito quando < k
    if denom == 0:
        return 0.0
    hits = sum(1 for cid in ranked_ids[:k] if cid in relevant_ids)
    return hits / denom


def dcg_at_k(ranked_ids: list[str], relevance: dict[str, int], k: int) -> float:
    dcg = 0.0
    for i, cid in enumerate(ranked_ids[:k], start=1):
        rel = 1.0 if relevance.get(cid, 0) >= 1 else 0.0
        dcg += rel / math.log2(i + 1)
    return dcg


def idcg_at_k(n_relevant: int, k: int) -> float:
    ideal = min(k, n_relevant)
    return sum(1.0 / math.log2(i + 1) for i in range(1, ideal + 1))


def ndcg_at_k(ranked_ids: list[str], relevance: dict[str, int], k: int) -> float:
    _require_relevant({cid for cid, rel in relevance.items() if rel >= 1})
    n_rel = sum(1 for rel in relevance.values() if rel >= 1)
    idcg = idcg_at_k(n_rel, k)
    if idcg == 0.0:
        return 0.0
    return dcg_at_k(ranked_ids, relevance, k) / idcg


def compute_metrics(ranked_ids: list[str], relevant_ids: set[str],
                    relevance: dict[str, int],
                    k_values: list[int]) -> dict[str, float]:
    """Calcula todas as métricas para uma pergunta em vários k."""
    _require_relevant(relevant_ids)
    out: dict[str, float] = {}
    for k in k_values:
        out[f"recall@{k}"] = recall_at_k(ranked_ids, relevant_ids, k)
        out[f"hit@{k}"] = hit_at_k(ranked_ids, relevant_ids, k)
        out[f"precision@{k}"] = precision_at_k(ranked_ids, relevant_ids, k)
        out[f"ndcg@{k}"] = ndcg_at_k(ranked_ids, relevance, k)
    out["mrr@10"] = mrr_at_k(ranked_ids, relevant_ids, 10)
    return out
