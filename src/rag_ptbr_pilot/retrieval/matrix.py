"""Matriz experimental e comparações do piloto.

Com ``E`` embeddings, a matriz completa tem ``2 + 4*E`` configurações:

- ``bm25`` e ``bm25_rerank`` (independem do embedding; calculadas uma vez);
- para cada embedding: ``dense_<e>``, ``dense_<e>_rerank``, ``hybrid_<e>``,
  ``hybrid_<e>_rerank``.

Com os 3 embeddings do piloto => 14 configurações. A matriz é gerada
programaticamente e permite selecionar um subconjunto por padrão de id.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigSpec:
    config_id: str
    initial_retrieval: str   # "bm25" | "dense" | "hybrid"
    embedding: str | None    # None para BM25
    rerank: bool


@dataclass(frozen=True)
class Comparison:
    label: str
    a: str   # método (numerador da comparação)
    b: str   # baseline (denominador)


def build_matrix(embeddings: list[str]) -> list[ConfigSpec]:
    specs: list[ConfigSpec] = [
        ConfigSpec("bm25", "bm25", None, False),
        ConfigSpec("bm25_rerank", "bm25", None, True),
    ]
    for e in embeddings:
        specs.append(ConfigSpec(f"dense_{e}", "dense", e, False))
        specs.append(ConfigSpec(f"dense_{e}_rerank", "dense", e, True))
        specs.append(ConfigSpec(f"hybrid_{e}", "hybrid", e, False))
        specs.append(ConfigSpec(f"hybrid_{e}_rerank", "hybrid", e, True))
    return specs


def select_matrix(specs: list[ConfigSpec], select: list[str] | None,
                  include_reranker: bool = True) -> list[ConfigSpec]:
    """Seleciona um subconjunto por padrões de id (substring)."""
    if not select or "all" in select or "*" in select:
        chosen = list(specs)
    else:
        chosen = [s for s in specs
                  if any(pat in s.config_id for pat in select)]
    if not include_reranker:
        chosen = [s for s in chosen if not s.rerank]
    return chosen


def base_config_id(spec: ConfigSpec) -> str:
    """Id da variante SEM reranker correspondente (mesmos N candidatos)."""
    if spec.rerank:
        return spec.config_id.removesuffix("_rerank")
    return spec.config_id


def standard_comparisons(embeddings: list[str]) -> list[Comparison]:
    """Comparações a apresentar (seção 'matriz experimental' do protocolo)."""
    comps: list[Comparison] = []
    for e in embeddings:
        comps += [
            Comparison("pipeline_total", f"hybrid_{e}_rerank", f"dense_{e}"),
            Comparison("hibridizacao", f"hybrid_{e}", f"dense_{e}"),
            Comparison("rerank_dense", f"dense_{e}_rerank", f"dense_{e}"),
            Comparison("rerank_hybrid", f"hybrid_{e}_rerank", f"hybrid_{e}"),
            Comparison("hibridizacao_com_rerank", f"hybrid_{e}_rerank", f"dense_{e}_rerank"),
        ]
    return comps
