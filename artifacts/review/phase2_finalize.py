"""Verify the completed technical run and write evidence; never approve gold."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from rag_ptbr_pilot import cli
from rag_ptbr_pilot.config import load_config
from rag_ptbr_pilot.indexing import LexicalNormalizer
from rag_ptbr_pilot.indexing.dense import DenseIndex
from rag_ptbr_pilot.persistence import load_frozen_corpus
from rag_ptbr_pilot.status import collect_status

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/review"


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf8"))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def command(label, argv):
    started = dt.datetime.now().isoformat()
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, encoding="utf8", errors="replace")
    (OUT / f"phase2_{label}.txt").write_text(result.stdout + result.stderr, encoding="utf8")
    record = dict(command=argv, started=started, returncode=result.returncode,
                  output=f"phase2_{label}.txt")
    print(json.dumps(record), flush=True)
    assert result.returncode == 0, record
    return record


def main():
    events = [json.loads(line) for line in (OUT / "phase2_index_events.jsonl").read_text(encoding="utf8").splitlines()]
    assert events[-1]["event"] == "complete", "Indexing and technical smoke are not complete"
    assert not any(e["event"] == "network_attempt_blocked" for e in events)
    assert any(e["event"] == "reranker_smoke_pass" for e in events)
    cfg = load_config()
    chunks, manifest = load_frozen_corpus(cfg)
    assert len(chunks) == 224
    expected_ids = [c.chunk_id for c in chunks]
    baseline = read("technical_baseline.json")
    hashes = {}
    for relative, expected in baseline["hashes"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
        hashes[relative] = dict(before=expected, after=actual, unchanged=True)
    bm25 = cli._load_bm25(cfg, chunks, LexicalNormalizer(cfg.retrieval.lexical), manifest.corpus_version)
    rows = [dict(index="bm25", checkpoint=None, revision=None, dimension=None,
                 shape=[bm25.n_docs], fingerprint=bm25.fingerprint,
                 corpus_version=manifest.corpus_version, status="VALID", action="reused")]
    smokes = read("phase2_index_validation.json")
    assert {s["embedding"] for s in smokes} == set(cfg.effective_embeddings())
    for name in cfg.effective_embeddings():
        directory = ROOT / "artifacts/indexes" / f"dense_{name}"
        disk = DenseIndex.load(directory)
        index = cli._load_dense_index(cfg, name, manifest.corpus_version)
        assert disk.chunk_ids == index.chunk_ids == expected_ids
        assert len(set(index.chunk_ids)) == 224
        assert np.issubdtype(index.matrix.dtype, np.floating)
        assert np.isfinite(index.matrix).all()
        assert np.allclose(np.linalg.norm(index.matrix, axis=1), 1, atol=1e-3)
        smoke = next(s for s in smokes if s["embedding"] == name)
        assert smoke["status"] == "VALID" and smoke["fingerprint"] == index.fingerprint
        assert smoke["query_shape"] == [3, index.dimension]
        assert all(len(r) == 5 and all(cid in expected_ids and np.isfinite(score) for cid, score in r)
                   for r in smoke["rankings"])
        rows.append(dict(index=name, checkpoint=index.checkpoint, revision=index.revision,
                         dimension=index.dimension, shape=list(index.matrix.shape),
                         fingerprint=index.fingerprint, corpus_version=manifest.corpus_version,
                         matrix_dtype=str(index.matrix.dtype), encoding_config=index.encoding_config,
                         status="VALID", action="reused" if name == "colibri" else "recomputed"))
    resources = {}
    index_end = next(i for i, e in enumerate(events) if e["event"] == "index_done")
    for name in ("qwen_embedding", "e5"):
        model_events = [e for e in events[:index_end] if e.get("model") == name]
        loaded = next(e for e in model_events if e["event"] == "load_done")
        batches = [e for e in model_events if e["event"] == "batch_done"]
        assert sum(e["size"] for e in batches) == 224
        resources[name] = dict(
            started=model_events[0]["timestamp"], finished=model_events[-1]["timestamp"],
            elapsed_seconds=(dt.datetime.fromisoformat(model_events[-1]["timestamp"])
                             - dt.datetime.fromisoformat(model_events[0]["timestamp"])).total_seconds(),
            load_seconds=loaded["elapsed"], device=loaded["device"], dtype=loaded["dtype"],
            batches=len(batches), batch_sizes=sorted({e["size"] for e in batches}),
            sampled_peak_rss_bytes=max(e["rss"] for e in model_events),
            sampled_peak_private_bytes=max(e["private"] for e in model_events),
            sampled_min_available_ram_bytes=min(e["available_ram"] for e in model_events),
            unloaded=model_events[-1]["event"] == "unload_done")
        assert resources[name]["unloaded"]
    checks = [command("pytest_final", [sys.executable, "-m", "pytest", "-o", "cache_dir=artifacts/review/.pytest_cache"])]
    for name in ("validate", "matrix"):
        checks.append(command(name + "_final", ["rag-ptbr", name]))
    checks.append(command("gold_verify_final", [sys.executable, "artifacts/review/phase2_verify_gold.py"]))
    for label, args in (("review_q001t01_final", ["--question-id", "q-001-t01"]),
                        ("review_next_final", ["--next"]), ("review_summary_final", ["--summary"])):
        checks.append(command(label, ["rag-ptbr", "review-gold", *args]))
    status = collect_status(cfg)
    assert all(i["status"] == "valid" for i in status["indexes"].values())
    assert all(m["status"] == "available" for m in status["models"].values())
    assert status["experiment"]["configurations"] == 14
    assert status["experiment"]["reasons"] == ["HUMAN_GOLD_REVIEW_REQUIRED"]
    gold = status["benchmark"]
    assert gold["validation"]["valid"] and gold["validation"]["errors"] == []
    assert (gold["total"], gold["approved"], gold["draft_ready"], gold["draft_pending"]) == (125, 0, 119, 6)
    save("phase2_status_final.json", status)
    for label, args in (("git_status_final", ["status", "--short"]),
                        ("git_diff_stat_final", ["diff", "--stat"]),
                        ("git_diff_check_final", ["diff", "--check"])):
        checks.append(command(label, ["git", *args]))
    result = dict(completed_at=dt.datetime.now().isoformat(), corpus_version=manifest.corpus_version,
                  chunks=len(chunks), indexes=rows, resources=resources, hash_checks=hashes,
                  checks=checks, status=status, process_stop=read("phase2_process_stop.json"),
                  cpu_benchmark=read("phase2_cpu_threads_benchmark.json"),
                  gold_source_check=read("phase2_gold_source_check.json"),
                  index_seconds=events[index_end]["elapsed"], network_attempts=0,
                  official_retrieval_executed=False, human_approvals_performed=0)
    save("phase2_results.json", result)
    for filename in ("technical_audit.md", "technical_results.json"):
        archive = OUT / ("phase1_" + filename)
        if not archive.exists():
            archive.write_bytes((OUT / filename).read_bytes())
    save("technical_results.json", result)
    lines = ["# Auditoria técnica — Fase 2", "", f"Conferência final: {result['completed_at']}.", "",
             "Os quatro índices passaram pelos loaders atuais. Reranker local disponível e smoke de inferência concluído.",
             "Único bloqueio para o experimento oficial: `HUMAN_GOLD_REVIEW_REQUIRED`.", "",
             "## Processo antigo PID 12008", "",
             "Encontrado em execução desde 10:00:20, com código anterior às correções, memória privada de 30,54 GB e sem artefatos Qwen/E5.",
             "Às 11:48:14, `CloseMainWindow()` retornou falso (sem janela); foi necessário `Stop-Process -Id 12008 -Force`.",
             "Ausência do PID confirmada após encerramento. Detalhes em `phase2_process_stop.json`.", "",
             "## Indexação e integridade", "",
             "Executado o handler atual `cli.cmd_index(SimpleNamespace(config=None))`, com instrumentação local em `phase2_index_run.py`.",
             "BM25 e Colibri reutilizados, com hashes idênticos ao baseline. Qwen e E5 recalculados sequencialmente, com unload entre modelos.",
             "Verificados corpus, IDs/ordem/unicidade, shape, dimensão, checkpoint/revision, fingerprint, encoding, dtype, finitude e normalização.", "",
             "| Índice | Checkpoint | Revision | Dimensão | Shape | Fingerprint | Corpus version | Status |",
             "|---|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(k) or "—") for k in
            ("index", "checkpoint", "revision", "dimension", "shape", "fingerprint", "corpus_version", "status")) + " |")
    lines += ["", "## Recursos e duração", "",
              "Torch CPU; precisão e checkpoints preservados. As matrizes são persistidas em float32.",
              "Memórias abaixo são máximos amostrados nos eventos, não uma medição contínua de pico.", "",
              "| Modelo | Device | Dtype | Batch | Tempo total (s) | RSS máximo amostrado (GiB) | Privada máxima amostrada (GiB) |",
              "|---|---|---|---|---|---|---|"]
    for name, resource in resources.items():
        lines.append(f"| {name} | {resource['device']} | {resource['dtype']} | {resource['batch_sizes']} | {resource['elapsed_seconds']:.2f} | {resource['sampled_peak_rss_bytes']/2**30:.2f} | {resource['sampled_peak_private_bytes']/2**30:.2f} |")
    lines += ["", "O tempo de Qwen inclui uma pausa de cerca de três minutos para um microbenchmark sintético isolado de threads.",
              "O ensaio de 1/2 threads não mostrou ganho; os ensaios restantes foram cancelados e a indexação retomada com 12 threads, sem mudanças.",
              "Registro: `phase2_cpu_threads_benchmark.json`. GPU RTX 3050 de 4096 MiB disponível no sistema, porém CUDA indisponível nesta instalação de torch.", "",
              "## Smoke técnico", "",
              "Três textos de perguntas reais foram codificados por cada embedding, sem uso de respostas esperadas ou origem para recuperar.",
              "Cada busca retornou cinco chunks existentes com scores finitos; dimensões compatíveis. Reranker produziu dois scores finitos.",
              "Rede bloqueada pelo runner; zero tentativas registradas. Rankings somente técnicos em `phase2_index_validation.json`, sem avaliação de qualidade.", "",
              "## Testes e revisão", "", "```text",
              (OUT / "phase2_pytest_final.txt").read_text(encoding="utf8").strip(), "```", "",
              "`rag-ptbr validate`: zero erros estruturais. `rag-ptbr matrix`: 14 configurações. `git diff --check`: código 0.",
              "Cobertura inclui caches parciais/incompatíveis, reutilização sem inferência, Gemma rejeitado, confirmação humana e status com fingerprint incompatível.",
              "`review-gold --question-id`, `--next` e `--summary` conferidos em modo de leitura. Aprovação exige ID explícito, reviewer e confirmação; testes de escrita usam fixtures sintéticas.", "",
              "## Benchmark", "",
              f"125 perguntas draft, zero aprovadas; 119 prontas e seis pendentes. {gold['positive_qrels']} qrels positivos para {gold['questions_with_positive_qrels']} perguntas; {gold['evidence_with_quote_and_page']} evidências com quote/página, {gold['evidence_with_chunks']} com chunks; {gold['required_groups']} grupos obrigatórios, {gold['empty_required_groups']} vazios.",
              f"Avisos: `{gold['validation']['warning_counts']}`. Os seis casos completos estão em `phase2_gold_pending.md`; q-003-m03 preserva MANUAL_VISUAL_REVIEW_REQUIRED.",
              "Invariantes conferidos diretamente nos YAMLs por `phase2_verify_gold.py`/`audit_gold`, incluindo referências, duplicatas, origem de evidências e justificativa de grupos factuais.", "",
              "Também foram conferidas as 176 citações literais nas páginas indicadas do Markdown; as 125 respostas esperadas coincidem com HEAD. Registro: `phase2_gold_source_check.json`.", "",
              "## Próxima ação", "", "```powershell", "rag-ptbr review-gold --next", "```", "",
              "Após decisões humanas, conferir `rag-ptbr status` e `rag-ptbr validate`; então executar retrieve → evaluate → report.",
              "Nenhuma aprovação real, retrieval/avaliação oficial, commit ou push realizado. Corpus e índices reutilizados preservados; hashes em `phase2_results.json`.",
              "A auditoria anterior permanece em `phase1_technical_audit.md` e `phase1_technical_results.json` como registro histórico.", ""]
    (OUT / "technical_audit.md").write_text("\n".join(lines), encoding="utf8")
    print("PHASE2_FINAL_VERIFICATION_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
