"""S4 cache preparation (protocol §3.2–§3.4).

Run without --freeze while S4 confirmations are pending. After confirmation,
--freeze records the metadata SHA256 through the existing write-once hash store.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from cofail_kg.kg.prepare import METADATA_FILE, file_hash, prepare_primekg

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/primekg")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data/cache")
    parser.add_argument("--freeze", action="store_true", help="Record kg_fingerprint after S4 confirmation")
    args = parser.parse_args()
    started = time.perf_counter()
    metadata = prepare_primekg(
        args.raw_dir, args.cache_dir,
        frozen_hashes=ROOT / "configs/frozen_hashes.yaml" if args.freeze else None,
    )
    print(json.dumps({
        "rows": metadata["row_count"], "nodes": metadata["node_count"],
        "reverse_sample": metadata["reverse_sample"],
        "metadata_sha256": file_hash(args.cache_dir / METADATA_FILE),
        "freeze_requested": args.freeze, "elapsed_seconds": time.perf_counter() - started,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
