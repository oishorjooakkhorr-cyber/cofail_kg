"""S39 (EXPLORATORY, decision log 2026-11-11): manifest and agent-input sheet for the full run.

Population: every query of the primary population (protocol §7.2) that is in none of the four S10 sets
(screening, smoke, pilot, expansion). No sampling: by protocol §8 step 1 a set larger than what remains
"contains all remaining queries". Queries listed in configs/full_run_exclusions.json (researcher
decision 2026-11-11 after the §19.1 leakage scan of the candidates) are left out. Lines are ordered by SHA256("42" + query_id) ascending (the §8 step 3
key, ties by query ID), so a model that is interrupted has covered a pseudo-random subset (engineering
choice; the S10 sets are ordered by query ID).

Outputs (same line formats as S10; protocol §8, §9.3):
    data/processed/manifests/full.jsonl             evaluation side
    data/agent_inputs/full.jsonl                    agent side, exactly four fields
    data/processed/manifests/full_provenance.json
    configs/frozen_hashes_full.yaml  key `manifests_full`  (written once)
configs/frozen_hashes.yaml is NOT written: it is a pinned run source of pilot_v1 and expansion_v1, and
any byte change to it would make their pinned-source check refuse a later re-analysis.
A second run must reproduce the same bytes; anything else is refused.

Usage:  python scripts/39_make_full_manifest.py
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

import pyarrow.parquet as pq

from cofail_kg.data.sampling import SEED, size_bin
from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once

ROOT = Path(__file__).resolve().parents[1]
EARLIER_SETS = ("screening", "smoke", "pilot", "expansion")
NAME = "full"
FULL_HASHES = "configs/frozen_hashes_full.yaml"
EXCLUSIONS = "configs/full_run_exclusions.json"
HASH_KEY = "manifests_full"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def jsonl(records):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                   for r in records).encode("utf-8")


def remaining_queries(population, drawn, excluded=()):
    """Primary-population rows neither drawn nor excluded, ordered by SHA256(seed + query_id), then ID."""
    ids = [r["query_id"] for r in population]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate population query IDs")
    missing = set(drawn) - set(ids)
    if missing:
        raise ValueError(f"Drawn queries absent from the primary population: {sorted(missing)[:5]}")
    excluded = set(excluded)
    stray = excluded - (set(ids) - set(drawn))
    if stray:
        raise ValueError(f"Excluded queries are not undrawn primary-population queries: {sorted(stray)[:5]}")
    rest = [r for r in population if r["query_id"] not in drawn and r["query_id"] not in excluded]
    return sorted(rest, key=lambda r: (hashlib.sha256((str(SEED) + r["query_id"]).encode()).hexdigest(),
                                       r["query_id"]))


def build_lines(rows, references, nodes):
    """Manifest and agent-sheet records for the rows, with the S10 consistency checks."""
    manifest, sheet = [], []
    for r in rows:
        q = references[r["query_id"]]
        node = nodes[q["s"]]
        if len(set(q["question_texts"])) != 1 or node["node_type"] != q["Type_S"]:
            raise ValueError(f"Invalid reference question/start node: {q['query_id']}")
        if r["relation_type"] != q["relation_type"] or int(r["target_count"]) != len(q["T_q"]):
            raise ValueError(f"Primary/S7 reference mismatch: {q['query_id']}")
        multiplicity = "SINGLE_BRIDGE" if len(q["B_q"]) == 1 else "MULTI_BRIDGE" if len(q["B_q"]) > 1 else "NO_BRIDGE"
        if r["bridge_multiplicity"] != multiplicity:
            raise ValueError(f"Primary/S7 multiplicity mismatch: {q['query_id']}")
        manifest.append(dict(query_id=r["query_id"], relation_type=r["relation_type"], multiplicity=multiplicity,
                             ambiguity_tag=r["ambiguity_tag"], tq_size_bin=size_bin(int(r["target_count"]))))
        sheet.append(dict(query_id=r["query_id"], question_text=q["question_texts"][0],
                          start_name=node["node_name"], start_id=q["s"]))
    return manifest, sheet


def publish(root, artifacts, hashes):
    """Write each artifact once; identical bytes are accepted, different bytes refused. Then freeze."""
    frozen_path = root / FULL_HASHES
    frozen = read_frozen_hashes(frozen_path)
    if HASH_KEY in frozen and frozen[HASH_KEY] != hashes:
        raise ValueError(f"Frozen `{HASH_KEY}` hashes differ; refusing to rebuild the full manifest")
    for path, data in artifacts.items():
        dest = root / path
        if dest.exists() and dest.read_bytes() != data:
            raise FileExistsError(f"Existing full-run artifact differs: {path}")
    for path, data in artifacts.items():
        dest = root / path
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("xb") as handle:
                handle.write(data)
    write_once(frozen_path, HASH_KEY, hashes)


def count(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return dict(sorted(out.items()))


def main():
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    summary = json.loads((ROOT / "data/processed/primary_population_summary.json").read_text(encoding="utf-8"))
    population_path = ROOT / "data/processed/primary_population.csv"
    if sha256(population_path) != summary["primary_population_sha256"]:
        raise ValueError("Primary population hash mismatch")
    drawn = {}
    for name in EARLIER_SETS:
        for path in (f"data/processed/manifests/{name}.jsonl", f"data/agent_inputs/{name}.jsonl"):
            if sha256(ROOT / path) != frozen["manifests"][path]:
                raise ValueError(f"Frozen S10 file changed: {path}")
        for line in (ROOT / f"data/processed/manifests/{name}.jsonl").read_text(encoding="utf-8").splitlines():
            query_id = json.loads(line)["query_id"]
            if query_id in drawn:
                raise ValueError(f"{query_id} is in two S10 sets")
            drawn[query_id] = name
    with population_path.open(newline="", encoding="utf-8") as stream:
        population = list(csv.DictReader(stream))
    if len(population) != summary["N_P"] or any(r["status"] != "CONSISTENT" or r["leaky_question"] != "False"
                                               or r["saturated"] != "False" for r in population):
        raise ValueError("Invalid primary population")
    excluded = json.loads((ROOT / EXCLUSIONS).read_text(encoding="utf-8"))["excluded"]
    rows = remaining_queries(population, drawn, excluded)
    if len(rows) != summary["N_P"] - len(drawn) - len(excluded):
        raise ValueError("Remaining count is not N_P minus the drawn and excluded queries")
    references = {q["query_id"]: q for q in pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()}
    nodes = {str(n["node_index"]): n for n in pq.read_table(ROOT / "data/cache/primekg_nodes.parquet").to_pylist()}
    manifest, sheet = build_lines(rows, references, nodes)
    manifest_path, sheet_path = f"data/processed/manifests/{NAME}.jsonl", f"data/agent_inputs/{NAME}.jsonl"
    artifacts = {manifest_path: jsonl(manifest), sheet_path: jsonl(sheet)}
    hashes = {path: hashlib.sha256(data).hexdigest() for path, data in sorted(artifacts.items())}
    inputs = ["data/processed/primary_population.csv", "data/processed/reference_queries.parquet",
              "data/cache/primekg_nodes.parquet", "scripts/39_make_full_manifest.py", "src/cofail_kg/data/sampling.py", EXCLUSIONS]
    report = {"status": "EXPLORATORY (decision log 2026-11-11, S39)", "seed": SEED,
              "order": "SHA256(seed + query_id) ascending, then query_id",
              "primary_population": len(population), "drawn_earlier": count([{"s": s} for s in drawn.values()], "s"),
              "excluded_after_leakage_scan": len(excluded), "queries": len(rows), "by_multiplicity": count(manifest, "multiplicity"),
              "by_relation_type": count(manifest, "relation_type"), "by_ambiguity_tag": count(manifest, "ambiguity_tag"),
              "by_tq_size_bin": count(manifest, "tq_size_bin"), "frozen_manifests_full": hashes,
              "sha256": {p: sha256(ROOT / p) for p in inputs}}
    provenance = ROOT / "data/processed/manifests/full_provenance.json"
    if provenance.exists():  # keep the first run's commit; everything else must be reproduced exactly
        report["git_commit"] = json.loads(provenance.read_text(encoding="utf-8"))["git_commit"]
    else:
        report["git_commit"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True,
                                              capture_output=True).stdout.strip()
    artifacts["data/processed/manifests/full_provenance.json"] = (json.dumps(report, indent=2, sort_keys=True,
                                                                             ensure_ascii=False) + "\n").encode("utf-8")
    publish(ROOT, artifacts, hashes)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
