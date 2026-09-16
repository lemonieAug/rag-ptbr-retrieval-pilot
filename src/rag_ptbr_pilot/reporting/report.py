"""Relatório Markdown e deltas pareados entre métodos.

Deltas pareados são calculados SOBRE AS MESMAS perguntas (perguntas avaliadas em
ambos os métodos). O piloto é pequeno e exploratório: sem conclusões sobre todo o
PT-BR, sem alegações de superioridade estatística, sem teste de significância.
"""

from __future__ import annotations

from ..manifest import RunManifest
from .evaluation import _mean


def paired_delta(summary_a: dict, summary_b: dict, metric: str) -> dict:
    """Delta pareado de ``metric`` entre duas configurações (mesmas perguntas)."""
    pa = summary_a.get("per_question", {})
    pb = summary_b.get("per_question", {})
    common = [
        qid for qid in pa
        if qid in pb
        and not pa[qid].get("blocked")
        and not pb[qid].get("blocked")
        and pa[qid].get("metrics", {}).get(metric) is not None
        and pb[qid].get("metrics", {}).get(metric) is not None
    ]
    deltas = [pa[qid]["metrics"][metric] - pb[qid]["metrics"][metric] for qid in common]
    return {"n": len(deltas), "mean_delta": _mean(deltas), "deltas": deltas}


def _fmt(x: float | None, nd: int = 4) -> str:
    if x is None:
        return "—"
    if x != x:  # NaN
        return "—"
    return f"{x:.{nd}f}"


def render_report(run_id: str, summaries: dict[str, dict],
                  comparisons: list, manifest: RunManifest,
                  primary_metric: str, k_values: list[int]) -> str:
    lines: list[str] = []
    lines.append(f"# Relatório de recuperação — {run_id}")
    lines.append("")
    lines.append(f"- Corpus: `{manifest.corpus_version}`")
    lines.append(f"- Config hash: `{manifest.config_hash}`")
    lines.append(f"- Configurações executadas: {len(summaries)}")
    lines.append(f"- Métrica primária (ordenamento): **{primary_metric}**")
    lines.append("")

    # Tabela de médias por configuração
    metric_cols = [primary_metric] + [f"recall@{k}" for k in k_values]
    header = ["config"] + metric_cols + ["grupos_cobertos"]
    lines.append("## Médias por configuração (sobre perguntas avaliadas)")
    lines.append("")
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for config_id, s in summaries.items():
        m = s.get("means", {})
        gc = s.get("group_coverage", {})
        row = [_fmt(m.get(c)) for c in metric_cols]
        row.append(_fmt(gc.get("mean_fraction")))
        lines.append("| " + config_id + " | " + " | ".join(row) + " |")
    lines.append("")

    # Latências médias por etapa
    timing_stages = sorted({
        stage for s in summaries.values() for stage in s.get("timings", {})
    })
    if timing_stages:
        lines.append("## Latência média por etapa (segundos, quando medida)")
        lines.append("")
        lines.append("| config | " + " | ".join(timing_stages) + " |")
        lines.append("|" + "---|" * (len(timing_stages) + 1))
        for config_id, s in summaries.items():
            t = s.get("timings", {})
            row = [_fmt(t.get(stage), 6) for stage in timing_stages]
            lines.append("| " + config_id + " | " + " | ".join(row) + " |")
        lines.append("")

    # Deltas pareados
    lines.append("## Deltas pareados (sobre as mesmas perguntas)")
    lines.append("")
    lines.append("| comparação | A | B | n | Δ " + primary_metric + " |")
    lines.append("|---|---|---|---|---|")
    for comp in comparisons:
        sa = summaries.get(comp.a)
        sb = summaries.get(comp.b)
        if sa is None or sb is None:
            continue
        delta = paired_delta(sa, sb, primary_metric)
        lines.append(
            f"| {comp.label} | {comp.a} | {comp.b} | {delta['n']} | "
            f"{_fmt(delta['mean_delta'])} |"
        )
    lines.append("")

    # Perguntas bloqueadas
    blocked: list[str] = []
    for config_id, s in summaries.items():
        for b in s.get("blocked_questions", []):
            blocked.append(f"{config_id}:{b['question_id']} ({b['reason']})")
    lines.append("## Perguntas bloqueadas (sem gold válido)")
    lines.append("")
    if blocked:
        for b in sorted(set(blocked)):
            lines.append(f"- {b}")
    else:
        lines.append("Nenhuma.")
    lines.append("")
    lines.append(
        "> Piloto exploratório. Sem conclusões sobre todo o PT-BR, sem alegações de "
        "superioridade estatística. Veja `docs/review.md` para limitações."
    )
    lines.append("")
    return "\n".join(lines)
