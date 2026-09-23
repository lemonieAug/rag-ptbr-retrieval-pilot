"""Record the wording and source-attributed answer explicitly approved by the user."""
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


def main():
    cfg = load_config()
    path = cfg.resolve(cfg.paths.questions_path)
    original = path.read_bytes()
    data = load_yaml(path)
    before = deepcopy(data)
    question = next(q for q in data["questions"] if q["question_id"] == "q-003-t17")
    assert question["review_status"] == "draft"
    assert question["text"] == "Qual métrica foi usada para escolher a melhor combinação de hiperparâmetros?"
    assert question["expected_answer"] == "Erro Quadrático Médio (RMSE)"
    folder = cfg.resolve(cfg.reporting.artifacts_dir) / "review" / "adjudication_q003t17"
    folder.mkdir(exist_ok=False)
    (folder / "questions.before.yaml").write_bytes(original)
    protected = [cfg.resolve(p) for p in (cfg.paths.qrels_path, cfg.paths.evidence_groups_path,
                 cfg.paths.chunks_path, cfg.paths.corpus_manifest_path)]
    protected += [p for p in (cfg.resolve(cfg.reporting.artifacts_dir) / "indexes").rglob("*") if p.is_file()]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    old_question = deepcopy(question)
    question["text"] = "Qual nome e sigla os autores atribuem à métrica usada para selecionar a melhor combinação de hiperparâmetros?"
    question["expected_answer"] = "Erro Quadrático Médio (RMSE), conforme denominado no artigo."
    question["notes"] = (
        "Pré-anotação A03-T17. Análise automática da redação original: AMBIGUOUS_EVIDENCE. "
        "O artigo chama a métrica de Erro Quadrático Médio (RMSE), e a explicação da seção 4 "
        "descreve média de diferenças quadráticas sem raiz. RMSE e MSE são conceitualmente "
        "diferentes. Adjudicação humana: Augusto Lemonie Gilioli aprovou explicitamente na "
        "conversa a nova pergunta sobre o nome e a sigla atribuídos pelos autores, com resposta "
        "qualificada por 'conforme denominado no artigo'. A inconsistência da fonte permanece "
        "documentada; não se infere qual métrica foi implementada nem se afirma equivalência "
        "matemática entre RMSE e MSE. Citação literal, página, chunk e qrel preservados.")
    temporary = folder / "questions.edited.yaml"
    save_yaml(temporary, data)
    assert path.read_bytes() == original, "Concurrent question change"
    os.replace(temporary, path)
    reviews = cfg.resolve(cfg.paths.reviews_dir)
    old_records = set(reviews.glob("*.yaml"))
    with (folder / "review_helper.log").open("w", encoding="utf8") as log, redirect_stdout(log):
        cmd_review_gold(SimpleNamespace(
            config=None, question_id="q-003-t17", decision="approve",
            reviewer="Augusto Lemonie Gilioli", confirm_human_review=True,
            summary=False, next_question=False,
            comments=('Aprovação humana explícita na conversa: "sim", para a pergunta sobre '
                      'nome e sigla atribuídos pelos autores e a resposta "Erro Quadrático Médio '
                      '(RMSE), conforme denominado no artigo." Inconsistência RMSE/MSE '
                      'documentada nas notas; evidência e qrel preservados.')))
    question["review_status"] = "approved"
    after = load_yaml(path)
    assert after == data
    assert all(a == b for a, b in zip(before["questions"], after["questions"])
               if a["question_id"] != "q-003-t17")
    assert question["evidence"] == old_question["evidence"]
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    new_records = set(reviews.glob("*.yaml")) - old_records
    assert len(new_records) == 1
    record = load_yaml(next(iter(new_records)))["reviews"][0]
    assert (record["target_id"], record["status"], record["reviewer"]) == (
        "q-003-t17", "approved", "Augusto Lemonie Gilioli")
    audit = audit_gold(cfg)
    assert audit["validation"]["valid"]
    assert (audit["approved"], audit["rejected"], audit["draft_pending"]) == (121, 2, 2)
    save_json(folder / "adjudication.json", {
        "completed_at": datetime.now(timezone.utc).isoformat(), "before": old_question,
        "after": question, "review_record": record, "protected_hashes": hashes,
        "protected_files_unchanged": True, "other_questions_unchanged": True, "audit": audit})
    save_json(folder.parent / "gold_current_audit.json", audit)
    print("Approved q-003-t17; 121 approved, 2 rejected, 2 pending; structural errors: 0")
    print(next(iter(new_records)))
    print(next(q for q in after["questions"] if q["review_status"] == "draft"))


if __name__ == "__main__":
    main()
