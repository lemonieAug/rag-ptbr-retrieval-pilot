"""Record the user's explicit approval of the 119 ready candidates, once."""
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from rag_ptbr_pilot.benchmark.audit import audit_gold, candidate_status
from rag_ptbr_pilot.benchmark.loaders import load_questions
from rag_ptbr_pilot.benchmark.review import cmd_review_gold
from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.io_utils import load_yaml
from rag_ptbr_pilot.schemas import ReviewRecord


def main():
    cfg = load_config()
    path = cfg.resolve(cfg.paths.questions_path)
    questions = load_questions(path)
    selected = [q.question_id for q in questions if q.review_status == "draft"
                and candidate_status(q) == "READY_FOR_HUMAN_REVIEW"]
    pending = {"q-001-t15", "q-001-t20", "q-001-m05", "q-003-t17", "q-003-m03", "q-004-t18"}
    assert len(questions) == 125 and len(selected) == 119
    assert all(q.review_status == "draft" for q in questions), "Approval already recorded or workspace changed"
    assert {q.question_id for q in questions} - set(selected) == pending
    assert audit_gold(cfg)["validation"]["valid"]
    before = {q.question_id: q.model_dump(mode="json") for q in questions}
    reviewer = "Augusto Lemonie Gilioli"
    folder = cfg.resolve(cfg.reporting.artifacts_dir) / "review" / ("human_approval_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    folder.mkdir()
    (folder / "questions.before.yaml").write_bytes(path.read_bytes())
    reviews_dir = cfg.resolve(cfg.paths.reviews_dir)
    old_reviews = set(reviews_dir.glob("*.yaml"))
    protected = [cfg.resolve(p) for p in (cfg.paths.qrels_path, cfg.paths.evidence_groups_path,
                 cfg.paths.chunks_path, cfg.paths.corpus_manifest_path)]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    authorization = {
        "reviewer": reviewer, "decision": "approve", "question_ids": selected,
        "excluded_question_ids": sorted(pending), "user_confirmation": "Confirmo tudo",
        "scope": "119 ready candidates explicitly confirmed in conversation; six pending cases excluded",
        "started_at": datetime.now(timezone.utc).isoformat(), "completed_question_ids": [],
        "protected_hashes": hashes,
    }
    manifest = folder / "approval.json"

    def save():
        manifest.write_text(json.dumps(authorization, ensure_ascii=False, indent=2), encoding="utf8")

    save()
    print(f"Registro e backup: {folder}", flush=True)
    comments = ('Aprovação humana em lote expressamente confirmada por Augusto Lemonie Gilioli '
                'na conversa: "Confirmo tudo", após definição do alcance como as 119 candidatas '
                'READY_FOR_HUMAN_REVIEW. Os seis casos pendentes foram excluídos. '
                'O assistente registrou a decisão do usuário pelo helper de revisão.')
    with (folder / "review_helper.log").open("w", encoding="utf8") as log:
        for number, question_id in enumerate(selected, 1):
            args = SimpleNamespace(config=None, question_id=question_id, decision="approve",
                                   reviewer=reviewer, comments=comments, confirm_human_review=True,
                                   summary=False, next_question=False)
            with redirect_stdout(log):
                cmd_review_gold(args)
            log.flush()
            authorization["completed_question_ids"].append(question_id)
            save()
            if number % 10 == 0 or number == len(selected):
                print(f"Aprovações registradas: {number}/{len(selected)}", flush=True)
    after = {q.question_id: q.model_dump(mode="json") for q in load_questions(path)}
    for question_id, original in before.items():
        expected = dict(original)
        if question_id in selected:
            expected["review_status"] = "approved"
        assert after[question_id] == expected, question_id
    new_reviews = set(reviews_dir.glob("*.yaml")) - old_reviews
    records = [ReviewRecord.model_validate(r) for p in new_reviews for r in load_yaml(p)["reviews"]]
    assert len(records) == 119 and {r.target_id for r in records} == set(selected)
    assert all(r.status == "approved" and r.reviewer == reviewer for r in records)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    report = audit_gold(cfg)
    assert report["approved"] == 119 and report["draft_pending"] == 6 and report["draft_ready"] == 0
    assert report["validation"]["valid"]
    authorization.update(completed_at=datetime.now(timezone.utc).isoformat(), status="complete",
                         review_records=len(records), result=report,
                         question_content_preserved=True, protected_files_unchanged=True)
    save()
    print(json.dumps({k: report[k] for k in ("total", "approved", "draft_ready", "draft_pending", "rejected")}), flush=True)
    print(f"APPROVAL_COMPLETE: {manifest}", flush=True)


if __name__ == "__main__":
    main()
