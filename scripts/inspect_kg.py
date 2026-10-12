"""Researcher-only S4 inspection CLI; not an experimental-agent tool (§10)."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from cofail_kg.kg.primekg_index import PrimeKGIndex

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data/cache")
    commands = parser.add_subparsers(dest="command", required=True)
    node = commands.add_parser("node", help="Find all normalized exact-name matches")
    node.add_argument("name")
    node.add_argument("--node-type")
    relations = commands.add_parser("relations", help="List relation labels and unique counts")
    relations.add_argument("node_id")
    neighbors = commands.add_parser("neighbors", help="List all unique neighbours in numeric ID order")
    neighbors.add_argument("node_id")
    neighbors.add_argument("--relation")
    neighbors.add_argument("--neighbor-type")
    args = parser.parse_args()
    started = time.perf_counter()
    index = PrimeKGIndex(args.cache_dir)
    print(f"Loaded and verified index in {time.perf_counter() - started:.3f}s", file=sys.stderr)
    try:
        if args.command == "node":
            result = index.find_by_name(args.name, args.node_type)
        elif args.command == "relations":
            result = index.relations_of(args.node_id)
        else:
            found = index.neighbors(args.node_id, args.relation, args.neighbor_type)
            result = {"count": len(found), "neighbors": found}
    except KeyError as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
