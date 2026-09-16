"""Orquestração da extração: PDF -> Markdown canônico + proveniência."""

from __future__ import annotations

from pathlib import Path

from ..errors import ConfigError
from ..io_utils import save_json, save_text
from ..manifest import sha256_text, timestamp_iso
from ..schemas import ArticleMetadata
from .markdown import render_markdown
from .pdf import extract_pdf


def build_provenance(extraction, md_text: str, corrections: list[str]) -> dict:
    tables_count = sum(len(p.tables) for p in extraction.pages)
    return {
        "doc_id": extraction.doc_id,
        "pdf_filename": Path(extraction.pdf_path).name,
        "pdf_sha256": extraction.pdf_sha256,
        "representation_sha256": sha256_text(md_text),
        "extractor": extraction.extractor,
        "extractor_version": extraction.extractor_version,
        "num_pages": len(extraction.pages),
        "tables_count": tables_count,
        "warnings": extraction.warnings,
        "review_items": extraction.review_items,
        "corrections": corrections,
        "pdf_metadata": extraction.pdf_metadata,
        "generated_at": timestamp_iso(),
    }


def extract_article(articles_dir: str | Path, meta: ArticleMetadata,
                    out_dir: str | Path) -> dict:
    """Extrai um artigo e grava ``<doc_id>.md`` + ``<doc_id>.provenance.json``."""
    articles_dir = Path(articles_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = articles_dir / meta.pdf_filename
    if not pdf_path.exists():
        raise ConfigError(
            f"PDF não encontrado: {pdf_path}. Coloque o arquivo em "
            f"{articles_dir} (ver README, seção 'onde colocar os PDFs')."
        )

    extraction = extract_pdf(pdf_path, meta.doc_id)
    md_text = render_markdown(extraction)
    md_path = out_dir / f"{meta.doc_id}.md"
    save_text(md_path, md_text)

    provenance = build_provenance(extraction, md_text, corrections=[])
    prov_path = out_dir / f"{meta.doc_id}.provenance.json"
    save_json(prov_path, provenance)

    return {
        "doc_id": meta.doc_id,
        "markdown_path": str(md_path),
        "provenance_path": str(prov_path),
        "num_pages": provenance["num_pages"],
        "tables_count": provenance["tables_count"],
        "warnings": provenance["warnings"],
        "review_items": provenance["review_items"],
    }
