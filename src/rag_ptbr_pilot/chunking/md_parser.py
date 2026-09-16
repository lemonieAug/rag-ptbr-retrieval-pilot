"""Parser do Markdown canônico em blocos (com página, seção e modalidade).

Lê o formato produzido por ``ingest.markdown``:

- ``<!-- PAGE N -->`` delimita página.
- ``<!-- TABLE id page=N -->`` ... ``<!-- /TABLE -->`` delimita tabela.
- Cabeçalhos (Markdown ``#``, numerados ou heurística de caixa alta) definem a
  seção corrente (melhor esforço; corrigível no Markdown).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..manifest import sha256_text

_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.+?)\s*#*\s*$")
_NUMBERED_HEADING_RE = re.compile(r"^\s*\d+(\.\d+)*\.?\s+\S.*$")
_TABLE_RE = re.compile(r"^<!--\s*TABLE\s+(\S+)\s+page=(\d+)\s*-->$")
_PAGE_RE = re.compile(r"^<!--\s*PAGE\s+(\d+)\s*-->$")

_COMMON_SECTIONS = {
    "resumo", "abstract", "introdução", "introducao", "introduction",
    "métodos", "metodos", "methods", "materiais e métodos",
    "materiais e metodos", "materials and methods", "resultados", "results",
    "discussão", "discussao", "discussion", "conclusão", "conclusao",
    "conclusion", "conclusões", "conclusoes", "referências", "referencias",
    "references", "bibliografia", "agradecimentos", "acknowledgements",
    "trabalhos relacionados", "related work", "avaliação", "avaliacao",
    "experimentos", "experiments", "limitações", "limitacoes",
}


@dataclass
class Block:
    block_id: str
    doc_id: str
    page: int | None
    section: str | None
    modality: str  # "text" | "table"
    text: str
    caption: str = ""
    source_block_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.source_block_hash:
            self.source_block_hash = sha256_text(self.text)


def _uppercase_ratio(s: str) -> float:
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


def _strip_md_heading(line: str) -> str:
    m = _HEADING_RE.match(line)
    if m:
        return m.group(1).strip()
    return line.strip().lstrip("#").strip()


def detect_heading(line: str) -> str | None:
    """Retorna o texto do cabeçalho se a linha é um cabeçalho, senão None."""
    s = line.strip()
    if not s:
        return None
    if s.startswith("#"):
        return _strip_md_heading(s)
    if _NUMBERED_HEADING_RE.match(s) and len(s) < 100:
        stripped = s.rstrip()
        if not stripped.endswith((".", ",", ";", ":")):
            return stripped
    low = s.lower().rstrip(":")
    if low in _COMMON_SECTIONS:
        return s.rstrip(":")
    if len(s) < 80 and _uppercase_ratio(s) > 0.6:
        return s
    return None


def _make_block(doc_id: str, index: int, page: int | None, section: str | None,
                modality: str, text: str, caption: str = "") -> Block:
    return Block(
        block_id=f"{doc_id}-b{index:04d}",
        doc_id=doc_id,
        page=page,
        section=section,
        modality=modality,
        text=text,
        caption=caption,
    )


def parse_blocks(md_text: str, doc_id: str) -> list[Block]:
    """Converte o Markdown canônico em blocos ordenados por leitura."""
    blocks: list[Block] = []
    current_page: int | None = None
    current_section: str | None = None
    seen_first_heading = False
    para_lines: list[str] = []
    in_table = False
    table_id = ""
    table_page: int | None = None
    table_caption = ""
    table_lines: list[str] = []
    counter = 0

    def flush_para() -> None:
        nonlocal para_lines, counter
        text = "\n".join(para_lines).strip()
        para_lines = []
        if text:
            blocks.append(_make_block(doc_id, counter, current_page,
                                      current_section, "text", text))
            counter += 1

    def flush_table() -> None:
        nonlocal table_lines, counter, in_table
        text = "\n".join(table_lines).strip()
        if text:
            blocks.append(_make_block(doc_id, counter, table_page,
                                      current_section, "table", text,
                                      caption=table_caption))
            counter += 1
        table_lines = []
        table_caption = ""
        in_table = False

    for raw in md_text.splitlines():
        line = raw.rstrip()
        t = _TABLE_RE.match(line)
        if t:
            flush_para()
            in_table = True
            table_id = t.group(1)
            table_page = int(t.group(2))
            table_lines = []
            table_caption = ""
            continue
        if line.strip() == "<!-- /TABLE -->":
            if in_table:
                flush_table()
            continue
        p = _PAGE_RE.match(line)
        if p:
            flush_para()
            current_page = int(p.group(1))
            continue
        if in_table:
            if line.startswith("**Tabela"):
                table_caption = line.strip("* ").split(":", 1)[-1].strip()
            else:
                table_lines.append(line)
            continue

        heading = detect_heading(line)
        if heading is not None:
            flush_para()
            # O primeiro cabeçalho é o título do documento (== doc_id): não vira seção.
            if not seen_first_heading and heading.strip() == doc_id:
                seen_first_heading = True
                continue
            seen_first_heading = True
            current_section = heading
            continue
        # Comentários HTML não reconhecidos (não-PAGE/TABLE) são ignorados.
        stripped = line.strip()
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue
        if not line.strip():
            flush_para()
            continue
        para_lines.append(line.strip())

    flush_para()
    if in_table:
        flush_table()
    return blocks
