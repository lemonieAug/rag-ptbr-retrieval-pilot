"""Geração RAG opcional (montagem de contexto + Ollama + avaliação humana)."""

from .context import ContextAssembly, assemble_context, format_context_entry
from .human_eval import (
    build_human_eval_rows,
    render_human_eval_csv,
    write_human_eval_csv,
)
from .ollama_client import GenerationResult, OllamaClient

__all__ = [
    "ContextAssembly",
    "GenerationResult",
    "OllamaClient",
    "assemble_context",
    "build_human_eval_rows",
    "format_context_entry",
    "render_human_eval_csv",
    "write_human_eval_csv",
]
