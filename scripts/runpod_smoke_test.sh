#!/usr/bin/env bash
set -euo pipefail

repo_dir="${RAG_PTBR_PILOT_ROOT:-/workspace/rag-ptbr-retrieval-pilot}"
cd "$repo_dir"
export RAG_PTBR_PILOT_ROOT="$repo_dir"
export HF_HOME="${HF_HOME:-/workspace/hf-cache}"
export PATH="${UV_PROJECT_ENVIRONMENT:-/workspace/.venv-rag-ptbr}/bin:$PATH"
python - <<'PY'
import os
import shutil
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
import torch
from rag_ptbr_pilot.adapters import get_embedding_adapter, get_reranker_adapter
from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.runtime import collect_environment

workspace = Path('/workspace')
if not workspace.is_dir() or not os.access(workspace, os.W_OK):
    raise SystemExit('/workspace não está acessível para escrita')
disk = shutil.disk_usage(workspace)
print(f'Python: {sys.version.split()[0]}')
print(f'PyTorch: {torch.__version__}; CUDA build: {torch.version.cuda}')
print(f'CUDA disponível: {torch.cuda.is_available()}')
if not torch.cuda.is_available():
    raise SystemExit('GPU CUDA ausente')
props = torch.cuda.get_device_properties(0)
print(f'CUDA runtime: {collect_environment()["gpu"]["cuda_runtime_version"]}')
print(f'GPU: {props.name}; VRAM: {props.total_memory / 2**30:.1f} GiB')
print(f'transformers: {version("transformers")}; sentence-transformers: {version("sentence-transformers")}')
print(f'/workspace livre: {disk.free / 2**30:.1f} GiB; HF_HOME: {os.environ.get("HF_HOME")}')

cfg = load_config()
for name in cfg.effective_embeddings():
    adapter = get_embedding_adapter(name, cfg)
    try:
        adapter.load()
        if adapter._device != 'cuda':
            raise RuntimeError(f'{name} carregou em {adapter._device}')
        query = adapter.encode_queries(['Qual é a evidência?'])
        document = adapter.encode_documents(['Um exemplo breve de evidência científica.'])
        if query.shape != document.shape or query.shape[0] != 1 or not np.isfinite(query).all() or not np.isfinite(document).all():
            raise RuntimeError(f'{name}: embeddings inválidos')
        print(f'{name}: PASS ({query.shape[1]} dimensões)')
    finally:
        adapter.unload()

reranker = get_reranker_adapter(cfg)
try:
    reranker.load()
    if reranker._device != 'cuda':
        raise RuntimeError(f'reranker carregou em {reranker._device}')
    score = reranker.score('Qual é a evidência?', ['Um exemplo breve de evidência científica.'])
    if len(score) != 1 or not np.isfinite(score[0]):
        raise RuntimeError('score inválido')
    print('reranker: PASS')
finally:
    reranker.unload()
print('RUNPOD ENVIRONMENT: PASS')
PY
