"""S22 review (offline, read-only): verify smoke_single_v135 records, coverage, saved metrics and context triggers.

Reads historical artifacts only; writes results/diagnostics/s22_review/verification.json. No inference.
The context trigger is the strict §9.1 test on exact counts: max prompt_eval_count > 0.9 * num_ctx.
"""
import json
from fractions import Fraction
from pathlib import Path
import subprocess

import yaml

from cofail_kg.agents.trace import load_episode_record, verify_reconstruction
from cofail_kg.kg.prepare import file_hash

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results/runs/smoke_single_v135"
DIAG = ROOT / "results/diagnostics/smoke_single_v135"
OUT = Path(__file__).with_name("verification.json")


def committed(path):
    """File content at HEAD, to show the hash files themselves are the committed ones."""
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)


def main():
    runtime = yaml.safe_load((ROOT / "configs/pilot.yaml").read_text(encoding="utf-8"))["runtime"]
    agents = runtime["agent_order"]
    query_ids = [json.loads(line)["query_id"] for line in
                 (ROOT / "data/agent_inputs/screening.jsonl").read_text(encoding="utf-8").splitlines()]
    out = {"run_id": "smoke_single_v135", "agents": agents, "query_count": len(query_ids), "per_agent": {}}
    files = sorted(p.name for p in RUN.glob("*__a*.json"))
    expected = sorted(f"{q}__{a}__a1.json" for q in query_ids for a in agents)
    out["record_files_match_manifest_x_agents"] = files == expected
    out["extra_or_missing"] = sorted(set(files) ^ set(expected))
    for agent in agents:
        hash_path = DIAG / agent / "final-run-hashes.json"
        rel = hash_path.relative_to(ROOT).as_posix()
        hashes = json.loads(hash_path.read_text(encoding="utf-8"))
        # core.autocrlf=true: the working copy has CRLF, the git object LF; compare content.
        hashes_committed = committed(rel) == hash_path.read_bytes().replace(b"\r\n", b"\n")
        mismatches = sorted(p for p, h in hashes.items() if file_hash(ROOT / p) != h)
        num_ctx = runtime["agents"][agent]["num_ctx"]
        statuses, triggers, max_prompt = {}, [], 0
        metrics_ok = []
        for q in query_ids:
            record = load_episode_record(RUN / f"{q}__{agent}__a1.json")
            verify_reconstruction(record)
            assert (record["query_id"], record["agent_id"], record["attempt"]) == (q, agent, 1)
            statuses[record["status"]] = statuses.get(record["status"], 0) + 1
            prompt = max((x for x in record["token_counts"]["prompt"] if x is not None), default=0)
            max_prompt = max(max_prompt, prompt)
            if Fraction(prompt) > Fraction(9, 10) * num_ctx:  # strict, exact
                triggers.append({"query_id": q, "prompt_eval_count": prompt, "num_ctx": num_ctx,
                                 "share": prompt / num_ctx})
            metric = json.loads((DIAG / agent / "metrics" / f"{q}.json").read_text(encoding="utf-8"))
            metrics_ok.append(metric["query_id"] == q and metric["agent_id"] == agent
                              and metric["episode_status"] == record["status"])
        out["per_agent"][agent] = {
            "hash_entries": len(hashes), "hash_file_equals_HEAD": hashes_committed,
            "hash_mismatches": mismatches, "status_counts": dict(sorted(statuses.items())),
            "reconstruction_checked": len(query_ids), "metrics_paired": all(metrics_ok),
            "num_ctx": num_ctx, "max_prompt_eval_count": max_prompt, "context_triggers": triggers}
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
