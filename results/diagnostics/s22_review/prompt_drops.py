"""S22 review (offline, read-only): per-turn prompt accounting for every smoke_single_v135 episode.

The message history only grows, so prompt_eval_count should rise from turn to turn. This script records
every decrease. For each turn it also gives: the cached-token count Ollama reports, done_reason, and an
upper-bound estimate of the next turn's prompt (previous prompt + previous output + new message
tokens). The new message tokens are estimated from the characters added, at that episode's own
tokens-per-character ratio measured on turns without a decrease. If the estimate is above num_ctx,
the runtime could not have fit the full history, which is expected input trimming.
Writes results/diagnostics/s22_review/prompt_drops.json.
"""
import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results/runs/smoke_single_v135"
OUT = Path(__file__).with_name("prompt_drops.json")


def chars(message):
    calls = json.dumps(message.get("tool_calls") or [], sort_keys=True)
    return len(message.get("content") or "") + (len(calls) if message.get("tool_calls") else 0)


def main():
    rows, drops = [], []
    for path in sorted(RUN.glob("*__a1.json")):
        r = json.loads(path.read_text(encoding="utf-8"))
        turns = [e for e in r["log_events"] if e["event"] == "CHAT_RESPONSE"]
        msgs = r["messages"]
        info = []
        for e in turns:
            raw = e["raw_response"]
            k = e["message_index"]  # index of the assistant message this response produced
            info.append({"message_index": k, "prompt": raw["prompt_eval_count"], "output": raw["eval_count"],
                         "cached": raw.get("prompt_eval_cached_count"), "done_reason": raw.get("done_reason"),
                         "history_chars": sum(chars(m) for m in msgs[:k])})
        ratios = [(b["prompt"] - a["prompt"] - a["output"]) / (b["history_chars"] - a["history_chars"] - 0)
                  for a, b in zip(info, info[1:])
                  if b["prompt"] >= a["prompt"] and b["history_chars"] > a["history_chars"]]
        ratio = median(ratios) if ratios else None
        n = 0
        for a, b in zip(info, info[1:]):
            if b["prompt"] < a["prompt"]:
                n += 1
                added = b["history_chars"] - a["history_chars"]
                estimate = a["prompt"] + a["output"] + (added * ratio if ratio else 0)
                drops.append({"agent_id": r["agent_id"], "query_id": r["query_id"], "status": r["status"],
                              "num_ctx": r["num_ctx"], "from_message": a["message_index"],
                              "to_message": b["message_index"], "prompt_before": a["prompt"],
                              "output_before": a["output"], "done_reason_before": a["done_reason"],
                              "prompt_after": b["prompt"], "cached_after": b["cached"],
                              "chars_added": added, "tokens_per_char": ratio,
                              "estimated_full_prompt": round(estimate),
                              "estimate_exceeds_num_ctx": estimate > r["num_ctx"]})
        rows.append({"agent_id": r["agent_id"], "query_id": r["query_id"], "drops": n,
                     "max_prompt": max(i["prompt"] for i in info),
                     "cached_nonzero_turns": sum(bool(i["cached"]) for i in info)})
    by_agent = {}
    for row in rows:
        s = by_agent.setdefault(row["agent_id"], {"episodes_with_drops": 0, "drops": 0, "cached_nonzero_turns": 0})
        s["episodes_with_drops"] += row["drops"] > 0
        s["drops"] += row["drops"]
        s["cached_nonzero_turns"] += row["cached_nonzero_turns"]
    out = {"by_agent": by_agent, "drops": drops}
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(by_agent, indent=1, sort_keys=True))
    for d in drops:
        print(d["agent_id"], d["query_id"], f"msg {d['from_message']}->{d['to_message']}",
              f"{d['prompt_before']}+{d['output_before']}({d['done_reason_before']}) -> {d['prompt_after']}",
              f"cached {d['cached_after']}", f"est {d['estimated_full_prompt']}", d["estimate_exceeds_num_ctx"])


if __name__ == "__main__":
    main()
