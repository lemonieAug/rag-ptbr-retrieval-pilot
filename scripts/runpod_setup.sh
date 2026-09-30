#!/usr/bin/env bash
set -euo pipefail

repo_dir="${RAG_PTBR_PILOT_ROOT:-/workspace/rag-ptbr-retrieval-pilot}"
cd "$repo_dir"
export RAG_PTBR_PILOT_ROOT="$repo_dir"
export HF_HOME="${HF_HOME:-/workspace/hf-cache}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-/workspace/uv-cache}"
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-/workspace/uv-python}"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-/workspace/.venv-rag-ptbr}"
mkdir -p "$HF_HOME" "$UV_CACHE_DIR" "$UV_PYTHON_INSTALL_DIR"

if ! command -v uv >/dev/null; then
    python -m pip install 'uv==0.12.5'
fi
uv sync --frozen --python 3.11.16 --extra ingest --extra models --extra generate --extra dev
export PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"
python - <<'PY'
import torch
print(f"PyTorch {torch.__version__}; CUDA build {torch.version.cuda}; disponível {torch.cuda.is_available()}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA indisponível: confirme GPU NVIDIA, driver e Pod com GPU.")
PY

rag-ptbr prepare-models
rag-ptbr matrix
rag-ptbr status
python scripts/check_artifacts.py
if [[ -f data/processed/chunks/corpus_manifest.json && -f data/processed/chunks/chunks.jsonl ]]; then
    rag-ptbr validate
fi
echo 'RUNPOD SETUP: PASS (retrieve não executado)'
