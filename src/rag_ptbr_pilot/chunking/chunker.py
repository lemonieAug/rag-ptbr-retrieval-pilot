"""Chunking: blocos -> chunks canônicos congelados.

Fluxo:
1. Parseia o Markdown canônico em blocos (página/seção/modalidade).
2. Divide cada bloco com o tokenizer de referência (alvo 350 / sobreposição 50).
3. Valida contra os tokenizers reais dos embeddings selecionados e, se algum
   chunk estourar o limite do modelo mais restritivo (E5 = 512), SUBDIVIDE o
   bloco UMA única vez para caber em todos os encoders.

Os mesmos chunks e o mesmo texto canônico são usados por TODOS os métodos.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..adapters.specs import EmbeddingSpec
from ..adapters.tokenizers import count_document_tokens, load_tokenizer
from ..config import ChunkingConfig
from ..manifest import hash_json, timestamp_iso
from ..schemas import ChunkRecord, CorpusManifest, Modality
from .md_parser import Block, parse_blocks
from .token_validation import (
    TokenValidationReport,
    compute_binding,
    load_validators,
    split_block_to_limit,
)
from .tokenizer_ref import SimpleTokenizer

_MODALITY_MAP = {"text": Modality.text, "table": Modality.table}


@dataclass
class ChunkingResult:
    chunks: list[ChunkRecord] = field(default_factory=list)
    report: TokenValidationReport = field(default_factory=TokenValidationReport)


def _make_chunk(block: Block, piece: str, index: int, ref: SimpleTokenizer) -> ChunkRecord:
    return ChunkRecord(
        chunk_id=f"{block.block_id}-c{index:03d}",
        doc_id=block.doc_id,
        block_id=block.block_id,
        page=block.page,
        section=block.section,
        modality=_MODALITY_MAP.get(block.modality, Modality.text),
        text=piece,
        token_count_ref=ref.count(piece),
        char_count=len(piece),
        source_block_hash=block.source_block_hash,
    )


def build_chunks(md_text: str, doc_id: str, chunking_cfg: ChunkingConfig,
                 specs: list[EmbeddingSpec], cache_dir: str | None) -> ChunkingResult:
    """Constrói os chunks canônicos de um documento com validação de tokens."""
    blocks = parse_blocks(md_text, doc_id)
    ref = SimpleTokenizer()
    result = ChunkingResult()

    binding_name, binding_limit = compute_binding(specs)
    result.report.binding_model = binding_name
    result.report.binding_limit = binding_limit

    validators: list = []
    binding_tokenizer = None
    binding_spec: EmbeddingSpec | None = None

    if chunking_cfg.require_token_validation and specs:
        validators = load_validators(specs, cache_dir)
        if binding_name is not None and binding_limit is not None:
            binding_spec = next((s for s in specs if s.name == binding_name), None)
            binding_tokenizer = load_tokenizer(binding_spec.checkpoint, cache_dir)

    for block in blocks:
        pieces = ref.split(block.text, chunking_cfg.target_tokens,
                           chunking_cfg.overlap_tokens)
        needs_subdivide = False
        if binding_tokenizer is not None and binding_spec is not None:
            for piece in pieces:
                if count_document_tokens(binding_spec, binding_tokenizer, piece) > binding_limit:
                    needs_subdivide = True
                    break

        if needs_subdivide:
            pieces = split_block_to_limit(
                binding_tokenizer, binding_spec, block.text,
                binding_limit, chunking_cfg.overlap_tokens,
            )
            result.report.subdivided_blocks.append(block.block_id)

        for i, piece in enumerate(pieces):
            if not piece.strip():
                continue
            result.chunks.append(_make_chunk(block, piece, i, ref))

    # Resumo por modelo (overflow após subdivisão) — contabiliza template+especiais.
    for spec, tokenizer, limit, _overhead in validators:
        overflow = 0
        limit_known = limit is not None
        for c in result.chunks:
            n = count_document_tokens(spec, tokenizer, c.text)
            if limit_known and n > limit:
                overflow += 1
                result.report.overflow_remaining.append({
                    "chunk_id": c.chunk_id, "model": spec.name, "tokens": n,
                })
        result.report.per_model[spec.name] = {
            "limit": limit,
            "limit_known": limit_known,
            "overflow_chunks": overflow,
        }

    return result


def compute_corpus_version(chunks: list[ChunkRecord]) -> str:
    payload = [
        {"chunk_id": c.chunk_id, "doc_id": c.doc_id, "text": c.text}
        for c in sorted(chunks, key=lambda c: c.chunk_id)
    ]
    return hash_json(payload)


def build_corpus_manifest(chunks: list[ChunkRecord], doc_hashes: dict,
                          chunking_cfg: ChunkingConfig,
                          report: TokenValidationReport) -> CorpusManifest:
    doc_ids = sorted({c.doc_id for c in chunks})
    return CorpusManifest(
        corpus_version=compute_corpus_version(chunks),
        frozen=True,
        chunk_count=len(chunks),
        doc_ids=doc_ids,
        chunking_config=chunking_cfg.model_dump(mode="json"),
        hashes={
            "documents": doc_hashes,
            "chunks": compute_corpus_version(chunks),
        },
        token_validation={
            "binding_model": report.binding_model,
            "binding_limit": report.binding_limit,
            "per_model": report.per_model,
            "subdivided_blocks": report.subdivided_blocks,
            "overflow_remaining": report.overflow_remaining,
        },
        generated_at=timestamp_iso(),
    )
