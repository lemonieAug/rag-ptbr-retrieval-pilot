"""Configuração global dos testes.

- Adiciona ``src/`` ao ``sys.path`` (permite rodar os testes sem instalar).
- Força modo offline do Hugging Face: NENHUM teste pode baixar modelos.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
