"""Configuração tipada (YAML -> Pydantic).

O arquivo padrão é ``configs/default.yaml``. Todos os defaults do experimento
estão registrados aqui e documentados no ``docs/protocol.md``.

Importar/validar configuração NÃO carrega modelos nem inicia downloads.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .adapters.specs import EMBEDDING_SPECS
from .io_utils import load_yaml
from .paths import project_root, resolve

DEFAULT_CONFIG_PATH = "configs/default.yaml"


# ---------------------------------------------------------------------------
# Sub-configurações
# ---------------------------------------------------------------------------


class PathsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    articles_dir: str = "data/raw/articles"
    metadata_path: str = "data/metadata/articles.yaml"
    extracted_dir: str = "data/processed/extracted"
    corrections_dir: str = "data/processed/corrections"
    chunks_path: str = "data/processed/chunks/chunks.jsonl"
    corpus_manifest_path: str = "data/processed/chunks/corpus_manifest.json"

    annotations_dir: str = "data/annotations"
    questions_path: str = "data/annotations/questions.yaml"
    qrels_path: str = "data/annotations/qrels.yaml"
    evidence_groups_path: str = "data/annotations/evidence_groups.yaml"
    reviews_dir: str = "data/annotations/reviews"


class ChunkingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_tokens: int = Field(default=350, gt=0)
    overlap_tokens: int = Field(default=50, ge=0)
    reference_tokenizer: str = "simple"
    # Cap de segurança por bloco antes de subdividir (evita blocos gigantes).
    max_block_tokens: int = Field(default=2000, gt=0)
    # Tabelas longas: subdivisão por grupos de linhas.
    table_row_group: int = Field(default=6, gt=0)
    repeat_table_header: bool = True
    # Exige validação com os tokenizers de todos os embeddings selecionados.
    require_token_validation: bool = True


class BM25Params(BaseModel):
    model_config = ConfigDict(extra="forbid")

    k1: float = Field(default=1.2, gt=0)
    b: float = Field(default=0.75, ge=0, le=1)


class RRFFusionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    c: float = Field(default=60.0, gt=0)
    weight_bm25: float = Field(default=1.0, gt=0)
    weight_dense: float = Field(default=1.0, gt=0)


class LexicalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lowercase: bool = True
    strip_accents: bool = False          # NÃO remover acentos (decisão metodológica)
    unicode_nfkc: bool = True            # normalização Unicode NFKC
    token_pattern: str = r"\w+"          # tokenização lexical fixa (Unicode)


class RetrievalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_n: int = Field(default=50, gt=0)
    bm25: BM25Params = Field(default_factory=BM25Params)
    rrf: RRFFusionConfig = Field(default_factory=RRFFusionConfig)
    lexical: LexicalConfig = Field(default_factory=LexicalConfig)
    normalize_embeddings: bool = True
    cosine_similarity: bool = True


class MetricsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    k_values: list[int] = Field(default_factory=lambda: [1, 5, 10])
    primary: str = "ndcg@10"


class DtypeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    colibri: str = "fp32"
    embeddinggemma: str = "bf16"
    qwen_embedding: str = "fp16"
    e5: str = "fp32"


class RerankerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkpoint: str = "Qwen/Qwen3-Reranker-0.6B"
    max_length: int = Field(default=8192, gt=0)
    instruction: str = (
        "Given a web search query, retrieve relevant passages that answer the query"
    )
    device: str = "auto"
    dtype: str = "fp16"


class GeneratorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: str = "ollama"
    model: str = "qwen3:14b"
    host: str = "http://127.0.0.1:11434"
    temperature: float = Field(default=0.0, ge=0)
    seed: int | None = None
    num_ctx: int = Field(default=8192, gt=0)
    reasoning: bool = False
    tag: str | None = None       # resolvido na preparação
    digest: str | None = None    # resolvido na preparação


class ModelsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    embeddings: list[str] = Field(
        default_factory=lambda: ["colibri", "embeddinggemma", "qwen_embedding", "e5"]
    )
    cache_dir: str = "artifacts/models"
    device: str = "auto"         # auto | cuda | cpu
    dtype: DtypeConfig = Field(default_factory=DtypeConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    generator: GeneratorConfig = Field(default_factory=GeneratorConfig)

    @field_validator("embeddings")
    @classmethod
    def _known_embeddings(cls, v: list[str]) -> list[str]:
        unknown = [n for n in v if n not in EMBEDDING_SPECS]
        if unknown:
            raise ValueError(
                f"Embeddings desconhecidos: {unknown}. "
                f"Opções: {sorted(EMBEDDING_SPECS)}"
            )
        if len(v) != len(set(v)):
            raise ValueError("Lista de embeddings com duplicatas")
        return v


class ExperimentsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # None = todas as configurações da matriz; senão, lista de ids/padrões.
    select: list[str] | None = None
    embeddings: list[str] | None = None   # sobrescreve models.embeddings
    include_reranker: bool = True
    seed: int = 42


class GenerationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_template: str = "prompts/generation.txt"
    top_k_context: int = Field(default=5, gt=0)
    context_budget_tokens: int = Field(default=4000, gt=0)
    response_reserve_tokens: int = Field(default=512, ge=0)
    human_eval_shuffle_seed: int = 7


class ReportingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results_dir: str = "results"
    artifacts_dir: str = "artifacts"
    render_report: bool = True


# ---------------------------------------------------------------------------
# Configuração raiz
# ---------------------------------------------------------------------------


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root: Path = Field(default_factory=project_root)
    language: str = "pt-BR"
    paths: PathsConfig = Field(default_factory=PathsConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    experiments: ExperimentsConfig = Field(default_factory=ExperimentsConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)

    @model_validator(mode="after")
    def _overlap_lt_target(self) -> "AppConfig":
        if self.chunking.overlap_tokens >= self.chunking.target_tokens:
            raise ValueError(
                "chunking.overlap_tokens deve ser menor que chunking.target_tokens"
            )
        return self

    # -- helpers de resolução -----------------------------------------------
    def resolve(self, path: str | Path) -> Path:
        return resolve(self.root, path)

    def articles_dir(self) -> Path:
        return self.resolve(self.paths.articles_dir)

    def effective_embeddings(self) -> list[str]:
        return self.experiments.embeddings or self.models.embeddings


def load_config(path: str | Path | None = None) -> AppConfig:
    """Carrega e valida a configuração YAML."""
    cfg_path = Path(path) if path else Path(DEFAULT_CONFIG_PATH)
    raw = load_yaml(cfg_path)
    cfg = AppConfig.model_validate(raw)
    return cfg


def config_to_dict(cfg: AppConfig) -> dict[str, Any]:
    """Exporta a configuração efetiva (para hash e manifesto).

    ``root`` é específico do ambiente (caminho absoluto da máquina) e é REMOVIDO
    do hash para que o ``config_hash`` seja portável entre máquinas/diretórios.
    """
    d = cfg.model_dump(mode="json")
    d.pop("root", None)
    return d
