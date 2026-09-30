#!/usr/bin/env bash
set -euo pipefail

repo_dir="${RAG_PTBR_PILOT_ROOT:-/workspace/rag-ptbr-retrieval-pilot}"
cd "$repo_dir"
export RAG_PTBR_PILOT_ROOT="$repo_dir"
export HF_HOME="${HF_HOME:-/workspace/hf-cache}"
export PATH="${UV_PROJECT_ENVIRONMENT:-/workspace/.venv-rag-ptbr}/bin:$PATH"

python scripts/check_artifacts.py --require-ready
rag-ptbr status
rag-ptbr validate
rag-ptbr index
reuse_log="$(mktemp)"
trap 'rm -f "$reuse_log"' EXIT
rag-ptbr index | tee "$reuse_log"
if [[ $(grep -c '^\[reuse\]' "$reuse_log") -ne 4 ]]; then
    echo 'Segunda indexação não reutilizou os quatro índices.' >&2
    exit 1
fi
rag-ptbr status
retrieve_log="$(mktemp)"
trap 'rm -f "$reuse_log" "$retrieve_log"' EXIT
rag-ptbr retrieve | tee "$retrieve_log"
run_id="$(sed -n 's/^Run ID: \(run-[A-Za-z0-9+_-]*\)$/\1/p' "$retrieve_log" | tail -n 1)"
if [[ -z "$run_id" || ! -f "results/$run_id/run_manifest.json" ]]; then
    echo 'RUN_ID não encontrado ou manifesto ausente.' >&2
    exit 1
fi
rag-ptbr evaluate --run-id "$run_id"
rag-ptbr report --run-id "$run_id"
echo "RESULTS: results/$run_id/"
