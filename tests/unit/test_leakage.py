"""Separação entre gold/avaliação e a entrada dos métodos (anti-vazamento)."""

import pytest

from rag_ptbr_pilot.benchmark.leakage import (
    assert_no_leakage,
    check_leakage,
    retrieval_query,
)
from rag_ptbr_pilot.schemas import Question


def _question():
    return Question(
        question_id="q1",
        text="Qual a prevalência relatada?",
        expected_answer="20,9%",
        origin_doc_id="art-001",
    )


def test_retrieval_query_is_only_question_text():
    q = _question()
    assert retrieval_query(q) == "Qual a prevalência relatada?"


def test_no_leakage_on_clean_query():
    q = _question()
    assert check_leakage("Qual a prevalência relatada?", q) == []


def test_detects_expected_answer_leak():
    q = _question()
    leaks = check_leakage("responda sabendo que a resposta é 20,9%", q)
    assert any("expected_answer" in l for l in leaks)


def test_detects_origin_doc_id_leak():
    q = _question()
    leaks = check_leakage("busque no artigo art-001", q)
    assert any("origin_doc_id" in l for l in leaks)


def test_assert_no_leakage_raises():
    q = _question()
    with pytest.raises(AssertionError):
        assert_no_leakage("origem art-001", q)
