"""Conversão da extração para Markdown com marcadores de página/tabela.

Formato gerado (parseável pelo chunker):

- ``<!-- PAGE N -->`` delimita o início de uma página.
- ``<!-- TABLE <id> page=N -->`` ... ``<!-- /TABLE -->`` delimita uma tabela,
  com legenda opcional e corpo em tabela Markdown.
"""

from __future__ import annotations

from .pdf import PdfExtraction, TableData


def _clean_cell(cell: str) -> str:
    # Células com '|' quebrariam a tabela Markdown.
    return cell.replace("|", "\\|").replace("\n", " ").strip()


def _render_table(t: TableData) -> str:
    lines: list[str] = []
    lines.append(f"<!-- TABLE {t.table_id} page={t.page} -->")
    if t.caption:
        lines.append(f"**Tabela (página {t.page}):** {t.caption.strip()}")
    if not t.rows:
        lines.append("_tabela vazia_")
        lines.append("<!-- /TABLE -->")
        return "\n".join(lines)

    # Normaliza o número de colunas pelo maior nº de células.
    ncols = max(len(r) for r in t.rows)
    padded = [r + [""] * (ncols - len(r)) for r in t.rows]

    header = padded[0]
    lines.append("| " + " | ".join(_clean_cell(c) for c in header) + " |")
    lines.append("| " + " | ".join("---" for _ in range(ncols)) + " |")
    for row in padded[1:]:
        lines.append("| " + " | ".join(_clean_cell(c) for c in row) + " |")
    lines.append("<!-- /TABLE -->")
    return "\n".join(lines)


def render_markdown(extraction: PdfExtraction) -> str:
    """Renderiza a extração como Markdown canônico (corrigível por humano)."""
    parts: list[str] = []
    parts.append(f"# {extraction.doc_id}\n")
    parts.append(
        "<!-- Documento extraído automaticamente. Corrija este arquivo quando "
        "necessário; o chunker o relê como fonte canônica. -->\n"
    )
    for page in extraction.pages:
        parts.append(f"\n<!-- PAGE {page.page_number} -->\n")
        if page.text.strip():
            parts.append(page.text.strip())
        for t in page.tables:
            parts.append("\n" + _render_table(t))
    return "\n".join(parts) + "\n"
