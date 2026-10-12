"""PrimeKG ingestion and inspection (protocol §3.2–§3.4, runbook S4).

Raw rows and node text are preserved. Cache metadata is deterministic and write-once;
the optional frozen_hashes argument is used only after the researcher confirms S4.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once

NODE_FIELDS = ["index", "id", "type", "name", "source"]
NODE_COLUMNS = [f"node_{field}" for field in NODE_FIELDS]
EDGE_COLUMNS = ["x_index", "y_index", "relation", "display_relation"]
CACHE_FILES = ("primekg_nodes.parquet", "primekg_edges.parquet")
METADATA_FILE = "primekg_metadata.json"


def file_hash(path: Path, algorithm: str = "sha256") -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def load_cache_metadata(cache_dir: Path | str) -> dict:
    """Verify cached bytes against the machine-written metadata (§3.4)."""
    cache_dir = Path(cache_dir)
    metadata = json.loads((cache_dir / METADATA_FILE).read_text(encoding="utf-8"))
    if metadata["schema_version"] != 1:
        raise ValueError("Unsupported PrimeKG cache schema")
    for name in CACHE_FILES:
        if file_hash(cache_dir / name) != metadata["cache_sha256"][name]:
            raise ValueError(f"PrimeKG cache checksum mismatch: {name}")
    return metadata


def _indices(values: pd.Series) -> pd.Series:
    if not values.str.fullmatch(r"0|[1-9][0-9]*").all():
        raise ValueError(f"Invalid canonical node index in {values.name}")
    return values.astype("int64")


def _reverse_sample(edges: pd.DataFrame, node_ids: np.ndarray) -> dict:
    """Sample stored rows; reverse identity uses relation, never display label (§0.4)."""
    codes, labels = pd.factorize(edges.relation, sort=True)
    size = max(len(node_ids), 1)
    if len(labels) * size * size > np.iinfo(np.int64).max:
        raise ValueError("Graph exceeds the supported 64-bit reverse-inspection key size")
    x = np.searchsorted(node_ids, edges.x_index)
    y = np.searchsorted(node_ids, edges.y_index)
    positions = np.array(
        sorted(random.Random(42).sample(range(len(edges)), min(10000, len(edges)))),
        dtype=np.int64,
    )
    keys = (codes * size + x) * size + y
    reversed_keys = (codes[positions] * size + y[positions]) * size + x[positions]
    keys.sort()
    locations = np.searchsorted(keys, reversed_keys)
    matches = locations < len(keys)
    matches[matches] = keys[locations[matches]] == reversed_keys[matches]
    return {
        "seed": 42, "method": "random.Random.sample without replacement",
        "size": len(positions), "matches": int(matches.sum()),
        "per_label": {
            label: {"size": int((codes[positions] == code).sum()),
                    "matches": int(matches[codes[positions] == code].sum())}
            for code, label in enumerate(labels)
        },
    }


def prepare_primekg(raw_dir: Path | str, cache_dir: Path | str, *,
                    chunk_size: int = 250000, frozen_hashes: Path | str | None = None) -> dict:
    """Build the S4 cache; refuse changed inputs, conflicting nodes, or overwrites.

    Uses the distributed nodes.csv, including isolated nodes. Every raw file is hashed,
    but only kg.csv and nodes.csv are parsed. Timing is excluded from the fingerprint.
    """
    raw_dir, cache_dir = Path(raw_dir), Path(cache_dir)
    for name in ("kg.csv", "nodes.csv"):
        if not (raw_dir / name).is_file():
            raise FileNotFoundError(raw_dir / name)
    raw_files = {
        path.relative_to(raw_dir).as_posix(): {
            "bytes": path.stat().st_size, "sha256": file_hash(path), "md5": file_hash(path, "md5")
        }
        for path in sorted(raw_dir.rglob("*")) if path.is_file()
    }
    metadata_path = cache_dir / METADATA_FILE
    if metadata_path.exists():
        metadata = load_cache_metadata(cache_dir)
        if metadata["raw_files"] != raw_files:
            raise ValueError("PrimeKG raw inputs differ from the existing cache; refusing replacement")
        if frozen_hashes is not None:
            write_once(frozen_hashes, "kg_fingerprint", file_hash(metadata_path))
        return metadata
    cache_dir.mkdir(parents=True, exist_ok=True)
    for name in CACHE_FILES:
        if (cache_dir / name).exists():
            raise FileExistsError(f"Unfinished or unrelated cache file; inspect before recovery: {cache_dir / name}")

    nodes = pd.read_csv(raw_dir / "nodes.csv", dtype=str, keep_default_na=False)
    if not set(NODE_COLUMNS).issubset(nodes.columns):
        raise ValueError(f"nodes.csv must contain {NODE_COLUMNS}")
    node_columns = list(nodes.columns)
    nodes = nodes[NODE_COLUMNS].copy()
    nodes.node_index = _indices(nodes.node_index)
    if nodes.node_index.duplicated().any():
        raise ValueError("Duplicate canonical node index in nodes.csv")
    nodes = nodes.sort_values("node_index").reset_index(drop=True)
    reference = nodes.set_index("node_index")
    counts: Counter = Counter()
    row_count = 0
    columns, examples = [], []
    schema = pa.schema([(name, pa.int64() if name.endswith("_index") else pa.string()) for name in EDGE_COLUMNS])
    with TemporaryDirectory(prefix=".primekg-", dir=cache_dir) as temporary:
        staging = Path(temporary)
        nodes.to_parquet(staging / CACHE_FILES[0], index=False)
        with pq.ParquetWriter(staging / CACHE_FILES[1], schema, compression="snappy") as writer:
            for chunk in pd.read_csv(raw_dir / "kg.csv", dtype=str, keep_default_na=False, chunksize=chunk_size):
                required = {f"{side}_{field}" for side in ("x", "y") for field in NODE_FIELDS} | {"relation", "display_relation"}
                if not required.issubset(chunk.columns):
                    raise ValueError(f"kg.csv is missing columns: {sorted(required - set(chunk.columns))}")
                columns = list(chunk.columns)
                examples.extend(chunk.head(max(0, 5 - len(examples))).to_dict("records"))
                for side in ("x", "y"):
                    chunk[f"{side}_index"] = _indices(chunk[f"{side}_index"])
                    observed = chunk[[f"{side}_{field}" for field in NODE_FIELDS]].drop_duplicates()
                    observed.columns = NODE_COLUMNS
                    observed = observed.set_index("node_index")
                    missing = observed.index.difference(reference.index)
                    if len(missing):
                        raise ValueError(f"Edge endpoint missing from nodes.csv: {missing[0]}")
                    different = (observed != reference.loc[observed.index]).any(axis=1)
                    if different.any():
                        raise ValueError(f"Conflicting node metadata at canonical index {observed.index[different][0]}")
                counts.update(chunk.groupby(["relation", "display_relation", "x_type", "y_type"]).size().to_dict())
                writer.write_table(pa.Table.from_pandas(chunk[EDGE_COLUMNS], schema=schema, preserve_index=False))
                row_count += len(chunk)
        edges = pd.read_parquet(staging / CACHE_FILES[1], columns=["x_index", "y_index", "relation"])
        incident = np.union1d(edges.x_index.to_numpy(), edges.y_index.to_numpy())
        metadata = {
            "schema_version": 1, "raw_files": raw_files, "columns": columns,
            "node_columns": node_columns, "examples": examples,
            "row_count": row_count, "node_count": len(nodes),
            "isolated_node_count": len(nodes) - len(incident),
            "canonical_id_columns": ["x_index", "y_index", "node_index"],
            "node_type_counts": nodes.groupby("node_type").size().to_dict(),
            "edge_convention": "either",
            "reverse_sample": _reverse_sample(edges, nodes.node_index.to_numpy()),
            "relation_counts": [
                dict(zip(["relation", "display_relation", "source_type", "target_type"], key), rows=int(count))
                for key, count in sorted(counts.items())
            ],
            "cache_sha256": {name: file_hash(staging / name) for name in CACHE_FILES},
        }
        payload = (json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        fingerprint = hashlib.sha256(payload).hexdigest()
        if frozen_hashes is not None:
            previous = read_frozen_hashes(frozen_hashes).get("kg_fingerprint")
            if previous is not None and previous != fingerprint:
                raise ValueError("Computed cache conflicts with the frozen kg_fingerprint")
        for name in CACHE_FILES:
            (staging / name).rename(cache_dir / name)
        with metadata_path.open("xb") as stream:
            stream.write(payload)
    if frozen_hashes is not None:
        write_once(frozen_hashes, "kg_fingerprint", fingerprint)
    return metadata
