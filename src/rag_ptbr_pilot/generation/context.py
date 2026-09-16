"""Montagem de contexto para geração RAG (etapa opcional).

Política única para todos os métodos: top-k inicial fixo, orçamento de contexto
fixo e mesma formatação. Evidências excluídas pelo orçamento são REGISTRADAS
(para calcular a cobertura após a montagem — não confundir ranking recuperado
com contexto efetivamente consumido).

Contagem de tokens: usa o tokenizador de referência (aproximação) por padrão e
contabiliza o template + a reserva para resposta. NÃO trata contagem de palavras
como contagem exata de tokens (ver ``docs/decisions.md``). Estouros evitáveis
são bloqueados, não truncados silenciosamente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..errors import ConfigError
from ..schemas import ChunkRecord
from ..chunking.tokenizer_ref import SimpleTokenizer

_REF = SimpleTokenizer()


def _default_count(text: str) -> int:
    return _REF.count(text)


@dataclass
class ContextAssembly:
    context_text: str
    included_chunk_ids: list[str] = field(default_factory=list)
    excluded_chunk_ids: list[str] = field(default_factory=list)
    context_tokens: int = 0
    prompt_tokens: int = 0
    response_reserve_tokens: int = 0
    total_estimated_tokens: int = 0
    overflow_blocked: bool = False
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "included_chunk_ids": self.included_chunk_ids,
            "excluded_chunk_ids": self.excluded_chunk_ids,
            "context_tokens": self.context_tokens,
            "prompt_tokens": self.prompt_tokens,
            "response_reserve_tokens": self.response_reserve_tokens,
            "total_estimated_tokens": self.total_estimated_tokens,
            "overflow_blocked": self.overflow_blocked,
            "note": self.note,
        }


def format_context_entry(chunk: ChunkRecord) -> str:
    """Entrada de contexto citável: usa o chunk_id como identificador de citação."""
    meta = f"doc={chunk.doc_id}"
    if chunk.page is not None:
        meta += f" | página {chunk.page}"
    return f"[ID: {chunk.chunk_id} | {meta}]\n{chunk.text.strip()}"


def assemble_context(ranked_ids: list[str],
                     chunk_by_id: dict[str, ChunkRecord],
                     top_k: int,
                     context_budget_tokens: int,
                     prompt_text: str,
                     response_reserve_tokens: int,
                     model_num_ctx: int,
                     count_tokens: Callable[[str], int] | None = None) -> ContextAssembly:
    """Monta o contexto respeitando orçamento fixo e reserva de resposta."""
    count = count_tokens or _default_count
    prompt_tokens = count(prompt_text)

    # Bloqueia estouro evitável: prompt + reserva já estouram a janela.
    if prompt_tokens + response_reserve_tokens > model_num_ctx:
        raise ConfigError(
            "Prompt de geração + reserva de resposta excedem a janela do modelo "
            f"({prompt_tokens} + {response_reserve_tokens} > {model_num_ctx}). "
            "Reduza o prompt ou a reserva."
        )

    available = model_num_ctx - prompt_tokens - response_reserve_tokens
    budget = min(context_budget_tokens, available)

    asm = ContextAssembly(
        context_text="",
        prompt_tokens=prompt_tokens,
        response_reserve_tokens=response_reserve_tokens,
    )

    candidates = ranked_ids[:top_k]
    parts: list[str] = []
    used = 0
    for cid in candidates:
        chunk = chunk_by_id[cid]
        entry = format_context_entry(chunk) + "\n"
        cost = count(entry)
        if used + cost > budget:
            asm.excluded_chunk_ids.append(cid)
            continue
        parts.append(entry)
        used += cost
        asm.included_chunk_ids.append(cid)

    asm.context_text = "\n".join(parts)
    asm.context_tokens = used
    asm.total_estimated_tokens = prompt_tokens + used + response_reserve_tokens
    asm.overflow_blocked = False
    if asm.excluded_chunk_ids:
        asm.note = (
            f"{len(asm.excluded_chunk_ids)} evidência(s) do top-{top_k} excluída(s) "
            "pelo orçamento de contexto (registradas para análise de cobertura)."
        )
    return asm
