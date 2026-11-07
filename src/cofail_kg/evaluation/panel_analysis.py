"""Evaluator-only checks for a panel run (S25): completeness, §19.1 audit selection, audit sheet.

Nothing agent-facing imports this module.

* `completeness`: the kill-and-resume test of §19.1 — the saved episodes equal manifest × agents,
  with no duplicate and none missing.
* `audit_selection`: §19.1 — per agent, among its SUCCESS episodes with at least one answer, ordered
  by SHA256("42" + query_id + agent_id), the first containing an OFF_QUESTION answer (if any) and the
  first not already chosen; an agent with fewer than 2 such episodes has all of them chosen.
* `audit_rows`: one row per retained answer of each chosen episode, for the researcher's manual audit.
"""

from __future__ import annotations

import hashlib
import re

AUDIT_COLUMNS = ("episode", "answer_id", "label_A", "label_B", "primary_path",
                 "my_label_A", "my_label_B", "notes")
_RECORD = re.compile(r"^(?P<query>[^_]+_\d+)__(?P<agent>.+)__a(?P<attempt>\d+)\.json$")


def completeness(plan: list[tuple[str, str]], filenames: list[str]) -> dict:
    """§19.1 kill-and-resume check: saved (agent, query) pairs vs. the manifest × agents plan."""
    seen: dict[tuple[str, str], list[str]] = {}
    for name in filenames:
        match = _RECORD.match(name)
        if not match:
            raise ValueError(f"Unexpected file in run directory: {name}")
        seen.setdefault((match["agent"], match["query"]), []).append(name)
    expected = set(plan)
    duplicates = sorted(k for k, v in seen.items() if len(v) > 1)
    missing = sorted(expected - set(seen))
    extra = sorted(set(seen) - expected)
    return {"expected": len(plan), "saved": sum(len(v) for v in seen.values()),
            "duplicates": [list(k) for k in duplicates], "missing": [list(k) for k in missing],
            "extra": [list(k) for k in extra],
            "pass": not duplicates and not missing and not extra and len(plan) == len(expected)}


def audit_key(query_id: str, agent_id: str) -> str:
    return hashlib.sha256(("42" + query_id + agent_id).encode("utf-8")).hexdigest()


def audit_selection(rows: list[dict], agent_order: list[str]) -> list[tuple[str, str]]:
    """§19.1 audit selection over S19 rows; returns (agent_id, query_id) in agent order."""
    chosen = []
    for agent in agent_order:
        eligible = sorted((r for r in rows if r["agent_id"] == agent and r["episode_status"] == "SUCCESS"
                           and len(r["answers"]) >= 1),
                          key=lambda r: audit_key(r["query_id"], agent))
        if len(eligible) < 2:
            chosen.extend((agent, r["query_id"]) for r in eligible)
            continue
        picks = []
        off = next((r for r in eligible if any(a["label_a"] == "OFF_QUESTION" for a in r["answers"])), None)
        if off is not None:
            picks.append(off["query_id"])
        # Two per agent (§19.1 "fewer than 2 ... all of them"; runbook/D4: 8 episodes for 4 agents):
        # without an OFF_QUESTION episode, the first two in hash order. Reading confirmed by the
        # researcher (decision log 2026-11-07, "S25 audit sheet filled ...").
        while len(picks) < 2:
            picks.append(next(r["query_id"] for r in eligible if r["query_id"] not in picks))
        chosen.extend((agent, q) for q in picks)
    return chosen


def render_path(path) -> str:
    if path is None:
        return ""
    if not path:
        return "(length 0: answer is s)"
    return " ; ".join(f"{e['u']} -{e['label']}-> {e['v']}" for e in path)


def submitted_ids(record: dict) -> list:
    """Answer IDs as the agent submitted them (FINAL_PARSED event), in submitted order."""
    parsed = [e for e in record.get("log_events", []) if e.get("event") == "FINAL_PARSED"]
    if len(parsed) != 1:
        raise ValueError(f"{record['query_id']}/{record['agent_id']}: expected one FINAL_PARSED event")
    return [a["id"] for a in parsed[0]["parsed"]["answers"]]


def audit_rows(selection: list[tuple[str, str]], rows: dict, records: dict) -> list[dict]:
    """One audit row per retained answer; `rows`/`records` are keyed by (agent_id, query_id)."""
    out = []
    for key in selection:
        row, record = rows[key], records[key]
        episode = f"{row['query_id']}__{row['agent_id']}__a{record['attempt']}"
        raw = submitted_ids(record)
        for answer in row["answers"]:
            answer_id = answer["node_id"]
            if answer_id is None:
                answer_id = f"unresolved:{raw[answer['submitted_index']]}"
            out.append({"episode": episode, "answer_id": answer_id, "label_A": answer["label_a"],
                        "label_B": answer["label_b"], "primary_path": render_path(answer["primary_path"]),
                        "my_label_A": "", "my_label_B": "", "notes": ""})
    return out
