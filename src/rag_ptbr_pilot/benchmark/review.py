"""Small, explicit human review CLI; never approves by default."""

from __future__ import annotations

from datetime import datetime, timezone
import os
import re
from uuid import uuid4

import yaml

from .loaders import load_articles, load_evidence_groups, load_qrels, load_questions
from .validation import validate_benchmark
from .audit import candidate_status, review_counts
from ..config import load_config
from ..errors import ValidationError
from ..io_utils import load_yaml, save_yaml
from ..persistence import load_chunks, load_frozen_corpus
from ..schemas import ReviewRecord, ReviewStatus


def register_review_parser(subparsers) -> None:
    parser = subparsers.add_parser("review-gold", help="Lista e registra revisão humana do gold.")
    parser.add_argument("--config", default=None)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--question-id")
    selection.add_argument("--next", action="store_true", dest="next_question",
                           help="Mostra o próximo draft, priorizando candidatos prontos; somente leitura.")
    selection.add_argument("--summary", action="store_true", help="Resume os estados atuais do gold.")
    parser.add_argument("--decision", choices=("approve", "reject"))
    parser.add_argument("--reviewer", help="Nome da pessoa que realizou a revisão.")
    parser.add_argument("--comments", default="")
    parser.add_argument("--confirm-human-review", action="store_true",
                        help="Confirma explicitamente que a revisão foi realizada por humano.")
    parser.set_defaults(handler=cmd_review_gold)


def cmd_review_gold(args) -> None:
    cfg = load_config(args.config)
    path = cfg.resolve(cfg.paths.questions_path)
    original = path.read_bytes()
    questions = load_questions(path)
    if args.decision and not args.question_id:
        raise ValidationError("Informe --question-id para registrar uma decisão.")
    if getattr(args, "summary", False):
        counts = review_counts(questions)
        for label, key in [("Total", "total"), ("Approved", "approved"),
                           ("Draft ready", "draft_ready"), ("Draft pending", "draft_pending"),
                           ("Rejected", "rejected")]:
            print(f"{label}: {counts[key]}")
        return
    if getattr(args, "next_question", False):
        drafts = [q for q in questions if q.review_status == ReviewStatus.draft]
        ready = [q for q in drafts if candidate_status(q) == "READY_FOR_HUMAN_REVIEW"]
        if not drafts:
            print("Nenhuma pergunta draft restante.")
            return
        args.question_id = (ready or drafts)[0].question_id
    if not args.question_id:
        if args.decision:
            raise ValidationError("Informe --question-id para registrar uma decisão.")
        drafts = [q for q in questions if q.review_status == ReviewStatus.draft]
        for q in drafts:
            print(f"{q.question_id} | {q.origin_doc_id} | {q.text}")
        print(f"Drafts: {len(drafts)}. Use --question-id ID para inspecionar.")
        return
    question = next((q for q in questions if q.question_id == args.question_id), None)
    if question is None:
        raise ValidationError(f"Pergunta inexistente: {args.question_id}")
    qrels = load_qrels(cfg.resolve(cfg.paths.qrels_path))
    groups = load_evidence_groups(cfg.resolve(cfg.paths.evidence_groups_path))
    mapped_ids = {cid for e in question.evidence for cid in e.chunk_ids}
    mapped_ids.update(q.chunk_id for q in qrels if q.question_id == question.question_id)
    mapped_ids.update(cid for g in groups if g.question_id == question.question_id for cid in g.chunk_ids)
    chunks_path = cfg.resolve(cfg.paths.chunks_path)
    mapped_chunks = [c for c in load_chunks(chunks_path) if c.chunk_id in mapped_ids] if chunks_path.exists() else []
    print(yaml.safe_dump({
        "question": question.model_dump(mode="json"),
        "qrels": [q.model_dump(mode="json") for q in qrels if q.question_id == question.question_id],
        "evidence_groups": [g.model_dump(mode="json") for g in groups
                            if g.question_id == question.question_id],
        "chunks": [c.model_dump(mode="json") for c in mapped_chunks],
    }, sort_keys=False, allow_unicode=True))
    if not args.decision:
        return
    if not args.reviewer or not args.reviewer.strip() or not args.confirm_human_review:
        raise ValidationError("Decisão exige --reviewer e --confirm-human-review após revisão humana.")
    if question.review_status != ReviewStatus.draft:
        raise ValidationError("O helper registra decisões somente para perguntas draft.")
    status = ReviewStatus.approved if args.decision == "approve" else ReviewStatus.rejected
    proposed = question.model_copy(update={"review_status": status})
    if status == ReviewStatus.approved:
        if not question.evidence:
            raise ValidationError("Aprovação exige evidências documentadas.")
        if "MANUAL_VISUAL_REVIEW_REQUIRED" in (question.notes or ""):
            raise ValidationError("Resolva e documente a revisão visual pendente antes de aprovar.")
        chunks, _ = load_frozen_corpus(cfg)
        report = validate_benchmark(
            load_articles(cfg.resolve(cfg.paths.metadata_path)),
            [proposed if q.question_id == question.question_id else q for q in questions],
            qrels, groups, chunks,
        )
        if report.errors:
            raise ValidationError("Aprovação bloqueada:\n" + "\n".join(report.errors))
        for evidence in proposed.evidence:
            source = cfg.resolve(cfg.paths.extracted_dir) / f"{evidence.doc_id}.md"
            source_text = source.read_text(encoding="utf-8") if source.exists() else ""
            pages = re.split(r"<!--\s*PAGE\s+(\d+)\s*-->", source_text)
            if len(pages) > 1:
                source_text = "\n".join(pages[i + 1] for i in range(1, len(pages), 2)
                                        if int(pages[i]) == evidence.page)
            if evidence.quote not in source_text:
                raise ValidationError(f"Citação literal não verificável no Markdown: {evidence.evidence_id}")
    raw = load_yaml(path)
    for item in raw["questions"]:
        if item["question_id"] == question.question_id:
            item["review_status"] = status.value
    record = ReviewRecord(
        review_id=f"review-{uuid4().hex}", target_type="question",
        target_id=question.question_id, status=status, reviewer=args.reviewer.strip(),
        comments=args.comments, date=datetime.now(timezone.utc).isoformat(),
    )
    review_path = cfg.resolve(cfg.paths.reviews_dir) / f"{record.review_id}.yaml"
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        save_yaml(temporary, raw)
        if path.read_bytes() != original:
            raise ValidationError("Perguntas alteradas durante a revisão; inspecione novamente.")
        save_yaml(review_path, {"reviews": [record.model_dump(mode="json")]})
        os.replace(temporary, path)
    except Exception:
        review_path.unlink(missing_ok=True)
        raise
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Registrado: {question.question_id} = {status.value}; revisão: {review_path}")
