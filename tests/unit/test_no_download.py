"""Ausência de downloads/carregamento de modelos em importações e validações.

Garante que importar o pacote (e rodar ``validate``/métricas) NÃO importa
torch/transformers/sentence-transformers e NÃO inicia downloads.
"""

import sys


def test_import_does_not_load_heavy_libraries():
    import rag_ptbr_pilot
    import rag_ptbr_pilot.cli
    import rag_ptbr_pilot.config
    import rag_ptbr_pilot.metrics.ranking
    import rag_ptbr_pilot.benchmark.validation

    for mod in ("torch", "transformers", "sentence_transformers"):
        assert mod not in sys.modules, f"{mod} foi importado indevidamente no import"


def test_validate_benchmark_runs_without_models():
    from rag_ptbr_pilot.benchmark.validation import validate_benchmark
    from rag_ptbr_pilot.schemas import (
        ArticleMetadata,
        ChunkRecord,
        EvidenceGroup,
        QrelEntry,
        Question,
    )

    articles = [ArticleMetadata(doc_id="d1", title="T", pdf_filename="d1.pdf")]
    questions = [Question(
        question_id="q1", text="pergunta?", expected_answer="resposta",
        origin_doc_id="d1", review_status="approved",
    )]
    chunks = [ChunkRecord(chunk_id="c1", doc_id="d1", block_id="d1-b0000",
                          text="texto de evidência", token_count_ref=3)]
    qrels = [QrelEntry(question_id="q1", chunk_id="c1", relevance=1)]
    groups = [EvidenceGroup(group_id="g1", question_id="q1", chunk_ids=["c1"])]

    report = validate_benchmark(articles, questions, qrels, groups, chunks)
    assert report.valid is True
    for mod in ("torch", "transformers", "sentence_transformers"):
        assert mod not in sys.modules


def test_config_loading_without_models():
    from rag_ptbr_pilot.config import AppConfig

    cfg = AppConfig()  # defaults, sem tocar em arquivos nem modelos
    assert cfg.retrieval.top_n == 50
    assert cfg.metrics.primary == "ndcg@10"
    assert set(cfg.effective_embeddings()) == {
        "colibri", "qwen_embedding", "e5"}
    for mod in ("torch", "transformers", "sentence_transformers"):
        assert mod not in sys.modules
