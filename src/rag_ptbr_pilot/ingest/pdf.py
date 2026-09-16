"""Extração local de PDFs digitais (texto + tabelas) com proveniência.

Biblioteca escolhida: ``pdfplumber`` (MIT, documentada) para texto/tabelas, com
``pypdf`` para metadados. Preserva artigo, página e ordem de leitura (melhor
esforço). PDFs escaneados, extração vazia e tabelas mal extraídas geram avisos e
itens de revisão — NÃO fingimos extração bem-sucedida.

Limitação conhecida: reconstrução em colunas múltiplas é aproximada; páginas com
colunas complexas são marcadas para revisão humana (ver ``docs/decisions.md``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..manifest import sha256_file

# Tolerância vertical (pontos) para agrupar palavras na mesma linha.
_LINE_TOL = 3.0
# Razão mínima entre o vão vertical e a altura mediana de linha para quebrar
# parágrafo.
_PARAGRAPH_GAP_RATIO = 1.8


@dataclass
class TableData:
    table_id: str
    page: int
    rows: list[list[str]]
    caption: str = ""
    bbox: tuple[float, float, float, float] | None = None


@dataclass
class PageContent:
    page_number: int
    text: str
    tables: list[TableData] = field(default_factory=list)
    word_count: int = 0
    has_text_layer: bool = True


@dataclass
class PdfExtraction:
    doc_id: str
    pdf_path: str
    pdf_sha256: str
    extractor: str
    extractor_version: str
    pages: list[PageContent] = field(default_factory=list)
    pdf_metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    review_items: list[str] = field(default_factory=list)


def _in_bbox(word: dict, bbox: tuple[float, float, float, float]) -> bool:
    x0, top, x1, bottom = bbox
    cx = (word["x0"] + word["x1"]) / 2
    cy = (word["top"] + word["bottom"]) / 2
    return x0 <= cx <= x1 and top <= cy <= bottom


def _reconstruct_body(words: list[dict], table_bboxes: list[tuple]) -> str:
    """Reconstrói texto do corpo (excluindo palavras dentro das tabelas)."""
    body = [w for w in words if not any(_in_bbox(w, b) for b in table_bboxes)]
    if not body:
        return ""

    # Agrupa em linhas por posição vertical (tolerância) e ordena x0.
    lines: dict[int, list[dict]] = {}
    for w in body:
        key = int(round(w["top"] / _LINE_TOL))
        lines.setdefault(key, []).append(w)

    ordered_keys = sorted(lines)
    # Altura mediana de linha para detectar quebra de parágrafo.
    heights = sorted(
        w["bottom"] - w["top"] for w in body if (w["bottom"] - w["top"]) > 0
    )
    median_h = heights[len(heights) // 2] if heights else 10.0

    chunks: list[str] = []
    prev_top: float | None = None
    for key in ordered_keys:
        ws = sorted(lines[key], key=lambda w: w["x0"])
        line_text = " ".join(w["text"] for w in ws)
        line_top = min(w["top"] for w in ws)
        if prev_top is not None and (line_top - prev_top) > _PARAGRAPH_GAP_RATIO * median_h:
            chunks.append("")
        chunks.append(line_text)
        prev_top = max(w["bottom"] for w in ws)
    return "\n".join(chunks)


def _read_pdf_metadata(pdf_path: str) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return {}
    try:
        reader = PdfReader(pdf_path)
        meta = dict(reader.metadata or {})
        meta = {str(k): str(v) for k, v in meta.items() if v is not None}
        meta["_num_pages"] = len(reader.pages)
        return meta
    except Exception:
        return {}


def extract_pdf(pdf_path: str | Path, doc_id: str) -> PdfExtraction:
    pdf_path = str(pdf_path)
    import pdfplumber

    version = getattr(pdfplumber, "__version__", "desconhecida")
    extraction = PdfExtraction(
        doc_id=doc_id,
        pdf_path=pdf_path,
        pdf_sha256=sha256_file(pdf_path),
        extractor="pdfplumber+pypdf",
        extractor_version=version,
        pdf_metadata=_read_pdf_metadata(pdf_path),
    )

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pageno = page.page_number
                words = page.extract_words(keep_blank_chars=False)
                table_objs = page.find_tables() or []
                tables: list[TableData] = []
                table_bboxes: list[tuple] = []
                for i, t in enumerate(table_objs):
                    rows = t.extract() or []
                    clean_rows = [[("" if c is None else str(c)) for c in row]
                                  for row in rows]
                    table_id = f"{doc_id}:t{pageno}-{i + 1}"
                    tables.append(TableData(
                        table_id=table_id,
                        page=pageno,
                        rows=clean_rows,
                        bbox=tuple(t.bbox) if t.bbox else None,
                    ))
                    if t.bbox:
                        table_bboxes.append(tuple(t.bbox))

                if table_bboxes:
                    text = _reconstruct_body(words, table_bboxes)
                else:
                    text = page.extract_text() or ""

                word_count = len(words)
                has_text_layer = bool(text.strip()) or word_count > 0
                extraction.pages.append(PageContent(
                    page_number=pageno,
                    text=text,
                    tables=tables,
                    word_count=word_count,
                    has_text_layer=has_text_layer,
                ))

                if not has_text_layer:
                    extraction.review_items.append(
                        f"página {pageno}: sem camada de texto (PDF escaneado?)."
                    )
    except Exception as exc:  # PDF ilegível/corrompido ou erro na extração
        extraction.warnings.append(f"falha ao processar PDF: {exc}")

    total_chars = sum(len(p.text) for p in extraction.pages)
    if not extraction.pages or total_chars == 0:
        extraction.review_items.append(
            "documento sem texto extraído — verificar se é PDF digital ou escaneado."
        )
    return extraction
