import pytest

from cofail_kg.evaluation.primary_population import build_population, feasibility


def record(i, kind="a", **changes):
    return dict(query_id=str(i), relation_type=kind, status="CONSISTENT", leaky_question=False,
                saturation_share=.5, bridge_multiplicity="SINGLE_BRIDGE", **changes)


def test_all_inclusion_rules_and_boundary():
    rows = [record(i, kind) for i, kind in enumerate(["a", "a", "a", "a", "b", "c", "d"])]
    rows[1]["status"] = "INCONSISTENT"
    rows[2]["leaky_question"] = True
    rows[3]["saturation_share"] = .50001
    confirmation = {"a": "CONFIRMED", "b": "UNCONFIRMABLE", "c": "UNCONFIRMED", "d": "CONFIRMED"}
    population, report = build_population(rows, {"a", "b", "c"}, confirmation, .5)
    assert [r["query_id"] for r in population] == ["0", "4"]
    assert report["N_P"] == 2 and report["K"] == 0 and report["outcome"] == "RED"
    assert report["excluded_queries"] == 5
    assert report["exclusion_counts"]["not_d1_pass"] == 1


@pytest.mark.parametrize("n,k,outcome", [(0,0,"RED"), (149,9,"RED"), (150,0,"YELLOW"),
    (649,9,"YELLOW"), (650,4,"YELLOW"), (650,5,"GREEN"), (700,9,"GREEN")])
def test_feasibility_in_stated_order(n, k, outcome):
    assert feasibility(n,k) == outcome


def test_k_uses_twenty_queries_and_counts_multiplicity():
    rows = [record(i,"a") for i in range(20)] + [record(20+i,"b") for i in range(19)]
    rows[0]["bridge_multiplicity"] = "MULTI_BRIDGE"
    _, report = build_population(rows, {"a","b"}, {"a":"CONFIRMED","b":"CONFIRMED"}, .5)
    assert report["K"] == 1 and report["N_P"] == 39
    assert report["by_type"]["a"]["queries"] == 20
    assert report["by_multiplicity"] == {"MULTI_BRIDGE":1,"SINGLE_BRIDGE":38}


def test_overlapping_exclusions_count_query_once():
    rows = [record(0)]
    rows[0].update(status="INCONSISTENT", leaky_question=True)
    _, report = build_population(rows, {"a"}, {"a":"CONFIRMED"}, .5)
    assert report["excluded_queries"] == 1
    assert report["exclusion_counts"]["inconsistent"] == report["exclusion_counts"]["leaky_question"] == 1


def test_unfilled_theta_or_missing_confirmation_fails():
    with pytest.raises(ValueError, match="theta"):
        build_population([record(0)], {"a"}, {"a":"CONFIRMED"}, None)
    with pytest.raises(ValueError, match="confirmation"):
        build_population([record(0)], {"a"}, {}, .5)


def test_script_requires_frozen_theta_and_preserves_completed_outputs(tmp_path):
    import csv
    import importlib.util
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1]/"scripts/09_primary_population.py"
    spec = importlib.util.spec_from_file_location("s9_population", path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    with pytest.raises(ValueError, match="FROZEN"):
        script.frozen_theta("| Saturation threshold θ | Recommended 0.50 | `[TBD@S9]` |")
    assert script.frozen_theta("| Saturation threshold θ | 0.50 | `[FROZEN]` at S9 |") == .5
    rows = [record(0)]
    population, report = build_population(rows, {"a"}, {"a":"CONFIRMED"}, .5)
    script.write_outputs(tmp_path, population, report, rows[0])
    with (tmp_path/script.FILES[0]).open(newline="", encoding="utf-8") as stream:
        saved = list(csv.DictReader(stream))
    assert saved[0]["query_id"] == "0" and saved[0]["theta"] == "0.5"
    summary = json.loads((tmp_path/script.FILES[1]).read_text())
    assert summary["primary_population_sha256"] == script.file_sha256(tmp_path/script.FILES[0])
    with pytest.raises(FileExistsError):
        script.write_outputs(tmp_path, population, report, rows[0])
