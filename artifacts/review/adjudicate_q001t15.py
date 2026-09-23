"""Apply the exact reformulation explicitly approved by the user."""
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
    question = next(q for q in data["questions"] if q["question_id"] == "q-001-t15")
    assert question["review_status"] == "draft"
    assert question["text"] == "Qual modelo apresentou desempenho superior em precisão e F1 score nas duas categorias de entidades?"
    directory = cfg.resolve(cfg.reporting.artifacts_dir) / "review" / "adjudication_q001t15"
    directory.mkdir(exist_ok=False)
    (directory / "questions.before.yaml").write_bytes(original)
    protected = [cfg.resolve(p) for p in (cfg.paths.qrels_path, cfg.paths.evidence_groups_path,
                 cfg.paths.chunks_path, cfg.paths.corpus_manifest_path)]
    protected += [p for p in (cfg.resolve(cfg.reporting.artifacts_dir) / "indexes").rglob("*") if p.is_file()]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    old_question = deepcopy(question)
    question["text"] = ("Segundo a interpretação apresentada pelos autores na seção de resultados, "
                        "qual modelo foi apontado como superior em precisão e F1 nas duas categorias de entidades?")
    question["notes"] = (
        "Pré-anotação A01-T15. Análise automática da redação original: SOURCE_CONTRADICTION. "
        "A narrativa afirma superioridade em precisão e F1 nas duas classes, mas a Tabela 3 "
        "empata F1 de legislação (FLAIR/TensorFlow: 0,89) e precisão de jurisprudência "
        "(FLAIR/spaCy: 0,78). Adjudicação humana: Augusto Lemonie Gilioli aprovou explicitamente "
        "na conversa a reformulação que atribui a conclusão à interpretação apresentada pelos autores. "
        "A nova pergunta recupera essa conclusão declarada; não estabelece superioridade absoluta "
        "a partir da tabela. A divergência permanece documentada. Resposta esperada, citação, "
        "página e qrel candidato preservados, com suporte na narrativa da seção 6.")
    temporary = directory / "questions.edited.yaml"
    save_yaml(temporary, data)
    assert path.read_bytes() == original, "Concurrent question change"
    os.replace(temporary, path)
    reviews_dir = cfg.resolve(cfg.paths.reviews_dir)
    old_reviews = set(reviews_dir.glob("*.yaml"))
    with (directory / "review_helper.log").open("w", encoding="utf8") as log, redirect_stdout(log):
        cmd_review_gold(SimpleNamespace(
            config=None, question_id="q-001-t15", decision="approve",
            reviewer="Augusto Lemonie Gilioli", confirm_human_review=True,
            summary=False, next_question=False,
            comments=('Aprovação humana explícita na conversa: "aprovo", para a redação que pergunta '
                      'qual modelo foi apontado como superior segundo a interpretação dos autores. '
                      'Mantida a resposta BiLSTM-CRF com FLAIR; empates da Tabela 3 documentados nas notas.')))
    after = load_yaml(path)
    question["review_status"] = "approved"
    assert after == data
    assert all(a == b for a, b in zip(before["questions"], after["questions"])
               if a["question_id"] != "q-001-t15")
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    new_reviews = set(reviews_dir.glob("*.yaml")) - old_reviews
    assert len(new_reviews) == 1
    record = load_yaml(next(iter(new_reviews)))["reviews"][0]
    assert (record["target_id"], record["status"], record["reviewer"]) == (
        "q-001-t15", "approved", "Augusto Lemonie Gilioli")
    audit = audit_gold(cfg)
    assert audit["validation"]["valid"] and audit["approved"] == 120 and audit["draft_pending"] == 5
    save_json(directory / "adjudication.json", {
        "completed_at": datetime.now(timezone.utc).isoformat(), "before": old_question,
        "after": question, "review_record": record, "protected_hashes": hashes,
        "protected_files_unchanged": True, "other_questions_unchanged": True, "audit": audit})
    print("Approved q-001-t15; 120 approved, 5 pending; structural errors: 0")
    print(next(iter(new_reviews)))


if __name__ == "__main__":
    main()
