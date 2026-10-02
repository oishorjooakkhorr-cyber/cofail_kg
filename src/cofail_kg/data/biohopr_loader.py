"""BioHopR loader (protocol §0.4, §3.1).

Loads the pinned BioHopR file downloaded by `scripts/02_download_biohopr.py` and returns its 2-hop
records with every original field unchanged, plus two added fields:

- `row_id` — "BH2_" + the record's 0-based position among the 2-hop records, zero-padded to 5
  digits (protocol §0.4).
- `row_sha256` — SHA256 of the original record (without the added fields) serialised as JSON with
  sorted keys (see `record_sha256` for the exact serialisation).

Which records are 2-hop records (S2 finding, revision 08f06692…): BioHopR stores the 1-hop and the
2-hop question in the same record (`hop1_question*` and `hop2_question*` fields); there are no
separate 1-hop records. Every record carries a 2-hop relation triple (`relation_hop2`). Every record
is therefore a 2-hop record, and its position among the 2-hop records is its position in the file.
The loader checks that every record has the same field set and refuses the file otherwise; it never
drops records.

Field roles (query entity, bridge) are not interpreted here (S5).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_RAW_DIR = Path("data/raw/biohopr")
DATA_FILENAME = "BioHopR.json"
METADATA_FILENAME = "metadata.json"
ROW_ID_PREFIX = "BH2_"
ROW_ID_WIDTH = 5
ADDED_FIELDS = ("row_id", "row_sha256")


class BioHopRLoadError(RuntimeError):
    """Raised when the raw file or its metadata fails a check."""


def file_sha256(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_row_id(position: int) -> str:
    """Protocol §0.4: "BH2_" + 0-based position among 2-hop records, zero-padded to 5 digits."""
    if position < 0 or position >= 10**ROW_ID_WIDTH:
        raise ValueError(f"position {position} does not fit a {ROW_ID_WIDTH}-digit row_id")
    return f"{ROW_ID_PREFIX}{position:0{ROW_ID_WIDTH}d}"


def record_sha256(record: dict[str, Any]) -> str:
    """SHA256 of the record's JSON with sorted keys.

    Serialisation: `json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`,
    encoded as UTF-8.
    """
    text = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [k for k, _ in pairs]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    if dups:
        raise BioHopRLoadError(f"duplicate JSON keys in a record: {dups}")
    return dict(pairs)


def read_metadata(raw_dir: Path | str = DEFAULT_RAW_DIR) -> dict[str, Any]:
    path = Path(raw_dir) / METADATA_FILENAME
    if not path.exists():
        raise BioHopRLoadError(f"{path} not found; run scripts/02_download_biohopr.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw_records(raw_dir: Path | str = DEFAULT_RAW_DIR) -> list[dict[str, Any]]:
    """Read the raw BioHopR JSON array after verifying its SHA256 against metadata.json."""
    raw_dir = Path(raw_dir)
    meta = read_metadata(raw_dir)
    data_path = raw_dir / DATA_FILENAME
    expected = meta.get("files", {}).get(DATA_FILENAME, {}).get("sha256")
    if expected is None:
        raise BioHopRLoadError(f"{raw_dir / METADATA_FILENAME}: no sha256 recorded for {DATA_FILENAME}")
    actual = file_sha256(data_path)
    if actual != expected:
        raise BioHopRLoadError(
            f"{data_path}: sha256 {actual} does not match metadata {expected}"
        )
    with open(data_path, encoding="utf-8") as f:
        records = json.load(f, object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(records, list):
        raise BioHopRLoadError(f"{data_path}: expected a JSON array, got {type(records).__name__}")
    return records


def add_row_ids(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return new dicts: each original record's fields unchanged, plus row_id and row_sha256.

    All records must be objects with an identical field set and must not already contain an added
    field name; otherwise BioHopRLoadError is raised (no record is dropped).
    """
    if not records:
        raise BioHopRLoadError("no records")
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise BioHopRLoadError(f"record {i}: expected an object, got {type(rec).__name__}")
    fields = set(records[0])
    for i, rec in enumerate(records):
        if set(rec) != fields:
            raise BioHopRLoadError(
                f"record {i}: field set differs from record 0 "
                f"(missing {sorted(fields - set(rec))}, extra {sorted(set(rec) - fields)})"
            )
    clash = sorted(fields & set(ADDED_FIELDS))
    if clash:
        raise BioHopRLoadError(f"records already contain added field names: {clash}")

    out = []
    for i, rec in enumerate(records):
        row = dict(rec)
        row["row_id"] = make_row_id(i)
        row["row_sha256"] = record_sha256(rec)
        out.append(row)
    return out


def load_biohopr(raw_dir: Path | str = DEFAULT_RAW_DIR) -> list[dict[str, Any]]:
    """Load the pinned BioHopR 2-hop rows (protocol §0.4, §3.1), in file order.

    Checks that the number of rows equals metadata.json's `row_count`.
    """
    raw_dir = Path(raw_dir)
    meta = read_metadata(raw_dir)
    rows = add_row_ids(load_raw_records(raw_dir))
    if len(rows) != meta.get("row_count"):
        raise BioHopRLoadError(
            f"loaded {len(rows)} rows but metadata row_count is {meta.get('row_count')}"
        )
    return rows
