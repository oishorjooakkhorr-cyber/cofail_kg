"""EXPLORATORY (researcher request, 2026-11-07): Cogito-14B with a q8_0 KV cache on the 4 smoke queries.

Question: does storing the KV cache as q8_0 instead of the frozen f16 let all 49/49 Cogito layers fit on
the GPU, and does that remove the long-context 240 s request timeouts seen in S22 and smoke_panel?

This is NOT a frozen runtime revision and changes no frozen file. It reuses scripts/25_run_panel.py
unchanged and overrides, in memory only, two of Cogito's runtime settings from configs/pilot.yaml:
    kv_cache_type: f16   -> q8_0
    gpu_layers:   47/49  -> 49/49   (the existing guard then requires size_vram == size)
Everything else (model digest, num_ctx 32768, num_predict 8192, 240 s timeout, seed, temperature,
prompt, tools, smoke manifest) is the frozen value. The pinned run config records kv_cache_type q8_0.
If the guard finds a different layer split or cache type, the run stops before any episode.

Usage:  python scripts/25_explore_cogito_kvq8.py
Output: results/runs/explore-cogito-kvq8-20261107/ (Cogito only, 4 episodes; no panel analysis).
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "explore-cogito-kvq8-20261107"
OVERRIDE = {"kv_cache_type": "q8_0", "gpu_layers": ["49/49"]}

spec = importlib.util.spec_from_file_location("panel_driver", ROOT / "scripts/25_run_panel.py")
PANEL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PANEL)

_frozen_load_panel = PANEL.S22.load_panel


def cogito_only(root=ROOT):
    """The frozen panel loader, then Cogito-14B alone with the exploratory KV override."""
    rows = [(row, {**settings, **OVERRIDE}) for row, settings in _frozen_load_panel(root)
            if row["agent_id"] == "Cogito-14B"]
    if len(rows) != 1:
        raise ValueError("Cogito-14B not found in the frozen panel")
    return rows


def main():
    PANEL.S22.load_panel = cogito_only
    PANEL.run("smoke", RUN_ID)


if __name__ == "__main__":
    main()
