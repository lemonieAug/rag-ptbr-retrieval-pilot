"""Resolução de caminhos do projeto.

O diretório raiz é resolvido a partir de ``RAG_PTBR_PILOT_ROOT`` ou do diretório
corrente. Todos os caminhos do pacote são relativos a essa raiz, mantendo a
portabilidade entre Linux e Windows (usando ``pathlib``).
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT_ENV = "RAG_PTBR_PILOT_ROOT"


def project_root() -> Path:
    """Retorna a raiz do projeto.

    Ordem de precedência:
    1. Variável de ambiente ``RAG_PTBR_PILOT_ROOT``.
    2. Diretório corrente de trabalho.
    """
    env_root = os.environ.get(PROJECT_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.cwd().resolve()


def resolve(root: Path, path: str | Path) -> Path:
    """Resolve um caminho relativo à raiz; caminhos absolutos são preservados."""
    p = Path(path)
    if p.is_absolute():
        return p
    return (root / p).resolve()
