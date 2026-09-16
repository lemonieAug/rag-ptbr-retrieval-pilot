"""Interfaces dos adaptadores (embeddings e reranker).

Nenhum import de ``torch``/``transformers`` aqui — os módulos concretos importam
essas bibliotecas DENTRO dos métodos ``load``/``encode``, para que importar o
pacote nunca carregue modelos nem inicie downloads.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from .specs import EmbeddingSpec, RerankerSpec


class EmbeddingAdapter(ABC):
    """Codifica consultas e documentos com um modelo de embedding específico.

    Vetores são sempre normalizados (norma L2 = 1) para uso com cosseno via
    produto interno. Dimensões nativas, sem redução/quantização.
    """

    def __init__(self, spec: EmbeddingSpec, cache_dir: str | None = None,
                 device: str = "auto", dtype: str | None = None) -> None:
        self.spec = spec
        self.cache_dir = cache_dir
        self.device = device
        self.dtype = dtype or spec.default_dtype
        self.dimension: int | None = None

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def checkpoint(self) -> str:
        return self.spec.checkpoint

    @abstractmethod
    def load(self) -> None:
        """Carrega o modelo/checkpoint. Lança MissingArtifactError se ausente."""

    @abstractmethod
    def unload(self) -> None:
        """Libera o modelo (GPU/memória) — execução em etapas."""

    @abstractmethod
    def encode_queries(self, texts: list[str]) -> np.ndarray:
        """Aplica o template OFICIAL de consulta e devolve vetores normalizados."""

    @abstractmethod
    def encode_documents(self, texts: list[str]) -> np.ndarray:
        """Aplica o template OFICIAL de documento e devolve vetores normalizados."""

    @abstractmethod
    def count_query_tokens(self, text: str) -> int:
        """Nº de tokens da consulta incluindo template + tokens especiais."""

    @abstractmethod
    def count_document_tokens(self, text: str) -> int:
        """Nº de tokens do documento incluindo template + tokens especiais."""


class RerankerAdapter(ABC):
    """Calcula relevância consulta–documento (0..1) com o reranker oficial."""

    def __init__(self, spec: RerankerSpec, cache_dir: str | None = None,
                 device: str = "auto", dtype: str | None = None,
                 max_length: int | None = None) -> None:
        self.spec = spec
        self.cache_dir = cache_dir
        self.device = device
        self.dtype = dtype or spec.default_dtype
        self.max_length = max_length or spec.max_length

    @property
    def name(self) -> str:
        return self.spec.name

    @abstractmethod
    def load(self) -> None:
        """Carrega o modelo. Lança MissingArtifactError se ausente."""

    @abstractmethod
    def unload(self) -> None:
        """Libera o modelo."""

    @abstractmethod
    def score(self, query: str, documents: list[str]) -> list[float]:
        """Relevância de cada documento para a consulta (mesma ordem)."""

    @abstractmethod
    def count_pair_tokens(self, query: str, document: str) -> int:
        """Nº de tokens do par formatado (para validação do limite de entrada)."""


def resolve_device(device: str) -> str:
    """Resolve 'auto' para cuda/cpu sem importar torch no topo."""
    if device in ("cuda", "cpu"):
        return device
    if device == "auto":
        import torch  # import sob demanda

        return "cuda" if torch.cuda.is_available() else "cpu"
    raise ValueError(f"device inválido: {device!r} (use auto|cuda|cpu)")


def resolve_dtype(dtype: str, device: str) -> Any:
    """Mapeia fp32/bf16/fp16 para tipos torch, respeitando suporte do device."""
    import torch  # import sob demanda

    if dtype == "fp16":
        return torch.float16
    if dtype == "bf16":
        if device == "cuda" and torch.cuda.is_bf16_supported():
            return torch.bfloat16
        if device == "cpu" and hasattr(torch, "bfloat16"):
            # CPU: bfloat16 é suportado em torch recente; caso contrário, fp32.
            return torch.bfloat16
        return torch.float32  # fallback seguro para EmbeddingGemma (nunca FP16)
    return torch.float32
