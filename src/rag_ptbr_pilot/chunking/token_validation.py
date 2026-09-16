"""Validação de limites de tokens com os tokenizers REAIS dos embeddings.

O alvo de 350/50 tokens (tokenizer de referência) NÃO é garantia de
compatibilidade. Aqui validamos cada chunk contra os tokenizers de TODOS os
embeddings selecionados, contabilizando template + tokens especiais, e
subdividimos blocos UMA única vez para caber em todos os encoders.

O limite de entrada do reranker é validado separadamente (``adapters.reranker``).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..adapters.specs import EmbeddingSpec
from ..adapters.tokenizers import count_document_tokens, load_tokenizer


@dataclass
class TokenValidationReport:
    binding_model: str | None = None
    binding_limit: int | None = None
    per_model: dict = field(default_factory=dict)
    subdivided_blocks: list = field(default_factory=list)
    overflow_remaining: list = field(default_factory=list)


def compute_binding(specs: list[EmbeddingSpec]) -> tuple[str | None, int | None]:
    """Modelo com o menor limite de entrada documentado (o que 'amarra' o chunk)."""
    limited = [(s.name, s.max_document_tokens)
               for s in specs if s.max_document_tokens is not None]
    if not limited:
        return None, None
    name, limit = min(limited, key=lambda t: t[1])
    return name, limit


def document_overhead(spec: EmbeddingSpec, tokenizer) -> int:
    """Tokens de template + especiais com texto vazio (overhead fixo)."""
    return count_document_tokens(spec, tokenizer, "")


def split_block_to_limit(tokenizer, spec: EmbeddingSpec, text: str,
                         limit: int, overlap: int) -> list[str]:
    """Subdivide um bloco em trechos que cabem em ``limit`` tokens do modelo.

    Corta nas fronteiras de tokens reais (offset mapping), preservando o texto.
    """
    overhead = document_overhead(spec, tokenizer)
    available = max(1, limit - overhead)
    enc = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    ids = enc["input_ids"]
    offsets = enc["offset_mapping"]
    if not ids or len(ids) <= available:
        return [text]

    pieces: list[str] = []
    start = 0
    while start < len(ids):
        end = min(start + available, len(ids))
        s = offsets[start][0]
        e = offsets[end - 1][1]
        piece = text[s:e]
        if piece.strip():
            pieces.append(piece)
        if end >= len(ids):
            break
        start = max(start + 1, end - overlap)
    return pieces


def load_validators(specs: list[EmbeddingSpec], cache_dir: str | None):
    """Carrega tokenizers (leve) e devolve (spec, tokenizer, limit, overhead)."""
    validators = []
    for spec in specs:
        tokenizer = load_tokenizer(spec.checkpoint, cache_dir)
        validators.append((spec, tokenizer, spec.max_document_tokens,
                           document_overhead(spec, tokenizer)))
    return validators
