"""RunPod preparation is pinned, configurable, and safe without a GPU."""

import json
import importlib.util
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from rag_ptbr_pilot.adapters import get_embedding_adapter, get_reranker_adapter
from rag_ptbr_pilot.adapters.base import resolve_device, resolve_dtype
from rag_ptbr_pilot.adapters.local import local_checkpoint
from rag_ptbr_pilot.config import AppConfig, load_config
from rag_ptbr_pilot.corpus_reference import (
    assert_canonical_sources, assert_official_corpus, load_reference, source_issues,
)
from rag_ptbr_pilot.errors import ConfigError, MissingArtifactError
from rag_ptbr_pilot.fetch import fetch_models
from rag_ptbr_pilot.io_utils import save_json
from rag_ptbr_pilot.model_revisions import pinned_revisions
from rag_ptbr_pilot.runtime import collect_environment, manifest_runtime_fields


def test_pins_match_specs_and_reject_wrong_revision(tmp_path):
    pins = pinned_revisions()
    assert len(pins) == 4
    assert all(len(sha) == 40 for sha in pins.values())
    checkpoint, expected = next(iter(pins.items()))
    cache = tmp_path / "models"
    snapshot = cache / ("models--" + checkpoint.replace("/", "--")) / "snapshots" / expected
    snapshot.mkdir(parents=True)
    save_json(cache / "revisions.json", {"revisions": {checkpoint: "0" * 40}})
    with pytest.raises(MissingArtifactError, match="incompatível"):
        local_checkpoint(checkpoint, cache)
    save_json(cache / "revisions.json", {"revisions": {checkpoint: expected}})
    assert local_checkpoint(checkpoint, cache) == str(snapshot)


def test_pin_file_rejects_checkpoint_change(tmp_path):
    path = tmp_path / "pins.yaml"
    content = Path("configs/model_revisions.yaml").read_text(encoding="utf-8")
    path.write_text(content.replace("Qwen/Qwen3-Embedding-4B", "other/model"), encoding="utf-8")
    with pytest.raises(ConfigError, match="Checkpoint pinado"):
        pinned_revisions(path)
    with pytest.raises(ValueError, match="revisões auditadas"):
        AppConfig.model_validate({"models": {"revisions_path": "other.yaml"}})


def test_prepare_models_passes_sha_and_verifies_snapshot(tmp_path, monkeypatch):
    revisions_file = tmp_path / "configs/model_revisions.yaml"
    revisions_file.parent.mkdir()
    shutil.copyfile("configs/model_revisions.yaml", revisions_file)
    cfg = AppConfig(root=tmp_path)
    calls = []

    def download(*, repo_id, revision, cache_dir):
        calls.append((repo_id, revision))
        snapshot = Path(cache_dir) / ("models--" + repo_id.replace("/", "--")) / "snapshots" / revision
        snapshot.mkdir(parents=True)
        for filename in ("config.json", "tokenizer.json", "model.safetensors"):
            (snapshot / filename).write_text("{}", encoding="utf-8")
        return str(snapshot)

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=download))
    result = fetch_models(cfg)
    assert calls == list(pinned_revisions(revisions_file).items())
    assert result == json.loads((tmp_path / "artifacts/models/revisions.json").read_text())["revisions"]


def test_prepare_models_rejects_wrong_snapshot(tmp_path, monkeypatch):
    revisions_file = tmp_path / "configs/model_revisions.yaml"
    revisions_file.parent.mkdir()
    shutil.copyfile("configs/model_revisions.yaml", revisions_file)
    cfg = AppConfig(root=tmp_path)

    def wrong_snapshot(*, repo_id, revision, cache_dir):
        path = Path(cache_dir) / ("models--" + repo_id.replace("/", "--")) / "snapshots" / "wrong"
        path.mkdir(parents=True)
        return str(path)

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=wrong_snapshot))
    with pytest.raises(ConfigError, match="Snapshot incompatível"):
        fetch_models(cfg)
    assert not (tmp_path / "artifacts/models/revisions.json").exists()


def test_batch_size_defaults_and_overrides(tmp_path):
    cfg = load_config()
    assert cfg.runtime.embedding_batch_size.model_dump() == {
        "colibri": 8, "qwen_embedding": 2, "e5": 2}
    assert cfg.runtime.reranker_batch_size == 8
    cfg.runtime.embedding_batch_size.e5 = 4
    cfg.runtime.reranker_batch_size = 3
    assert get_embedding_adapter("e5", cfg).batch_size == 4
    assert get_reranker_adapter(cfg).batch_size == 3
    with pytest.raises(ValueError):
        AppConfig.model_validate({"runtime": {"reranker_batch_size": 0}})
    assert AppConfig(root=tmp_path).resolve("artifacts/models") == tmp_path / "artifacts/models"


