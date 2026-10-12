"""EXPLORATORY, read-only: " (disease)" suffix preview over all 2-hop rows.

Exploratory, viewed before the §12 suffix decision. Computes no hop-2 score and no label set.

For every row (S5 roles: hop2 = query entity, hop1 = bridge, answer = targets) and each name field:
- resolve the name under §12 as written (exact normalized name among nodes of the field's type:
  Type_S for hop2, Type_B for hop1, Type_T for answers); exactly one -> resolved, none ->
  not_found, several -> ambiguous;
- for each name that does not resolve, resolve name + " (disease)" the same way, with the same
  type filter: exactly one -> "would resolve", otherwise "still unresolved".
Answer names are distinct raw strings per row (§0.4).

Writes results/diagnostics/suffix_preview.csv (per relation type x field),
suffix_preview_names.csv (each distinct unresolved name) and suffix_preview_summary.md.
Usage: python scripts/explore_suffix_preview.py
"""

from __future__ import annotations

import csv
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results/diagnostics"
LABEL = "exploratory, viewed before the §12 suffix decision"
SUFFIX = " (disease)"
FIELDS = ("answer", "hop2", "hop1")
COLUMNS = ["evidence", "relation_type", "field", "node_type", "rows", "names_checked",
           "unresolved_names", "unresolved_not_found", "unresolved_ambiguous", "rows_with_unresolved",
           "distinct_unresolved_names", "would_resolve_with_suffix", "still_unresolved_with_suffix",
           "rows_fully_resolved_with_suffix"]


def status(find: Callable[[str, str], list[str]], name: str, node_type: str) -> str:
    n = len(find(name, node_type))
    return "resolved" if n == 1 else ("not_found" if n == 0 else "ambiguous")


def preview(rows: list[dict], find: Callable[[str, str], list[str]]) -> tuple[list[dict], list[dict]]:
    """Return (per type x field counts, per distinct unresolved name details)."""
    agg: dict[tuple[str, str], dict] = {}
    names: dict[tuple[str, str, str], dict] = {}
    for row in rows:
        rtype = row["relation_hop2"]
        type_s, type_b, type_t = rtype.split(":")
        for field, ntype, values in (("answer", type_t, sorted(set(row["answer"]))),
                                     ("hop2", type_s, [row["hop2"]]), ("hop1", type_b, [row["hop1"]])):
            a = agg.setdefault((rtype, field), {
                "relation_type": rtype, "field": field, "node_type": ntype, "rows": 0, "names_checked": 0,
                "unresolved_names": 0, "unresolved_not_found": 0, "unresolved_ambiguous": 0,
                "rows_with_unresolved": 0, "distinct": set(), "would_resolve_with_suffix": 0,
                "still_unresolved_with_suffix": 0, "rows_fully_resolved_with_suffix": 0})
            a["rows"] += 1
            bad = fixed = 0
            for v in values:
                a["names_checked"] += 1
                st = status(find, v, ntype)
                if st == "resolved":
                    continue
                bad += 1
                a["unresolved_names"] += 1
                a["unresolved_" + st] += 1
                a["distinct"].add(v)
                st2 = status(find, v + SUFFIX, ntype)
                if st2 == "resolved":
                    fixed += 1
                    a["would_resolve_with_suffix"] += 1
                else:
                    a["still_unresolved_with_suffix"] += 1
                d = names.setdefault((rtype, field, v), {
                    "evidence": LABEL, "relation_type": rtype, "field": field, "node_type": ntype, "name": v,
                    "status": st, "with_suffix": st2, "rows": 0})
                d["rows"] += 1
            if bad:
                a["rows_with_unresolved"] += 1
                if fixed == bad:
                    a["rows_fully_resolved_with_suffix"] += 1
    out = []
    for key in sorted(agg, key=lambda k: (k[0], FIELDS.index(k[1]))):
        a = agg[key]
        a["distinct_unresolved_names"] = len(a.pop("distinct"))
        out.append({"evidence": LABEL, **a})
    detail = [names[k] for k in sorted(names, key=lambda k: (k[0], FIELDS.index(k[1]), k[2]))]
    return out, detail


def summary(agg: list[dict]) -> str:
    lines = ["# \" (disease)\" suffix preview — per-type summary", "",
             f"**{LABEL[0].upper() + LABEL[1:]}.** No hop-2 scores or label sets computed.", "",
             "Names resolved under §12 as written with the field's type filter; unresolved names re-tried "
             "with \" (disease)\" appended. Answer counts are (row, distinct name) pairs. "
             "Full counts: `suffix_preview.csv`; names: `suffix_preview_names.csv`.", "",
             "| relation type | field (type) | rows | unresolved names (not found / ambiguous) "
             "| rows with any | would resolve + suffix | still unresolved | rows fully fixed |",
             "|---|---|---|---|---|---|---|---|"]
    for a in agg:
        lines.append(f"| {a['relation_type']} | {a['field']} ({a['node_type']}) | {a['rows']} "
                     f"| {a['unresolved_names']} ({a['unresolved_not_found']} / {a['unresolved_ambiguous']}) "
                     f"| {a['rows_with_unresolved']} | {a['would_resolve_with_suffix']} "
                     f"| {a['still_unresolved_with_suffix']} | {a['rows_fully_resolved_with_suffix']} |")
    tot = defaultdict(int)
    for a in agg:
        for k in ("unresolved_names", "rows_with_unresolved", "would_resolve_with_suffix",
                  "still_unresolved_with_suffix", "rows_fully_resolved_with_suffix"):
            tot[(a["field"], k)] += a[k]
    lines += ["", "**Totals by field.**"]
    for f in FIELDS:
        lines.append(f"- {f}: {tot[(f, 'unresolved_names')]} unresolved in {tot[(f, 'rows_with_unresolved')]} "
                     f"rows; +suffix resolves {tot[(f, 'would_resolve_with_suffix')]}, "
                     f"still unresolved {tot[(f, 'still_unresolved_with_suffix')]}; "
                     f"rows fully fixed {tot[(f, 'rows_fully_resolved_with_suffix')]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    from cofail_kg.data.biohopr_loader import load_biohopr
    from cofail_kg.kg.primekg_index import PrimeKGIndex

    t0 = time.perf_counter()
    rows = load_biohopr(ROOT / "data/raw/biohopr")
    kg = PrimeKGIndex(ROOT / "data/cache")
    agg, detail = preview(rows, lambda name, t: [n["id"] for n in kg.find_by_name(name, t)])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "suffix_preview.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(agg)
    with open(OUT_DIR / "suffix_preview_names.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(detail[0]) if detail else ["evidence"], lineterminator="\n")
        w.writeheader()
        w.writerows(detail)
    (OUT_DIR / "suffix_preview_summary.md").write_text(summary(agg), encoding="utf-8")
    print(f"{len(rows)} rows; {len(detail)} distinct unresolved (type, field, name); "
          f"{time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
