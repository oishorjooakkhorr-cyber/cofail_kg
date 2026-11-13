"""S34 (DESCRIPTIVE) — intervention smoke test: tool-output differences versus the original run.

Usage (from the repository root, after scripts/25_run_panel.py run --manifest intervention_smoke
--run-id intervention_smoke):
    python scripts/47_s34_smoke_report.py --combined pilot_expansion_v1 --run-id intervention_smoke

Runbook S34: report tool-output differences versus the original run for the same queries. The researcher
checks by hand: only the intended structure changed; agents can still navigate; a valid route exists.
Decision log 2026-11-12 "Plan after D7", section A3: BH2_05290 × 4 agents, run ID `intervention_smoke`.

For every tool call of every smoke episode:
* replay: the call is re-executed on the PrimeKG index without and with the episode's saved overlay
  (KGEnvironment, budget never reached, the run's page size). The recorded result must equal the overlay
  replay exactly (the script stops otherwise); "changed by the overlay" = the two replays differ.
* versus the original run: if the original episode of the same (query, agent) made the same call (same tool
  and arguments), its recorded result is compared. Every difference must be one the overlay explains.
Also reported per episode: status, calls, answers, whether the agent reached the hidden node u from s
through an R1 label and what it got when it asked u for the hidden label; per query, the S33 valid-route
check (results/interventions/manifest.jsonl).

Engineering conventions (documented, not protocol): calls answered with the budget-exhausted message are
not replayed (they never reach the KG); arguments are compared as canonical JSON (sorted keys); outputs are
write-once. No interpretation is written.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.agents.kg_env import BUDGET_EXHAUSTED, KGEnvironment, Overlay, ToolConfig  # noqa: E402
from cofail_kg.agents.trace import load_episode_record  # noqa: E402
from cofail_kg.kg.primekg_index import PrimeKGIndex  # noqa: E402

NOTE = ("DESCRIPTIVE (D7 DESCRIPTIVE; decision log 2026-11-12 \"Plan after D7\", section A). Treatment-only "
        "smoke test; not used in any gate.")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_key(call: dict) -> str:
    return json.dumps({"tool": call["tool"], "arguments": call["arguments"]}, sort_keys=True)


def describe(call: dict, plain, surgery) -> str:
    """Short, complete description of how the overlay changed one call's output."""
    args = call["arguments"]
    if isinstance(plain, dict) and isinstance(surgery, dict) and call["tool"] == "inspect_entity":
        p = {r["label"]: r for r in plain["relations"]}
        s = {r["label"]: r for r in surgery["relations"]}
        parts = [f"label `{lab}` removed ({p[lab]['neighbor_count']} neighbours)" for lab in sorted(set(p) - set(s))]
        parts += [f"label `{lab}`: {p[lab]['neighbor_count']} → {s[lab]['neighbor_count']} neighbours"
                  for lab in sorted(set(p) & set(s)) if p[lab] != s[lab]]
        return f"inspect_entity({args.get('entity_id')}): " + "; ".join(parts)
    if call["tool"] == "get_neighbors":
        head = f"get_neighbors({args.get('entity_id')}, {args.get('relation')!r})"
        if isinstance(surgery, str):
            return f"{head}: {plain['total_count'] if isinstance(plain, dict) else plain!r} → {surgery!r}"
        removed = sorted({i["id"] for i in plain["items"]} - {i["id"] for i in surgery["items"]}, key=int)
        return f"{head}: total {plain['total_count']} → {surgery['total_count']}; removed {removed}"
    return f"{call['tool']}({args}): output changed"


def compare_episode(record: dict, original: dict, index, page_size: int, overlay: Overlay) -> dict:
    plain = KGEnvironment(index, ToolConfig(page_size=page_size, budget=10**9))
    surgery = KGEnvironment(index, ToolConfig(page_size=page_size, budget=10**9), overlay=overlay,
                            query_id=overlay.query_id)
    orig = {}
    for call in original["call_log"]:
        if call.get("result") != BUDGET_EXHAUSTED:
            orig.setdefault(call_key(call), call.get("result"))
    calls, changed, same_call, identical, differing, unexplained = 0, [], 0, 0, [], []
    for i, call in enumerate(record["call_log"]):
        if call.get("result") == BUDGET_EXHAUSTED:
            continue
        calls += 1
        r_plain = plain.call(call["tool"], call["arguments"])
        r_surgery = surgery.call(call["tool"], call["arguments"])
        if call.get("result") != r_surgery:
            raise ValueError(f"{record['query_id']}/{record['agent_id']} call {i}: recorded result differs from "
                             f"the overlay replay")
        by_overlay = r_plain != r_surgery
        if by_overlay:
            changed.append({"call_index": i, "description": describe(call, r_plain, r_surgery)})
        key = call_key(call)
        if key in orig:
            same_call += 1
            if orig[key] == call.get("result"):
                identical += 1
            else:
                differing.append(i)
                if not by_overlay:
                    unexplained.append(i)
    return {"calls": calls, "calls_changed_by_overlay": changed, "same_calls_as_original": same_call,
            "identical_to_original": identical, "different_from_original": differing,
            "different_and_not_explained_by_overlay": unexplained}


