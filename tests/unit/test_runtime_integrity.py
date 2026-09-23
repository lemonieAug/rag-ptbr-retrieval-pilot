from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from rag_ptbr_pilot.adapters.embeddings import HFTransformersEmbedding
from rag_ptbr_pilot.adapters.local import local_checkpoint
from rag_ptbr_pilot.adapters.specs import get_embedding_spec
from rag_ptbr_pilot.config import AppConfig
from rag_ptbr_pilot.errors import ConfigError, MissingArtifactError
from rag_ptbr_pilot.indexing.dense import DenseIndex
from rag_ptbr_pilot.io_utils import save_json


def test_checkpoint_is_pinned_local_path(tmp_path):
    snapshot = tmp_path / "models--org--model" / "snapshots" / "fixed"
    snapshot.mkdir(parents=True)
    save_json(tmp_path / "revisions.json", {"revisions": {"org/model": "fixed"}})
    assert local_checkpoint("org/model", tmp_path) == str(snapshot)
    with pytest.raises(MissingArtifactError):
        local_checkpoint("org/absent", tmp_path)


def test_hf_encoding_is_bounded_preserves_order(monkeypatch):
    adapter = HFTransformersEmbedding(get_embedding_spec("e5"))
    batches = []

    def encode(batch, template):
        batches.append(batch)
        return np.array([[int(t)] for t in batch], dtype=np.float32)

    monkeypatch.setattr(adapter, "_encode_batch", encode)
    result = adapter.encode_documents([str(i) for i in range(7)])
    assert [len(b) for b in batches] == [2, 2, 2, 1]
    assert result[:, 0].tolist() == list(range(7))


@pytest.mark.parametrize("matrix,ids,dimension", [
    (np.ones((1, 2)), ["a", "b"], 2),
    (np.array([[np.nan, 0]]), ["a"], 2),
    (np.array([[2., 0]]), ["a"], 2),
    (np.eye(2), ["a", "a"], 2),
])
def test_dense_load_rejects_corrupt_matrix(tmp_path, matrix, ids, dimension):
    DenseIndex("e5", "checkpoint", "revision", dimension, ids, matrix).save(tmp_path)
    with pytest.raises(ValueError, match="corrompido"):
        DenseIndex.load(tmp_path)


def test_legacy_encoding_only_accepts_original_dtype_and_template(monkeypatch):
    from rag_ptbr_pilot import cli
    from rag_ptbr_pilot.adapters import specs
    from rag_ptbr_pilot.manifest import hash_json

    cfg = AppConfig()
    assert hash_json(cli._encoding_config(cfg, "colibri")) == cli._LEGACY_ENCODING_HASHES["colibri"]
    cfg.models.dtype.colibri = "fp16"
    assert hash_json(cli._encoding_config(cfg, "colibri")) != cli._LEGACY_ENCODING_HASHES["colibri"]
    cfg.models.dtype.colibri = "fp32"
    monkeypatch.setitem(specs.EMBEDDING_SPECS, "colibri",
                        replace(specs.get_embedding_spec("colibri"), document_template="changed {text}"))
    assert hash_json(cli._encoding_config(cfg, "colibri")) != cli._LEGACY_ENCODING_HASHES["colibri"]


def test_index_reuses_valid_caches_without_loading_models(tmp_path, monkeypatch):
    from rag_ptbr_pilot import cli, adapters
    cfg = AppConfig(root=tmp_path)
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    monkeypatch.setattr(cli, "load_frozen_corpus", lambda _: ([], SimpleNamespace(corpus_version="fixed")))
    monkeypatch.setattr(cli, "_load_bm25", lambda *args: object())
    loaded = []
    monkeypatch.setattr(cli, "_load_dense_index", lambda cfg, name, version: loaded.append(name))
    monkeypatch.setattr(adapters, "get_embedding_adapter", lambda *args: pytest.fail("valid index loaded model"))
    cli.cmd_index(SimpleNamespace(config=None))
    assert loaded == cfg.effective_embeddings()


def test_removed_embedding_is_not_configurable():
    with pytest.raises(ValueError):
        AppConfig.model_validate({"models": {"embeddings": ["embeddinggemma"]}})
    with pytest.raises(ValueError):
        AppConfig.model_validate({"experiments": {"embeddings": ["embeddinggemma"]}})


def test_reranker_rejects_ignored_configuration():
    with pytest.raises(ValueError):
        AppConfig.model_validate({"models": {"reranker": {"checkpoint": "other"}}})


def test_bm25_rejects_modified_statistics_even_with_original_fingerprint(tmp_path):
    from rag_ptbr_pilot.cli import _load_bm25
    from rag_ptbr_pilot.indexing import BM25Index, LexicalNormalizer, bm25_fingerprint
    from rag_ptbr_pilot.schemas import ChunkRecord
    cfg = AppConfig(root=tmp_path)
    normalizer = LexicalNormalizer(cfg.retrieval.lexical)
    chunks = [ChunkRecord(chunk_id="c1", doc_id="d1", block_id="b1", text="evidence", token_count_ref=1)]
    index = BM25Index()
    index.build(chunks, normalizer)
    index.fingerprint = bm25_fingerprint("fixed", index.k1, index.b, cfg.retrieval.lexical.model_dump(mode="json"))
    path = tmp_path / "artifacts/indexes/bm25.json"
    save_json(path, index.to_dict())
    assert _load_bm25(cfg, chunks, normalizer, "fixed").n_docs == 1
    index.avgdl = 99
    save_json(path, index.to_dict())
    with pytest.raises(ConfigError, match="BM25 corrompido"):
        _load_bm25(cfg, chunks, normalizer, "fixed")


def test_corpus_tampering_is_detected(tmp_path):
    from rag_ptbr_pilot.chunking.chunker import build_corpus_manifest
    from rag_ptbr_pilot.chunking.token_validation import TokenValidationReport
    from rag_ptbr_pilot.persistence import load_frozen_corpus, save_chunks, save_manifest
    from rag_ptbr_pilot.schemas import ChunkRecord
    cfg = AppConfig(root=tmp_path)
    chunks = [ChunkRecord(chunk_id="c1", doc_id="d1", block_id="b1", text="original", token_count_ref=1)]
    manifest = build_corpus_manifest(chunks, {}, cfg.chunking, TokenValidationReport())
    save_manifest(cfg.resolve(cfg.paths.corpus_manifest_path), manifest)
    save_chunks(cfg.resolve(cfg.paths.chunks_path), chunks)
    assert load_frozen_corpus(cfg)[1].corpus_version == manifest.corpus_version
    chunks[0].text = "tampered"
    save_chunks(cfg.resolve(cfg.paths.chunks_path), chunks)
    with pytest.raises(ConfigError, match="Corpus congelado"):
        load_frozen_corpus(cfg)
