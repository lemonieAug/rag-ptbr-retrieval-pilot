"""Structural gold checks and explicit human review, with synthetic data only."""

from argparse import Namespace

import pytest

from rag_ptbr_pilot.benchmark import review
from rag_ptbr_pilot.benchmark.validation import validate_benchmark
from rag_ptbr_pilot.config import AppConfig
from rag_ptbr_pilot.errors import ValidationError
from rag_ptbr_pilot.io_utils import load_yaml, save_yaml
from rag_ptbr_pilot.persistence import save_chunks
from rag_ptbr_pilot.schemas import ArticleMetadata, ChunkRecord, EvidenceGroup, EvidenceRef, QrelEntry, Question


@pytest.fixture
def gold():
    articles = [ArticleMetadata(doc_id="d1", title="Synthetic", pdf_filename="d1.pdf", pages=3)]
    chunks = [ChunkRecord(chunk_id="c1", doc_id="d1", block_id="b1", page=1,
                          text="Trecho literal.", token_count_ref=3)]
    questions = [Question(question_id="q1", text="Pergunta?", expected_answer="Resposta",
                          origin_doc_id="d1", evidence=[EvidenceRef(
                              evidence_id="e1", doc_id="d1", page=1,
                              quote="Trecho literal.", chunk_ids=["c1"])])]
    qrels = [QrelEntry(question_id="q1", chunk_id="c1", relevance=1)]
    return articles, questions, qrels, [], chunks


def test_draft_warning_survives_complete_candidates(gold):
    report = validate_benchmark(*gold)
    assert report.valid
    assert report.warning_counts == {"draft": 1}


@pytest.mark.parametrize("update,expected", [
    ({"chunk_ids": ["missing"]}, "chunk inexistente"),
    ({"page": 2}, "página incompatível"),
    ({"page": 4}, "excede total"),
    ({"required_group": "missing"}, "required_group inexistente"),
    ({"chunk_ids": ["c1", "c1"]}, "chunk_ids duplicados"),
    ({"doc_id": "d2"}, "outro documento"),
])
def test_invalid_evidence_references(gold, update, expected):
    gold[1][0].evidence[0] = gold[1][0].evidence[0].model_copy(update=update)
    assert any(expected in e for e in validate_benchmark(*gold).errors)


def test_group_reference_must_belong_to_same_question(gold):
    gold[1].append(Question(question_id="q2", text="Outra?", expected_answer="Outra", origin_doc_id="d1"))
    gold[3].append(EvidenceGroup(group_id="g2", question_id="q2"))
    gold[1][0].evidence[0].required_group = "g2"
    assert any("required_group inexistente" in e for e in validate_benchmark(*gold).errors)


def test_empty_required_group_blocks_approved_only(gold):
    gold[3].append(EvidenceGroup(group_id="g1", question_id="q1"))
    report = validate_benchmark(*gold)
    assert report.valid
    assert report.warning_counts["empty_required_group"] == 1
    gold[1][0].review_status = "approved"
    assert any("grupo obrigatório g1 vazio" in e for e in validate_benchmark(*gold).errors)


def test_group_chunk_needs_positive_qrel(gold):
    gold[3].append(EvidenceGroup(group_id="g1", question_id="q1", chunk_ids=["c1"]))
    gold[2][0].relevance = 0
    assert any("grupo g1: chunk c1 sem qrel positivo" in e for e in validate_benchmark(*gold).errors)


@pytest.mark.parametrize("field,value", [("page", None), ("chunk_ids", []), ("quote", "")])
def test_approved_evidence_cannot_remain_incomplete(gold, field, value):
    setattr(gold[1][0].evidence[0], field, value)
    assert validate_benchmark(*gold).valid
    gold[1][0].review_status = "approved"
    assert not validate_benchmark(*gold).valid