def test_cpu_fallback_and_safe_cuda_metadata(monkeypatch):
    fake_torch = SimpleNamespace(
        float16="fp16", float32="fp32", bfloat16="bf16",
        version=SimpleNamespace(cuda=None),
        cuda=SimpleNamespace(is_available=lambda: False, device_count=lambda: 0),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setenv("HF_TOKEN", "secret-value")
    monkeypatch.setenv("RUNPOD_API_KEY", "another-secret")
    assert resolve_device("auto") == "cpu"
    assert resolve_dtype("fp16", "cpu") == "fp32"
    env = collect_environment()
    assert env["gpu"]["cuda_available"] is False
    assert env["gpu"]["device_name"] is None
    assert "secret-value" not in json.dumps(env)
    assert "another-secret" not in json.dumps(env)


def test_manifest_runtime_metadata_is_allowlisted():
    cfg = AppConfig()
    env = {
        "gpu": {"device_name": "NVIDIA test", "total_vram_bytes": 24 * 2**30,
                "torch_cuda_version": "12.4", "cuda_runtime_version": "12.4"},
        "platform": "Linux", "hostname": "pod", "runpod": True,
        "hf_cache_path": "/workspace/hf-cache", "HF_TOKEN": "secret-value",
    }
    fields = manifest_runtime_fields(cfg, env, {"e5": "cuda"}, {"e5": "torch.float32"})
    assert fields["hardware"]["total_vram_bytes"] == 24 * 2**30
    assert fields["hardware"]["runtime_devices"]["e5"] == "cuda"
    assert fields["parameters"]["batch_sizes"]["reranker_batch_size"] == 8
    assert "secret-value" not in json.dumps(fields)


def test_gpu_metadata_collection_survives_missing_runtime_api(monkeypatch):
    fake_torch = SimpleNamespace(
        version=SimpleNamespace(cuda="12.4"),
        cuda=SimpleNamespace(
            is_available=lambda: True, device_count=lambda: 1,
            get_device_name=lambda _: "NVIDIA test",
            get_device_properties=lambda _: SimpleNamespace(total_memory=24 * 2**30),
            cudart=lambda: SimpleNamespace(cudaRuntimeGetVersion=lambda _: (_ for _ in ()).throw(OSError())),
        ),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    gpu = collect_environment()["gpu"]
    assert gpu["device_name"] == "NVIDIA test"
    assert gpu["total_vram_bytes"] == 24 * 2**30
    assert gpu["cuda_runtime_version"] is None


def test_missing_ignored_artifacts_are_reported_as_missing(tmp_path):
    spec = importlib.util.spec_from_file_location("check_artifacts", "scripts/check_artifacts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.inventory(AppConfig(root=tmp_path))
    assert rows["RAW PDFs"][0] == "MISSING"
    assert rows["EXTRACTED DATA"][0] == "MISSING"
    assert rows["FROZEN CORPUS"][0] == "MISSING"


def test_fresh_clone_lists_exact_missing_paths(tmp_path):
    reference_path = tmp_path / "configs/corpus_reference.yaml"
    reference_path.parent.mkdir()
    shutil.copyfile("configs/corpus_reference.yaml", reference_path)
    annotations = tmp_path / "data/annotations"
    annotations.mkdir(parents=True)
    for filename in ("questions.yaml", "qrels.yaml", "evidence_groups.yaml"):
        shutil.copyfile(Path("data/annotations") / filename, annotations / filename)
    spec = importlib.util.spec_from_file_location("check_artifacts", "scripts/check_artifacts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.inventory(AppConfig(root=tmp_path))
    assert "data/processed/chunks/chunks.jsonl" in rows["FROZEN CORPUS"][1]
    assert "data/processed/chunks/corpus_manifest.json" in rows["FROZEN CORPUS"][1]
    assert "art-001_ner_juridico_ptbr.pdf" in rows["RAW PDFs"][1]
    assert "data/processed/extracted/art-001.md" in rows["EXTRACTED DATA"][1]
    assert rows["BENCHMARK"][0] == "READY"
    assert "aguarda corpus" in rows["BENCHMARK"][1]
    original_argv = sys.argv
    try:
        sys.argv = ["check_artifacts.py", "--require-ready"]
        module.load_config = lambda: AppConfig(root=tmp_path)
        assert module.main() == 2
    finally:
        sys.argv = original_argv


def test_reference_matches_versioned_audit_and_blocks_wrong_corpus(tmp_path):
    reference_path = tmp_path / "configs/corpus_reference.yaml"
    reference_path.parent.mkdir()
    shutil.copyfile("configs/corpus_reference.yaml", reference_path)
    cfg = AppConfig(root=tmp_path)
    reference = load_reference(cfg)
    baseline = json.loads(Path("artifacts/review/technical_baseline.json").read_text(encoding="utf-8"))
    assert reference["corpus_version"] == baseline["corpus_version"]
    assert reference["chunks_sha256"] == baseline["hashes"]["data/processed/chunks/chunks.jsonl"]
    chunks = cfg.resolve(cfg.paths.chunks_path)
    chunks.parent.mkdir(parents=True)
    chunks.write_text("not audited", encoding="utf-8")
    with pytest.raises(ConfigError, match="corpus_version incompatível"):
        assert_official_corpus(cfg, SimpleNamespace(corpus_version="0" * 64))
    with pytest.raises(ConfigError, match="chunks.jsonl divergente"):
        assert_official_corpus(cfg, SimpleNamespace(corpus_version=reference["corpus_version"]))


def test_frozen_corpus_requires_both_transferred_files(tmp_path):
    from rag_ptbr_pilot.persistence import load_frozen_corpus
    cfg = AppConfig(root=tmp_path)
    with pytest.raises(ConfigError, match="Corpus auditado ausente") as exc:
        load_frozen_corpus(cfg)
    assert "chunks.jsonl" in str(exc.value)
    assert "corpus_manifest.json" in str(exc.value)


def test_reconstruction_requires_canonical_pdfs(tmp_path, monkeypatch):
    from rag_ptbr_pilot import cli
    reference_path = tmp_path / "configs/corpus_reference.yaml"
    reference_path.parent.mkdir()
    shutil.copyfile("configs/corpus_reference.yaml", reference_path)
    cfg = AppConfig(root=tmp_path)
    reference = load_reference(cfg)
    missing, wrong = source_issues(cfg, reference, "pdf")
    assert len(missing) == 5 and not wrong
    wrong_pdf = cfg.resolve("data/raw/articles/art-001_ner_juridico_ptbr.pdf")
    wrong_pdf.parent.mkdir(parents=True)
    wrong_pdf.write_bytes(b"not the audited PDF")
    missing, wrong = source_issues(cfg, reference, "pdf")
    assert len(missing) == 4 and wrong == ["data/raw/articles/art-001_ner_juridico_ptbr.pdf"]
    with pytest.raises(ConfigError, match="Fontes canônicas pdf"):
        assert_canonical_sources(cfg, include_markdown=False)

    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    monkeypatch.setattr(cli, "load_frozen_corpus", lambda _: (
        [], SimpleNamespace(corpus_version=reference["corpus_version"])))
    monkeypatch.setattr(cli, "_load_bm25", lambda *args: (_ for _ in ()).throw(ConfigError("ausente")))
    with pytest.raises(ConfigError, match="Fontes canônicas pdf"):
        cli.cmd_index(SimpleNamespace(config=None))
    assert not (tmp_path / "artifacts/indexes/bm25.json").exists()


def test_direct_retrieve_stops_before_models_on_wrong_version(tmp_path, monkeypatch):
    from rag_ptbr_pilot import cli
    reference_path = tmp_path / "configs/corpus_reference.yaml"
    reference_path.parent.mkdir()
    shutil.copyfile("configs/corpus_reference.yaml", reference_path)
    cfg = AppConfig(root=tmp_path)
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    monkeypatch.setattr(cli, "load_frozen_corpus", lambda _: (
        [], SimpleNamespace(corpus_version="0" * 64)))
    with pytest.raises(ConfigError, match="corpus_version incompatível"):
        cli.cmd_retrieve(SimpleNamespace(config=None))
    assert not (tmp_path / "results").exists()


def test_setup_and_smoke_do_not_run_official_retrieval():
    for filename in ("runpod_setup.sh", "runpod_smoke_test.sh", "rebuild_audited_corpus.sh"):
        script = Path("scripts", filename).read_text(encoding="utf-8")
        assert "rag-ptbr retrieve" not in script
        assert "rag-ptbr evaluate" not in script
    official = Path("scripts/run_official_experiment.sh").read_text(encoding="utf-8")
    assert 'rag-ptbr retrieve | tee "$retrieve_log"' in official
