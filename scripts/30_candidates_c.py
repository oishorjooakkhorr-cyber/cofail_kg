"""S30 Gate D7 quantity C: candidate queries meeting the protocol §21 candidate rule with a matched control.

Usage (from the repository root, after scripts/30_combined_analysis.py):
    python scripts/30_candidates_c.py --combined pilot_expansion_v1

decision_rules.md D7: `C` = number of candidate **queries** meeting the §21 candidate rule (frozen at S29)
with a matched control. The outcome of D7 is not derived here.

Protocol §21 as read by the researcher (four answers on 2026-11-10, two follow-ups on 2026-11-11; logged
in docs/decision_log.md):
1. Control location: same query, same mechanism, another node at the same hop position, not used by any
   agent. For a hop-2 feature at u ≠ s, the hop-1 nodes are the neighbours of s through an R1 label
   (follow-up A). For a feature at s (step 1: SHORTCUT, WRONG_TURN_HOP1) s is the only node at that
   position, so the control is another label at s.
2. "Used by an agent" = opened by a tool call: some agent of the original run called get_neighbors on
   that node with that label (any page, any neighbor_type, whether or not the call succeeded).
3. Degree match: branch degree of (u, r) (number of unique neighbours of u through r), within ±25% of the
   treatment's, else the nearest. So a matched control exists whenever any eligible control exists.
4. Surgery: hide label r at node u (every edge incident to u with label r, either direction, the frozen
   S4 edge convention).
5. "Same label where possible" for a hop-2 feature: same label only (follow-up B). If no eligible hop-1
   node carries the treatment label, there is no matched control (treatment-only exploratory).

Candidate rule (§21): a CONSISTENT query with CF3^{Q,H1} = 1 or a PCF event shared by ≥ 3 agents (§16.3),
whose shared feature can be blocked while at least one valid route remains (valid route: s –r1→ b –r2→ t,
r1 ∈ R1, b ∈ B_q, r2 ∈ R2, t ∈ T_q). Feature = the (u, r) event shared by the most agents (ties: the
earliest step on the holders' primary paths, then the smaller numeric node ID, then label).

Engineering conventions (documented, not protocol):
* For a feature at s, the other labels considered are r' ∉ R1 (a step-1 wrong turn); for SHORTCUT, r'
  must also reach a node of Type_T from s (a one-step path to a Type_T answer).
* A CF3^{Q,H1} = 1 query with no PCF event shared by ≥ 3 agents has no (u, r) feature to block; it is
  listed with reason NO_SHARED_FEATURE and does not count in C (no such query occurs if the list says so).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 0.25  # §21 "within ±25%"


def load_script(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------------------------ graph helpers

class Graph:
    """Cached neighbour lookups on a PrimeKGIndex-like object (neighbors(node, label), relations_of(node))."""

    def __init__(self, kg):
        self.kg = kg
        self._nb: dict[tuple[str, str], frozenset[str]] = {}
        self._rel: dict[str, list[dict]] = {}

    def neighbors(self, node: str, label: str) -> frozenset[str]:
        key = (str(node), label)
        if key not in self._nb:
            self._nb[key] = frozenset(n["id"] for n in self.kg.neighbors(str(node), label))
        return self._nb[key]

    def labels(self, node: str) -> list[str]:
        if node not in self._rel:
            self._rel[node] = self.kg.relations_of(str(node))
        return [r["label"] for r in self._rel[node]]

    def node_type(self, node: str) -> str:
        return self.kg.get_node(str(node))["type"]

    def branch_degree(self, node: str, label: str) -> int:
        """§21: number of unique neighbours of `node` through `label`."""
        return len(self.neighbors(node, label))


def hidden(edge_u: str, edge_v: str, label: str, block: tuple[str, str] | None) -> bool:
    """True if the edge (edge_u, label, edge_v) is removed by hiding label block[1] at node block[0]."""
    return block is not None and label == block[1] and block[0] in (edge_u, edge_v)


def valid_route_remains(g: Graph, ref: dict, r1: list[str], r2: list[str], block) -> bool:
    """§21 valid route s –r1→ b –r2→ t with b ∈ B_q, t ∈ T_q, in the graph with `block` hidden."""
    s, targets = ref["s"], set(ref["T_q"])
    for b in sorted(ref["B_q"], key=int):
        if not any(b in g.neighbors(s, l1) and not hidden(s, b, l1, block) for l1 in r1):
            continue
        for l2 in r2:
            reach = {t for t in g.neighbors(b, l2) & targets if not hidden(b, t, l2, block)}
            if reach:
                return True
    return False


# ------------------------------------------------------------------------------ records: what was used

def opened(records: list[dict]) -> tuple[set[tuple[str, str]], set[str]]:
    """(node, label) pairs any agent opened with get_neighbors, and nodes any tool call touched."""
    pairs, nodes = set(), set()
    for rec in records:
        for call in rec["call_log"]:
            args = call.get("arguments") or {}
            if "entity_id" not in args:
                continue
            node = str(args["entity_id"]).strip()
            nodes.add(node)
            if call.get("tool") == "get_neighbors" and args.get("relation") is not None:
                pairs.add((node, str(args["relation"])))
    return pairs, nodes


# ------------------------------------------------------------------------------------ feature choice

MECHANISM_BY_STEP = {1: "WRONG_TURN_HOP1", 2: "WRONG_TURN_HOP2"}


def _steps(case: dict) -> list[tuple[int, int, str]]:
    """(step index, path length, mechanism) of the case's (node, label) on each holder's primary path."""
    out = []
    for answers in case["per_agent"].values():
        for ans in answers:
            path = ans["primary_path"] or []
            for i, e in enumerate(path):
                if e["u"] == case["node_id"] and e["label"] == case["relation"]:
                    out.append((i, len(path), "SHORTCUT" if len(path) == 1
                                else MECHANISM_BY_STEP.get(i + 1, f"STEP_{i + 1}")))
    return out


def choose_feature(q: dict) -> dict | None:
    """§21: the (u, r) event shared by the most agents; ties: earliest on primary paths."""
    events = {}
    for c in q["pcf_rel_cases"] + q["pcf_shortcut_cases"]:
        if c["agent_count"] < 3:
            continue
        steps = _steps(c)
        mechs = sorted({m for _, _, m in steps})
        if len(mechs) != 1:
            raise ValueError(f"{q['query_id']}: event ({c['node_id']}, {c['relation']}) has mechanisms {mechs}")
        key = (c["node_id"], c["relation"])
        old = events.get(key)
        if old is None or c["agent_count"] > old["agent_count"]:
            events[key] = {"u": c["node_id"], "r": c["relation"], "agent_count": c["agent_count"],
                           "agents": sorted(c["agents"]), "mechanism": mechs[0],
                           "earliest_step": min(i for i, _, _ in steps) + 1}
    if not events:
        return None
    return sorted(events.values(), key=lambda e: (-e["agent_count"], e["earliest_step"], int(e["u"]), e["r"]))[0]


# ----------------------------------------------------------------------------------- matched controls

def control_slots(g: Graph, ref: dict, feature: dict, r1: list[str]) -> list[tuple[str, str]]:
    """Every (u', r') at the feature's hop position with the same mechanism (researcher's §21 reading)."""
    s, u, r = ref["s"], feature["u"], feature["r"]
    if u == s:  # SHORTCUT or WRONG_TURN_HOP1: s is the only node at step 1 -> other labels at s
        others = [l for l in g.labels(s) if l != r and l not in r1]
        if feature["mechanism"] == "SHORTCUT":
            others = [l for l in others if any(g.node_type(n) == ref["Type_T"] for n in g.neighbors(s, l))]
        return [(s, l) for l in sorted(others)]
    hop1 = set().union(*(g.neighbors(s, l) for l in r1)) - {s, u}   # follow-up A: through an R1 label
    return [(n, r) for n in sorted(hop1, key=int) if r in g.labels(n)]  # follow-up B: same label only


def matched_controls(g: Graph, ref: dict, feature: dict, r1, r2, used_pairs) -> dict:
    bd = g.branch_degree(feature["u"], feature["r"])
    slots = control_slots(g, ref, feature, r1)
    eligible, opened_slots = [], 0
    for node, label in slots:
        if (node, label) in used_pairs:
            opened_slots += 1
            continue
        if not valid_route_remains(g, ref, r1, r2, (node, label)):
            continue
        cbd = g.branch_degree(node, label)
        eligible.append({"node": node, "label": label, "branch_degree": cbd, "abs_diff": abs(cbd - bd),
                         "within_25pct": abs(cbd - bd) <= TOLERANCE * bd})
    eligible.sort(key=lambda c: (c["abs_diff"], int(c["node"]), c["label"]))
    return {"treatment_branch_degree": bd, "slots": len(slots), "slots_opened_by_an_agent": opened_slots,
            "eligible": len(eligible), "within_25pct": sum(c["within_25pct"] for c in eligible),
            "closest": eligible[:3]}


def evaluate(q: dict, ref: dict, status: str, records: list[dict], g: Graph) -> dict:
    out = {"query_id": q["query_id"], "relation_type": q["relation_type"], "ambiguity_tag": q["ambiguity_tag"],
           "status": status, "cf3_h1": int(q["hop1_clean"]["cf3"])}
    if status != "CONSISTENT":
        return {**out, "candidate": False, "reason": "NOT_CONSISTENT"}
    feature = choose_feature(q)
    if feature is None:
        return {**out, "candidate": False, "reason": "NO_SHARED_FEATURE"}
    r1, r2 = q["R1"], q["R2"]
    out["feature"] = feature
    if not valid_route_remains(g, ref, r1, r2, None):
        raise ValueError(f"{q['query_id']}: no valid route even in the unmodified graph")
    if not valid_route_remains(g, ref, r1, r2, (feature["u"], feature["r"])):
        return {**out, "candidate": False, "reason": "NO_VALID_ROUTE_AFTER_BLOCK"}
    used_pairs, _nodes = opened(records)
    out["controls"] = matched_controls(g, ref, feature, r1, r2, used_pairs)
    out["candidate"] = True
    out["has_matched_control"] = out["controls"]["eligible"] > 0
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--combined", required=True)
    args = parser.parse_args(argv)
    report = load_script("s28_report", "28_pilot_report.py")
    launcher = load_script("screening_launcher", "20_screen_models.py")
    data = report.load_combined(args.combined)
    refs, _t, _m, status, kg, _d = launcher.load_evaluator()
    g = Graph(kg)
    flagged = [q for q in sorted(data["cofailure"]["queries"], key=lambda q: q["query_id"])
               if q["hop1_clean"]["cf3"] or q["pcf_rel3"] or q["pcf_node3"] or q["pcf_shortcut3"]]
    if any(q["pcf_node3"] for q in flagged):
        raise NotImplementedError("PCF_NODE3 candidates (OFF_PATH_NODE) need a node-level surgery rule")
    rows = [evaluate(q, refs[q["query_id"]], status[q["query_id"]],
                     [data["records"][(a, q["query_id"])] for a in data["agents"]], g) for q in flagged]
    c = sum(bool(r.get("has_matched_control")) for r in rows)
    out_dir = ROOT / "results/combined" / args.combined
    launcher.pin_manifest(out_dir / "d7_C.json", {
        "combined": args.combined, "C": c, "flagged_queries": len(flagged),
        "candidates": sum(r["candidate"] for r in rows), "queries": rows})
    lines = []
    for r in rows:
        f = r.get("feature") or {}
        ctl = r.get("controls", {})
        best = ctl.get("closest", [{}])[0] if ctl.get("closest") else {}
        lines.append({"query_id": r["query_id"], "candidate": r["candidate"], "reason": r.get("reason", ""),
                      "mechanism": f.get("mechanism", ""), "u": f.get("u", ""), "r": f.get("r", ""),
                      "holders": f.get("agent_count", ""), "treatment_branch_degree": ctl.get("treatment_branch_degree", ""),
                      "control_slots": ctl.get("slots", ""),
                      "slots_opened_by_an_agent": ctl.get("slots_opened_by_an_agent", ""),
                      "eligible_controls": ctl.get("eligible", ""), "within_25pct": ctl.get("within_25pct", ""),
                      "closest_control": f"({best['node']}, {best['label']}) bd={best['branch_degree']}" if best else "",
                      "has_matched_control": bool(r.get("has_matched_control"))})
    for line in lines:
        print(json.dumps(line, ensure_ascii=False), flush=True)
    print(f"C = {c} (of {len(flagged)} flagged queries)", flush=True)
    csv_path = out_dir / "d7_C.csv"
    if csv_path.exists():
        raise FileExistsError(f"{csv_path} exists; not overwritten")
    with csv_path.open("x", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(lines[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(lines)


if __name__ == "__main__":
    main()
