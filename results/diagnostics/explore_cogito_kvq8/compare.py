"""EXPLORATORY comparison: Cogito-14B smoke episodes, frozen f16 KV (smoke_panel) vs q8_0 KV
(explore-cogito-kvq8-20261107). Offline, read-only. Labels come from the independent S25 checker
(results/diagnostics/s25_audit_check/independent_label_check.py), run against each run folder.
Writes comparison.json next to this file.
"""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import statistics
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
RUNS = {"f16 (smoke_panel)": ROOT / "results/runs/smoke_panel",
        "q8_0 (explore)": ROOT / "results/runs/explore-cogito-kvq8-20261107"}
QUERIES = ["BH2_01682", "BH2_03951", "BH2_04459", "BH2_04474"]


def load_checker(run, scratch):
    spec = importlib.util.spec_from_file_location("chk", ROOT / "results/diagnostics/s25_audit_check/independent_label_check.py")
    chk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chk)
    chk.RUN, chk.HERE, chk.WALK = run, scratch, scratch / "walk"
    return chk


def server_stats(run):
    logs = sorted((run / "runtime/Cogito-14B").glob("server-*.stderr.log"))
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in logs)
    evals = [(int(n), float(r)) for n, r in
             re.findall(r"\|\s+eval time =\s+[\d.]+ ms /\s+(\d+) tokens \(.*?([\d.]+) tokens per second\)", text)]
    return {"layers": sorted(set(re.findall(r"offloaded (\d+/\d+) layers to GPU", text))),
            "kv_lines": sorted(set(re.findall(r"llama_kv_cache: size =.*", text))),
            "eval_requests": len(evals),
            "eval_tok_s_median": round(statistics.median(r for _, r in evals), 2) if evals else None,
            "eval_tok_s_min": round(min(r for _, r in evals), 2) if evals else None,
            "eval_tok_s_long_replies(>=1000 tok)": [round(r, 2) for n, r in evals if n >= 1000]}


def main():
    scratch = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "_scratch"
    out = {}
    for name, run in RUNS.items():
        chk = load_checker(run, scratch / name.split()[0])
        (scratch / name.split()[0]).mkdir(parents=True, exist_ok=True)
        chk.main()
        checks = json.loads((scratch / name.split()[0] / "label_checks.json").read_text(encoding="utf-8"))
        labels = {e["episode"].split("__")[0]: Counter(f"{a['mine']['label_a']}/{a['mine']['label_b']}"
                                                       for a in e.get("answers", []))
                  for e in checks["episodes"] if "Cogito" in e["episode"]}
        episodes = {}
        for q in QUERIES:
            r = json.loads((run / f"{q}__Cogito-14B__a1.json").read_text(encoding="utf-8"))
            t = r["timestamps"]
            secs = (datetime.fromisoformat(t["finished_at"]) - datetime.fromisoformat(t["started_at"])).total_seconds()
            episodes[q] = {"status": r["status"], "cause": r["cause"], "seconds": round(secs, 1),
                           "tool_calls": len(r["call_log"]), "requests": len(r["token_counts"]["prompt"]),
                           "peak_prompt_tokens": max(r["token_counts"]["prompt"] or [0]),
                           "max_completion_tokens": max(r["token_counts"]["completion"] or [0]),
                           "labels": dict(labels.get(q, {}))}
        out[name] = {"server": server_stats(run), "episodes": episodes}
    (HERE / "comparison.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
