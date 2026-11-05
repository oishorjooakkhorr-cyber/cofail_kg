"""S22 review (offline, read-only): match each Qwen prompt-count drop to the llama-server request log.

For every request, llama-server logs `new prompt ... task.n_tokens = N`, preceded (when the slot is reused) by
`selected slot by LCP similarity, f_sim_best = S, f_keep = K`. K is the share of the previous cached prompt
kept as a common prefix. When the history only grows, the previous prompt is a prefix of the new one,
so K is close to 1. If messages after the system prompt were removed, only that prefix is shared, so K is low.
Requests are matched to episode turns in log order, using n_tokens == prompt_eval_count.
Writes results/diagnostics/s22_review/prompt_drops_log.json.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results/runs/smoke_single_v135"
LOG = next((ROOT / "results/diagnostics/smoke_single_v135/Qwen35-9B").glob("server-run-*.stderr.log"))
DROPS = Path(__file__).with_name("prompt_drops.json")
OUT = Path(__file__).with_name("prompt_drops_log.json")


def main():
    requests, keep = [], None
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"selected slot by LCP similarity, f_sim_best = ([\d.]+).*f_keep = ([\d.]+)", line)
        if m:
            keep = (float(m.group(1)), float(m.group(2)))
        m = re.search(r"new prompt, n_ctx_slot = (\d+), n_keep = (\d+), task.n_tokens = (\d+)", line)
        if m:
            requests.append({"n_tokens": int(m.group(3)), "f_sim": keep and keep[0], "f_keep": keep and keep[1]})
            keep = None
    # Episode turns in run order (episodes ran in manifest order; timestamps order the turns).
    turns = []
    for path in RUN.glob("*__Qwen35-9B__a1.json"):
        r = json.loads(path.read_text(encoding="utf-8"))
        for e in r["log_events"]:
            if e["event"] == "CHAT_RESPONSE":
                turns.append((e["raw_response"]["created_at"], r["query_id"], e["message_index"],
                              e["raw_response"]["prompt_eval_count"]))
    turns.sort()
    # Greedy in-order match on token count; the synthetic probe requests are skipped automatically.
    matched, i = {}, 0
    for t in turns:
        while i < len(requests) and requests[i]["n_tokens"] != t[3]:
            i += 1
        if i == len(requests):
            raise ValueError(f"no log request matches turn {t}")
        matched[(t[1], t[2])] = requests[i]
        i += 1
    drops = [d for d in json.loads(DROPS.read_text(encoding="utf-8"))["drops"] if d["agent_id"] == "Qwen35-9B"]
    first = {}
    for _, q, k, _ in turns:
        first[q] = min(first.get(q, k), k)
    # Baseline: later turns of an episode that are not drops (a first turn follows another conversation).
    growth = [v["f_keep"] for k, v in matched.items() if v["f_keep"] is not None and k[1] != first[k[0]]
              and (k[0], k[1]) not in {(d["query_id"], d["to_message"]) for d in drops}]
    rows = [{**{k: d[k] for k in ("query_id", "from_message", "to_message", "prompt_before", "prompt_after")},
             **matched[(d["query_id"], d["to_message"])]} for d in drops]
    out = {"log": LOG.relative_to(ROOT).as_posix(), "turns_matched": len(matched), "drops": rows,
           "non_drop_f_keep_min": min(growth), "non_drop_f_keep_median": sorted(growth)[len(growth) // 2]}
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("turns matched", len(matched), "| non-drop f_keep min", out["non_drop_f_keep_min"],
          "median", out["non_drop_f_keep_median"])
    for r in rows:
        print(r["query_id"], f"msg {r['from_message']}->{r['to_message']}", r["prompt_before"], "->",
              r["prompt_after"], "f_keep", r["f_keep"], "f_sim", r["f_sim"])


if __name__ == "__main__":
    main()
