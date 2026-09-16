"""Relatórios e avaliação."""

from .evaluation import (
    QuestionEvaluation,
    build_qrel_index,
    evaluate_config,
    evaluate_question,
)
from .report import paired_delta, render_report

__all__ = [
    "QuestionEvaluation",
    "build_qrel_index",
    "evaluate_config",
    "evaluate_question",
    "paired_delta",
    "render_report",
]
