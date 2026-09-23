"""Technical index execution and query smoke; never reads answers or origin IDs."""
import os
os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1", TOKENIZERS_PARALLELISM="false")
import datetime
import hashlib
import json
import pathlib
import socket
import time
from types import SimpleNamespace
import psutil
import numpy as np
import torch
from rag_ptbr_pilot import cli
from rag_ptbr_pilot.adapters import get_embedding_adapter, get_reranker_adapter
from rag_ptbr_pilot.adapters.embeddings import HFTransformersEmbedding, SentenceTransformerEmbedding
from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.persistence import load_frozen_corpus

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOG = ROOT / "artifacts/review/phase2_index_events.jsonl"
def event(kind, **fields):
    proc = psutil.Process()
    row = dict(timestamp=datetime.datetime.now().isoformat(), event=kind, pid=proc.pid,
               rss=proc.memory_info().rss, private=proc.memory_info().private,
               available_ram=psutil.virtual_memory().available,
               cpu_seconds=sum(proc.cpu_times()[:2]), **fields)
    with LOG.open("a", encoding="utf-8") as out:
        out.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False), flush=True)

def deny_network(*args, **kwargs):
    event("network_attempt_blocked", destination=str(args[1:] if len(args)>1 else args))
    raise RuntimeError("Network forbidden during local indexing/smoke")
socket.socket.connect = deny_network
socket.socket.connect_ex = deny_network
socket.create_connection = deny_network
torch.set_num_threads(psutil.cpu_count(logical=False))
event("start", torch=torch.__version__, threads=torch.get_num_threads(), cuda_available=torch.cuda.is_available())
cfg = load_config(None)
chunks, manifest = load_frozen_corpus(cfg)
preserve_paths = [ROOT / "artifacts/indexes/bm25.json", *sorted((ROOT / "artifacts/indexes/dense_colibri").glob("*"))]
baseline = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in preserve_paths if p.is_file()}
(ROOT / "artifacts/review/phase2_preserved_index_hashes.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")

for cls in (HFTransformersEmbedding, SentenceTransformerEmbedding):
    original_load, original_unload = cls.load, cls.unload
    def load(self, original=original_load):
        event("load_start", model=self.name)
        started = time.perf_counter()
        original(self)
        event("load_done", model=self.name, elapsed=time.perf_counter()-started,
              device=str(self._device), dtype=str(self._dtype), dimension=self.dimension)
    def unload(self, original=original_unload):
        original(self)
        event("unload_done", model=self.name)
    cls.load, cls.unload = load, unload
original_batch = HFTransformersEmbedding._encode_batch
def batch(self, texts, template):
    started = time.perf_counter()
    event("batch_start", model=self.name, size=len(texts))
    result = original_batch(self, texts, template)
    event("batch_done", model=self.name, size=len(texts), elapsed=time.perf_counter()-started)
    return result
HFTransformersEmbedding._encode_batch = batch
started = time.perf_counter()
cli.cmd_index(SimpleNamespace(config=None))
event("index_done", elapsed=time.perf_counter()-started)
for p in preserve_paths:
    if p.is_file():
        assert hashlib.sha256(p.read_bytes()).hexdigest() == baseline[str(p.relative_to(ROOT))]
event("existing_index_hashes_preserved")

texts = [q.text for q in cli.load_questions(cfg.resolve(cfg.paths.questions_path))[:3]]
smokes = []
for name in cfg.effective_embeddings():
    idx = cli._load_dense_index(cfg, name, manifest.corpus_version)
    adapter = get_embedding_adapter(name, cfg)
    try:
        adapter.load()
        vectors = adapter.encode_queries(texts)
        assert vectors.shape == (len(texts), idx.dimension)
        assert np.isfinite(vectors).all()
        rankings = []
        for vector in vectors:
            ranking = idx.search(vector, 5)
            assert len(ranking) == 5 and all(cid in idx.chunk_ids and np.isfinite(score) for cid, score in ranking)
            rankings.append(ranking)
        smokes.append(dict(embedding=name, shape=list(idx.matrix.shape), dimension=idx.dimension,
                           checkpoint=idx.checkpoint, revision=idx.revision, fingerprint=idx.fingerprint,
                           corpus_version=manifest.corpus_version, matrix_dtype=str(idx.matrix.dtype),
                           queries=texts, query_shape=list(vectors.shape), rankings=rankings, status="VALID"))
        event("query_smoke_pass", model=name)
    finally:
        adapter.unload()
    (ROOT / "artifacts/review/phase2_index_validation.json").write_text(json.dumps(smokes, indent=2, ensure_ascii=False), encoding="utf-8")
reranker = get_reranker_adapter(cfg)
try:
    event("reranker_load_start")
    reranker.load()
    scores = reranker.score(texts[0], [c.text for c in chunks[:2]])
    assert len(scores) == 2 and np.isfinite(scores).all()
    event("reranker_smoke_pass", scores=scores)
finally:
    reranker.unload()
event("complete")
