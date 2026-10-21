"""Offline saved-trace audit; no inference or changes to protocol/D3 outcomes."""

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

from cofail_kg.agents.run_agent import parse_final
from cofail_kg.agents.trace import load_episode_record


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def classification(recovered, final_at_context, earlier_at_context):
    if recovered:
        return "recovered_at_16k"
    if final_at_context:
        return "direct_context_truncation_no_16k_test"
    if earlier_at_context:
        return "context_pressure_with_final_schema_failure"
    return "unresolved_parse_failure"


assert classification(True, True, True) == "recovered_at_16k"
assert classification(False, True, True) == "direct_context_truncation_no_16k_test"
assert classification(False, False, True) == "context_pressure_with_final_schema_failure"
assert classification(False, False, False) == "unresolved_parse_failure"


def main():
    baseline = json.loads((OUT / "integrity-before.json").read_text(encoding="utf-8"))
    comparison = json.loads((ROOT / "results/diagnostics/s20/gemma4-e4b-16k/comparison.json").read_text())
    recovered = {r["query_id"] for r in comparison["rows"] if r["status_16k"] == "SUCCESS"}
    models, failures = [], []
    for manifest in sorted((ROOT / "results/runs/screening").glob("*/*.config.json")):
        snapshot = json.loads(manifest.read_text())
        agent = snapshot["agent"]["agent_id"]
        records = [load_episode_record(manifest.parent / f"{q}__{agent}__a1.json")
                   for q in snapshot["query_ids"]]
        assert len(records) == len({r["query_id"] for r in records}) == 20
        counts = Counter(r["status"] for r in records)
        labels = Counter()
        for record in records:
            assert record["num_ctx"] == 8192 and record["num_predict"] == 4096
            if record["status"] == "SUCCESS":
                continue
            responses = {e["message_index"]: e["raw_response"] for e in record["log_events"]
                         if e["event"] == "CHAT_RESPONSE"}
            attempts = []
            for event in record["log_events"]:
                if event["event"] != "PARSE_ERROR":
                    continue
                response = responses[event["message_index"]]
                prompt, output = response.get("prompt_eval_count"), response.get("eval_count")
                at_context = (response.get("done_reason") == "length"
                              and type(prompt) is int and type(output) is int
                              and prompt + output == record["num_ctx"]
                              and output < record["num_predict"])
                try:
                    parse_final(response["message"].get("content", ""), [])
                except ValueError as error:
                    replay_error = str(error)
                else:
                    raise AssertionError("Saved parse failure unexpectedly parses")
                assert replay_error == event["message"], (agent, record["query_id"])
                attempts.append({"message_index": event["message_index"],
                                 "prompt_tokens": prompt, "output_tokens": output,
                                 "token_sum": prompt + output if type(prompt) is int and type(output) is int else None,
                                 "exact_context_boundary": at_context,
                                 "parser_error_reproduced": replay_error,
                                 "raw_response": response})
            label = "request_timeout_not_parse_failure"
            if record["status"] == "PARSE_FAIL":
                assert len(attempts) == 2
                label = classification(agent == "Gemma4-E4B" and record["query_id"] in recovered,
                                       attempts[-1]["exact_context_boundary"],
                                       any(a["exact_context_boundary"] for a in attempts[:-1]))
                labels[label] += 1
            path = manifest.parent / f"{record['query_id']}__{agent}__a1.json"
            failures.append({"agent_id": agent, "query_id": record["query_id"],
                             "status": record["status"], "cause": record["cause"],
                             "evidence_label": label, "episode_path": path.relative_to(ROOT).as_posix(),
                             "episode_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                             "num_ctx": record["num_ctx"], "num_predict": record["num_predict"],
                             "parse_attempts": attempts,
                             "errors": [e for e in record["log_events"] if e["event"] == "ERROR"]})
        models.append({"agent_id": agent, "model": snapshot["identity"]["tag"],
                       "episodes": len(records), "success": counts["SUCCESS"],
                       "parse_fail": counts["PARSE_FAIL"], "error": counts["ERROR"],
                       "timeout": counts["TIMEOUT"],
                       "direct_context_truncation": labels["direct_context_truncation_no_16k_test"],
                       "mixed_context_and_schema": labels["context_pressure_with_final_schema_failure"],
                       "recovered_at_16k": labels["recovered_at_16k"],
                       "unresolved_parse_failure": labels["unresolved_parse_failure"]})
    assert len(models) == 7 and sum(m["episodes"] for m in models) == 140
    assert sum(m["parse_fail"] for m in models) == 10
    assert sum(m["direct_context_truncation"] for m in models) == 5
    assert sum(m["mixed_context_and_schema"] for m in models) == 1
    assert sum(m["recovered_at_16k"] for m in models) == 4
    assert sum(m["error"] for m in models) == 4
    assert all(m["unresolved_parse_failure"] == 0 for m in models)
    assert len(failures) == 14
    for group in baseline.values():
        for path, digest in group.items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    with (OUT / "evidence.json").open("x", encoding="utf-8") as handle:
        json.dump({"scope": "All seven official S20 candidates; no inference", "models": models,
                   "non_success_episodes": failures}, handle, indent=2)
    with (OUT / "model-summary.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(models[0]))
        writer.writeheader()
        writer.writerows(models)
    proof = {"groups_verified": {name: len(group) for name, group in baseline.items()},
             "episodes_audited": 140, "saved_parse_attempts_reproduced": sum(
                 len(f["parse_attempts"]) for f in failures), "classification_selfchecks": 4,
             "model_calls": 0, "drift": [], "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (OUT / "integrity-after.json").open("x", encoding="utf-8") as handle:
        json.dump(proof, handle, indent=2)
    print(json.dumps({"models": models, "verification": proof}, indent=2))


if __name__ == "__main__":
    main()
