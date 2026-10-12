import json
import subprocess
import sys
from pathlib import Path

from cofail_kg.kg.prepare import prepare_primekg
from test_primekg_prepare import raw_graph

ROOT = Path(__file__).resolve().parents[1]


def test_inspection_cli_on_synthetic_cache(raw_graph, tmp_path):
    cache = tmp_path / "cache"
    prepare_primekg(raw_graph, cache)
    command = [sys.executable, str(ROOT / "scripts/inspect_kg.py"), "--cache-dir", str(cache)]
    result = subprocess.run(command + ["node", "alpha"], capture_output=True, text=True, check=True)
    assert [node["id"] for node in json.loads(result.stdout)] == ["10", "99"]
    result = subprocess.run(command + ["neighbors", "10", "--relation", "drug_effect"],
                            capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)["count"] == 1
    assert json.loads(result.stdout)["neighbors"][0]["id"] == "40"
    result = subprocess.run(command + ["relations", "missing"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Unknown node ID" in result.stderr


def test_prepare_cli_keeps_freeze_opt_in(raw_graph, tmp_path):
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/04_prepare_primekg.py"),
        "--raw-dir", str(raw_graph), "--cache-dir", str(tmp_path / "cache"),
    ], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)["freeze_requested"] is False
    assert json.loads(result.stdout)["rows"] == 7
