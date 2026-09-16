"""Testes de grupos de evidência: alternativas (OR) e cobertura completa."""

import pytest

from rag_ptbr_pilot.metrics.coverage import (
    all_groups_covered,
    group_coverage,
    recall_in_set,
    required_groups,
)
from rag_ptbr_pilot.schemas import EvidenceGroup


def _group(gid, chunk_ids, required=True):
    return EvidenceGroup(group_id=gid, question_id="q1", required=required,
                         chunk_ids=chunk_ids)


def test_alternatives_satisfy_same_group():
    g1 = _group("g1", ["a", "b"])
    g2 = _group("g2", ["c"])
    ranked = ["b", "c", "z"]  # "b" satisfaz g1 (alternativa), "c" satisfaz g2
    gc = group_coverage(ranked, [g1, g2])
    assert gc["covered"] == 2
    assert gc["total"] == 2
    assert gc["fraction"] == pytest.approx(1.0)
    assert all_groups_covered(ranked, [g1, g2]) is True


def test_partial_coverage_and_required_only():
    g1 = _group("g1", ["a", "b"])
    g2 = _group("g2", ["c"])
    g_optional = _group("g3", ["d"], required=False)
    ranked = ["a", "z"]
    assert all_groups_covered(ranked, [g1, g2, g_optional]) is False
    gc = group_coverage(ranked, [g1, g2, g_optional])
    assert gc["total"] == 2  # opcional não conta
    assert gc["fraction"] == pytest.approx(0.5)
    # required_groups ignora opcionais
    assert [g.group_id for g in required_groups([g1, g2, g_optional])] == ["g1", "g2"]


def test_recall_in_set_uses_total_relevant():
    assert recall_in_set(["a", "b"], {"a", "c"}) == pytest.approx(0.5)
    assert recall_in_set([], {"a"}) == 0.0
