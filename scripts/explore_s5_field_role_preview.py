"""EXPLORATORY, read-only: field-role preview for protocol §3.1, disjoint from the S5 sample.

Exploratory evidence, disjoint from the S5 sample, viewed before the §3.1 amendment decision.
Not the S5 field-role check: it chooses no construction, selects no labels, passes or fails nothing.

Sample: per relation type, rows ordered by SHA256("42" + row_id) (hex, ascending); positions 6-10
only. Positions 1-5 are the S5 sample (§3.1) and are never resolved, analysed or written; a type
with 5 or fewer rows gets one "no disjoint rows available" line.

Per row (working hypothesis of §3.1: hop2 = query entity s, hop1 = stored bridge, answer = targets):
- s resolved as Type_S and the bridge as Type_B, by the §12 reference policy (§3.3 identity type map;
  lower-case, NFKC, whitespace collapse and trim): exactly one node -> resolved; none -> not_found;
  several -> ambiguous. not_found and ambiguous are "unresolved".
- Answers are a set of names (§0.4); each name resolved as Type_T the same way.
- Structural columns (any label, §3.2 either-direction convention, s excluded as in §6):
  adjacency of s and bridge; resolved answers reachable through the stored bridge; reachable only
  through another Type_B neighbour of s (not s, not the stored bridge); reachable through neither.
  The three reach counts partition the resolved answers. They are NA when s or the bridge is
  unresolved, so "unresolved" never shows up as a structural failure.

Usage: python scripts/explore_s5_field_role_preview.py
Writes results/diagnostics/s5_field_role_preview.csv and s5_field_role_preview_summary.md.
"""

from __future__ import annotations

import csv
import hashlib
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results/diagnostics"
LABEL = "exploratory evidence, disjoint from the S5 sample, viewed before the §3.1 amendment decision"
S5_SAMPLE_SIZE = 5
PREVIEW_POSITIONS = slice(5, 10)  # 0-based: positions 6-10 in SHA256 order

COLUMNS = [
    "evidence", "relation_type", "position", "row_id",
    "query_entity", "query_status", "query_node_id",
    "bridge", "bridge_status", "bridge_node_id",
    "structural_status", "s_bridge_adjacent",
    "answers_total", "answers_resolved", "answers_unresolved",
    "answers_resolving_to_s",
    "reach_via_stored_bridge", "reach_only_via_other_bridge", "reach_via_neither",
    "other_type_b_neighbours_of_s",
]


def order_key(row_id: str) -> str:
    return hashlib.sha256(("42" + row_id).encode("utf-8")).hexdigest()


def preview_rows(rows: list[dict]) -> dict[str, list[tuple[int, dict]]]:
    """Per relation type: [(1-based position, row)] for positions 6-10 only. S5 rows are dropped here."""
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_type[r["relation_hop2"]].append(r)
    out = {}
    for rtype in sorted(by_type):
        ordered = sorted(by_type[rtype], key=lambda r: order_key(r["row_id"]))
        out[rtype] = [(PREVIEW_POSITIONS.start + 1 + i, r) for i, r in enumerate(ordered[PREVIEW_POSITIONS])]
    return out


def resolve(find: Callable[[str, str], list[str]], name: str, node_type: str) -> tuple[str, str | None]:
    """§12 reference policy: exactly one node of the filter type -> resolved."""
    hits = find(name, node_type)
    if len(hits) == 1:
        return "resolved", hits[0]
    return ("not_found" if not hits else "ambiguous"), None


def analyse_row(
    row: dict,
    types: tuple[str, str, str],
    find: Callable[[str, str], list[str]],
    nbrs: Callable[[str, str], set[str]],
) -> dict:
    """One preview row. `find(name, type)` -> node ids; `nbrs(node_id, type)` -> neighbour ids of that type."""
    type_s, type_b, type_t = types
    q_status, s = resolve(find, row["hop2"], type_s)
    b_status, b = resolve(find, row["hop1"], type_b)

    names = sorted(set(row["answer"]))
    resolved: dict[str, str] = {}
    for name in names:
        status, node = resolve(find, name, type_t)
        if status == "resolved":
            resolved[name] = node
    out = {
        "query_entity": row["hop2"], "query_status": q_status, "query_node_id": s,
        "bridge": row["hop1"], "bridge_status": b_status, "bridge_node_id": b,
        "answers_total": len(names), "answers_resolved": len(resolved),
        "answers_unresolved": len(names) - len(resolved),
        "answers_resolving_to_s": None, "s_bridge_adjacent": None,
        "reach_via_stored_bridge": None, "reach_only_via_other_bridge": None,
        "reach_via_neither": None, "other_type_b_neighbours_of_s": None,
    }
    if s is None or b is None:
        out["structural_status"] = "not_computed_" + ("query_unresolved" if s is None else "bridge_unresolved")
        return out
    if b == s:
        out["structural_status"] = "not_computed_bridge_is_s"
        return out

    s_type_b = nbrs(s, type_b) - {s}
    others = s_type_b - {b}
    via_b = nbrs(b, type_t) - {s}
    via_other: set[str] = set()
    for o in sorted(others, key=int):
        via_other |= nbrs(o, type_t)
    via_other -= {s}

    targets = list(resolved.values())
    n_bridge = sum(t in via_b for t in targets)
    n_other = sum(t not in via_b and t in via_other for t in targets)
    out.update({
        "structural_status": "computed",
        "s_bridge_adjacent": b in s_type_b,
        "answers_resolving_to_s": sum(t == s for t in targets),
        "reach_via_stored_bridge": n_bridge,
        "reach_only_via_other_bridge": n_other,
        "reach_via_neither": len(targets) - n_bridge - n_other,
        "other_type_b_neighbours_of_s": len(others),
    })
    return out


