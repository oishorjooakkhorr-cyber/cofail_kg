"""Replay S14 without inference; verify every S18 path against raw calls (§11/§14).

Run from the repository root; stdout is JSON. Assertions are the self-checks.
"""

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from cofail_kg.agents.run_agent import parse_final
from cofail_kg.agents.trace import load_episode_record
from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.evaluation.answer_labels import label_answers
from cofail_kg.evaluation.normalize import normalize_agent_answers
from cofail_kg.evaluation.path_labels import label_paths
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes


def main():
    episode = Path("results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json")
    record = load_episode_record(episode)
    previous = json.loads(Path("results/diagnostics/s17/s14_labels.json").read_text())
    paths = [episode, Path("data/processed/reference_queries.parquet"),
             Path("data/processed/primary_population.csv"),
             Path("results/semantics/relation_mapping.json"),
             Path("results/diagnostics/s17/s14_labels.json")]
    hashes = {p.as_posix(): file_sha256(p) for p in paths}
    for name, digest in previous["source_hashes"].items():
        assert file_sha256(name) == digest
    frozen = read_frozen_hashes(Path("configs/frozen_hashes.yaml"))
    assert hashes[paths[3].as_posix()] == frozen["relation_mapping"]
    assert file_sha256("data/cache/primekg_metadata.json") == frozen["kg_fingerprint"] == record["kg_fingerprint"]
    q = pd.read_parquet(paths[1]).set_index("query_id").loc[record["query_id"]].to_dict()
    q["query_id"] = record["query_id"]
    population = pd.read_csv(paths[2]).set_index("query_id").loc[record["query_id"]]
    assert population["status"] == "CONSISTENT" and q["construction"] == "BRIDGE"
    spec = json.loads(paths[3].read_text())["per_type"][q["relation_type"]]
    assert spec["R1"] == ["drug_protein"] and spec["R2"] == ["disease_protein"]
    kg = PrimeKGIndex("data/cache")
    parsed = parse_final(record["raw_final_output"], [])
    assert parsed is not None
    normalized = normalize_agent_answers(kg, parsed["answers"], q["Type_T"])
    labels_a = label_answers(normalized.answers, q, consistent=True)
    result = label_paths(normalized.answers, record, q, spec, kg)
    assert len(result["answers"]) == 21 and result["hop1_status"] == "H1_CLEAN" and result["found_r1"]
    assert labels_a == [a["label"] for a in previous["answers"]] == ["GOLD"] * 21
    assert [a.node_id for a in normalized.answers] == [a["node_id"] for a in previous["answers"]]

    # Direct inspection of all four raw calls identifies the only two-hop chain:
    # call 1: 14097 -> 111; call 3: 111 -> each of the 21 returned diseases.
    assert len(record["call_log"]) == 4 and q["s"] == "14097"
    assert kg.get_node("111")["type"] == q["Type_B"] == "gene/protein"
    hop1_neighbors = kg.neighbors_by_label("14097", q["Type_B"])["drug_protein"]
    hop2_neighbors = kg.neighbors_by_label("111", q["Type_T"])["disease_protein"]
    assert "111" in hop1_neighbors
    rows = []
    for i, resolution, label_a, item in zip(normalized.kept_indices, normalized.answers, labels_a, result["answers"]):
        x = resolution.node_id
        expected = [{"u": "14097", "label": "drug_protein", "v": "111", "creation_index": 1},
                    {"u": "111", "label": "disease_protein", "v": x, "creation_index": 3}]
        assert item["primary_path"] == expected
        raw_checks = []
        for edge in expected:
            call = record["call_log"][edge["creation_index"]]
            assert call["success"] and call["tool"] == "get_neighbors"
            assert call["arguments"]["entity_id"] == edge["u"]
            assert call["arguments"]["relation"] == edge["label"]
            assert call["arguments"]["page"] == 1
            returned = [n for n in call["result"]["items"] if n["id"] == edge["v"]]
            assert len(returned) == 1
            assert returned[0]["type"] == kg.get_node(edge["v"])["type"]
            raw_checks.append({"call_index": edge["creation_index"], "page": 1, "returned": returned[0]})
        assert kg.get_node(x)["type"] == q["Type_T"] == "disease" and x in hop2_neighbors
        assert item["label_b"] == "SUPPORTED" and item["h1"] == 1
        assert item["primary_reason_codes"] == item["reason_codes"] == []
        assert not (label_a == "OFF_QUESTION" and item["label_b"] == "SUPPORTED")
        rows.append({"submitted_index": i, "node_id": x, "name": kg.get_node(x)["name"],
                     "label_a": label_a, **item, "raw_call_checks": raw_checks})
    print(json.dumps({"query_id": record["query_id"], "construction": q["construction"],
                      "in_primary_population": True, "status": population["status"],
                      "counts": dict(Counter(a["label_b"] for a in rows)),
                      "hop1_status": result["hop1_status"], "found_r1": result["found_r1"],
                      "answers": rows, "source_hashes": hashes}, indent=2))


if __name__ == "__main__":
    main()
