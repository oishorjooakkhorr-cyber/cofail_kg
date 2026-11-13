"""Tests for scripts/49_weighted_rate.py (Phase J PW), on tiny synthetic strata."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pw", ROOT / "scripts/49_weighted_rate.py")
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)


def flag(cf3_h1=0, cf3=0, cf4=0):
    return {"CF3^{Q,H1}": cf3_h1, "CF3^Q": cf3, "CF4^Q": cf4}


def fixture():
    # Population: stratum A has 90 queries, stratum B has 10. Sample: 2 from A, 8 from B.
    population = {f"A{i:03d}": ("tA", "SINGLE_BRIDGE") for i in range(90)}
    population.update({f"B{i:03d}": ("tB", "MULTI_BRIDGE") for i in range(10)})
    sample = ["A000", "A001"] + [f"B{i:03d}" for i in range(8)]
    flags = {q: flag() for q in sample}
    flags["A000"] = flag(1, 1, 0)          # 1 of 2 in A
    flags["B000"] = flag(0, 1, 1)          # CF3^{Q,H1} 0 of 8 in B
    return population, sample, flags


def test_wilson_known_values():
    lo, hi = pw.wilson(6, 500)
    # Hand computation: centre 0.0157207, half-width 0.0102097 (z = 1.959964).
    assert lo == pytest.approx(0.005511, abs=1e-5)
    assert hi == pytest.approx(0.025930, abs=1e-5)
    lo, hi = pw.wilson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.27753, abs=1e-4)


def test_weighted_rate_is_stratified_estimator():
    r = pw.compute(*fixture())
    e = r["metrics"]["CF3^{Q,H1}"]
    assert e["sample_rate"] == pytest.approx(1 / 10)
    assert e["weighted_rate"] == pytest.approx(0.9 * (1 / 2) + 0.1 * (0 / 8))
    e = r["metrics"]["CF3^Q"]
    assert e["weighted_rate"] == pytest.approx(0.9 * (1 / 2) + 0.1 * (1 / 8))


def test_interval_contains_estimate_and_is_deterministic():
    strata = pw.strata_table(*fixture())
    a = pw.estimate(strata, "CF3^{Q,H1}", draws=20_000)
    b = pw.estimate(strata, "CF3^{Q,H1}", draws=20_000)
    assert a == b
    lo, hi = a["weighted_interval_95"]
    assert 0.0 <= lo < hi <= 1.0


def test_median_lies_inside_interval_and_above_plugin_for_zero_strata():
    population = {f"A{i}": ("tA", "SINGLE_BRIDGE") for i in range(100)}
    population.update({f"B{i}": ("tB", "SINGLE_BRIDGE") for i in range(100)})
    sample = [f"A{i}" for i in range(10)] + [f"B{i}" for i in range(10)]
    flags = {q: flag() for q in sample}
    flags["A0"] = flag(1, 1, 1)
    e = pw.compute(population, sample, flags)["metrics"]["CF3^{Q,H1}"]
    lo, hi = e["weighted_interval_95"]
    assert lo <= e["weighted_median"] <= hi
    assert e["weighted_rate"] == pytest.approx(0.5 * 0.1)
    assert e["weighted_median"] > e["weighted_rate"]


def test_zero_strata_widen_interval_but_not_estimate():
    population = {f"A{i}": ("tA", "SINGLE_BRIDGE") for i in range(100)}
    sample = [f"A{i}" for i in range(10)]
    flags = {q: flag() for q in sample}
    e = pw.compute(population, sample, flags)["metrics"]["CF3^{Q,H1}"]
    assert e["weighted_rate"] == 0.0
    assert e["weighted_interval_95"][1] > 0.0


def test_strata_table_counts():
    strata = pw.strata_table(*fixture())
    assert strata[("tA", "SINGLE_BRIDGE")]["N"] == 90 and strata[("tA", "SINGLE_BRIDGE")]["n"] == 2
    assert strata[("tB", "MULTI_BRIDGE")]["y"]["CF4^Q"] == 1


def test_refuses_sample_outside_population():
    population, sample, flags = fixture()
    flags["Z1"] = flag()
    with pytest.raises(ValueError, match="not in the population"):
        pw.compute(population, sample + ["Z1"], flags)


def test_refuses_unsampled_stratum():
    population, sample, flags = fixture()
    population["C1"] = ("tC", "SINGLE_BRIDGE")
    with pytest.raises(ValueError, match="no sampled query"):
        pw.compute(population, sample, flags)


def test_refuses_missing_flags():
    population, sample, flags = fixture()
    del flags["B007"]
    with pytest.raises(ValueError, match="without co-failure flags"):
        pw.compute(population, sample, flags)
