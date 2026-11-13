"""Tests for scripts/44_make_repeat8.py (Phase J RP manifest builder) on tiny synthetic files."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("repeat8", ROOT / "scripts/44_make_repeat8.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def jsonl(rows):
    return b"".join(json.dumps(r, separators=(",", ":")).encode() + b"\n" for r in rows)


def files(pilot_ids, expansion_ids):
    def m(ids):
        return {"manifest": jsonl({"query_id": q, "relation_type": "t", "x": i} for i, q in enumerate(ids)),
                "sheet": jsonl({"query_id": q, "question_text": f"Q {q}"} for q in ids)}
    return {"pilot": m(pilot_ids), "expansion": m(expansion_ids)}


EIGHT = [f"Q{i}" for i in range(8)]


def test_lines_are_copied_byte_for_byte_and_sorted():
    src = files(["Q7", "P1", "Q2"], ["Q5", "Q0", "E1", "Q1", "Q3", "Q4", "Q6"])
    out = M.build(EIGHT, src)
    ids = [json.loads(x)["query_id"] for x in out["sheet"].splitlines()]
    assert ids == EIGHT
    originals = {json.loads(x)["query_id"]: x for s in src.values() for x in s["manifest"].splitlines(keepends=True)}
    assert out["manifest"] == b"".join(originals[q] for q in EIGHT)


def test_missing_duplicate_or_wrong_count_stops():
    with pytest.raises(ValueError, match="not found"):
        M.build(EIGHT, files(EIGHT[:7], []))
    with pytest.raises(ValueError, match="more than one source"):
        M.build(EIGHT, files(EIGHT, ["Q3"]))
    with pytest.raises(ValueError, match="expected 8"):
        M.build(EIGHT[:7], files(EIGHT, []))


def test_line_without_newline_stops():
    src = files(EIGHT, [])
    src["pilot"]["sheet"] = src["pilot"]["sheet"].rstrip(b"\n")
    with pytest.raises(ValueError, match="no newline"):
        M.build(EIGHT, src)


def test_write_bytes_once(tmp_path):
    p = tmp_path / "x.jsonl"
    M.write_bytes_once(p, b"a\n")
    M.write_bytes_once(p, b"a\n")
    with pytest.raises(FileExistsError):
        M.write_bytes_once(p, b"b\n")
