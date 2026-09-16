"""Separação entre gold/avaliação e a entrada dos métodos (anti-vazamento).

Nenhum recuperador/reranker/gerador recebe resposta gold, qrels, grupos
obrigatórios ou ``origin_doc_id`` como pista. Estes campos pertencem
exclusivamente à avaliação.

A API do pipeline já é estruturalmente segura (``RetrievalRunner.run_query``
recebe apenas ``query_id`` + ``query_text``), e estas funções oferecem a
verificação explícita + testável.
"""

from __future__ import annotations

from ..schemas import Question

# Campos de avaliação que NUNCA podem aparecer na consulta/entrada dos métodos.
GOLD_FIELDS = ("expected_answer", "origin_doc_id")


def retrieval_query(question: Question) -> str:
    """Texto de busca enviado aos métodos: SOMENTE o texto da pergunta."""
    return question.text.strip()


def check_leakage(query_text: str, question: Question) -> list[str]:
    """Retorna a lista de vazamentos de gold detectados no texto de busca."""
    leaks: list[str] = []
    low = query_text.lower()
    ans = question.expected_answer.strip()
    if ans and ans.lower() in low:
        leaks.append("expected_answer presente no texto de busca")
    origin = question.origin_doc_id.strip()
    if origin and origin.lower() in low:
        leaks.append("origin_doc_id presente no texto de busca")
    return leaks


def assert_no_leakage(query_text: str, question: Question) -> None:
    """Levanta AssertionError se houver vazamento de gold na consulta."""
    leaks = check_leakage(query_text, question)
    if leaks:
        raise AssertionError(f"Vazamento de gold na consulta: {leaks}")
