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
    warning_counts: dict[str, int] = field(default_factory=dict)

    def warn(self, category: str, message: str) -> None:
        self.warnings.append(message)
        self.warning_counts[category] = self.warning_counts.get(category, 0) + 1

    @property
    def valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {"errors": self.errors, "warnings": self.warnings,
                "valid": self.valid, "warning_counts": self.warning_counts}


def validate_benchmark(articles: list[ArticleMetadata],
                       questions: list[Question],
                       qrels: list[QrelEntry],
                       groups: list[EvidenceGroup],
                       chunks: list[ChunkRecord]) -> ValidationReport:
    rep = ValidationReport()
    doc_ids = {a.doc_id for a in articles}
    chunk_ids = {c.chunk_id for c in chunks}
    chunk_by_id = {c.chunk_id: c for c in chunks}
    article_by_id = {a.doc_id: a for a in articles}
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
    for c in chunks:
        if c.doc_id not in doc_ids:
            rep.errors.append(f"chunk {c.chunk_id}: doc_id inexistente ({c.doc_id})")

    def incomplete(q: Question, category: str, message: str) -> None:
        if q.review_status == ReviewStatus.approved:
            rep.errors.append(message)
        else:
            rep.warn(category, message)

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
    seen_groups: set[str] = set()
    for g in groups:
        if g.group_id in seen_groups:
            rep.errors.append(f"group_id duplicado: {g.group_id}")
        seen_groups.add(g.group_id)
        if g.question_id not in q_ids:
            rep.errors.append(f"grupo {g.group_id} referencia pergunta inexistente")
        elif g.required and not g.chunk_ids:
            incomplete(q_by_id[g.question_id], "empty_required_group",
                       f"pergunta {g.question_id}: grupo obrigatório {g.group_id} vazio")
        if len(set(g.chunk_ids)) != len(g.chunk_ids):
            rep.errors.append(f"grupo {g.group_id}: chunk_ids duplicados")
        for cid in g.chunk_ids:
            if cid not in chunk_ids:
                rep.errors.append(f"grupo {g.group_id} referencia chunk inexistente: {cid}")
            elif not any(qr.chunk_id == cid and qr.relevance == 1
                         for qr in qrel_by_q[g.question_id]):
                rep.errors.append(f"grupo {g.group_id}: chunk {cid} sem qrel positivo")

    # Perguntas: origem e evidências verificáveis
    for q in questions:
        if q.review_status == ReviewStatus.draft:
            rep.warn("draft", f"pergunta {q.question_id}: draft — aguarda revisão humana; fora da avaliação")
        if q.origin_doc_id not in doc_ids:
            rep.errors.append(
                f"pergunta {q.question_id}: origin_doc_id inexistente "
                f"({q.origin_doc_id}) — mistura de fixture sintética?"
            )
        for e in q.evidence:
            prefix = f"pergunta {q.question_id}: evidência {e.evidence_id}"
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
                    rep.warn("missing_quote",
                        f"pergunta {q.question_id}: evidência {e.evidence_id} "
                        "sem citação literal (draft)"
                    )
            if e.page is None:
                incomplete(q, "missing_page", f"{prefix} sem página verificada")
            elif e.doc_id in article_by_id:
                pages = article_by_id[e.doc_id].pages
                if pages is not None and e.page > pages:
                    rep.errors.append(f"{prefix}: página {e.page} excede total {pages}")
            if not e.chunk_ids:
                incomplete(q, "missing_evidence_chunks", f"{prefix} sem chunks de suporte")
            if len(set(e.chunk_ids)) != len(e.chunk_ids):
                rep.errors.append(f"{prefix}: chunk_ids duplicados")
            for cid in e.chunk_ids:
                c = chunk_by_id.get(cid)
                if c is None:
                    rep.errors.append(f"{prefix}: chunk inexistente ({cid})")
                elif c.doc_id != e.doc_id:
                    rep.errors.append(f"{prefix}: chunk {cid} pertence a outro documento")
                elif e.page is not None and c.page is not None and c.page != e.page:
                    rep.errors.append(f"{prefix}: página incompatível com chunk {cid}")
                if not any(qr.chunk_id == cid and qr.relevance == 1
                           for qr in qrel_by_q[q.question_id]):
                    incomplete(q, "evidence_without_qrel", f"{prefix}: chunk {cid} sem qrel positivo")
            if e.required_group:
                linked = next((g for g in group_by_q[q.question_id]
                               if g.group_id == e.required_group), None)
                if linked is None:
                    rep.errors.append(f"{prefix}: required_group inexistente para a pergunta ({e.required_group})")
                elif not set(e.chunk_ids).issubset(linked.chunk_ids):
                    rep.errors.append(f"{prefix}: chunks fora do required_group {e.required_group}")
        # Relevância anotada
        relevant = [qr for qr in qrel_by_q[q.question_id] if qr.relevance == 1]
        if not relevant:
            if q.review_status == ReviewStatus.approved:
                rep.errors.append(
                    f"pergunta {q.question_id}: aprovada mas sem chunk relevante (qrel)"
                )
            else:
                rep.warn("missing_qrels",
                    f"pergunta {q.question_id}: draft sem relevância anotada — fora da avaliação"
                )
        if q.question_type == "multi_evidence" and not any(g.required for g in group_by_q[q.question_id]):
            incomplete(q, "missing_required_groups",
                       f"pergunta {q.question_id}: multi-evidência sem grupos obrigatórios")

    return rep