def navigation(record: dict, s: str, r1: list[str], u: str, r: str) -> dict:
    reached = any(c["tool"] == "get_neighbors" and c.get("success") and str(c["arguments"].get("entity_id")) == s
                  and c["arguments"].get("relation") in r1 and any(str(x["id"]) == u for x in c["result"]["items"])
                  for c in record["call_log"])
    asked = [c.get("result") if isinstance(c.get("result"), str) else "listed"
             for c in record["call_log"] if c["tool"] == "get_neighbors"
             and str(c["arguments"].get("entity_id")) == u and c["arguments"].get("relation") == r]
    return {"reached_u_from_s_via_R1": reached, "asked_u_for_hidden_label": asked}


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", default="results/interventions/smoke")
    args = ap.parse_args(argv)
    report = _load("s28_report", "28_pilot_report.py")
    b5 = _load("b5_concentration", "42_b5_concentration.py")
    original = report.load_combined(args.combined)
    run_dir = ROOT / "results/runs" / args.run_id
    s33 = {r["query_id"]: r for r in (json.loads(x) for x in (ROOT / "results/interventions/manifest.jsonl")
                                      .read_text(encoding="utf-8").splitlines() if x.strip())}
    index = PrimeKGIndex(ROOT / "data/cache")
    episodes, commits = [], set()
    for agent in original["agents"]:
        pinned = json.loads((run_dir / "configs" / f"{agent}.config.json").read_text(encoding="utf-8"))
        commits.add(pinned["config"]["git_commit"])
        for qid in pinned["query_ids"]:
            paths = sorted(run_dir.glob(f"{qid}__{agent}__a*.json"))
            record = load_episode_record(paths[-1])
            event = record["log_events"][0]
            if event.get("overlay_sha256") != pinned["config"]["overlay_sha256"] or event.get("overlay") is None:
                raise ValueError(f"{qid}/{agent}: the record does not carry the run's overlay")
            ov = Overlay(qid, tuple(map(tuple, event["overlay"]["hide_labels"])),
                         tuple(map(tuple, event["overlay"]["hide_edges"])))
            if ov.to_json() != s33[qid]["overlay"]:
                raise ValueError(f"{qid}: saved overlay differs from the S33 manifest")
            (u, r), = ov.hide_labels
            orig_record = original["records"][(agent, qid)]
            cmp = compare_episode(record, orig_record, index, pinned["config"]["page_size"], ov)
            episodes.append({"query_id": qid, "agent_id": agent, "attempt": record["attempt"],
                             "status": record["status"], "original_status": orig_record["status"],
                             "hidden": [u, r], **navigation(record, s33[qid]["s"], s33[qid]["R1"], u, r),
                             **cmp})
    queries = {q: {"valid_route_after": s33[q]["valid_route_after"],
                   "valid_bridges_after": s33[q]["valid_bridges_after"],
                   "only_intended_edges_hidden": s33[q]["only_intended_edges_hidden"],
                   "hidden_edge_count": s33[q]["hidden_edge_count"]}
               for q in sorted({e["query_id"] for e in episodes})}
    commit, clean = b5.git_state()
    payload = {"stage": "S34", "status": "DESCRIPTIVE", "note": NOTE, "run_id": args.run_id,
               "inference_commits": sorted(commits), "git_commit": commit, "git_tracked_clean": clean,
               "queries": queries, "episodes": episodes,
               "unexplained_differences": sum(len(e["different_and_not_explained_by_overlay"]) for e in episodes)}
    lines = [f"# S34 — Intervention smoke test `{args.run_id}` (DESCRIPTIVE)\n", f"{NOTE}\n",
             f"Produced by `scripts/47_s34_smoke_report.py` at commit `{commit}` (tracked files clean: {clean}); "
             f"inference commit(s): " + ", ".join(f"`{c}`" for c in sorted(commits)) + ".\n",
             f"**Differences from the original run not explained by the overlay: "
             f"{payload['unexplained_differences']}.** Every recorded tool output equals the replay with the "
             f"overlay (checked call by call).\n", "## Per query (S33 checks)\n",
             "| Query | Hidden edges | Only intended edges hidden | Valid route after | Valid bridges after |",
             "|---|---|---|---|---|"]
    for q, v in queries.items():
        lines.append(f"| {q} | {v['hidden_edge_count']} | {v['only_intended_edges_hidden']} | "
                     f"{v['valid_route_after']} | {', '.join(v['valid_bridges_after'])} |")
    lines += ["", "## Per episode\n", "| Query | Agent | Status (original → smoke) | Calls | Same calls as "
              "original: identical / different | Calls changed by overlay | Reached u via R1 | "
              "Asked u for hidden label → result |", "|---|---|---|---|---|---|---|---|"]
    for e in episodes:
        asked = "; ".join(e["asked_u_for_hidden_label"]) or "not asked"
        lines.append(f"| {e['query_id']} | {e['agent_id']} | {e['original_status']} → {e['status']} | {e['calls']} | "
                     f"{e['identical_to_original']} / {len(e['different_from_original'])} | "
                     f"{len(e['calls_changed_by_overlay'])} | {e['reached_u_from_s_via_R1']} | {asked} |")
    lines += ["", "## Every tool output the overlay changed\n"]
    for e in episodes:
        for c in e["calls_changed_by_overlay"]:
            lines.append(f"- {e['agent_id']}, call {c['call_index']}: {c['description']}")
    md = "\n".join(lines) + "\n"
    out = ROOT / args.out
    b5.write_once(out / "s34_smoke.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    b5.write_once(out / "s34_smoke_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
