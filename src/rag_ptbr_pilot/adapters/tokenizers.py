"""Carregamento de tokenizers e contagem de tokens (leve, sob demanda).

Usado pela validação de chunks (``chunking.token_validation``) e pelos próprios
adaptadores. Carrega SOMENTE o tokenizer (não o modelo), e nunca baixa nada se
``local_files_only=True`` — falha com instrução útil quando o artefato falta.
"""

from __future__ import annotations

from ..errors import MissingArtifactError
from .specs import EmbeddingSpec, RERANKER_SPEC
from .local import local_checkpoint

_SPECIALS = {
    "task": RERANKER_SPEC.instruction,
    "query": "",
    "text": "",
}


def load_tokenizer(checkpoint: str, cache_dir: str | None = None,
                   local_files_only: bool = True,
                   revisions_path: str | None = None):
    """Carrega um tokenizer do HF (leve). Importa transformers sob demanda."""
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:  # pragma: no cover
        raise MissingArtifactError(
            "Biblioteca 'transformers' não instalada. Instale as dependências "
            "pesadas: pip install -e '.[models]'"
        ) from exc

    kwargs = {"local_files_only": local_files_only}
    if cache_dir:
        kwargs["cache_dir"] = cache_dir
    try:
        return AutoTokenizer.from_pretrained(
            local_checkpoint(checkpoint, cache_dir, revisions_path), **kwargs)
    except Exception as exc:  # OSError/EnvironmentError quando falta no cache
        raise MissingArtifactError(
            f"Tokenizer de {checkpoint!r} não encontrado no cache local. "
            f"Rode primeiro: rag-ptbr prepare-models (ou huggingface-cli download "
            f"{checkpoint}). Erro original: {exc}"
        ) from exc


def _format_template(template: str, text: str, task: str) -> str:
    values = dict(_SPECIALS)
    values["task"] = task or _SPECIALS["task"]
    values["query"] = text
    values["text"] = text
    return template.format_map(values)


def count_document_tokens(spec: EmbeddingSpec, tokenizer, text: str) -> int:
    """Tokens de um documento com o template oficial + tokens especiais."""
    formatted = _format_template(spec.document_template, text, spec.task_instruction)
    return len(tokenizer.encode(formatted, add_special_tokens=True))


def count_query_tokens(spec: EmbeddingSpec, tokenizer, text: str) -> int:
    """Tokens de uma consulta com o template oficial + tokens especiais."""
    formatted = _format_template(spec.query_template, text, spec.task_instruction)
    return len(tokenizer.encode(formatted, add_special_tokens=True))


def count_reranker_pair_tokens(tokenizer, query: str, document: str,
                               instruction: str | None = None) -> int:
    """Tokens do par formatado para o reranker, incluindo prefixo/sufixo."""
    from .specs import RERANKER_SPEC as R

    inst = instruction or R.instruction
    formatted = (
        f"<Instruct>: {inst}\n<Query>: {query}\n<Document>: {document}"
    )
    prefix_tokens = tokenizer.encode(R.prefix, add_special_tokens=False)
    suffix_tokens = tokenizer.encode(R.suffix, add_special_tokens=False)
    body = tokenizer.encode(formatted, add_special_tokens=True)
    return len(prefix_tokens) + len(body) + len(suffix_tokens)
