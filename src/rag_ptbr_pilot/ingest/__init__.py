"""Ingestão: extração de PDFs, conversão Markdown e proveniência."""

from .extractor import build_provenance, extract_article
from .markdown import render_markdown
from .pdf import PdfExtraction, extract_pdf

__all__ = [
    "PdfExtraction",
    "extract_pdf",
    "render_markdown",
    "build_provenance",
    "extract_article",
]
