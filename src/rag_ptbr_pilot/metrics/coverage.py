"""Cobertura de informações necessárias (grupos obrigatórios) e de candidatos.

Os qrels convencionais e a cobertura de grupos obrigatórios respondem a
perguntas DIFERENTES e ficam separados:

- ``recall_in_set``: fração dos chunks relevantes presentes em um conjunto
  candidato (usada para medir cobertura antes/depois da seleção top-N da fusão).
- ``group_coverage``: fração dos grupos obrigatórios satisfeitos por um ranking.
"""

from __future__ import annotations

from ..errors import NoGoldError
from ..schemas import EvidenceGroup


def recall_in_set(candidate_ids: list[str], relevant_ids: set[str]) -> float:
    """Fração dos relevantes presentes no conjunto candidato (sem rank)."""
    if not relevant_ids:
        raise NoGoldError("pergunta sem gold válido")
    if not candidate_ids:
        return 0.0
    hits = sum(1 for cid in set(candidate_ids) if cid in relevant_ids)
    return hits / len(relevant_ids)


def required_groups(groups: list[EvidenceGroup]) -> list[EvidenceGroup]:
    return [g for g in groups if g.required]


def _group_satisfied(group: EvidenceGroup, present: set[str]) -> bool:
    return any(cid in present for cid in group.chunk_ids)


def group_coverage(ranked_ids: list[str], groups: list[EvidenceGroup]) -> dict:
    """Fração de grupos obrigatórios cobertos por um ranking."""
    req = required_groups(groups)
    if not req:
        return {"covered": 0, "total": 0, "fraction": 0.0, "covered_ids": []}
    present = set(ranked_ids)
    covered_ids = [g.group_id for g in req if _group_satisfied(g, present)]
    return {
        "covered": len(covered_ids),
        "total": len(req),
        "fraction": len(covered_ids) / len(req),
        "covered_ids": covered_ids,
    }


def all_groups_covered(ranked_ids: list[str], groups: list[EvidenceGroup]) -> bool:
    req = required_groups(groups)
    if not req:
        return True
    present = set(ranked_ids)
    return all(_group_satisfied(g, present) for g in req)
