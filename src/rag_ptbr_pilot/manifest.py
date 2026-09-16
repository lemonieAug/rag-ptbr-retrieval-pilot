"""Hashing determinístico e registro de execução (manifesto).

Hashes são usados para:
- invalidar caches quando texto/modelo/dimensão muda;
- vincular rankings e métricas à versão exata do corpus/benchmark;
- reproduzir execuções (arquivos a guardar — ver README, seção de reprodutibilidade).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

HASH_CHUNK = 8192


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Hash SHA-256 de um arquivo, lido em blocos (funciona para PDFs grandes)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(HASH_CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(obj: object) -> str:
    """Serialização JSON canônica (chaves ordenadas, separadores compactos)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=str)


def hash_json(obj: object) -> str:
    return sha256_text(canonical_json(obj))


def short_hash(value: str, n: int = 12) -> str:
    return value[:n]


def timestamp_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class RunManifest:
    """Registro de uma execução futura (corpus, benchmark, modelos, ambiente)."""

    run_id: str
    created_at: str = field(default_factory=timestamp_iso)
    config_hash: str = ""
    corpus_version: str = ""
    prompts_hash: str = ""
    qrels_hash: str = ""
    # Checkpoints/revisões reais (resolvidos na preparação dos modelos)
    model_revisions: dict = field(default_factory=dict)
    # Biblioteca e ambiente
    package_version: str = ""
    library_versions: dict = field(default_factory=dict)
    python_version: str = ""
    hardware: dict = field(default_factory=dict)
    seed: int | None = None
    # Parâmetros efetivos da execução
    parameters: dict = field(default_factory=dict)
    # Configurações realmente executadas
    configurations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "config_hash": self.config_hash,
            "corpus_version": self.corpus_version,
            "prompts_hash": self.prompts_hash,
            "qrels_hash": self.qrels_hash,
            "model_revisions": self.model_revisions,
            "package_version": self.package_version,
            "library_versions": self.library_versions,
            "python_version": self.python_version,
            "hardware": self.hardware,
            "seed": self.seed,
            "parameters": self.parameters,
            "configurations": self.configurations,
        }
