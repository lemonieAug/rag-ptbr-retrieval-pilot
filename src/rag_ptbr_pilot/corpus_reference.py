"""Versioned identity and source checks for this edition's audited corpus."""

from __future__ import annotations

import re

from .errors import ConfigError
from .io_utils import load_yaml
from .manifest import sha256_file, sha256_text

REFERENCE_PATH = "configs/corpus_reference.yaml"


def load_reference(cfg) -> dict:
    path = cfg.resolve(REFERENCE_PATH)
    try:
        reference = load_yaml(path)
    except OSError as exc:
        raise ConfigError(f"Referência do corpus ausente: {path}") from exc
    if not isinstance(reference, dict) or not isinstance(reference.get("documents"), dict):
        raise ConfigError(f"Referência do corpus inválida: {path}")
    for key in ("corpus_version", "chunks_sha256"):
        if not isinstance(reference.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", reference[key]):
            raise ConfigError(f"{key} inválido em {path}")
    for doc_id, entry in reference["documents"].items():
        if (not isinstance(entry, dict) or not re.fullmatch(r"[A-Za-z0-9_-]+", doc_id)
                or not isinstance(entry.get("pdf_filename"), str)
                or not re.fullmatch(r"[A-Za-z0-9_.-]+\.pdf", entry["pdf_filename"])):
            raise ConfigError(f"Documento inválido em {path}: {doc_id}")
        for key in ("pdf_sha256", "md_sha256"):
            if not isinstance(entry.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                raise ConfigError(f"{key} inválido para {doc_id} em {path}")
    return reference


def source_issues(cfg, reference: dict, kind: str) -> tuple[list[str], list[str]]:
    """Return relative paths missing and paths whose bytes/text differ from audit."""
    if kind not in ("pdf", "markdown"):
        raise ValueError(kind)
    missing, incompatible = [], []
    for doc_id, entry in reference["documents"].items():
        relative = (f"{cfg.paths.articles_dir}/{entry['pdf_filename']}" if kind == "pdf"
                    else f"{cfg.paths.extracted_dir}/{doc_id}.md")
        path = cfg.resolve(relative)
        if not path.is_file():
            missing.append(relative)
            continue
        try:
            actual = sha256_file(path) if kind == "pdf" else sha256_text(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            incompatible.append(relative)
            continue
        if actual != entry["pdf_sha256" if kind == "pdf" else "md_sha256"]:
            incompatible.append(relative)
    return missing, incompatible


def assert_canonical_sources(cfg, *, include_markdown: bool) -> None:
    reference = load_reference(cfg)
    kinds = ("pdf", "markdown") if include_markdown else ("pdf",)
    for kind in kinds:
        missing, incompatible = source_issues(cfg, reference, kind)
        if missing or incompatible:
            raise ConfigError(
                f"Fontes canônicas {kind} necessárias antes de reconstruir o corpus. "
                f"Ausentes: {missing}; hashes divergentes: {incompatible}."
            )


def assert_official_corpus(cfg, manifest) -> None:
    reference = load_reference(cfg)
    if manifest.corpus_version != reference["corpus_version"]:
        raise ConfigError(
            f"corpus_version incompatível: {manifest.corpus_version}; "
            f"esperado {reference['corpus_version']}. Transfira o corpus auditado."
        )
    chunks_path = cfg.resolve(cfg.paths.chunks_path)
    if sha256_file(chunks_path) != reference["chunks_sha256"]:
        raise ConfigError(f"chunks.jsonl divergente da auditoria: {chunks_path}")
