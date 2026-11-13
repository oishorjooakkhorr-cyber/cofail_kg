"""Phase J RP — build the `repeat8` manifest and agent-input sheet (EXPLORATORY).

Usage (from the repository root):
    python scripts/44_make_repeat8.py --combined pilot_expansion_v1

Runbook RP: build a manifest and agent-input sheet "repeat8" with the 8 flagged queries (decision log
2026-11-12 "Plan after D7", section D: "The 8 flagged queries × 4 agents = 32 episodes, original sheet,
everything identical, run ID `repeat_v1`"), and add their write-once hashes to configs/frozen_hashes.yaml.

The 8 flagged queries are the `queries` of results/combined/<id>/d7_C.json (protocol §21 candidate rule,
S30; the same 8 listed by S31). Each manifest line and each agent-input line is copied byte for byte from
the pilot or expansion file that holds the query ("original sheet"); both source files must match their
frozen SHA256 first.

Engineering conventions (documented, not protocol):
* Lines are ordered by query_id ascending (the source manifests are not merged in any other order).
* The hashes go into a new write-once key `manifests_repeat8` of configs/frozen_hashes.yaml: the existing
  `manifests` key is itself write-once (src/cofail_kg/utils/frozen_hashes.py) and cannot gain entries.
  scripts/25_run_panel.py and tests/test_leakage.py read both keys.
* Output files are write-once: an identical re-run is allowed, any difference stops the script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once as write_hash_once  # noqa: E402

NAME = "repeat8"
KEY = "manifests_repeat8"
EXPECTED = 8   # decision log 2026-11-12, section D
SOURCES = ("pilot", "expansion")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lines_by_query(data: bytes, where: str) -> dict[str, bytes]:
    """query_id -> the exact line (with its newline) of a JSONL file."""
    out = {}
    for n, line in enumerate(data.splitlines(keepends=True), 1):
        if not line.strip():
            continue
        qid = json.loads(line)["query_id"]
        if qid in out:
            raise ValueError(f"{where}: duplicate {qid} at line {n}")
        if not line.endswith(b"\n"):
            raise ValueError(f"{where}: line {n} has no newline")
        out[qid] = line
    return out


def build(query_ids: list[str], files: dict[str, dict[str, bytes]]) -> dict[str, bytes]:
    """{'manifest': bytes, 'sheet': bytes} for `query_ids`, copied from the source files in `files`.

    `files[source][kind]` holds the raw bytes of that source's manifest ('manifest') or sheet ('sheet').
    """
    if len(query_ids) != EXPECTED or len(set(query_ids)) != EXPECTED:
        raise ValueError(f"expected {EXPECTED} distinct flagged queries, got {query_ids}")
    out = {}
    for kind in ("manifest", "sheet"):
        found: dict[str, bytes] = {}
        for source in sorted(files):
            for qid, line in lines_by_query(files[source][kind], f"{source} {kind}").items():
                if qid in query_ids:
                    if qid in found:
                        raise ValueError(f"{qid} is in more than one source {kind}")
                    found[qid] = line
        missing = sorted(set(query_ids) - set(found))
        if missing:
            raise ValueError(f"{kind}: not found in {sorted(files)}: {missing}")
        out[kind] = b"".join(found[q] for q in sorted(query_ids))
    if [json.loads(x)["query_id"] for x in out["manifest"].splitlines()] != \
            [json.loads(x)["query_id"] for x in out["sheet"].splitlines()]:
        raise ValueError("manifest and sheet list different queries")
    return out


def write_bytes_once(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"{path} exists with different content; not overwritten")
        return
    with path.open("xb") as h:
        h.write(data)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True)
    args = ap.parse_args(argv)
    frozen_path = ROOT / "configs/frozen_hashes.yaml"
    frozen = read_frozen_hashes(frozen_path)["manifests"]
    files = {}
    for source in SOURCES:
        files[source] = {}
        for kind, rel in (("manifest", f"data/processed/manifests/{source}.jsonl"),
                          ("sheet", f"data/agent_inputs/{source}.jsonl")):
            data = (ROOT / rel).read_bytes()
            if sha256_bytes(data) != frozen[rel]:
                raise ValueError(f"{rel}: SHA256 differs from configs/frozen_hashes.yaml (protocol §3.4)")
            files[source][kind] = data
    d7 = json.loads((ROOT / "results/combined" / args.combined / "d7_C.json").read_text(encoding="utf-8"))
    query_ids = sorted(q["query_id"] for q in d7["queries"])
    if d7["flagged_queries"] != len(query_ids):
        raise ValueError(f"d7_C.json lists {len(query_ids)} queries but flagged_queries = {d7['flagged_queries']}")
    out = build(query_ids, files)
    targets = {"manifest": f"data/processed/manifests/{NAME}.jsonl", "sheet": f"data/agent_inputs/{NAME}.jsonl"}
    for kind, rel in targets.items():
        write_bytes_once(ROOT / rel, out[kind])
    hashes = {rel: sha256_bytes(out[kind]) for kind, rel in sorted(targets.items(), key=lambda kv: kv[1])}
    written = write_hash_once(frozen_path, KEY, hashes)
    print(json.dumps({"queries": query_ids, "hashes": hashes, "frozen_key": KEY, "written": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
