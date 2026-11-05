"""S22 review (offline, read-only): independent re-derivation of Label A / Label B / H1 for selected answers.

Deliberately does NOT import cofail_kg.evaluation or cofail_kg.agents.trace: it rebuilds appearance and
trace edges from the raw call_log, node types from the raw S4 node table, and reference sets from the S7
parquet, then compares with the saved S22 metrics. Protocol §11, §13, §14.1, §14.3.
Writes results/diagnostics/s22_review/label_checks.json.
"""
from collections import deque
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results/runs/smoke_single_v135"
METRICS = ROOT / "results/diagnostics/smoke_single_v135"
OUT = Path(__file__).with_name("label_checks.json")

# (query, agent, which answer) chosen to cover every observed (Label A, Label B) pair and all four agents.
# "first" = first retained answer; an int = index into the saved metrics answer list.
SELECTION = [
    ("BH2_03762", "Ministral3-8B", 0),   # GOLD / SUPPORTED
    ("BH2_05686", "Gemma4-E4B", "ALT_VALID"),  # ALT_VALID / SUPPORTED
    ("BH2_03881", "Gemma4-E4B", "GOLD"),  # GOLD / PATH_INVALID
    ("BH2_03881", "Gemma4-E4B", "OFF_QUESTION"),  # OFF_QUESTION / PATH_INVALID, H1_MIXED agent
    ("BH2_05366", "Granite41-8B", 0),    # OFF_QUESTION / PATH_INVALID, H1_WRONG agent
    ("BH2_03762", "Granite41-8B", "OFF_QUESTION"),
    ("BH2_06427", "Granite41-8B", "OFF_QUESTION"),
    ("BH2_03760", "Qwen35-9B", 0),       # Qwen OFF_QUESTION / PATH_INVALID
    ("BH2_05843", "Qwen35-9B", "ALT_VALID"),
]


def pick(answers, which):
    if isinstance(which, int):
        return answers[which]
    return next(a for a in answers if a["label_a"] == which)


def main():
    refs = {q["query_id"]: q for q in pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()}
    mapping = json.loads((ROOT / "results/semantics/relation_mapping.json").read_text(encoding="utf-8"))["per_type"]
    nodes = pd.read_parquet(ROOT / "data/cache/primekg_nodes.parquet", columns=["node_index", "node_type", "node_name"])
    ntype = dict(zip(nodes["node_index"].astype(str), nodes["node_type"]))
    nname = dict(zip(nodes["node_index"].astype(str), nodes["node_name"]))
    rows = []
    for q, agent, which in SELECTION:
        ref = refs[q]
        r1, r2 = set(mapping[ref["relation_type"]]["R1"]), set(mapping[ref["relation_type"]]["R2"])
        s, tb, tt = ref["s"], ref["Type_B"], ref["Type_T"]
        record = json.loads((RUN / f"{q}__{agent}__a1.json").read_text(encoding="utf-8"))
        metric = json.loads((METRICS / agent / "metrics" / f"{q}.json").read_text(encoding="utf-8"))
        answer = pick(metric["answers"], which)
        x = answer["node_id"]
        submitted = json.loads(record["raw_final_output"].strip().removeprefix("```json").removesuffix("```"))
        submitted_item = submitted["answers"][answer["submitted_index"]]

        appeared, edges = set(), []
        for i, call in enumerate(record["call_log"]):
            if not call["success"]:
                continue
            if call["tool"] == "inspect_entity":
                appeared.add(str(call["result"]["id"]))
            elif call["tool"] == "get_neighbors":
                u = str(call["arguments"]["entity_id"])
                for item in call["result"]["items"]:
                    appeared.add(str(item["id"]))
                    edges.append((i, u, call["arguments"]["relation"], str(item["id"])))
        out = {}
        for _, u, r, v in edges:
            out.setdefault(u, []).append((r, v))

        # Label A (§13), directly from the S7 sets.
        if x in ref["A_star_q"]:
            label_a = "GOLD"
        elif x in ref["G_q"]:
            label_a = "GOLD_BRIDGE_EXTRA"
        elif x in ref["T_q"]:
            label_a = "ALT_VALID"
        else:
            label_a = "OFF_QUESTION"
        # Label B (§14.1).
        bridges = sorted({v for u, r, v in ((e[1], e[2], e[3]) for e in edges)
                          if u == s and r in r1 and v != s and ntype[v] == tb}, key=int)
        support = [(b, r) for b in bridges for r, v in out.get(b, []) if v == x and r in r2 and x != s and ntype[x] == tt]
        prev, dq = {s: None}, deque([s])  # BFS shortest path (edge count only) as evidence of reachability
        while dq:
            u = dq.popleft()
            for r, v in out.get(u, []):
                if v not in prev:
                    prev[v] = (u, r)
                    dq.append(v)
        if x not in appeared:
            label_b = "UNGROUNDED"
        elif support:
            label_b = "SUPPORTED"
        elif x in prev:
            label_b = "PATH_INVALID"
        else:
            label_b = "KG_UNSUPPORTED"
        shortest = []
        node = x
        while x in prev and prev[node] is not None:
            u, r = prev[node]
            shortest.insert(0, f"{u} -{r}-> {node}")
            node = u
        # H1 (§14.3): some R1/Type_B bridge b != x from s from which x is reachable avoiding s.
        h1 = 0
        if label_b in ("SUPPORTED", "PATH_INVALID") and x != s:
            for b in bridges:
                if b == x:
                    continue
                seen, stack = {b}, [b]
                while stack:
                    for _, v in out.get(stack.pop(), []):
                        if v != s and v not in seen:
                            seen.add(v)
                            stack.append(v)
                if x in seen:
                    h1 = 1
                    break
        rows.append({
            "query_id": q, "agent_id": agent, "relation_type": ref["relation_type"], "s": s,
            "R1": sorted(r1), "R2": sorted(r2), "Type_B": tb, "Type_T": tt,
            "submitted": submitted_item, "canonical_answer_id": x, "canonical_name": nname[x], "answer_type": ntype[x],
            "recorded": {"label_a": answer["label_a"], "label_b": answer["label_b"], "h1": answer["h1"],
                         "primary_path": answer["primary_path"], "primary_reason_codes": answer["primary_reason_codes"]},
            "independent": {"label_a": label_a, "label_b": label_b, "h1": h1},
            "evidence": {"in_A_star_q": x in ref["A_star_q"], "in_G_q": x in ref["G_q"], "in_T_q": x in ref["T_q"],
                         "appeared": x in appeared, "supporting_bridges": support[:3],
                         "shortest_trace_path": shortest},
            "agree": (label_a, label_b, h1) == (answer["label_a"], answer["label_b"], answer["h1"]),
        })
    OUT.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(row["query_id"], row["agent_id"], row["canonical_answer_id"], row["recorded"]["label_a"],
              row["recorded"]["label_b"], row["recorded"]["h1"], "->", row["independent"], "AGREE" if row["agree"] else "DISAGREE",
              row["evidence"]["shortest_trace_path"])


if __name__ == "__main__":
    main()
