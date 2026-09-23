"""Regenerate the read-only Phase 2 gold inventory and six-case review table."""

import json
from pathlib import Path

from rag_ptbr_pilot.benchmark.audit import audit_gold, candidate_status
from rag_ptbr_pilot.benchmark.loaders import load_questions
from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.io_utils import save_json


cfg = load_config()
output = cfg.resolve(cfg.reporting.artifacts_dir) / "review"
audit = audit_gold(cfg)
save_json(output / "phase2_gold_audit.json", audit)
snapshot = json.loads((output / "gold_review.json").read_text(encoding="utf8"))
proposals = {q["question_id"]: q for q in snapshot["questions"]}
actions = {
    "q-001-t15": "Conferir Tabela 3 e narrativa; delimitar a afirmação de superioridade e registrar a adjudicação dos empates.",
    "q-001-t20": "Conferir contribuição na fonte e decidir reformulação/rejeição para o corpus congelado; não atribuir suporte ao campo section nem inventar qrel.",
    "q-001-m05": "Conferir associação modelo/linha na tabela original; decidir reformulação/rejeição ou futura versão de corpus. Resolver o grupo FLAIR vazio antes de aprovar.",
    "q-003-t17": "Adjudicar nomenclatura RMSE/MSE confrontando definição da seção 4; documentar se a resposta reproduz o termo usado pelo artigo.",
    "q-003-m03": "Ler visualmente Figuras 2/3, atribuir resultados a Campo Verde/Maracaju e documentar suporte recuperável; resolver a marca visual antes de aprovar.",
    "q-004-t18": "Conferir resumo, conclusão e Tabela 4; adjudicar divergência 24,81%/24,87% e registrar a referência adotada.",
}


def cell(text):
    return str(text).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


lines = ["# Casos pendentes — Fase 2", "",
         "Leitura dos YAMLs atuais e justificativas do pacote de candidatos. Nenhuma aprovação ou alteração de resposta.", "",
         "| question_id | problema | expected_answer | evidência encontrada | motivo da pendência | ação humana necessária |",
         "|---|---|---|---|---|---|"]
for question in load_questions(cfg.resolve(cfg.paths.questions_path)):
    if question.question_id not in actions:
        continue
    proposal = proposals[question.question_id]
    assert candidate_status(question) == proposal["automatic_status"], question.question_id
    evidence = "\n\n".join(
        f"{e.doc_id}, p. {e.page}; chunks: {', '.join(e.chunk_ids) or 'SEM CHUNK'}; quote: {e.quote}"
        for e in question.evidence)
    values = [question.question_id, candidate_status(question), question.expected_answer,
              evidence, proposal["observations"], actions[question.question_id]]
    lines.append("| " + " | ".join(cell(v) for v in values) + " |")
(output / "phase2_gold_pending.md").write_text("\n".join(lines) + "\n", encoding="utf8")
print(json.dumps({k: v for k, v in audit.items() if k != "validation"}, ensure_ascii=True, indent=2))
if not audit["validation"]["valid"]:
    raise SystemExit("Gold invariant errors; inspect phase2_gold_audit.json")
