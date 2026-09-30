"""Reranker oficial Qwen/Qwen3-Reranker-0.6B (formato e score do model card).

O score é a probabilidade P("yes") obtida por softmax sobre os logits dos tokens
``yes``/``no`` (ver código oficial do model card, seção "Using Transformers").
NÃO é similaridade de embeddings nem nota inventada pelo gerador.

O reranker APENAS reordena os candidatos recebidos; nunca adiciona documentos.
"""

from __future__ import annotations

import math
from typing import Any

from ..errors import MissingArtifactError
from .base import RerankerAdapter, resolve_device, resolve_dtype
from .specs import RERANKER_SPEC, RerankerSpec
from .local import local_checkpoint


class Qwen3Reranker(RerankerAdapter):
    """Qwen/Qwen3-Reranker-0.6B."""

    def load(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise MissingArtifactError(
                "Bibliotecas 'torch'/'transformers' não instaladas. "
                "Instale: pip install -e '.[models]'"
            ) from None

        checkpoint_path = local_checkpoint(self.spec.checkpoint, self.cache_dir, self.revisions_path)
        device = resolve_device(self.device)
        dtype = resolve_dtype(self.dtype, device)
        tok_kwargs: dict[str, Any] = {
            "padding_side": "left",
            "local_files_only": True,
        }
        model_kwargs: dict[str, Any] = {
            "local_files_only": True,
            "torch_dtype": dtype,
        }
        if self.cache_dir:
            tok_kwargs["cache_dir"] = self.cache_dir
            model_kwargs["cache_dir"] = self.cache_dir

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, **tok_kwargs)
            self._model = AutoModelForCausalLM.from_pretrained(
                checkpoint_path, **model_kwargs
            )
        except Exception as exc:
            raise MissingArtifactError(
                f"Falha ao carregar {self.spec.checkpoint!r} do cache local. "
                f"Rode primeiro: rag-ptbr prepare-models. Erro: {exc}"
            ) from exc

        self._model.eval()
        self._model.to(device)
        self._device = device
        self._dtype = dtype
        self._token_true_id = self._tokenizer.convert_tokens_to_ids("yes")
        self._token_false_id = self._tokenizer.convert_tokens_to_ids("no")
        self._prefix_tokens = self._tokenizer.encode(
            self.spec.prefix, add_special_tokens=False
        )
        self._suffix_tokens = self._tokenizer.encode(
            self.spec.suffix, add_special_tokens=False
        )

    def unload(self) -> None:
        if getattr(self, "_model", None) is not None:
            import gc

            import torch

            del self._model
            self._model = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def _format(self, query: str, document: str) -> str:
        return (
            f"<Instruct>: {self.spec.instruction}\n"
            f"<Query>: {query}\n"
            f"<Document>: {document}"
        )

    def count_pair_tokens(self, query: str, document: str) -> int:
        from .tokenizers import count_reranker_pair_tokens

        return count_reranker_pair_tokens(
            self._tokenizer, query, document, self.spec.instruction
        )

    def score(self, query: str, documents: list[str]) -> list[float]:
        import torch

        if not documents:
            return []

        formatted = [self._format(query, d) for d in documents]
        # Valida limite de entrada: bloqueia estouro evitável.
        prefix_len = len(self._prefix_tokens)
        suffix_len = len(self._suffix_tokens)
        body_limit = self.max_length - prefix_len - suffix_len
        for d, f in zip(documents, formatted):
            n = len(self._tokenizer.encode(f, add_special_tokens=True))
            if n > body_limit:
                raise MissingArtifactError(
                    f"Par consulta–documento excede o limite do reranker "
                    f"({n} > {body_limit} tokens do corpo). Reduza o documento."
                )

        scores: list[float] = []
        batch_size = self.batch_size
        for start in range(0, len(formatted), batch_size):
            batch = formatted[start:start + batch_size]
            inputs = self._tokenizer(
                batch,
                padding=False,
                truncation="longest_first",
                return_attention_mask=False,
                max_length=body_limit,
            )
            for i, ids in enumerate(inputs["input_ids"]):
                inputs["input_ids"][i] = (
                    self._prefix_tokens + ids + self._suffix_tokens
                )
            padded = self._tokenizer.pad(
                inputs, padding=True, return_tensors="pt", max_length=self.max_length
            )
            padded = {k: v.to(self._device) for k, v in padded.items()}
            with torch.no_grad():
                logits = self._model(**padded, use_cache=False).logits[:, -1, :]
            true_vec = logits[:, self._token_true_id]
            false_vec = logits[:, self._token_false_id]
            pair = torch.stack([false_vec, true_vec], dim=1)
            pair = torch.nn.functional.log_softmax(pair, dim=1)
            batch_scores = pair[:, 1].exp().tolist()
            scores.extend(float(s) for s in batch_scores)
        return scores


def build_reranker(cache_dir: str | None = None, device: str = "auto",
                   dtype: str | None = None,
                   max_length: int | None = None, batch_size: int = 8,
                   revisions_path: str | None = None) -> RerankerAdapter:
    return Qwen3Reranker(RERANKER_SPEC, cache_dir=cache_dir, device=device,
                         dtype=dtype, max_length=max_length,
                         batch_size=batch_size, revisions_path=revisions_path)
