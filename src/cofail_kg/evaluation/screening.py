"""Evaluator-only S20 measurements and D3 criteria (protocol section 9.1)."""

from datetime import datetime
import json
from statistics import median

from cofail_kg.agents.tool_schemas import TOOL_SCHEMAS


def call_counts(record):
    """D3 attempts include all native calls and recorded TEXT_TOOL_CALL occurrences.

    Count emitted calls, including malformed/unexecuted calls, from assistant
    messages rather than the subset that reached the KG environment. D3 requires
    declared names, required arguments and schema types; KG validity is separate.
    """
    schemas = {s["function"]["name"]: s["function"]["parameters"] for s in TOOL_SCHEMAS}
    native = well_formed = 0
    for message in record["messages"]:
        if message.get("role") != "assistant":
            continue
        for call in message.get("tool_calls", []):
            native += 1
            function = call.get("function", {}) if isinstance(call, dict) else {}
            name = function.get("name") if isinstance(function, dict) else None
            schema = schemas.get(name) if isinstance(name, str) else None
            if schema is None:
                continue
            arguments = function.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except ValueError:
                    continue
            if not isinstance(arguments, dict) or not set(schema["required"]) <= arguments.keys():
                continue
            types = {"string": str, "integer": int}
            if all(type(arguments[k]) is types[v["type"]]
                   for k, v in schema["properties"].items() if k in arguments):
                well_formed += 1
    text = sum(e.get("event") == "TEXT_TOOL_CALL" for e in record.get("log_events", []))
    return {"native_calls": native, "text_tool_calls": text,
            "attempted_calls": native + text, "well_formed_calls": well_formed}


def aggregate_model(records, metrics, identity, expected=20):
    """Observed screening quantities; D3 verdicts exist only for a complete set.

    Competence denominator is all screening queries, including technical failures.
    This is D3 competence, not a section 16 answer-failure/co-failure metric.
    """
    n = len(records)
    if (n != len(metrics) or n > expected
            or len({r["query_id"] for r in records}) != n):
        raise ValueError("Duplicate queries or incomplete/misaligned screening metrics")
    counts = {k: 0 for k in ("native_calls", "text_tool_calls", "attempted_calls", "well_formed_calls")}
    wall = []
    prompts = []
    competent = 0
    for record, row in zip(records, metrics):
        if record["model"] != {k: identity[k] for k in ("tag", "digest", "quantization")}:
            raise ValueError("Screening model identity differs from manifest")
        for k, v in call_counts(record).items():
            counts[k] += v
        elapsed = (datetime.fromisoformat(record["timestamps"]["finished_at"])
                   - datetime.fromisoformat(record["timestamps"]["started_at"])).total_seconds()
        if elapsed < 0:
            raise ValueError("Negative episode wall time")
        wall.append(elapsed)
        prompts.extend(x for x in record["token_counts"]["prompt"] if x is not None)
        competent += record["status"] == "SUCCESS" and any(
            a["label_a"] in ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID") and a["label_b"] == "SUPPORTED"
            for a in row["answers"])
    success = sum(r["status"] == "SUCCESS" for r in records)
    oom = sum(r["status"] == "ERROR" and r["cause"] == "OUT_OF_MEMORY" for r in records)
    rate = counts["well_formed_calls"] / counts["attempted_calls"] if counts["attempted_calls"] else None
    complete = n == expected
    verdicts = {"pass_well_formed": rate is not None and rate >= .9,
                "pass_success": success / n >= .9 if n else False,
                "pass_competence": competent / n >= .4 if n else False,
                "pass_time": median(wall) <= 300 if wall else False, "pass_oom": oom == 0}
    return {"run_id": records[0]["run_id"] if records else None,
            "agent_id": records[0]["agent_id"] if records else None,
            **identity, "episodes_completed": n, "episodes_expected": expected,
            "complete": complete, **counts, "well_formed_rate": rate,
            "success_episodes": success, "success_rate": success / n if n else None,
            "competent_episodes": competent, "competence": competent / n if n else None,
            "median_wall_seconds": median(wall) if wall else None, "out_of_memory_episodes": oom,
            "largest_prompt_eval_count": max(prompts, default=None),
            "median_tool_calls": median([m["tool_calls_used"] for m in metrics]) if n else None,
            "budget_hit_share": sum(m["budget_exhausted"] for m in metrics) / n if n else None,
            **{k: v if complete else None for k, v in verdicts.items()},
            "d3_pass": all(verdicts.values()) if complete else None}
