"""S2: download the pinned BioHopR revision to data/raw/biohopr/ (protocol §3.1, §3.4).

- Downloads BioHopR.json and the dataset card README.md at the pinned revision.
- Verifies BioHopR.json against the SHA256 the Hub reports for its LFS object.
- Never overwrites: if a target file already exists, its SHA256 must match the download, otherwise
  the script stops. A rerun with everything in place changes nothing.
- Writes data/raw/biohopr/metadata.json once (repo, revision, download time, row count, file SHA256).
- Writes `biohopr_revision` to configs/frozen_hashes.yaml if absent; refuses a different value.

Usage (from the repository root):
    python scripts/02_download_biohopr.py [--revision <commit hash>]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import huggingface_hub
from huggingface_hub import HfApi, hf_hub_download

from cofail_kg.data.biohopr_loader import DATA_FILENAME, METADATA_FILENAME, file_sha256
from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once

ROOT = Path(__file__).resolve().parents[1]
REPO_ID = "knowlab-research/BioHopR"
PINNED_REVISION = "08f06692c3900347e7405ba55ff6a6d330f55ddb"
FILES = (DATA_FILENAME, "README.md")
FROZEN_KEY = "biohopr_revision"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--revision", default=PINNED_REVISION)
    ap.add_argument("--out", type=Path, default=ROOT / "data/raw/biohopr")
    ap.add_argument("--frozen-hashes", type=Path, default=ROOT / "configs/frozen_hashes.yaml")
    args = ap.parse_args()

    frozen = read_frozen_hashes(args.frozen_hashes).get(FROZEN_KEY)
    if frozen is not None and frozen != args.revision:
        print(f"ERROR: {args.frozen_hashes} freezes {FROZEN_KEY}={frozen}; "
              f"requested revision {args.revision}", file=sys.stderr)
        return 1

    info = HfApi().dataset_info(REPO_ID, revision=args.revision, files_metadata=True)
    if info.sha != args.revision:
        print(f"ERROR: Hub resolved revision to {info.sha}, expected {args.revision}", file=sys.stderr)
        return 1
    lfs_sha = {s.rfilename: s.lfs.sha256 for s in info.siblings if s.lfs is not None}

    args.out.mkdir(parents=True, exist_ok=True)
    file_meta = {}
    for name in FILES:
        cached = Path(hf_hub_download(REPO_ID, name, repo_type="dataset", revision=args.revision))
        sha = file_sha256(cached)
        if name in lfs_sha and sha != lfs_sha[name]:
            print(f"ERROR: {name}: downloaded sha256 {sha} != Hub LFS sha256 {lfs_sha[name]}",
                  file=sys.stderr)
            return 1
        target = args.out / name
        if target.exists():
            existing = file_sha256(target)
            if existing != sha:
                print(f"ERROR: {target} exists with sha256 {existing}, download has {sha}; "
                      "refusing to overwrite data/raw", file=sys.stderr)
                return 1
            print(f"{target}: already present, sha256 matches")
        else:
            shutil.copyfile(cached, target)
            print(f"{target}: written")
        file_meta[name] = {"sha256": sha, "size_bytes": target.stat().st_size}

    with open(args.out / DATA_FILENAME, encoding="utf-8") as f:
        row_count = len(json.load(f))

    meta_path = args.out / METADATA_FILENAME
    if meta_path.exists():
        old = json.loads(meta_path.read_text(encoding="utf-8"))
        same = (old.get("repo") == REPO_ID and old.get("revision") == args.revision
                and old.get("row_count") == row_count and old.get("files") == file_meta)
        if not same:
            print(f"ERROR: {meta_path} exists and disagrees with this download; "
                  "refusing to overwrite", file=sys.stderr)
            return 1
        print(f"{meta_path}: already present and consistent")
    else:
        meta = {
            "repo": REPO_ID,
            "repo_type": "dataset",
            "revision": args.revision,
            "download_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "row_count": row_count,
            "files": file_meta,
            "huggingface_hub_version": huggingface_hub.__version__,
        }
        meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{meta_path}: written")

    wrote = write_once(args.frozen_hashes, FROZEN_KEY, args.revision)
    print(f"{args.frozen_hashes}: {FROZEN_KEY} {'written' if wrote else 'already frozen (same value)'}")
    print(f"revision={args.revision} row_count={row_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
