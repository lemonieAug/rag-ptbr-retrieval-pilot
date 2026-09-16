"""Avaliação: métricas por pergunta, médias e cobertura por etapa.

Separa (i) métricas de ranking (nDCG/Recall/MRR/Hit/Precision), (ii) cobertura
de candidatos por etapa (bm25/dense/rrf_union/rrf_topn/to_rerank/final) e
(iii) cobertura de grupos obrigatórios. Perguntas sem gold são bloqueadas.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from ..errors import NoGoldError
from ..metrics.coverage import group_coverage, recall_in_set
from ..metrics.ranking import compute_metrics
from ..retrieval.results import QueryRetrieval
from ..schemas import EvidenceGroup, QrelEntry, Question

STAGES = ["bm25", "dense", "rrf_union", "rrf_topn", "to_rerank", "final"]


@dataclass
class QuestionEvaluation:
    question_id: str
    blocked: bool = False
    blocked_reason: str = ""
    metrics: dict = field(default_factory=dict)
    group_coverage: dict = field(default_factory=dict)
    stage_recall: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "blocked": self.blocked,
            "blocked_reason": self.blocked_reason,
            "metrics": self.metrics,
            "group_coverage": self.group_coverage,
            "stage_recall": self.stage_recall,
        }


def build_qrel_index(qrels: list[QrelEntry]) -> tuple[dict, dict]:
    relevant: dict[str, set[str]] = defaultdict(set)
    relevance: dict[str, dict[str, int]] = defaultdict(dict)
    for qr in qrels:
        relevance[qr.question_id][qr.chunk_id] = qr.relevance
        if qr.relevance >= 1:
            relevant[qr.question_id].add(qr.chunk_id)
    return relevant, relevance


def evaluate_question(qr: QueryRetrieval, relevant_ids: set[str],
                      relevance_map: dict[str, int],
                      groups: list[EvidenceGroup],
                      k_values: list[int]) -> QuestionEvaluation:
    ev = QuestionEvaluation(question_id=qr.query_id)
    if not relevant_ids:
        ev.blocked = True
        ev.blocked_reason = "sem gold válido (nenhum chunk relevante anotado)"
        return ev

    ev.metrics = compute_metrics(qr.final_ids(), relevant_ids, relevance_map, k_values)
    ev.group_coverage = group_coverage(qr.final_ids(), groups)
    ev.stage_recall = {
        stage: recall_in_set(qr.stage_ids(stage), relevant_ids)
        for stage in STAGES if qr.stage_ids(stage)
    }
    return ev


def _mean(values: list[float]) -> float | None:
    # None (não NaN) quando não há valores: JSON válido e "ausente" no relatório.
    return sum(values) / len(values) if values else None


def evaluate_config(query_results: dict[str, QueryRetrieval],
                    relevant: dict, relevance: dict,
                    groups_by_q: dict[str, list[EvidenceGroup]],
                    questions_by_id: dict[str, Question],
                    k_values: list[int]) -> dict:
    per_question: dict[str, dict] = {}
    metric_accum: dict[str, list[float]] = defaultdict(list)
    article_accum: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    timing_accum: dict[str, list[float]] = defaultdict(list)
    blocked: list[dict] = []
    group_fractions: list[float] = []
    all_covered_count = 0
    multi_q_count = 0

    for qid, qr in query_results.items():
        rel_ids = relevant.get(qid, set())
        rel_map = relevance.get(qid, {})
        groups = groups_by_q.get(qid, [])
        ev = evaluate_question(qr, rel_ids, rel_map, groups, k_values)
        per_question[qid] = ev.to_dict()

        for stage, dt in qr.timings.items():
            if isinstance(dt, (int, float)):
                timing_accum[stage].append(dt)

        if ev.blocked:
            blocked.append({"question_id": qid, "reason": ev.blocked_reason})
            continue

        for key, val in ev.metrics.items():
            metric_accum[key].append(val)
        doc_id = questions_by_id[qid].origin_doc_id if qid in questions_by_id else "?"
        for key, val in ev.metrics.items():
            article_accum[doc_id][key].append(val)

        gc = ev.group_coverage
        if gc.get("total", 0) > 0:
            group_fractions.append(gc["fraction"])
            multi_q_count += 1
            if gc["covered"] == gc["total"]:
                all_covered_count += 1

    means = {k: _mean(v) for k, v in metric_accum.items()}
    timings = {stage: _mean(v) for stage, v in timing_accum.items()}
    per_article = {
        doc: {k: _mean(v) for k, v in acc.items()}
        for doc, acc in sorted(article_accum.items())
    }

    return {
        "per_question": per_question,
        "means": means,
        "timings": timings,
        "per_article": per_article,
        "blocked_questions": blocked,
        "group_coverage": {
            "mean_fraction": _mean(group_fractions),
            "questions_with_groups": multi_q_count,
            "questions_all_covered": all_covered_count,
        },
        "n_questions_evaluated": len(query_results) - len(blocked),
    }