@pytest.fixture
def review_workspace(tmp_path, monkeypatch, gold):
    cfg = AppConfig(root=tmp_path)
    for field, key, values in [
        ("metadata_path", "articles", gold[0]), ("questions_path", "questions", gold[1]),
        ("qrels_path", "qrels", gold[2]), ("evidence_groups_path", "evidence_groups", gold[3]),
    ]:
        save_yaml(cfg.resolve(getattr(cfg.paths, field)), {key: [v.model_dump(mode="json") for v in values]})
    extracted = cfg.resolve(cfg.paths.extracted_dir)
    save_chunks(cfg.resolve(cfg.paths.chunks_path), gold[4])
    extracted.mkdir(parents=True)
    (extracted / "d1.md").write_text("<!-- PAGE 1 -->\nTrecho literal.", encoding="utf-8")
    monkeypatch.setattr(review, "load_config", lambda _: cfg)
    monkeypatch.setattr(review, "load_frozen_corpus", lambda _: (gold[4], None))
    return cfg


def args(**kwargs):
    return Namespace(**({"config": None, "question_id": None, "decision": None,
                         "reviewer": None, "comments": "", "confirm_human_review": False} | kwargs))


def test_review_list_and_show_do_not_write(review_workspace, capsys):
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    before = path.read_bytes()
    review.cmd_review_gold(args())
    review.cmd_review_gold(args(question_id="q1"))
    assert path.read_bytes() == before
    output = capsys.readouterr().out
    assert "Trecho literal." in output
    assert "block_id: b1" in output
    assert not review_workspace.resolve(review_workspace.paths.reviews_dir).exists()


@pytest.mark.parametrize("kwargs", [{}, {"reviewer": "Human"}, {"confirm_human_review": True},
                                   {"reviewer": " ", "confirm_human_review": True}])
def test_decision_requires_identified_explicit_human_action(review_workspace, kwargs):
    with pytest.raises(ValidationError, match="Decisão exige"):
        review.cmd_review_gold(args(question_id="q1", decision="approve", **kwargs))
    assert load_yaml(review_workspace.resolve(review_workspace.paths.questions_path))["questions"][0]["review_status"] == "draft"


@pytest.mark.parametrize("decision,status", [("approve", "approved"), ("reject", "rejected")])
def test_explicit_review_writes_status_and_record(review_workspace, decision, status):
    review.cmd_review_gold(args(question_id="q1", decision=decision, reviewer="Human fixture",
                               confirm_human_review=True, comments="Synthetic unit test"))
    assert load_yaml(review_workspace.resolve(review_workspace.paths.questions_path))["questions"][0]["review_status"] == status
    records = list(review_workspace.resolve(review_workspace.paths.reviews_dir).glob("*.yaml"))
    assert len(records) == 1
    record = load_yaml(records[0])["reviews"][0]
    assert record["reviewer"] == "Human fixture"
    assert record["target_id"] == "q1"
    assert record["status"] == status


@pytest.mark.parametrize("problem", ["visual", "missing_quote", "nonliteral_quote", "empty_group", "wrong_source_page"])
def test_approval_blocks_unresolved_support(review_workspace, problem):
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    data = load_yaml(path)
    if problem == "visual":
        data["questions"][0]["notes"] = "MANUAL_VISUAL_REVIEW_REQUIRED"
    elif problem == "missing_quote":
        data["questions"][0]["evidence"][0]["quote"] = ""
    elif problem == "nonliteral_quote":
        data["questions"][0]["evidence"][0]["quote"] = "Inventado"
    elif problem == "wrong_source_page":
        (review_workspace.resolve(review_workspace.paths.extracted_dir) / "d1.md").write_text(
            "<!-- PAGE 2 -->\nTrecho literal.", encoding="utf-8")
    else:
        save_yaml(review_workspace.resolve(review_workspace.paths.evidence_groups_path),
                  {"evidence_groups": [{"group_id": "g1", "question_id": "q1"}]})
    save_yaml(path, data)
    with pytest.raises(ValidationError):
        review.cmd_review_gold(args(question_id="q1", decision="approve", reviewer="Human fixture",
                                   confirm_human_review=True))
    assert load_yaml(path)["questions"][0]["review_status"] == "draft"
    assert not review_workspace.resolve(review_workspace.paths.reviews_dir).exists()


