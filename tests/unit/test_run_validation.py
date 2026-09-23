from types import SimpleNamespace

import pytest

from rag_ptbr_pilot.config import AppConfig, config_to_dict
from rag_ptbr_pilot.errors import ConfigError
from rag_ptbr_pilot.io_utils import save_json, save_jsonl
from rag_ptbr_pilot.manifest import hash_json, sha256_file
from rag_ptbr_pilot.retrieval.results import QueryRetrieval
from rag_ptbr_pilot.run_validation import benchmark_hashes, validate_run


@pytest.fixture
def run_fixture(tmp_path, monkeypatch):
    from rag_ptbr_pilot import run_validation
    cfg = AppConfig(root=tmp_path)
    cfg.experiments.select = ["bm25"]
    cfg.experiments.include_reranker = False
    for path in (cfg.paths.questions_path, cfg.paths.evidence_groups_path):
        target = cfg.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(run_validation, "load_frozen_corpus",
                        lambda _: ([], SimpleNamespace(corpus_version="fixed")))
    run_dir = tmp_path / "run-test"
    ranking = run_dir / "rankings/bm25.jsonl"
    row = QueryRetrieval("q1", "bm25", "bm25", None, False).to_dict()
    save_jsonl(ranking, [row])
    manifest = dict(run_id=run_dir.name, config_hash=hash_json(config_to_dict(cfg)),
                    corpus_version="fixed", qrels_hash=hash_json([]), prompts_hash="",
                    model_revisions={}, configurations=["bm25"], **benchmark_hashes(cfg),
                    ranking_hashes={ranking.name: sha256_file(ranking)})
    save_json(run_dir / "run_manifest.json", manifest)
    return cfg, run_dir, [SimpleNamespace(question_id="q1")], manifest, ranking


def test_matching_run_is_accepted(run_fixture):
    cfg, run_dir, questions, _, _ = run_fixture
    assert validate_run(cfg, run_dir, questions, [])["run_id"] == "run-test"


@pytest.mark.parametrize("field", ["config_hash", "corpus_version", "qrels_hash", "prompts_hash",
                                   "model_revisions", "questions_hash", "evidence_groups_hash"])
def test_incompatible_run_is_rejected(run_fixture, field):
    cfg, run_dir, questions, manifest, _ = run_fixture
    manifest[field] = "changed"
    save_json(run_dir / "run_manifest.json", manifest)
    with pytest.raises(ConfigError, match=field):
        validate_run(cfg, run_dir, questions, [])


def test_no_approved_questions_is_rejected(run_fixture):
    cfg, run_dir, _, _, _ = run_fixture
    with pytest.raises(ConfigError, match="Nenhuma pergunta aprovada"):
        validate_run(cfg, run_dir, [], [])


def test_missing_configuration_ranking_is_rejected(run_fixture):
    cfg, run_dir, questions, manifest, _ = run_fixture
    manifest["configurations"] = []
    save_json(run_dir / "run_manifest.json", manifest)
    with pytest.raises(ConfigError, match="Rankings incompletos"):
        validate_run(cfg, run_dir, questions, [])


def test_modified_ranking_is_rejected(run_fixture):
    cfg, run_dir, questions, _, ranking = run_fixture
    save_jsonl(ranking, [{"query_id": "q1", "config_id": "bm25"}])
    with pytest.raises(ConfigError, match="Ranking alterado"):
        validate_run(cfg, run_dir, questions, [])


def test_malformed_ranking_is_rejected_even_if_hash_matches(run_fixture):
    cfg, run_dir, questions, manifest, ranking = run_fixture
    save_jsonl(ranking, [{"query_id": "q1", "config_id": "bm25"}])
    manifest["ranking_hashes"][ranking.name] = sha256_file(ranking)
    save_json(run_dir / "run_manifest.json", manifest)
    with pytest.raises(ConfigError, match="Ranking inválido"):
        validate_run(cfg, run_dir, questions, [])
