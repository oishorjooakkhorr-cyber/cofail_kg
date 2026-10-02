"""S2: write BioHopR inspection files (protocol §3.1; LEAKY_QUESTION input, §7.1).

Outputs (from the repository root):
- results/diagnostics/biohopr/inspection_20.md — 20 rows sampled with random.Random(42), listed in
  row_id order, every field shown; `answer` shown as its first 5 items plus its count.
- results/diagnostics/biohopr/hop1_in_question.csv — every row whose hop2_question_multi contains
  the hop1 field's text under at least one of three match variants (case-sensitive substring,
  case-insensitive substring, case-insensitive whole word). Descriptive only: the protocol's
  LEAKY_QUESTION flag is computed later, against resolved gold names.

Usage: python scripts/02_inspect_biohopr.py
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from pathlib import Path

from cofail_kg.data.biohopr_loader import load_biohopr

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results/diagnostics/biohopr"
SEED = 42
N_SAMPLE = 20
N_ANSWERS_SHOWN = 5
QUESTION_FIELD = "hop2_question_multi"  # candidate field for the leak count; not a protocol choice


def whole_word_ci(needle: str, haystack: str) -> bool:
    """Case-insensitive match not preceded or followed by a word character (\\w)."""
    pattern = r"(?<!\w)" + re.escape(needle.lower()) + r"(?!\w)"
    return re.search(pattern, haystack.lower()) is not None


def fmt(value) -> str:
    """Show a value as JSON in a code span so whitespace and newlines stay visible."""
    return "`" + json.dumps(value, ensure_ascii=False).replace("`", "\\`") + "`"


def write_inspection(rows: list[dict], path: Path) -> list[int]:
    idx = sorted(random.Random(SEED).sample(range(len(rows)), N_SAMPLE))
    fields = sorted(k for k in rows[0] if k not in ("row_id", "row_sha256", "answer"))
    lines = [
        "# BioHopR inspection — 20 rows",
        "",
        f"Sample: `sorted(random.Random({SEED}).sample(range({len(rows)}), {N_SAMPLE}))`. "
        f"`answer` shows the first {N_ANSWERS_SHOWN} items and the count. "
        "String values are shown JSON-escaped (\\n = newline).",
        "",
    ]
    for i in idx:
        r = rows[i]
        lines += [f"## {r['row_id']}", "", "| Field | Value |", "|---|---|"]
        lines.append(f"| row_sha256 | `{r['row_sha256']}` |")
        for k in fields:
            lines.append(f"| {k} | {fmt(r[k]).replace('|', '&#124;')} |")
        ans = r["answer"]
        lines.append(f"| answer (count) | {len(ans)} |")
        lines.append(f"| answer (first {N_ANSWERS_SHOWN}) | "
                     f"{fmt(ans[:N_ANSWERS_SHOWN]).replace('|', '&#124;')} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return idx


def write_hop1_matches(rows: list[dict], path: Path) -> dict[str, int]:
    counts = {"case_sensitive_substring": 0, "case_insensitive_substring": 0,
              "case_insensitive_whole_word": 0, "case_insensitive_whole_word_len_ge_4": 0}
    out = []
    for r in rows:
        h, q = r["hop1"], r[QUESTION_FIELD]
        cs = h in q
        ci = h.lower() in q.lower()
        ww = whole_word_ci(h, q)
        ww4 = ww and len(h) >= 4
        for key, flag in zip(counts, (cs, ci, ww, ww4)):
            counts[key] += flag
        if cs or ci or ww:
            out.append([r["row_id"], r["relation_hop2"], h, q, int(cs), int(ci), int(ww), int(ww4)])
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row_id", "relation_hop2", "hop1", QUESTION_FIELD, *counts])
        w.writerows(out)
    return counts


def main() -> int:
    rows = load_biohopr(ROOT / "data/raw/biohopr")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    idx = write_inspection(rows, OUT_DIR / "inspection_20.md")
    print(f"inspection_20.md: rows {[rows[i]['row_id'] for i in idx]}")
    counts = write_hop1_matches(rows, OUT_DIR / "hop1_in_question.csv")
    print(f"hop1 text in {QUESTION_FIELD} (of {len(rows)} rows):")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
