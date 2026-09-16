"""Schemas tipados do domínio (Pydantic v2).

Estes modelos definem o contrato dos arquivos de benchmark e dos dados
processados. A validação acontece na leitura, rejeitando IDs inexistentes,
tipos inválidos e campos obrigatórios ausentes.

Campos de avaliação (resposta gold, qrels, grupos obrigatórios, ``origin_doc_id``)
NUNCA são passados aos recuperadores/reranker/gerador — ver ``benchmark.leakage``.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Enumerações
# ---------------------------------------------------------------------------


class ReviewStatus(str, Enum):
    """Estado de revisão humana de um item do benchmark."""

    draft = "draft"          # rascunho — fora da avaliação por padrão
    approved = "approved"    # revisado e aprovado — entra nas métricas
    rejected = "rejected"    # rejeitado — não entra nas métricas


class QuestionType(str, Enum):
    """Tipo de pergunta do benchmark."""

    factual = "factual"              # responde com uma evidência
    multi_evidence = "multi_evidence"  # exige mais de uma evidência


class Modality(str, Enum):
    """Modalidade predominante do bloco/evidência."""

    text = "text"
    table = "table"
    visual = "visual"    # descrição visual preparada por humano (opcional)
    mixed = "mixed"


# ---------------------------------------------------------------------------
# Metadados de artigos
# ---------------------------------------------------------------------------


class ArticleMetadata(BaseModel):
    """Metadados de um artigo do corpus (data/metadata/articles.yaml)."""

    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$",
                        description="Identificador estável do artigo.")
    title: str = Field(..., min_length=1)
    authors: list[str] = Field(default_factory=list)
    year: int | None = Field(default=None, ge=1800, le=2200)
    venue: str | None = None
    language: str = "pt-BR"
    pdf_filename: str = Field(..., description="Nome do arquivo em data/raw/articles/.")
    pages: int | None = Field(default=None, ge=0)
    notes: str | None = None


# ---------------------------------------------------------------------------
# Perguntas, evidências e qrels
# ---------------------------------------------------------------------------


class EvidenceRef(BaseModel):
    """Evidência verificada no PDF que suporta a resposta de referência.

    ``quote`` é o trecho canônico no PDF. ``chunk_ids`` opcionalmente aponta os
    chunks que materializam a evidência (resolvido após o congelamento).
    ``required_group`` vincula a evidência a um grupo obrigatório de uma
    pergunta multi-evidência.
    """

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    doc_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    page: int | None = Field(default=None, ge=1)
    section: str | None = None
    quote: str = ""
    chunk_ids: list[str] = Field(default_factory=list)
    required_group: str | None = None


class Question(BaseModel):
    """Pergunta do benchmark (data/annotations/questions.yaml)."""

    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    text: str = Field(..., min_length=1)
    expected_answer: str = Field(..., min_length=1)
    origin_doc_id: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Artigo de origem — SOMENTE para anotação/avaliação.",
    )
    evidence: list[EvidenceRef] = Field(default_factory=list)
    question_type: QuestionType = QuestionType.factual
    modality: Modality = Modality.text
    review_status: ReviewStatus = ReviewStatus.draft
    notes: str | None = None

    @field_validator("evidence")
    @classmethod
    def _evidence_ids_unique(cls, v: list[EvidenceRef]) -> list[EvidenceRef]:
        ids = [e.evidence_id for e in v]
        if len(ids) != len(set(ids)):
            raise ValueError("evidence_id duplicado dentro da pergunta")
        return v


class QrelEntry(BaseModel):
    """Relevância binária de um chunk para uma pergunta (qrels)."""

    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    chunk_id: str
    relevance: int = Field(..., ge=0, le=1,
                           description="1 = suporte efetivo à resposta; 0 = não relevante.")


class EvidenceGroup(BaseModel):
    """Grupo obrigatório de uma pergunta multi-evidência.

    - Cada grupo representa UMA informação necessária para a resposta.
    - ``chunk_ids`` contém alternativas (OR) que satisfazem o mesmo grupo.
    - Cobertura completa exige satisfazer TODOS os grupos obrigatórios.
    """

    model_config = ConfigDict(extra="forbid")

    group_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    question_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    required: bool = True
    description: str = ""
    chunk_ids: list[str] = Field(default_factory=list)


class ReviewRecord(BaseModel):
    """Registro de revisão humana de um item do benchmark."""

    model_config = ConfigDict(extra="forbid")

    review_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]+$")
    target_type: Literal["question", "evidence", "qrel", "group", "chunk", "doc"]
    target_id: str
    status: ReviewStatus
    reviewer: str = ""
    comments: str = ""
    date: str = ""


# ---------------------------------------------------------------------------
# Dados processados (chunks e corpus)
# ---------------------------------------------------------------------------


class ChunkRecord(BaseModel):
    """Chunk canônico congelado (data/processed/chunks/chunks.jsonl)."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    doc_id: str
    block_id: str = Field(..., description="Identificador do bloco de origem.")
    page: int | None = Field(default=None, ge=1)
    section: str | None = None
    modality: Modality = Modality.text
    text: str
    token_count_ref: int = Field(..., ge=0)
    char_count: int = Field(default=0, ge=0)
    source_block_hash: str = ""

    @field_validator("text")
    @classmethod
    def _text_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("texto canônico do chunk vazio")
        return v


class CorpusManifest(BaseModel):
    """Manifesto do corpus congelado (corpus_manifest.json)."""

    model_config = ConfigDict(extra="allow")

    corpus_version: str
    frozen: bool = False
    chunk_count: int
    doc_ids: list[str]
    chunking_config: dict = Field(default_factory=dict)
    hashes: dict = Field(default_factory=dict)
    token_validation: dict = Field(default_factory=dict)
    generated_at: str = ""
