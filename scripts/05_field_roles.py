"""S5: field-role verification (protocol §3.1; runbook S5).

Reads the pinned BioHopR rows and the S4 PrimeKG cache; writes, in results/semantics/:
- field_roles.csv          one line per sampled row (5 per relation type, §3.1)
- field_roles_summary.md   per-relation-type evidence and the §3.1 failure-rule outcome
- field_roles_summary.json the same, machine-readable, with provenance

Refuses to overwrite existing outputs (completed results are never overwritten).
The rule outcome is reported, not acted on: exclusions and the §3.1 field-role decision are the
researcher's (decision log).

Usage: python scripts/05_field_roles.py
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

from cofail_kg.data.biohopr_loader import load_biohopr, read_metadata
from cofail_kg.data.field_roles import analyse_row, evaluate, s5_sample, type_row_counts
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/semantics"
FILES = ("field_roles.csv", "field_roles_summary.md", "field_roles_summary.json")
COLUMNS = [
    "relation_type", "sample_position", "row_id", "row_status", "resolvable", "supports",
    "hop2", "hop2_status", "hop2_node_id", "hop1", "hop1_status", "hop1_node_id",
    "type_s", "type_b", "type_t", "type_fields_agree",
    "labels_hop2_hop1", "c1_adjacent", "c2_some_answer_via_hop1", "c3_every_answer_reachable",
    "answers_total", "answers_resolved", "answers_unresolved", "unresolved_answers",
    "answers_resolving_to_s", "reach_via_stored_bridge", "reach_only_via_other_bridge",
    "reach_via_neither", "other_type_b_neighbours_of_hop2",
]


def cell(v):
    if v is None:
        return "NA"
    if isinstance(v, list):
        return "; ".join(v)
    return v


def git_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout.strip()


def summary_md(ev: dict, prov: dict) -> str:
    out = [
        "# S5 field-role verification — per-relation-type summary",
        "",
        "Protocol §3.1 (v1.3.2). Working hypothesis: `hop2` = query entity, `hop1` = bridge, "
        "`answer` = targets. Sample: first 5 rows per relation type in SHA256(\"42\" + row_id) order. "
        "Any label; §3.2 edge convention; §12 reference policy. Full rows: `field_roles.csv`.",
        "",
        "| relation type | rows in dataset | sampled | resolvable | supporting | support | outcome |",
        "|---|---|---|---|---|---|---|",
    ]
    for t, v in ev["per_type"].items():
        share = "NA" if v["support_share"] is None else f"{v['support_share']:.0%}"
        oc = v["outcome"] + (f" ({v['fail_reason']})" if v["fail_reason"] else "")
        out.append(f"| {t} | {v['rows_in_dataset']} | {v['sampled']} | {v['resolvable']} "
                   f"| {v['supporting']} | {share} | {oc} |")
    out += ["", "**§3.1 failure rule.**",
            f"- Failing types: {', '.join(ev['failing_types']) or 'none'}",
            f"- Rows covered by failing types: {ev['failing_rows_in_dataset']} of {ev['total_rows']} "
            f"({ev['failing_coverage']:.2%})",
            f"- Rule outcome: **{ev['rule_outcome']}**", ""]
    conflicts = {t: v for t, v in ev["per_type"].items() if v["conflicting_rows"] or v["unresolved_rows"]}
    if conflicts:
        out.append("**Conflicting and unresolved rows.**")
        for t, v in conflicts.items():
            out.append(f"- {t}: conflicting {v['conflicting_rows'] or 'none'}; "
                       f"unresolved {v['unresolved_rows'] or 'none'}")
        out.append("")
    out += ["**Provenance.**"] + [f"- {k}: `{v}`" for k, v in prov.items()]
    return "\n".join(out) + "\n"


def main() -> int:
    existing = [f for f in FILES if (OUT / f).exists()]
    if existing:
        print(f"ERROR: {existing} already exist in {OUT}; completed results are never overwritten.",
              file=sys.stderr)
        return 1
    t0 = time.perf_counter()
    raw_dir = ROOT / "data/raw/biohopr"
    rows = load_biohopr(raw_dir)
    revision = read_metadata(raw_dir)["revision"]
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    if revision != frozen["biohopr_revision"]:
        raise RuntimeError(f"BioHopR revision {revision} != frozen {frozen['biohopr_revision']}")
    kg = PrimeKGIndex(ROOT / "data/cache")
    t_load = time.perf_counter() - t0

    cache: dict[tuple[str, str], set[str]] = {}

    def find(name, node_type):
        return [n["id"] for n in kg.find_by_name(name, node_type)]

    def nbrs(node_id, node_type):
        if (node_id, node_type) not in cache:
            cache[(node_id, node_type)] = {n["id"] for n in kg.neighbors(node_id, neighbor_type=node_type)}
        return cache[(node_id, node_type)]

    def labels_between(u, v):
        return sorted(r["label"] for r in kg.relations_of(u)
                      if any(n["id"] == v for n in kg.neighbors(u, label=r["label"])))

    records = []
    for rtype, items in s5_sample(rows).items():
        for position, row in items:
            rec = {"relation_type": rtype, "sample_position": position, "row_id": row["row_id"]}
            rec.update(analyse_row(row, find, nbrs, labels_between))
            records.append(rec)
    ev = evaluate(records, type_row_counts(rows))

    prov = {
        "biohopr_revision": revision,
        "kg_fingerprint": frozen["kg_fingerprint"],
        "git_commit": git_commit(),
        "protocol_version": "1.3.2",
        "run_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "field_roles.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for rec in records:
            w.writerow({k: cell(rec[k]) for k in COLUMNS})
    (OUT / "field_roles_summary.md").write_text(summary_md(ev, prov), encoding="utf-8")
    (OUT / "field_roles_summary.json").write_text(
        json.dumps({"provenance": prov, **ev}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(records)} sampled rows; rule outcome {ev['rule_outcome']}; "
          f"load {t_load:.1f}s, total {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
