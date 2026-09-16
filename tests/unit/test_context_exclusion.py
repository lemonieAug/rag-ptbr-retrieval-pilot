"""Registro de evidências excluídas do contexto e bloqueio de estouro."""

import pytest

from rag_ptbr_pilot.errors import ConfigError
from rag_ptbr_pilot.generation.context import assemble_context
from rag_ptbr_pilot.schemas import ChunkRecord


def _chunk(cid, words):
    text = " ".join([words] * 40)  # 40 tokens de referência
    return ChunkRecord(chunk_id=cid, doc_id="d", block_id=cid, text=text,
                       token_count_ref=40, char_count=len(text))


def test_excluded_evidence_is_recorded():
    chunks = {f"c{i}": _chunk(f"c{i}", "palavra") for i in range(5)}
    ranked = ["c0", "c1", "c2", "c3", "c4"]
    asm = assemble_context(
        ranked, chunks,
        top_k=3,
        context_budget_tokens=60,
        prompt_text="pergunta",
        response_reserve_tokens=5,
        model_num_ctx=200,
    )
    # top-3 = [c0, c1, c2]; orçamento 60 só comporta ~1 entrada
    assert len(asm.included_chunk_ids) + len(asm.excluded_chunk_ids) == 3
    assert asm.excluded_chunk_ids  # houve exclusão registrada
    assert asm.included_chunk_ids == ["c0"]


def test_no_exclusion_when_budget_fits():
    chunks = {f"c{i}": _chunk(f"c{i}", "palavra") for i in range(3)}
    ranked = ["c0", "c1", "c2"]
    asm = assemble_context(
        ranked, chunks, top_k=3, context_budget_tokens=10000,
        prompt_text="pergunta", response_reserve_tokens=5, model_num_ctx=20000,
    )
    assert asm.excluded_chunk_ids == []
    assert asm.included_chunk_ids == ["c0", "c1", "c2"]


def test_overflow_is_blocked_not_silently_truncated():
    chunks = {"c0": _chunk("c0", "palavra")}
    with pytest.raises(ConfigError):
        assemble_context(
            ["c0"], chunks, top_k=1, context_budget_tokens=10,
            prompt_text="p" * 100, response_reserve_tokens=50, model_num_ctx=100,
        )
