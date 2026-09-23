"""Record the exact conclusion-attributed question explicitly approved by the user."""
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
from types import SimpleNamespace

from rag_ptbr_pilot.benchmark.audit import audit_gold
from rag_ptbr_pilot.benchmark.review import cmd_review_gold
from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.io_utils import load_yaml, save_yaml, save_json
from rag_ptbr_pilot.status import collect_status


def main():
    cfg = load_config()
    path = cfg.resolve(cfg.paths.questions_path)
    original = path.read_bytes()
    data = load_yaml(path)
    before = deepcopy(data)
    question = next(q for q in data["questions"] if q["question_id"] == "q-004-t18")
    assert question["review_status"] == "draft"
    assert question["text"] == "Em qual cenário o AMN alcança ganhos médios de pelo menos 25,35% em PBR e 24,87% em RDB?"
    folder = cfg.resolve(cfg.reporting.artifacts_dir) / "review" / "adjudication_q004t18"
    folder.mkdir(exist_ok=False)
    (folder / "questions.before.yaml").write_bytes(original)
    protected = [cfg.resolve(p) for p in (cfg.paths.qrels_path, cfg.paths.evidence_groups_path,
                 cfg.paths.chunks_path, cfg.paths.corpus_manifest_path)]
    protected += [p for p in (cfg.resolve(cfg.reporting.artifacts_dir) / "indexes").rglob("*") if p.is_file()]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    old_question = deepcopy(question)
    question["text"] = "Segundo a conclusão do artigo, em qual cenário o AMN alcança ganhos médios de pelo menos 25,35% em PBR e 24,87% em RDB?"
    question["notes"] = (
        "Pré-anotação A04-T18. Análise automática da redação original: SOURCE_CONTRADICTION. "
        "Conflito interno da fonte: o resumo (p.1) registra 24,81% de RDB mínimo em baixa "
        "incidência de XT; a conclusão e a Tabela 4 (p.12) registram 24,87%. Adjudicação humana: "
        "Augusto Lemonie Gilioli aprovou explicitamente na conversa a reformulação que atribui "
        "a afirmação à conclusão do artigo. A resposta permanece 'No cenário de baixa incidência "
        "de XT'. A divergência com o resumo permanece documentada; não se afirma que o valor "
        "do resumo foi corrigido ou que a fonte é consistente. Citações literais, páginas, "
        "chunks e qrels preservados, com suporte na conclusão e na Tabela 4.")
    temporary = folder / "questions.edited.yaml"
    save_yaml(temporary, data)
    assert path.read_bytes() == original, "Concurrent question change"
    os.replace(temporary, path)
    reviews = cfg.resolve(cfg.paths.reviews_dir)
    old_records = set(reviews.glob("*.yaml"))
    with (folder / "review_helper.log").open("w", encoding="utf8") as log, redirect_stdout(log):
        cmd_review_gold(SimpleNamespace(
            config=None, question_id="q-004-t18", decision="approve",
            reviewer="Augusto Lemonie Gilioli", confirm_human_review=True,
            summary=False, next_question=False,
            comments=('Aprovação humana explícita na conversa: "sim", para a redação '
                      '"Segundo a conclusão do artigo, em qual cenário o AMN alcança ganhos '
                      'médios de pelo menos 25,35% em PBR e 24,87% em RDB?". Resposta mantida: '
                      'baixa incidência de XT. Divergência do resumo (24,81%) versus '
                      'conclusão/Tabela 4 (24,87%) documentada nas notas.')))
    question["review_status"] = "approved"
    after = load_yaml(path)
    assert after == data
    assert all(a == b for a, b in zip(before["questions"], after["questions"])
               if a["question_id"] != "q-004-t18")
    assert question["expected_answer"] == old_question["expected_answer"]
    assert question["evidence"] == old_question["evidence"]
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    new_records = set(reviews.glob("*.yaml")) - old_records
    assert len(new_records) == 1
    record = load_yaml(next(iter(new_records)))["reviews"][0]
    assert (record["target_id"], record["status"], record["reviewer"]) == (
        "q-004-t18", "approved", "Augusto Lemonie Gilioli")
    audit = audit_gold(cfg)
    assert audit["validation"]["valid"]
    assert (audit["approved"], audit["rejected"], audit["draft_pending"]) == (122, 3, 0)
    status = collect_status(cfg)
    assert status["experiment"]["ready_for_retrieval"] and not status["experiment"]["reasons"]
    records = [r for p in reviews.glob("*.yaml") for r in load_yaml(p).get("reviews", [])]
    for q in after["questions"]:
        matches = [r for r in records if r["target_type"] == "question" and r["target_id"] == q["question_id"]]
        assert len(matches) == 1 and matches[0]["status"] == q["review_status"]
        assert matches[0]["reviewer"] == "Augusto Lemonie Gilioli"
    save_json(folder / "adjudication.json", {
        "completed_at": datetime.now(timezone.utc).isoformat(), "before": old_question,
        "after": question, "review_record": record, "protected_hashes": hashes,
        "protected_files_unchanged": True, "other_questions_unchanged": True,
        "questions_with_matching_review_record": len(after["questions"]), "audit": audit})
    save_json(folder.parent / "gold_current_audit.json", audit)
    save_json(folder.parent / "status_after_human_review.json", status)
    print("Approved q-004-t18; 122 approved, 3 rejected, 0 pending; structural errors: 0")
    print(next(iter(new_records)))
    print(status["experiment"])


if __name__ == "__main__":
    main()
