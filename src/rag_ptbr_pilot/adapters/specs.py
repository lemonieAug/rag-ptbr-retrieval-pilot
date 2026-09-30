"""Especificações dos modelos (embeddings, reranker, gerador).

Cada spec registra o formato OFICIAL de consulta/documento/pooling/precisão,
conforme os model cards consultados (ver ``docs/decisions.md`` para as fontes e
as decisões tomadas). Revisões auditadas ficam em ``configs/model_revisions.yaml``;
``prepare-models`` confere os snapshots e grava as revisões no manifesto.

Nenhum destes módulos importa ``torch``/``transformers`` no topo — o carregamento
é sempre sob demanda.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Instrução de tarefa padrão usada pelos modelos "instruct" (E5 e Qwen).
DEFAULT_TASK_INSTRUCTION = (
    "Given a web search query, retrieve relevant passages that answer the query"
)


@dataclass(frozen=True)
class EmbeddingSpec:
    name: str
    checkpoint: str
    family: str
    # Template textual (documentado). {task} e {query}/{text} são preenchidos.
    query_template: str
    document_template: str
    task_instruction: str
    # "sentence_transformers" -> usa prompt_name oficial do modelo;
    # "mean" -> average pooling explícito; "last_token" -> pooling oficial Qwen.
    pooling: Literal["sentence_transformers", "mean", "last_token"]
    uses_prompt_name: bool
    query_prompt_name: str | None = None
    document_prompt_name: str | None = None
    default_dtype: str = "fp32"            # fp32 | bf16 | fp16
    # Limite de entrada documentado (None = resolver na preparação dos modelos).
    max_document_tokens: int | None = None
    max_document_tokens_note: str = ""
    gated: bool = False
    fp16_incompatible: bool = False
    dimension_note: str = ""


@dataclass(frozen=True)
class RerankerSpec:
    name: str
    checkpoint: str
    # Formato oficial (ver docs/decisions.md e model card Qwen3-Reranker-0.6B):
    instruction: str
    system_prompt: str
    prefix: str
    suffix: str
    max_length: int
    default_dtype: str = "fp16"
    score_via: str = "softmax_yes_no"


@dataclass(frozen=True)
class GeneratorSpec:
    backend: str
    model: str
    host: str
    temperature: float
    num_ctx: int
    reasoning: bool
    tag: str | None
    digest: str | None


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

EMBEDDING_SPECS: dict[str, EmbeddingSpec] = {
    "colibri": EmbeddingSpec(
        name="colibri",
        checkpoint="tardellirs/colibri-embed-ptbr",
        family="gemma",
        query_template="task: search result | query: {query}",
        document_template="title: none | text: {text}",
        task_instruction="",
        pooling="sentence_transformers",
        uses_prompt_name=True,
        query_prompt_name="query",
        document_prompt_name="document",
        default_dtype="fp32",
        max_document_tokens=None,
        max_document_tokens_note="Derivado de EmbeddingGemma; verificar limite no prep.",
        gated=False,
        fp16_incompatible=False,
        dimension_note="768-dim (Matryoshka disponível, mas NÃO usado no piloto).",
    ),
    "qwen_embedding": EmbeddingSpec(
        name="qwen_embedding",
        checkpoint="Qwen/Qwen3-Embedding-4B",
        family="qwen",
        query_template="Instruct: {task}\nQuery:{query}",
        document_template="{text}",
        task_instruction=DEFAULT_TASK_INSTRUCTION,
        pooling="last_token",
        uses_prompt_name=False,
        query_prompt_name=None,
        document_prompt_name=None,
        default_dtype="fp16",
        max_document_tokens=8192,
        max_document_tokens_note="Exemplo oficial usa 8192; contexto nominal 32k.",
        gated=False,
        fp16_incompatible=False,
        dimension_note="2560-dim.",
    ),
    "e5": EmbeddingSpec(
        name="e5",
        checkpoint="intfloat/multilingual-e5-large-instruct",
        family="e5",
        query_template="Instruct: {task}\nQuery: {query}",
        document_template="{text}",
        task_instruction=DEFAULT_TASK_INSTRUCTION,
        pooling="mean",
        uses_prompt_name=False,
        query_prompt_name=None,
        document_prompt_name=None,
        default_dtype="fp32",
        max_document_tokens=512,
        max_document_tokens_note="Limite oficial documentado no model card (limitations).",
        gated=False,
        fp16_incompatible=False,
        dimension_note="1024-dim.",
    ),
}

# ---------------------------------------------------------------------------
# Reranker (fixo no piloto)
# ---------------------------------------------------------------------------

RERANKER_SPEC = RerankerSpec(
    name="qwen3_reranker",
    checkpoint="Qwen/Qwen3-Reranker-0.6B",
    instruction=DEFAULT_TASK_INSTRUCTION,
    system_prompt=(
        'Judge whether the Document meets the requirements based on the Query '
        'and the Instruct provided. Note that the answer can only be "yes" or "no".'
    ),
    prefix=(
        '<|im_start|>system\n'
        'Judge whether the Document meets the requirements based on the Query '
        'and the Instruct provided. Note that the answer can only be "yes" or "no".'
        '<|im_end|>\n<|im_start|>user\n'
    ),
    suffix=('<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'),
    max_length=8192,
    default_dtype="fp16",
    score_via="softmax_yes_no",
)

# ---------------------------------------------------------------------------
# Gerador secundário (Qwen3 14B via Ollama local) — etapa opcional
# ---------------------------------------------------------------------------

GENERATOR_SPEC = GeneratorSpec(
    backend="ollama",
    model="qwen3:14b",
    host="http://127.0.0.1:11434",
    temperature=0.0,
    num_ctx=8192,
    reasoning=False,
    tag=None,      # resolvido na preparação (ex.: qwen3:14b com tag/digest reais)
    digest=None,
)


def get_embedding_spec(name: str) -> EmbeddingSpec:
    try:
        return EMBEDDING_SPECS[name]
    except KeyError as exc:  # pragma: no cover - guarda de configuração
        raise KeyError(
            f"Embedding desconhecido: {name!r}. Opções: {sorted(EMBEDDING_SPECS)}"
        ) from exc