def test_next_prioritizes_ready_drafts_without_writing(review_workspace, capsys):
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    data = load_yaml(path)
    ready = dict(data["questions"][0], question_id="q2",
                 notes="Análise automática: READY_FOR_HUMAN_REVIEW.")
    data["questions"].append(ready)
    save_yaml(path, data)
    before = path.read_bytes()
    review.cmd_review_gold(args(next_question=True))
    assert "question_id: q2" in capsys.readouterr().out
    assert path.read_bytes() == before
    assert not review_workspace.resolve(review_workspace.paths.reviews_dir).exists()


@pytest.mark.parametrize("selection", [{"next_question": True}, {"summary": True}])
def test_implicit_selection_cannot_record_decision(review_workspace, selection):
    with pytest.raises(ValidationError, match="question-id"):
        review.cmd_review_gold(args(decision="approve", reviewer="Human fixture",
                                   confirm_human_review=True, **selection))


def test_summary_uses_current_annotation_status(review_workspace, capsys):
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    data = load_yaml(path)
    data["questions"][0]["notes"] = "Análise automática: READY_FOR_HUMAN_REVIEW."
    save_yaml(path, data)
    review.cmd_review_gold(args(summary=True))
    assert "Draft ready: 1" in capsys.readouterr().out
    data["questions"][0]["review_status"] = "approved"
    save_yaml(path, data)
    review.cmd_review_gold(args(summary=True))
    output = capsys.readouterr().out
    assert "Approved: 1" in output
    assert "Draft ready: 0" in output


def test_next_reports_no_drafts(review_workspace, capsys):
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    data = load_yaml(path)
    data["questions"][0]["review_status"] = "rejected"
    save_yaml(path, data)
    review.cmd_review_gold(args(next_question=True))
    assert "Nenhuma pergunta draft" in capsys.readouterr().out


def test_gold_audit_counts_current_yaml(review_workspace):
    from rag_ptbr_pilot.benchmark.audit import audit_gold

    summary = audit_gold(review_workspace)
    assert summary["total"] == summary["evidence_with_quote"] == summary["positive_qrels"] == 1
    assert summary["questions_with_positive_qrels"] == 1
    assert summary["validation"]["valid"]


def test_gold_audit_rejects_evidence_and_positive_qrel_from_other_article(review_workspace, gold):
    from rag_ptbr_pilot.benchmark.audit import audit_gold

    article = gold[0][0].model_copy(update={"doc_id": "d2"})
    save_yaml(review_workspace.resolve(review_workspace.paths.metadata_path),
              {"articles": [a.model_dump(mode="json") for a in gold[0] + [article]]})
    gold[4][0].doc_id = "d2"
    save_chunks(review_workspace.resolve(review_workspace.paths.chunks_path), gold[4])
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    data = load_yaml(path)
    data["questions"][0]["evidence"][0]["doc_id"] = "d2"
    save_yaml(path, data)
    report = audit_gold(review_workspace)["validation"]
    assert any("evidência e1 de outro artigo" in e for e in report["errors"])
    assert any("qrel positivo q1/c1: outro artigo" in e for e in report["errors"])


@pytest.mark.parametrize("notes", [None, "REQUIRED_GROUP_JUSTIFICATION:",
                                   "REQUIRED_GROUP_JUSTIFICATION:   \nOther note"])
def test_gold_audit_requires_factual_group_justification(review_workspace, notes):
    from rag_ptbr_pilot.benchmark.audit import audit_gold

    save_yaml(review_workspace.resolve(review_workspace.paths.evidence_groups_path),
              {"evidence_groups": [{"group_id": "g1", "question_id": "q1", "chunk_ids": ["c1"]}]})
    path = review_workspace.resolve(review_workspace.paths.questions_path)
    data = load_yaml(path)
    data["questions"][0]["notes"] = notes
    save_yaml(path, data)
    assert any("sem justificativa" in e for e in audit_gold(review_workspace)["validation"]["errors"])

    data["questions"][0]["notes"] = "REQUIRED_GROUP_JUSTIFICATION: Requires both dates in one factual comparison."
    save_yaml(path, data)
    assert not any("sem justificativa" in e for e in audit_gold(review_workspace)["validation"]["errors"])
