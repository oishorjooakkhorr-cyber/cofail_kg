"""Investigate two S6 failures and describe construction mixtures, without rule changes.

Uses the original S6 sample and selected R1, checks every R2 subset independently
against raw edge orientations, and reproduces the original candidate scores.
Outputs are diagnostic only; no mappings or exclusions are changed.
"""

import csv
import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import pandas as pd

from cofail_kg.data.biohopr_loader import file_sha256, load_biohopr, read_metadata
from cofail_kg.data.field_roles import analyse_row
from cofail_kg.evaluation.normalize import index_finder, resolve_reference
from cofail_kg.evaluation.relation_mapping import candidate_sets, score_type, validation_sample
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
TYPES = ("disease:effect/phenotype:drug", "effect/phenotype:drug:disease")


def category(gold, bridge, union):
    if gold == bridge and gold == union:
        return "BOTH"
    if gold == bridge:
        return "BRIDGE_ONLY"
    return "UNION_ONLY" if gold == union else "NEITHER"


def difference(gold, reached):
    return {"reached": sorted(reached, key=int), "extra": sorted(reached - gold, key=int),
            "missing": sorted(gold - reached, key=int), "exact": gold == reached}


def main():
    out = ROOT / "results/semantics/s6_remaining_investigation"
    if out.exists():
        raise FileExistsError(f"Preserve existing investigation: {out}")
    protected = ["docs/frozen_pilot_protocol.md", "docs/decision_rules.md", "configs/frozen_hashes.yaml",
                 "results/semantics/relation_mapping_proposed.json", "results/semantics/relation_type_exclusions.json"]
    before = {p: file_sha256(ROOT / p) for p in protected}
    proposal = json.loads((ROOT / protected[3]).read_text(encoding="utf-8"))
    frozen = read_frozen_hashes(ROOT / protected[2])
    rows = load_biohopr(ROOT / "data/raw/biohopr")
    assert read_metadata(ROOT / "data/raw/biohopr")["revision"] == frozen["biohopr_revision"]
    assert file_sha256(ROOT / "data/cache/primekg_metadata.json") == frozen["kg_fingerprint"]
    metadata = json.loads((ROOT / "data/cache/primekg_metadata.json").read_text())
    release = {}
    for name, expected_md5 in (("kg.csv", "aac8191d4fbc5bf09cdf8c3c78b4e75f"),
                               ("nodes.csv", "7f9ab4109c54049e819ecd14e15a6038")):
        path = ROOT / "data/raw/primekg" / name
        sha = file_sha256(path)
        with path.open("rb") as stream:
            md5 = hashlib.file_digest(stream, "md5").hexdigest()
        assert sha == metadata["raw_files"][name]["sha256"] and md5 == expected_md5
        release[name] = {"sha256": sha, "md5": md5, "matches_frozen_and_S4_record": True}
    print("Frozen inputs and S4-recorded release checksums verified.", flush=True)
    kg = PrimeKGIndex(ROOT / "data/cache")
    find = index_finder(kg)

    @lru_cache(None)
    def neighbors(node, kind, label=None):
        return {n["id"] for n in kg.neighbors(node, label, kind)}

    def resolved_find(name, kind):
        result = resolve_reference(find, name, kind)
        return [result.node_id] if result.resolved else []

    def labels_between(s, b):
        return sorted(r["label"] for r in kg.relations_of(s)
                      if b in neighbors(s, kg.get_node(b)["type"], r["label"]))

    prepared, needed, summaries = {}, set(), {}
    for t in TYPES:
        source = [r for r in rows if r["relation_hop2"] == t]
        old = proposal["per_type"][t]
        st, bt, tt = t.split(":")
        sample, skipped = validation_sample(source, find)
        assert [r["row_id"] for r in sample] == old["sample_row_ids"]
        assert not skipped and not any(r["unresolved_answers"] for r in sample)
        fresh = score_type(source, find, lru_cache(None)(kg.neighbors_by_label),
                           kg.candidate_labels(st, bt), kg.candidate_labels(bt, tt))
        fresh.pop("candidate_scores")
        assert fresh == old, f"S6 reproduction differs for {t}"
        lookup = {r["row_id"]: r for r in source}
        records = []
        for r in sample:
            raw = lookup[r["row_id"]]
            bridges = set().union(*(neighbors(r["s"], bt, label) for label in old["R1"])) - {r["s"]}
            roles = analyse_row(raw, resolved_find, lambda n, k: neighbors(n, k), labels_between)
            needed.update({r["s"], r["b"]} | bridges)
            records.append({**r, "bridges": bridges, "roles": roles, "raw": raw})
        available = sum(bool(resolved_find(r["hop2"], st)) and bool(resolved_find(r["hop1"], bt)) for r in source)
        prepared[t] = records
        summaries[t] = {"dataset_rows": len(source), "query_bridge_resolvable_in_type": available,
                        "validation_rows": len(sample), "skipped": 0,
                        "supporting_rows_on_fresh_role_check": sum(r["roles"]["supports"] for r in records),
                        "field_types_agree": all(r["roles"]["type_fields_agree"] for r in records),
                        "original_scores_reproduced": True, "R1": old["R1"]}
        print(f"{t}: original scores reproduced; {available}/{len(source)} rows have resolved query/bridge.", flush=True)

    outgoing, incoming = defaultdict(lambda: defaultdict(set)), defaultdict(lambda: defaultdict(set))
    needed_int = {int(n) for n in needed}
    scanned = 0
    for chunk in pd.read_csv(ROOT / "data/raw/primekg/kg.csv", usecols=["x_index", "y_index", "relation"], chunksize=400000):
        selected = chunk[chunk.x_index.isin(needed_int) | chunk.y_index.isin(needed_int)]
        for label, x, y in selected[["relation", "x_index", "y_index"]].itertuples(index=False, name=None):
            if x in needed_int:
                outgoing[str(x)][label].add(str(y))
            if y in needed_int:
                incoming[str(y)][label].add(str(x))
        scanned += len(chunk)
    assert scanned == 8100498
    print("Raw graph scan complete; checking candidate paths in both stored orientations.", flush=True)

    def raw_neighbors(node, kind, labels, orientation):
        return {i for label in labels for i in orientation[node][label] if kg.get_node(i)["type"] == kind}

    results, csv_rows = {}, []
    for t, records in prepared.items():
        old = proposal["per_type"][t]
        _, bt, tt = t.split(":")
        r1 = old["R1"]
        scenario = old["scenarios"][0]
        assert scenario["BRIDGE"]["sets"] == scenario["UNION"]["sets"] and len(scenario["BRIDGE"]["sets"]) == 1
        best = scenario["BRIDGE"]["sets"][0]
        categories, mismatches, details = Counter(), Counter(), []
        for record in records:
            s, b, gold, bridges = (record[k] for k in ("s", "b", "gold", "bridges"))
            for orient in (outgoing, incoming):
                assert raw_neighbors(s, bt, r1, orient) - {s} == bridges
            variants = []
            for labels in candidate_sets(old["candidates"]["hop2"]):
                bridge = set().union(*(neighbors(b, tt, label) for label in labels)) - {s}
                union = set().union(*(neighbors(n, tt, label) for n in bridges for label in labels)) - {s}
                for orient in (outgoing, incoming):
                    assert raw_neighbors(b, tt, labels, orient) - {s} == bridge
                    raw_union = set().union(*(raw_neighbors(n, tt, labels, orient) for n in bridges)) - {s}
                    assert raw_union == union
                variants.append({"R2": list(labels), "BRIDGE": difference(gold, bridge), "UNION": difference(gold, union)})
                if list(labels) == best:
                    cat = category(gold, bridge, union)
                    categories[cat] += 1
                    for construction, reached in (("BRIDGE", bridge), ("UNION", union)):
                        pattern = "EXACT" if gold == reached else "EXTRA_ONLY" if gold < reached else "MISSING_ONLY" if reached < gold else "EXTRA_AND_MISSING"
                        mismatches[construction + ":" + pattern] += 1
                    csv_rows.append({"relation_type": t, "row_id": record["row_id"], "category": cat,
                                     "gold": len(gold), "bridges": len(bridges), "bridge_targets": len(bridge),
                                     "union_targets": len(union), "bridge_extra": len(bridge-gold),
                                     "bridge_missing": len(gold-bridge), "union_extra": len(union-gold), "union_missing": len(gold-union)})
            details.append({"row_id": record["row_id"], "question": record["raw"]["hop2_question_multi"],
                            "s": s, "b": b, "gold": sorted(gold, key=int), "bridges": sorted(bridges, key=int),
                            "field_roles": record["roles"], "category": cat, "variants": variants})
        summaries[t].update({"R2_for_exploration": best, "mixture_counts": dict(categories),
                             "difference_patterns": dict(mismatches), "raw_orientations_and_index_agree": True})
        results[t] = details
        print(t, json.dumps(summaries[t]), flush=True)
    assert before == {p: file_sha256(ROOT / p) for p in protected}
    all_ids = {i for rs in results.values() for r in rs for i in r["gold"] + r["bridges"] + [r["s"], r["b"]]}
    for rs in results.values():
        for r in rs:
            for v in r["variants"]:
                for c in ("BRIDGE", "UNION"):
                    all_ids.update(v[c]["reached"])
    evidence = {"scope": "Exploratory fixed-S6-sample investigation; no mixed rule adopted or exclusions changed.",
                "summaries": summaries, "records": results, "nodes": {i: kg.get_node(i) for i in sorted(all_ids, key=int)},
                "raw_rows_scanned": scanned, "release_checks": release, "protected_sha256": before,
                "script_sha256": file_sha256(Path(__file__)), "biohopr_revision": frozen["biohopr_revision"]}
    out.mkdir()
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out / "mixtures.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(csv_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)


if __name__ == "__main__":
    main()
