"""Replay saved S14 with all §15 metrics; assertions verify raw-call evidence.

Run from the repository root; JSON goes to stdout. No inference/episode writes.
"""

import json
from pathlib import Path

import pandas as pd

from cofail_kg.agents.trace import load_episode_record
from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.evaluation.agent_metrics import agent_metrics, degree_statistics
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes


def main():
    episode = Path("results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json")
    record = load_episode_record(episode)
    previous = json.loads(Path("results/diagnostics/s18/s14_labels.json").read_text(encoding="utf-8"))
    for name, digest in previous["source_hashes"].items():
        assert file_sha256(name) == digest
    frozen = read_frozen_hashes(Path("configs/frozen_hashes.yaml"))
    assert file_sha256("results/semantics/relation_mapping.json") == frozen["relation_mapping"]
    assert file_sha256("data/cache/primekg_metadata.json") == frozen["kg_fingerprint"] == record["kg_fingerprint"]
    q = pd.read_parquet("data/processed/reference_queries.parquet").set_index("query_id").loc[record["query_id"]].to_dict()
    q["query_id"] = record["query_id"]
    population = pd.read_csv("data/processed/primary_population.csv").set_index("query_id").loc[q["query_id"]]
    assert population["status"] == "CONSISTENT" and q["construction"] == "BRIDGE"
    spec = json.loads(Path("results/semantics/relation_mapping.json").read_text())["per_type"][q["relation_type"]]
    targets = pd.read_parquet("data/processed/reference_targets.parquet")
    targets = targets[targets.query_id == q["query_id"]]
    bridge_targets = {str(b): group.target.tolist() for b, group in targets.groupby("bridge", sort=True)}
    kg = PrimeKGIndex("data/cache")
    nodes = pd.read_parquet("data/cache/primekg_nodes.parquet")
    edges = pd.read_parquet("data/cache/primekg_edges.parquet")
    degrees = degree_statistics(nodes, edges)
    row = agent_metrics(record, q, spec, bridge_targets, kg, degrees, consistent=True)

    # Raw inspection: calls 1/3 contain the sole source bridge/all 21 answers.
    assert len(record["call_log"]) == 4 and row["tool_calls_used"] == 4 and row["pages_requested"] == 2
    first, second = record["call_log"][1], record["call_log"][3]
    assert first["arguments"] == {"entity_id": "14097", "relation": "drug_protein", "neighbor_type": "gene/protein", "page": 1}
    assert [n["id"] for n in first["result"]["items"]] == ["111"]
    assert first["result"]["page_size"] == 50 and first["result"]["total_count"] == 1
    assert second["arguments"] == {"entity_id": "111", "relation": "disease_protein", "neighbor_type": "disease", "page": 1}
    assert second["result"]["total_count"] == len(second["result"]["items"]) == 21
    assert first["result"]["has_more"] is False and second["result"]["has_more"] is False
    assert row["bridges_explored"] == ["111"] and row["bridge_rank"] == {"111": 1}
    assert row["early_stop"] is False and row["bridge_conditional_recall"] == {"111": 1.0}
    assert row["answer_count"] == row["resolved_count"] == row["label_a_counts"]["GOLD"] == 21
    assert row["question_valid_precision"] == row["benchmark_precision"] == 1.0
    assert row["benchmark_recall"] == row["benchmark_f1"] == 1.0
    assert row["budget_exhausted"] is False and row["text_tool_call_count"] == 0
    assert row["hop1_status"] == "H1_CLEAN" and row["found_r1"] is True
    fields = ("node_id", "label_a", "label_b", "h1", "primary_path", "primary_reason_codes", "reason_codes")
    for answer, old in zip(row["answers"], previous["answers"], strict=True):
        assert {k: answer[k] for k in fields} == {k: old[k] for k in fields}
        assert answer["first_seen_page"] == 1 and answer["list_size"] == answer["primary_path_max_list_size"] == 21
        assert answer["node_id"] in [n["id"] for n in second["result"]["items"]]
    # Independently use the S4 lookup for every reported node degree/percentile.
    for node, stat in row["node_statistics"].items():
        assert stat["degree"] == kg.degree(node)
        same_type = [n for n in degrees if kg.get_node(n)["type"] == kg.get_node(node)["type"]]
        expected = 100 * sum(degrees[n]["degree"] <= stat["degree"] for n in same_type) / len(same_type)
        assert abs(stat["degree_percentile"] - expected) < 1e-10
    sources = list(previous["source_hashes"]) + ["data/processed/reference_targets.parquet",
               "data/cache/primekg_nodes.parquet", "data/cache/primekg_edges.parquet"]
    print(json.dumps({"metrics": row, "source_hashes": {p: file_sha256(p) for p in sources}}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
