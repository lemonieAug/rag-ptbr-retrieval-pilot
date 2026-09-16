"""Validação cruzada do benchmark (sem carregar modelos).

Rejeita IDs inexistentes, evidências sem suporte verificável, perguntas sem
relevância anotada e mistura acidental entre fixtures sintéticas e benchmark
real. Perguntas ``draft`` ficam fora da avaliação por padrão (aviso).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from ..schemas import (
    ArticleMetadata,
    ChunkRecord,
    EvidenceGroup,
    QrelEntry,
    Question,
    ReviewStatus,
)


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {"errors": self.errors, "warnings": self.warnings,
                "valid": self.valid}


def validate_benchmark(articles: list[ArticleMetadata],
                       questions: list[Question],
                       qrels: list[QrelEntry],
                       groups: list[EvidenceGroup],
                       chunks: list[ChunkRecord]) -> ValidationReport:
    rep = ValidationReport()
    doc_ids = {a.doc_id for a in articles}
    chunk_ids = {c.chunk_id for c in chunks}
    q_ids = {q.question_id for q in questions}
    q_by_id = {q.question_id: q for q in questions}
    qrel_by_q: dict[str, list[QrelEntry]] = defaultdict(list)
    group_by_q: dict[str, list[EvidenceGroup]] = defaultdict(list)

    if len(articles) != len(doc_ids):
        rep.errors.append("doc_id duplicado nos metadados de artigos")
    if len(questions) != len(q_ids):
        rep.errors.append("question_id duplicado nas perguntas")
    if len(chunks) != len(chunk_ids):
        rep.errors.append("chunk_id duplicado nos chunks")

    for qr in qrels:
        qrel_by_q[qr.question_id].append(qr)
    for g in groups:
        group_by_q[g.question_id].append(g)

    # IDs inexistentes em qrels
    for qr in qrels:
        if qr.question_id not in q_ids:
            rep.errors.append(f"qrel referencia pergunta inexistente: {qr.question_id}")
        if qr.chunk_id not in chunk_ids:
            rep.errors.append(f"qrel referencia chunk inexistente: {qr.chunk_id}")

    # Qrels duplicados (mesma pergunta+chunk)
    seen_qrel: set[tuple[str, str]] = set()
    for qr in qrels:
        key = (qr.question_id, qr.chunk_id)
        if key in seen_qrel:
            rep.errors.append(f"qrel duplicado: {key}")
        seen_qrel.add(key)

    # Grupos
    for g in groups:
        if g.question_id not in q_ids:
            rep.errors.append(f"grupo {g.group_id} referencia pergunta inexistente")
        for cid in g.chunk_ids:
            if cid not in chunk_ids:
                rep.errors.append(f"grupo {g.group_id} referencia chunk inexistente: {cid}")

    # Perguntas: origem e evidências verificáveis
    for q in questions:
        if q.origin_doc_id not in doc_ids:
            rep.errors.append(
                f"pergunta {q.question_id}: origin_doc_id inexistente "
                f"({q.origin_doc_id}) — mistura de fixture sintética?"
            )
        for e in q.evidence:
            if e.doc_id not in doc_ids:
                rep.errors.append(
                    f"pergunta {q.question_id}: evidência {e.evidence_id} "
                    f"aponta doc inexistente ({e.doc_id})"
                )
            if not e.quote.strip():
                if q.review_status == ReviewStatus.approved:
                    rep.errors.append(
                        f"pergunta {q.question_id}: evidência {e.evidence_id} "
                        "sem citação literal (sem suporte verificável)"
                    )
                else:
                    rep.warnings.append(
                        f"pergunta {q.question_id}: evidência {e.evidence_id} "
                        "sem citação literal (draft)"
                    )
        # Relevância anotada
        relevant = [qr for qr in qrel_by_q[q.question_id] if qr.relevance == 1]
        if not relevant:
            if q.review_status == ReviewStatus.approved:
                rep.errors.append(
                    f"pergunta {q.question_id}: aprovada mas sem chunk relevante (qrel)"
                )
            else:
                rep.warnings.append(
                    f"pergunta {q.question_id}: draft sem relevância anotada — fora da avaliação"
                )
        if q.question_type == "multi_evidence" and not group_by_q[q.question_id]:
            rep.warnings.append(
                f"pergunta {q.question_id}: multi-evidência sem grupos obrigatórios"
            )

    return rep
