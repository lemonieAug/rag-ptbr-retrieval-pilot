"""Testes da matriz experimental: geração programática e seleção."""

from rag_ptbr_pilot.retrieval.matrix import build_matrix, select_matrix

EMBEDDINGS = ["colibri", "embeddinggemma", "qwen_embedding", "e5"]


def test_full_matrix_is_18_for_4_embeddings():
    specs = build_matrix(EMBEDDINGS)
    assert len(specs) == 18  # 2 + 4*4
    ids = [s.config_id for s in specs]
    assert "bm25" in ids
    assert "bm25_rerank" in ids
    assert "dense_e5" in ids and "hybrid_e5_rerank" in ids


def test_matrix_contains_all_variants_per_embedding():
    specs = build_matrix(["colibri"])
    ids = {s.config_id for s in specs}
    assert ids == {
        "bm25", "bm25_rerank",
        "dense_colibri", "dense_colibri_rerank",
        "hybrid_colibri", "hybrid_colibri_rerank",
    }


def test_select_by_substring_includes_rerank_variant():
    specs = build_matrix(["colibri", "e5"])
    sel = select_matrix(specs, ["dense_colibri"], include_reranker=True)
    assert [s.config_id for s in sel] == ["dense_colibri", "dense_colibri_rerank"]


def test_select_excluding_reranker():
    specs = build_matrix(["colibri", "e5"])
    sel = select_matrix(specs, ["dense_colibri"], include_reranker=False)
    assert [s.config_id for s in sel] == ["dense_colibri"]


def test_select_all():
    specs = build_matrix(["colibri"])
    assert len(select_matrix(specs, None, True)) == len(specs)
    assert len(select_matrix(specs, ["all"], True)) == len(specs)
