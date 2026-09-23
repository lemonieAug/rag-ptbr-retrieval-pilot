"""Incomplete or incompatible on-disk caches must never be reused."""
from types import SimpleNamespace

import numpy as np
import pytest

from rag_ptbr_pilot import cli
from rag_ptbr_pilot.adapters.specs import get_embedding_spec
from rag_ptbr_pilot.config import AppConfig
from rag_ptbr_pilot.errors import ConfigError
from rag_ptbr_pilot.indexing.dense import DenseIndex
from rag_ptbr_pilot.io_utils import load_json, save_json


@pytest.fixture
def dense_cache(tmp_path, monkeypatch):
    cfg = AppConfig(root=tmp_path)
    chunks = [SimpleNamespace(chunk_id="a"), SimpleNamespace(chunk_id="b")]
    spec = get_embedding_spec("e5")
    monkeypatch.setattr(cli, "_load_revisions", lambda _: {spec.checkpoint: "fixed-revision"})
    monkeypatch.setattr(cli, "load_chunks", lambda _: chunks)
    matrix = np.eye(2, 1024, dtype=np.float32)
    idx = DenseIndex("e5", spec.checkpoint, "fixed-revision", 1024,
                     [c.chunk_id for c in chunks], matrix,
                     cli.dense_fingerprint("corpus", "e5", spec.checkpoint, "fixed-revision", 1024),
                     cli._encoding_config(cfg, "e5"))
    directory = tmp_path / "artifacts/indexes/dense_e5"
    idx.save(directory)
    return cfg, directory


@pytest.mark.parametrize("mutation", ["missing_meta", "missing_matrix", "empty_matrix", "truncated_matrix", "short_matrix", "short_ids", "wrong_ids", "wrong_fingerprint", "wrong_revision", "wrong_encoding"])
def test_retrieval_loader_rejects_incomplete_or_incompatible_cache(dense_cache, mutation):
    cfg, directory = dense_cache
    meta_path = directory / "meta.json"
    meta = load_json(meta_path)
    if mutation == "missing_meta":
        meta_path.unlink()
    elif mutation == "missing_matrix":
        (directory / "matrix.npy").unlink()
    elif mutation == "empty_matrix":
        (directory / "matrix.npy").write_bytes(b"")
    elif mutation == "truncated_matrix":
        path = directory / "matrix.npy"
        path.write_bytes(path.read_bytes()[:100])
    elif mutation == "short_matrix":
        np.save(directory / "matrix.npy", np.eye(1, 1024, dtype=np.float32))
    else:
        if mutation == "short_ids":
            meta["chunk_ids"] = ["a"]
        elif mutation == "wrong_ids":
            meta["chunk_ids"] = ["b", "a"]
        elif mutation == "wrong_fingerprint":
            meta["fingerprint"] = "other-corpus"
        elif mutation == "wrong_revision":
            meta["revision"] = "other-revision"
        elif mutation == "wrong_encoding":
            meta["encoding_config"]["dtype"] = "fp16"
        save_json(meta_path, meta)
    with pytest.raises((ConfigError, RuntimeError, ValueError, OSError)):
        cli._load_dense_index(cfg, "e5", "corpus")


def test_compatible_cache_passes_real_retrieval_loader(dense_cache):
    cfg, _ = dense_cache
    idx = cli._load_dense_index(cfg, "e5", "corpus")
    assert idx.chunk_ids == ["a", "b"]
    assert idx.matrix.shape == (2, 1024)


@pytest.mark.parametrize("dtype", [np.int64, np.complex64, np.bool_])
def test_dense_loader_rejects_unsupported_matrix_dtype(dense_cache, dtype):
    _, directory = dense_cache
    np.save(directory / "matrix.npy", np.eye(2, 1024, dtype=dtype))
    with pytest.raises(ValueError, match="corrompido"):
        DenseIndex.load(directory)


@pytest.mark.parametrize("values", [[[np.inf, 0]], [[0., 0.]]])
def test_dense_loader_rejects_infinite_or_zero_vectors(tmp_path, values):
    index = DenseIndex("e5", "checkpoint", "revision", 2, ["a"], np.asarray(values))
    index.save(tmp_path)
    with pytest.raises(ValueError, match="corrompido"):
        DenseIndex.load(tmp_path)
