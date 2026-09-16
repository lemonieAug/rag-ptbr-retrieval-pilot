"""Planilha CSV de avaliação humana (correção, suporte e citações).

Identificadores cegos e ordem embaralhada: o avaliador não vê o método/config
durante o julgamento. O mapeamento cego->identidade é salvo em JSON à parte.
Não exige juiz automático da mesma família como fonte principal de avaliação.
"""

from __future__ import annotations

import csv
import io
import random
from pathlib import Path


def build_human_eval_rows(generations: list, questions_by_id: dict,
                          shuffle_seed: int) -> tuple[list[dict], dict]:
    """Retorna (linhas embaralhadas, mapeamento cego->identidade)."""
    rows: list[dict] = []
    mapping: dict[str, dict] = {}
    for g in generations:
        q = questions_by_id.get(g.question_id)
        rows.append({
            "question": q.text if q else g.question_id,
            "generated_answer": g.response,
            "evidence_context": getattr(g, "context_text", "") or "",
            "context_included_ids": ", ".join(getattr(g, "context_included", []) or []),
            "correctness": "",
            "support": "",
            "citations_ok": "",
            "notes": "",
            "_identity": {"question_id": g.question_id, "config_id": g.config_id},
        })

    rng = random.Random(shuffle_seed)
    rng.shuffle(rows)
    for i, row in enumerate(rows):
        blind_id = f"item-{i + 1:03d}"
        mapping[blind_id] = row.pop("_identity")
        row["blind_id"] = blind_id
    return rows, mapping


def render_human_eval_csv(rows: list[dict]) -> str:
    fieldnames = [
        "blind_id", "question", "generated_answer", "evidence_context",
        "context_included_ids", "correctness", "support", "citations_ok", "notes",
    ]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    return buf.getvalue()


def write_human_eval_csv(rows: list[dict], mapping: dict,
                         csv_path: str | Path, mapping_path: str | Path) -> None:
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    Path(csv_path).write_text(render_human_eval_csv(rows), encoding="utf-8")

    from ..io_utils import save_json

    save_json(mapping_path, mapping)
