import copy
import hashlib
import json
import re
from pathlib import Path

import pytest

from cofail_kg.data.biohopr_loader import (
    BioHopRLoadError,
    add_row_ids,
    load_biohopr,
    make_row_id,
    record_sha256,
)

REAL_DIR = Path(__file__).resolve().parents[1] / "data/raw/biohopr"


def _rec(i):
    return {
        "relation_hop2": "drug:gene/protein:disease",
        "hop1": f"G{i}",
        "hop2": f"Drug {i}",
        "answer": [f"disease {i}a", f"disease {i}b"],
        "hop2_question_multi": f"Name all diseases ... drug Drug {i}.",
        "prompt": "Q\nAnswer:\n",
        "unicode": "α-β",
    }


def _write_fixture(tmp_path, records, row_count=None):
    data = json.dumps(records, ensure_ascii=False).encode("utf-8")
    (tmp_path / "BioHopR.json").write_bytes(data)
    meta = {
        "repo": "test/fixture",
        "revision": "0" * 40,
        "row_count": len(records) if row_count is None else row_count,
        "files": {"BioHopR.json": {"sha256": hashlib.sha256(data).hexdigest(),
                                   "size_bytes": len(data)}},
    }
    (tmp_path / "metadata.json").write_text(json.dumps(meta), encoding="utf-8")
    return tmp_path


@pytest.fixture
def fixture_dir(tmp_path):
    return _write_fixture(tmp_path, [_rec(i) for i in range(4)])


def test_row_count_equals_metadata(fixture_dir):
    meta = json.loads((fixture_dir / "metadata.json").read_text())
    assert len(load_biohopr(fixture_dir)) == meta["row_count"]


def test_row_count_mismatch_raises(tmp_path):
    d = _write_fixture(tmp_path, [_rec(i) for i in range(4)], row_count=5)
    with pytest.raises(BioHopRLoadError, match="row_count"):
        load_biohopr(d)


def test_row_id_unique_padded_sequential(fixture_dir):
    rows = load_biohopr(fixture_dir)
    ids = [r["row_id"] for r in rows]
    assert ids == ["BH2_00000", "BH2_00001", "BH2_00002", "BH2_00003"]
    assert len(set(ids)) == len(ids)
    assert all(re.fullmatch(r"BH2_\d{5}", i) for i in ids)


def test_make_row_id_bounds():
    assert make_row_id(7632) == "BH2_07632"
    with pytest.raises(ValueError):
        make_row_id(100000)
    with pytest.raises(ValueError):
        make_row_id(-1)


def test_original_fields_unchanged(fixture_dir):
    originals = [_rec(i) for i in range(4)]
    rows = load_biohopr(fixture_dir)
    for orig, row in zip(originals, rows):
        stripped = {k: v for k, v in row.items() if k not in ("row_id", "row_sha256")}
        assert stripped == orig
        assert set(row) == set(orig) | {"row_id", "row_sha256"}


def test_add_row_ids_does_not_mutate_input():
    recs = [_rec(i) for i in range(3)]
    before = copy.deepcopy(recs)
    add_row_ids(recs)
    assert recs == before


def test_row_sha256_definition(fixture_dir):
    rows = load_biohopr(fixture_dir)
    orig = _rec(0)
    expected = hashlib.sha256(
        json.dumps(orig, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert rows[0]["row_sha256"] == expected == record_sha256(orig)
    # Independent of key order in the source record.
    assert record_sha256(dict(reversed(list(orig.items())))) == expected


def test_rerun_identical(fixture_dir):
    a = load_biohopr(fixture_dir)
    b = load_biohopr(fixture_dir)
    assert [(r["row_id"], r["row_sha256"]) for r in a] == [(r["row_id"], r["row_sha256"]) for r in b]


def test_file_sha_mismatch_raises(fixture_dir):
    p = fixture_dir / "BioHopR.json"
    p.write_bytes(p.read_bytes() + b" ")
    with pytest.raises(BioHopRLoadError, match="sha256"):
        load_biohopr(fixture_dir)


def test_inconsistent_field_set_raises(tmp_path):
    recs = [_rec(i) for i in range(3)]
    del recs[1]["hop1"]
    d = _write_fixture(tmp_path, recs)
    with pytest.raises(BioHopRLoadError, match="record 1"):
        load_biohopr(d)


def test_added_field_clash_raises(tmp_path):
    recs = [dict(_rec(i), row_id="x") for i in range(2)]
    d = _write_fixture(tmp_path, recs)
    with pytest.raises(BioHopRLoadError, match="added field"):
        load_biohopr(d)


def test_duplicate_json_keys_raise(tmp_path):
    data = b'[{"a": 1, "a": 2}]'
    (tmp_path / "BioHopR.json").write_bytes(data)
    meta = {"row_count": 1, "files": {"BioHopR.json": {"sha256": hashlib.sha256(data).hexdigest()}}}
    (tmp_path / "metadata.json").write_text(json.dumps(meta))
    with pytest.raises(BioHopRLoadError, match="duplicate"):
        load_biohopr(tmp_path)


@pytest.mark.skipif(not (REAL_DIR / "metadata.json").exists(),
                    reason="real BioHopR not downloaded (scripts/02_download_biohopr.py)")
def test_real_file_count_and_rerun():
    meta = json.loads((REAL_DIR / "metadata.json").read_text(encoding="utf-8"))
    a = load_biohopr(REAL_DIR)
    b = load_biohopr(REAL_DIR)
    assert len(a) == meta["row_count"]
    ids = [r["row_id"] for r in a]
    assert len(set(ids)) == len(ids)
    assert all(re.fullmatch(r"BH2_\d{5}", i) for i in ids)
    assert [(r["row_id"], r["row_sha256"]) for r in a] == [(r["row_id"], r["row_sha256"]) for r in b]
    raw = json.loads((REAL_DIR / "BioHopR.json").read_text(encoding="utf-8"))
    for orig, row in zip(raw, a):
        assert {k: v for k, v in row.items() if k not in ("row_id", "row_sha256")} == orig
