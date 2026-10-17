"""Replay saved S14 answers and verify two Label A results (protocol §6/§13).

Run from the repository root; emits JSON to stdout, makes no model calls.
Assertions are the self-checks for this stage-specific diagnostic script.
"""

import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from cofail_kg.agents.run_agent import parse_final
from cofail_kg.agents.trace import load_episode_record
from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.evaluation.answer_labels import label_answers
from cofail_kg.evaluation.normalize import normalize_agent_answers
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes


def main():
    episode = Path("results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json")
    record = load_episode_record(episode)
    paths = [episode, Path("data/processed/reference_queries.parquet"),
             Path("data/processed/reference_targets.parquet"),
             Path("data/processed/primary_population.csv"),
             Path("results/semantics/relation_mapping.json"),
             Path("results/diagnostics/s16/s14_normalization.json")]
    hashes = {p.as_posix(): file_sha256(p) for p in paths}
    frozen = read_frozen_hashes(Path("configs/frozen_hashes.yaml"))
    assert hashes[paths[4].as_posix()] == frozen["relation_mapping"]
    previous = json.loads(paths[5].read_text(encoding="utf-8"))
    assert hashes[episode.as_posix()] == previous["source_episode_sha256"]
    assert hashes[paths[1].as_posix()] == previous["reference_queries_sha256"]
    query_id = record["query_id"]
    q = pd.read_parquet(paths[1]).set_index("query_id").loc[query_id].to_dict()
    population = pd.read_csv(paths[3]).set_index("query_id").loc[query_id]
    assert population["status"] == "CONSISTENT"
    assert q["construction"] == population["construction"] == "BRIDGE"
    spec = json.loads(paths[4].read_text(encoding="utf-8"))["per_type"][q["relation_type"]]
    assert spec["construction"] == q["construction"]
    assert set(q["A_star_q"]) == set(q["G_q"]) == set(q["T_q_gold_bridges"])
    kg = PrimeKGIndex("data/cache")
    assert file_sha256("data/cache/primekg_metadata.json") == frozen["kg_fingerprint"] == record["kg_fingerprint"]
    parsed = parse_final(record["raw_final_output"], [])
    assert parsed is not None
    normalized = normalize_agent_answers(kg, parsed["answers"], q["Type_T"])
    assert [asdict(item) for item in normalized.items] == [
        {k: v for k, v in item.items() if k != "submitted"} for item in previous["items"]]
    assert normalized.kept_indices == previous["kept_indices"]
    labels = label_answers(normalized.answers, q, consistent=population["status"] == "CONSISTENT")
    answers = [{"submitted_index": i, **parsed["answers"][i], "node_id": result.node_id,
                "label": label} for i, result, label in
               zip(normalized.kept_indices, normalized.answers, labels)]
    assert len(answers) == 21 and Counter(labels) == {"GOLD": 21}

    targets = pd.read_parquet(paths[2])
    targets = targets.loc[targets.query_id.eq(query_id)]
    checks = []
    for answer in answers[:2]:
        node = answer["node_id"]
        bridges = sorted(set(targets.loc[targets.target.eq(node), "bridge"]), key=int)
        gold_bridges = sorted(set(bridges) & set(q["gold_bridges"]), key=int)
        assert gold_bridges and node in q["A_star_q"] and node in q["G_q"]
        paths_checked = []
        for bridge in bridges:
            hop1 = kg.neighbors_by_label(q["s"], q["Type_B"])
            hop2 = kg.neighbors_by_label(bridge, q["Type_T"])
            r1 = [r for r in spec["R1"] if bridge in hop1.get(r, set())]
            r2 = [r for r in spec["R2"] if node in hop2.get(r, set())]
            assert r1 and r2
            paths_checked.append({"bridge": kg.get_node(bridge), "R1": r1, "R2": r2,
                                  "gold_bridge": bridge in q["gold_bridges"]})
        checks.append({**answer, "construction": q["construction"],
                       "in_reference_targets": True, "in_A_star_q": True, "in_G_q": True,
                       "paths": paths_checked})
    print(json.dumps({"query_id": query_id, "relation_type": q["relation_type"],
                      "construction": q["construction"], "status": population["status"],
                      "in_primary_population": True, "source": kg.get_node(q["s"]),
                      "counts": dict(Counter(labels)), "answers": answers,
                      "hand_checks": checks, "source_hashes": hashes}, indent=2))


if __name__ == "__main__":
    main()
