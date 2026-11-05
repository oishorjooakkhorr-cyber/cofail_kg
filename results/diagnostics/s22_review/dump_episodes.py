"""S22 review (offline, read-only): readable transcripts of selected smoke_single_v135 episodes.

Writes results/diagnostics/s22_review/episodes/<query>__<agent>.md with every message (content in full),
every tool call with arguments and the full returned result, the raw final output and the saved evaluated
answers. Nothing is truncated.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results/runs/smoke_single_v135"
METRICS = ROOT / "results/diagnostics/smoke_single_v135"
OUT = Path(__file__).with_name("episodes")
EPISODES = [("BH2_02033", "Ministral3-8B"), ("BH2_05843", "Gemma4-E4B"), ("BH2_03762", "Granite41-8B"),
            ("BH2_05366", "Qwen35-9B"), ("BH2_03879", "Qwen35-9B")]


def main():
    OUT.mkdir(exist_ok=True)
    for q, agent in EPISODES:
        record = json.loads((RUN / f"{q}__{agent}__a1.json").read_text(encoding="utf-8"))
        metric = json.loads((METRICS / agent / "metrics" / f"{q}.json").read_text(encoding="utf-8"))
        lines = [f"# {q} — {agent}", "", f"- status: {record['status']} (cause {record['cause']})",
                 f"- model: {record['model']['tag']} {record['model']['digest']}",
                 f"- num_ctx {record['num_ctx']}, num_predict {record['num_predict']}, temperature {record['temperature']}, seed {record['seed']}",
                 f"- prompt tokens per turn: {record['token_counts']['prompt']}",
                 f"- hop1_status {metric['hop1_status']}, tool calls {metric['tool_calls_used']}, budget exhausted {metric['budget_exhausted']}",
                 "", "## Messages", ""]
        for i, m in enumerate(record["messages"]):
            calls = [f"{c['function']['name']}({json.dumps(c['function']['arguments'], sort_keys=True)})"
                     for c in m.get("tool_calls") or []]
            lines += [f"### [{i}] {m['role']}" + (f" — calls {calls}" if calls else ""), "", "```text",
                      m.get("content") or "", "```", ""]
        lines += ["## Call log", ""]
        for i, c in enumerate(record["call_log"]):
            lines += [f"### call {i}: {c['tool']} {json.dumps(c['arguments'], sort_keys=True)} success={c['success']}",
                      "", "```json", json.dumps(c["result"], indent=1, sort_keys=True), "```", ""]
        lines += ["## Raw final output", "", "```text", str(record["raw_final_output"]), "```", "",
                  "## Evaluated answers (saved S22 metrics)", "",
                  "|#|node|label A|label B|h1|primary path|primary codes|", "|---|---|---|---|---|---|---|"]
        for a in metric["answers"]:
            path = " ; ".join(f"{e['u']}-{e['label']}->{e['v']}" for e in a["primary_path"] or [])
            lines.append(f"|{a['submitted_index']}|{a['node_id']}|{a['label_a']}|{a['label_b']}|{a['h1']}|{path}|"
                         f"{','.join(a['primary_reason_codes'])}|")
        (OUT / f"{q}__{agent}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(q, agent, record["status"], len(record["messages"]), "messages", len(record["call_log"]), "calls",
              len(metric["answers"]), "answers")


if __name__ == "__main__":
    main()
