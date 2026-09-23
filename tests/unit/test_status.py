"""Local status must reject incomplete artifacts and never load models."""

import json
import subprocess
import sys
from types import SimpleNamespace

from rag_ptbr_pilot.config import AppConfig
from rag_ptbr_pilot.io_utils import save_json
from rag_ptbr_pilot.status import checkpoint_available, collect_status


def test_checkpoint_rejects_missing_declared_shard(tmp_path):
    save_json(tmp_path / "revisions.json", {"revisions": {"org/model": "rev"}})
    snapshot = tmp_path / "models--org--model" / "snapshots" / "rev"
    snapshot.mkdir(parents=True)
    for name in ("config.json", "tokenizer.json", "model-01.safetensors"):
        (snapshot / name).write_text("{}", encoding="utf8")
    save_json(snapshot / "model.safetensors.index.json",
              {"weight_map": {"a": "model-01.safetensors", "b": "model-02.safetensors"}})
    assert checkpoint_available("org/model", tmp_path)["status"] == "unavailable"
    (snapshot / "model-02.safetensors").write_text("{}", encoding="utf8")
    assert checkpoint_available("org/model", tmp_path)["status"] == "available"


def test_status_marks_missing_workspace_blocked(tmp_path):
    result = collect_status(AppConfig(root=tmp_path))
    assert not result["experiment"]["ready_for_retrieval"]
    assert "CORPUS_INVALID" in result["experiment"]["reasons"]
    assert "LOCAL_MODELS_UNAVAILABLE" in result["experiment"]["reasons"]
    assert result["experiment"]["configurations"] == 14


def test_status_reports_incompatible_fingerprints_without_crashing(tmp_path, monkeypatch):
    from rag_ptbr_pilot import cli, status
    from rag_ptbr_pilot.indexing.store import ensure_compatible

    monkeypatch.setattr(status, "load_frozen_corpus", lambda _: (
        [], SimpleNamespace(doc_ids=["doc"], frozen=True, corpus_version="current")))
    monkeypatch.setattr(status, "checkpoint_available", lambda *args: {"status": "available"})
    monkeypatch.setattr(status, "audit_gold", lambda _: {
        "validation": {"valid": True}, "draft_ready": 1, "draft_pending": 0, "approved": 0})

    def incompatible(*args):
        ensure_compatible("stale", "current", "test index")

    monkeypatch.setattr(cli, "_load_bm25", incompatible)
    monkeypatch.setattr(cli, "_load_dense_index", incompatible)
    result = collect_status(AppConfig(root=tmp_path))
    assert len(result["indexes"]) == 4
    assert all(index["status"] == "invalid" for index in result["indexes"].values())
    assert "INDEXES_UNAVAILABLE_OR_INVALID" in result["experiment"]["reasons"]
    assert not result["experiment"]["ready_for_retrieval"]


def test_status_and_summary_do_not_import_models(tmp_path):
    script = (
        "import json,sys; from pathlib import Path; "
        "from rag_ptbr_pilot.cli import build_parser; "
        "from rag_ptbr_pilot.config import AppConfig; "
        "from rag_ptbr_pilot.status import collect_status; "
        "build_parser(); collect_status(AppConfig(root=Path(sys.argv[1]))); "
        "print(json.dumps([m for m in ('torch','transformers','sentence_transformers','huggingface_hub') if m in sys.modules]))"
    )
    completed = subprocess.run([sys.executable, "-c", script, str(tmp_path)],
                               check=True, capture_output=True, text=True)
    assert json.loads(completed.stdout) == []