def summarise(records: list[dict], empty_types: list[str]) -> str:
    lines = [
        "# S5 field-role preview — per-type summary",
        "",
        f"**{LABEL[0].upper() + LABEL[1:]}.**",
        "",
        "Rows 6–10 per relation type in SHA256(\"42\" + row_id) order; the first 5 (the S5 sample) were",
        "never analysed. Not the S5 check: no construction chosen, no label selection, no pass/fail.",
        "Counts are answer names (set semantics, §0.4). Reach columns cover resolved answers only and",
        "are summed over rows whose structure was computed. Full table: `s5_field_role_preview.csv`.",
        "",
        "| relation type | rows | s unresolved | bridge unresolved | computed | s–bridge adjacent "
        "| answers (resolved / unresolved) | via stored bridge | only via other bridge | via neither |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_type[r["relation_type"]].append(r)
    for rtype in sorted(set(by_type) | set(empty_types)):
        rs = by_type.get(rtype, [])
        if not rs:
            lines.append(f"| {rtype} | 0 | no disjoint rows available | | | | | | | |")
            continue
        comp = [r for r in rs if r["structural_status"] == "computed"]
        s = lambda k, xs=comp: sum(r[k] for r in xs)  # noqa: E731
        lines.append(
            f"| {rtype} | {len(rs)} "
            f"| {sum(r['query_status'] != 'resolved' for r in rs)} "
            f"| {sum(r['bridge_status'] != 'resolved' for r in rs)} "
            f"| {len(comp)} | {sum(bool(r['s_bridge_adjacent']) for r in comp)}/{len(comp)} "
            f"| {sum(r['answers_resolved'] for r in rs)} / {sum(r['answers_unresolved'] for r in rs)} "
            f"| {s('reach_via_stored_bridge')} | {s('reach_only_via_other_bridge')} | {s('reach_via_neither')} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    from cofail_kg.data.biohopr_loader import load_biohopr
    from cofail_kg.kg.primekg_index import PrimeKGIndex

    t0 = time.perf_counter()
    rows = load_biohopr(ROOT / "data/raw/biohopr")
    kg = PrimeKGIndex(ROOT / "data/cache")
    t_load = time.perf_counter() - t0

    cache: dict[tuple[str, str], set[str]] = {}

    def find(name: str, node_type: str) -> list[str]:
        return [n["id"] for n in kg.find_by_name(name, node_type)]

    def nbrs(node_id: str, node_type: str) -> set[str]:
        key = (node_id, node_type)
        if key not in cache:
            cache[key] = {n["id"] for n in kg.neighbors(node_id, neighbor_type=node_type)}
        return cache[key]

    records, empty = [], []
    for rtype, items in preview_rows(rows).items():
        if not items:
            empty.append(rtype)
            continue
        types = tuple(rtype.split(":"))
        if len(types) != 3:
            raise ValueError(f"relation type {rtype!r} is not a Query:Bridge:Target triple")
        for position, row in items:
            rec = {"evidence": LABEL, "relation_type": rtype, "position": position, "row_id": row["row_id"]}
            rec.update(analyse_row(row, types, find, nbrs))
            records.append(rec)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "s5_field_role_preview.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for rec in records:
            w.writerow({k: ("NA" if rec[k] is None else rec[k]) for k in COLUMNS})
        for rtype in empty:
            w.writerow({k: "NA" for k in COLUMNS} | {"evidence": LABEL, "relation_type": rtype,
                                                    "structural_status": "no disjoint rows available"})
    (OUT_DIR / "s5_field_role_preview_summary.md").write_text(summarise(records, empty), encoding="utf-8")
    print(f"{len(records)} preview rows, {len(empty)} type(s) without disjoint rows; "
          f"load {t_load:.1f}s, total {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
