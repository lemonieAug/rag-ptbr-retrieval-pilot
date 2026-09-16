"""Adaptadores reais dos quatro embeddings (carregamento sob demanda).

Formatos implementados conforme os model cards consultados (ver ``docs/decisions.md``):

- ``colibri`` e ``embeddinggemma``: SentenceTransformer com ``prompt_name``
  oficial (query -> ``task: search result | query: ``; document ->
  ``title: none | text: ``). Pooling/normalização gerenciados pela própria ST.
- ``e5``: transformers, instruction na consulta
  (``Instruct: {task}\\nQuery: {query}``), documento sem instruction,
  average pooling + normalize, limite 512 tokens.
- ``qwen_embedding``: transformers, instruction na consulta
  (``Instruct: {task}\\nQuery:{query}``), documento sem instruction,
  last-token pooling (pooling oficial) + normalize.

EmbeddingGemma usa FP32/BF16 (nunca FP16 — incompatibilidade documentada das
ativações). Todos carregam de cache local e falham com instrução útil se ausente.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ..errors import ConfigError, MissingArtifactError
from .base import EmbeddingAdapter, resolve_device, resolve_dtype
from .specs import EmbeddingSpec
from .tokenizers import count_document_tokens, count_query_tokens, load_tokenizer


def _mean_pool(last_hidden_states: Any, attention_mask: Any) -> Any:
    import torch

    last_hidden = last_hidden_states.masked_fill(
        ~attention_mask[..., None].bool(), 0.0
    )
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


def _last_token_pool(last_hidden_states: Any, attention_mask: Any) -> Any:
    import torch

    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    sequence_lengths = attention_mask.sum(dim=1) - 1
    batch_size = last_hidden_states.shape[0]
    return last_hidden_states[
        torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths
    ]


def _import_missing() -> None:
    raise MissingArtifactError(
        "Bibliotecas 'torch'/'transformers'/'sentence-transformers' não instaladas. "
        "Instale: pip install -e '.[models]' (veja o README para o PyTorch)."
    )


class SentenceTransformerEmbedding(EmbeddingAdapter):
    """colibri / embeddinggemma — usa os prompt_name oficiais da ST."""

    def load(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            _import_missing()

        device = resolve_device(self.device)
        dtype = resolve_dtype(self.dtype, device)
        # EmbeddingGemma: garantir que nunca rode em FP16 (incompatibilidade
        # documentada das ativações) — forçar BF16 com fallback para FP32.
        if self.spec.fp16_incompatible and getattr(dtype, "__name__", "") == "float16":
            dtype = resolve_dtype("bf16", device)
        model_kwargs: dict[str, Any] = {"local_files_only": True, "torch_dtype": dtype}
        tokenizer_kwargs: dict[str, Any] = {"local_files_only": True}
        try:
            self._model = SentenceTransformer(
                self.checkpoint,
                cache_folder=self.cache_dir,
                device=device,
                model_kwargs=model_kwargs,
                tokenizer_kwargs=tokenizer_kwargs,
            )
        except Exception as exc:
            raise MissingArtifactError(
                f"Falha ao carregar {self.checkpoint!r} do cache local. "
                f"Rode primeiro: rag-ptbr prepare-models. Erro: {exc}"
            ) from exc
        self._device = device
        self._dtype = dtype
        self.dimension = int(self._model.get_sentence_embedding_dimension())

    def unload(self) -> None:
        if getattr(self, "_model", None) is not None:
            import gc

            import torch

            self._model.to("cpu")
            del self._model
            self._model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

    def _encode(self, texts: list[str], prompt_name: str | None) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimension or 0), dtype=np.float32)
        kwargs: dict[str, Any] = {
            "normalize_embeddings": True,
            "convert_to_numpy": True,
            "show_progress_bar": False,
            "batch_size": 8,
        }
        if prompt_name is not None:
            kwargs["prompt_name"] = prompt_name
        out = self._model.encode(texts, **kwargs)
        return np.asarray(out, dtype=np.float32)

    def encode_queries(self, texts: list[str]) -> np.ndarray:
        return self._encode(texts, self.spec.query_prompt_name)

    def encode_documents(self, texts: list[str]) -> np.ndarray:
        return self._encode(texts, self.spec.document_prompt_name)

    def _tokenizer(self):
        if getattr(self, "_tok", None) is None:
            self._tok = load_tokenizer(self.checkpoint, self.cache_dir)
        return self._tok

    def count_query_tokens(self, text: str) -> int:
        return count_query_tokens(self.spec, self._tokenizer(), text)

    def count_document_tokens(self, text: str) -> int:
        return count_document_tokens(self.spec, self._tokenizer(), text)


class HFTransformersEmbedding(EmbeddingAdapter):
    """e5 (mean pooling) / qwen_embedding (last-token pooling) via transformers."""

    def load(self) -> None:
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ImportError:
            _import_missing()

        device = resolve_device(self.device)
        dtype = resolve_dtype(self.dtype, device)
        model_kwargs: dict[str, Any] = {
            "local_files_only": True,
            "torch_dtype": dtype,
        }
        if self.cache_dir:
            model_kwargs["cache_dir"] = self.cache_dir
        tok_kwargs: dict[str, Any] = {"local_files_only": True}
        if self.cache_dir:
            tok_kwargs["cache_dir"] = self.cache_dir
        if self.spec.pooling == "last_token":
            tok_kwargs["padding_side"] = "left"

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.checkpoint, **tok_kwargs)
            self._model = AutoModel.from_pretrained(self.checkpoint, **model_kwargs)
        except Exception as exc:
            raise MissingArtifactError(
                f"Falha ao carregar {self.checkpoint!r} do cache local. "
                f"Rode primeiro: rag-ptbr prepare-models. Erro: {exc}"
            ) from exc

        self._model.eval()
        self._model.to(device)
        self._device = device
        self._dtype = dtype
        # Dimensão nativa: infere do hidden size do modelo.
        self.dimension = int(self._model.config.hidden_size)

    def unload(self) -> None:
        if getattr(self, "_model", None) is not None:
            import gc

            import torch

            self._model.to("cpu")
            del self._model
            self._model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

    def _format(self, template: str, text: str) -> str:
        return template.format_map({
            "task": self.spec.task_instruction,
            "query": text,
            "text": text,
        })

    def _encode(self, texts: list[str], template: str) -> np.ndarray:
        import torch
        import torch.nn.functional as F

        if not texts:
            return np.zeros((0, self.dimension or 0), dtype=np.float32)

        max_len = self.spec.max_document_tokens
        formatted = [self._format(template, t) for t in texts]
        if max_len is not None:
            for t in formatted:
                n = len(self._tokenizer.encode(t, add_special_tokens=True))
                if n > max_len:
                    raise ConfigError(
                        f"Texto excede o limite de {max_len} tokens do modelo "
                        f"{self.name} ({n} tokens). Reduza o chunk/bloco ou a consulta. "
                        "Truncamento silencioso é proibido no piloto."
                    )

        batch = self._tokenizer(
            formatted,
            padding=True,
            truncation=True,
            max_length=max_len,
            return_tensors="pt",
        )
        batch = {k: v.to(self._device) for k, v in batch.items()}
        with torch.no_grad():
            outputs = self._model(**batch)
        if self.spec.pooling == "mean":
            emb = _mean_pool(outputs.last_hidden_state, batch["attention_mask"])
        else:
            emb = _last_token_pool(outputs.last_hidden_state, batch["attention_mask"])
        emb = F.normalize(emb, p=2, dim=1)
        return emb.detach().cpu().numpy().astype(np.float32)

    def encode_queries(self, texts: list[str]) -> np.ndarray:
        return self._encode(texts, self.spec.query_template)

    def encode_documents(self, texts: list[str]) -> np.ndarray:
        return self._encode(texts, self.spec.document_template)

    def count_query_tokens(self, text: str) -> int:
        return count_query_tokens(self.spec, self._tokenizer, text)

    def count_document_tokens(self, text: str) -> int:
        return count_document_tokens(self.spec, self._tokenizer, text)


def build_embedding_adapter(name: str, cache_dir: str | None = None,
                            device: str = "auto",
                            dtype: str | None = None) -> EmbeddingAdapter:
    from .specs import get_embedding_spec

    spec = get_embedding_spec(name)
    if spec.pooling == "sentence_transformers":
        return SentenceTransformerEmbedding(spec, cache_dir=cache_dir,
                                            device=device, dtype=dtype)
    return HFTransformersEmbedding(spec, cache_dir=cache_dir,
                                   device=device, dtype=dtype)
