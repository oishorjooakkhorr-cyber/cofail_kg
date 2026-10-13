import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "investigation", Path(__file__).resolve().parents[1] / "scripts/06_investigate_remaining.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize("gold,bridge,union,expected", [
    ({1}, {1}, {1}, "BOTH"),
    ({1}, {1}, {1, 2}, "BRIDGE_ONLY"),
    ({1, 2}, {1}, {1, 2}, "UNION_ONLY"),
    ({1, 3}, {1}, {1, 2}, "NEITHER"),
])
def test_mixture_categories_require_exact_sets(gold, bridge, union, expected):
    assert module.category(gold, bridge, union) == expected


def test_difference_does_not_count_extras_as_missing():
    assert module.difference({"1", "2"}, {"2", "3"}) == {
        "reached": ["2", "3"], "extra": ["3"], "missing": ["1"], "exact": False}
