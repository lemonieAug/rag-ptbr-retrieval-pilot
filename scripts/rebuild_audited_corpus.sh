#!/usr/bin/env bash
set -euo pipefail

repo_dir="${RAG_PTBR_PILOT_ROOT:-/workspace/rag-ptbr-retrieval-pilot}"
cd "$repo_dir"
export RAG_PTBR_PILOT_ROOT="$repo_dir"
export PATH="${UV_PROJECT_ENVIRONMENT:-/workspace/.venv-rag-ptbr}/bin:$PATH"

python scripts/check_artifacts.py --require-canonical-sources
if [[ -e data/processed/chunks/chunks.jsonl || -e data/processed/chunks/corpus_manifest.json ]]; then
    echo 'Corpus já presente; não sobrescrever arquivos congelados.' >&2
    exit 2
fi
rag-ptbr chunk
python scripts/check_artifacts.py --require-ready
echo 'CORPUS AUDITADO: PASS'
