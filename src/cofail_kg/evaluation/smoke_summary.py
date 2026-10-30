"""S22 single-agent smoke summary: descriptive per-model tallies of S16–S19 outputs, no interpretation.

Counts come from saved episode records (§19) and their `agent_metrics` rows (§14–§16). The only
check is the runbook S22 assertion that no answer is both OFF_QUESTION and SUPPORTED.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


class OffQuestionSupported(AssertionError):
    """An answer is labelled both OFF_QUESTION (Label A) and SUPPORTED (Label B)."""


def off_question_supported(metrics: Iterable[dict[str, Any]]) -> list[tuple[str, str, str]]:
    """(agent_id, query_id, node_id) for every answer labelled OFF_QUESTION and SUPPORTED."""
    return [(m["agent_id"], m["query_id"], str(a["node_id"])) for m in metrics for a in m["answers"]
            if a["label_a"] == "OFF_QUESTION" and a["label_b"] == "SUPPORTED"]


def _sum(rows: Iterable[dict[str, int]]) -> dict[str, int]:
    total: Counter = Counter()
    for row in rows:
        if row is None:  # Episodes without scored answers (e.g. PARSE_FAIL) have no label counts.
            continue
        total.update({k: v for k, v in row.items() if v})
    return dict(sorted(total.items()))


def model_summary(records: list[dict[str, Any]], metrics: list[dict[str, Any]], num_ctx: int) -> dict[str, Any]:
    """Per-model tallies; records and metrics are paired by position and must share query IDs."""
    if [r["query_id"] for r in records] != [m["query_id"] for m in metrics]:
        raise ValueError("Records and metrics are not paired by query")
    n = len(records)
    prompts = [(r["query_id"], max((x for x in r["token_counts"]["prompt"] if x is not None), default=None))
               for r in records]
    largest = max((p for _, p in prompts if p is not None), default=None)
    over90 = sorted(q for q, p in prompts if p is not None and p > 0.9 * num_ctx)
    errors = Counter(r["cause"] for r in records if r["status"] == "ERROR")
    return {
        "episodes": n,
        "status_counts": dict(sorted(Counter(r["status"] for r in records).items())),
        "error_causes": dict(sorted(errors.items())),
        "out_of_memory_episodes": errors.get("OUT_OF_MEMORY", 0),
        "label_a": _sum(m["label_a_counts"] for m in metrics),
        "label_b": _sum(m["label_b_counts"] for m in metrics),
        "reason_codes": _sum(m["reason_counts"] for m in metrics),
        "primary_reason_codes": _sum(m["primary_reason_counts"] for m in metrics),
        "hop1_status": dict(sorted(Counter(m["hop1_status"] for m in metrics).items())),
        "early_stop_share": sum(bool(m["early_stop"]) for m in metrics) / n if n else None,
        "budget_hit_share": sum(bool(m["budget_exhausted"]) for m in metrics) / n if n else None,
        "largest_prompt_tokens": largest,
        "num_ctx": num_ctx,
        "largest_prompt_share_of_num_ctx": largest / num_ctx if largest is not None else None,
        "episodes_prompt_over_90pct_num_ctx": over90,
    }


def _counts(value: dict[str, int]) -> str:
    return ", ".join(f"{k} {v}" for k, v in value.items()) or "none"


def render_markdown(run_id: str, summaries: dict[str, dict[str, Any]],
                    violations: list[tuple[str, str, str]]) -> str:
    lines = [f"# S22 single-agent smoke summary — run `{run_id}`", "",
             "Descriptive tallies of S16–S19 evaluation over all saved episodes. No interpretation.", "",
             "## Overview", "",
             "|Agent|Episodes|Status counts|ERROR causes|Early-stop share|Budget-hit share|"
             "Largest prompt / num_ctx|Episodes > 90% num_ctx|",
             "|---|---:|---|---|---:|---:|---|---|"]
    for agent, s in summaries.items():
        share = "n/a" if s["largest_prompt_tokens"] is None else (
            f"{s['largest_prompt_tokens']} / {s['num_ctx']} ({s['largest_prompt_share_of_num_ctx']:.1%})")
        lines.append(f"|{agent}|{s['episodes']}|{_counts(s['status_counts'])}|{_counts(s['error_causes'])}|"
                     f"{s['early_stop_share']:.2f}|{s['budget_hit_share']:.2f}|{share}|"
                     f"{', '.join(s['episodes_prompt_over_90pct_num_ctx']) or 'none'}|")
    for agent, s in summaries.items():
        lines += ["", f"## {agent}", "",
                  f"- Label A: {_counts(s['label_a'])}",
                  f"- Label B: {_counts(s['label_b'])}",
                  f"- Reason codes (all): {_counts(s['reason_codes'])}",
                  f"- Reason codes (primary path): {_counts(s['primary_reason_codes'])}",
                  f"- Hop-1 status: {_counts(s['hop1_status'])}",
                  f"- OUT_OF_MEMORY episodes: {s['out_of_memory_episodes']}"]
    lines += ["", "## Assertion: no answer is both OFF_QUESTION and SUPPORTED", ""]
    lines.append("PASS: none found." if not violations else
                 "FAIL: " + "; ".join(f"{a} {q} node {n}" for a, q, n in violations))
    return "\n".join(lines) + "\n"
