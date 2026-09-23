"""Read-only gold inventory and cross-file invariants, without model loading."""

from __future__ import annotations

import re

from .loaders import load_articles, load_evidence_groups, load_qrels, load_questions
from .validation import validate_benchmark
from ..persistence import load_chunks
from ..schemas import ReviewStatus


def candidate_status(question) -> str:
    """Read the current annotation, never the potentially stale review snapshot."""
    match = re.search(r"Análise automática:\s*([A-Z_]+)", question.notes or "")
    return match.group(1) if match else "UNCLASSIFIED"


def review_counts(questions) -> dict[str, int]:
    drafts = [q for q in questions if q.review_status == ReviewStatus.draft]
    ready = sum(candidate_status(q) == "READY_FOR_HUMAN_REVIEW" for q in drafts)
    return {
        "total": len(questions),
        "approved": sum(q.review_status == ReviewStatus.approved for q in questions),
        "draft_ready": ready,
        "draft_pending": len(drafts) - ready,
        "rejected": sum(q.review_status == ReviewStatus.rejected for q in questions),
    }


def audit_gold(cfg) -> dict:
    articles = load_articles(cfg.resolve(cfg.paths.metadata_path))
    questions = load_questions(cfg.resolve(cfg.paths.questions_path))
    qrels = load_qrels(cfg.resolve(cfg.paths.qrels_path))
    groups = load_evidence_groups(cfg.resolve(cfg.paths.evidence_groups_path))
    chunks = load_chunks(cfg.resolve(cfg.paths.chunks_path))
    report = validate_benchmark(articles, questions, qrels, groups, chunks)
    q_by_id = {q.question_id: q for q in questions}
    chunk_by_id = {c.chunk_id: c for c in chunks}
    for q in questions:
        for evidence in q.evidence:
            if evidence.doc_id != q.origin_doc_id:
                report.errors.append(f"pergunta {q.question_id}: evidência {evidence.evidence_id} de outro artigo")
    for qr in qrels:
        if qr.relevance and qr.question_id in q_by_id and qr.chunk_id in chunk_by_id:
            if chunk_by_id[qr.chunk_id].doc_id != q_by_id[qr.question_id].origin_doc_id:
                report.errors.append(f"qrel positivo {qr.question_id}/{qr.chunk_id}: outro artigo")
    for group in groups:
        question = q_by_id.get(group.question_id)
        if (question and question.question_type == "factual" and group.required
                and not re.search(r"REQUIRED_GROUP_JUSTIFICATION:[ \t]*\S", question.notes or "")):
            report.errors.append(f"pergunta factual {question.question_id}: grupo {group.group_id} sem justificativa explícita")
    evidence = [e for q in questions for e in q.evidence]
    return {
        **review_counts(questions),
        "evidence_refs": len(evidence),
        "evidence_with_quote": sum(bool(e.quote.strip()) for e in evidence),
        "evidence_with_quote_and_page": sum(bool(e.quote.strip()) and e.page is not None for e in evidence),
        "evidence_with_chunks": sum(bool(e.chunk_ids) for e in evidence),
        "qrels": len(qrels),
        "positive_qrels": sum(qr.relevance == 1 for qr in qrels),
        "questions_with_positive_qrels": len({qr.question_id for qr in qrels if qr.relevance == 1}),
        "required_groups": sum(g.required for g in groups),
        "empty_required_groups": sum(g.required and not g.chunk_ids for g in groups),
        "pending": [{"question_id": q.question_id, "classification": candidate_status(q)}
                    for q in questions if q.review_status == ReviewStatus.draft
                    and candidate_status(q) != "READY_FOR_HUMAN_REVIEW"],
        "validation": report.to_dict(),
    }
