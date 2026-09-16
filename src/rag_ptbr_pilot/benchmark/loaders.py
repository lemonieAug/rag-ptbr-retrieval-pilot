"""Carregamento validado dos arquivos de benchmark (Pydantic).

Convenção YAML: cada arquivo tem uma chave de topo:
``articles`` / ``questions`` / ``qrels`` / ``evidence_groups``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from ..errors import ConfigError, ValidationError
from ..io_utils import load_yaml
from ..schemas import (
    ArticleMetadata,
    EvidenceGroup,
    QrelEntry,
    Question,
)

T = TypeVar("T", bound=BaseModel)


def _load_list(path: str | Path, key: str, model: Type[T], what: str) -> list[T]:
    if not Path(path).exists():
        raise ConfigError(
            f"Arquivo de {what} não encontrado: {path}. Copie o template de "
            f"configs/templates/ e preencha (ver README)."
        )
    raw = load_yaml(path)
    items = raw.get(key, [])
    out: list[T] = []
    for i, item in enumerate(items):
        try:
            out.append(model.model_validate(item))
        except PydanticValidationError as exc:
            raise ValidationError(f"{what} inválido no item {i}: {exc}") from exc
    return out


def load_articles(path: str | Path) -> list[ArticleMetadata]:
    return _load_list(path, "articles", ArticleMetadata, "metadados de artigos")


def load_questions(path: str | Path) -> list[Question]:
    return _load_list(path, "questions", Question, "perguntas")


def load_qrels(path: str | Path) -> list[QrelEntry]:
    return _load_list(path, "qrels", QrelEntry, "qrels")


def load_evidence_groups(path: str | Path) -> list[EvidenceGroup]:
    return _load_list(path, "evidence_groups", EvidenceGroup, "grupos de evidência")
