"""Monitor the owned index runner and finalize only after its complete event."""
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil

root = Path(__file__).resolve().parents[2]
out = root / "artifacts/review"
proc = psutil.Process(3164)
assert proc.cmdline()[-1] == "artifacts/review/phase2_index_run.py"
while True:
    events = [json.loads(line) for line in (out / "phase2_index_events.jsonl").read_text(encoding="utf8").splitlines()]
    index_end = next((i for i, e in enumerate(events) if e['event'] == 'index_done'), len(events))
    documents_done = {name: sum(e['size'] for e in events[:index_end]
                               if e['event'] == 'batch_done' and e.get('model') == name)
                      for name in ('qwen_embedding', 'e5')}
    queries_done = {name: sum(e['size'] for e in events[index_end:]
                             if e['event'] == 'batch_done' and e.get('model') == name)
                    for name in ('qwen_embedding', 'e5')}
    if events[-1]["event"] == "complete":
        with (out / "phase2_finalize_console.log").open("w", encoding="utf8") as log:
            finished = subprocess.run([sys.executable, "-X", "utf8", "artifacts/review/phase2_finalize.py"],
                                      cwd=root, stdout=log, stderr=subprocess.STDOUT)
        (out / "phase2_watch_result.json").write_text(json.dumps({
            "completed_at": datetime.datetime.now().isoformat(), "finalizer_returncode": finished.returncode}), encoding="utf8")
        (out / "phase2_progress.json").write_text(json.dumps({
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "complete" if finished.returncode == 0 else "verification_failed",
            "documents_done": documents_done, "queries_done": queries_done,
            "finalizer_returncode": finished.returncode,
            "last_event": events[-1]}, indent=2), encoding="utf8")
        raise SystemExit(finished.returncode)
    if not proc.is_running():
        raise SystemExit("Index process exited without a complete event; inspect console log")
    mem = proc.memory_info()
    sample = dict(timestamp=datetime.datetime.now().isoformat(), pid=proc.pid,
                  rss=mem.rss, private=mem.private, peak_rss=mem.peak_wset,
                  peak_private=mem.peak_pagefile, available_ram=psutil.virtual_memory().available,
                  cpu_seconds=sum(proc.cpu_times()[:2]), last_event=events[-1],
                  documents_done=documents_done, queries_done=queries_done)
    with (out / "phase2_resource_samples.jsonl").open("a", encoding="utf8") as log:
        log.write(json.dumps(sample) + "\n")
    (out / "phase2_progress.json").write_text(json.dumps(sample, indent=2), encoding="utf8")
    time.sleep(30)
