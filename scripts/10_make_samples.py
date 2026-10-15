"""S10 manifests and isolated agent sheets, protocol §8, §9.3 and §3.4."""

import csv
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import pyarrow.parquet as pq
import yaml

from cofail_kg.data.biohopr_loader import file_sha256
from cofail_kg.data.sampling import SEED, SET_SPECS, draw_samples, size_bin
from cofail_kg.utils.frozen_hashes import read_frozen_hashes, write_once

ROOT = Path(__file__).resolve().parents[1]


def jsonl(records):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",",":"))+"\n" for r in records).encode("utf-8")


def make_artifacts(samples, reports, references, nodes, provenance):
    artifacts, config = {}, {"seed":SEED,"sets":{}}
    lines = ["# S10 — Sampling report", "", "Seed 42; sets are disjoint and selected in screening → smoke → pilot → expansion order.",
             "Pilot default confirmed: 25 SINGLE_BRIDGE / 75 MULTI_BRIDGE. Bins are descriptive only.", "",
             "| Set | Target | Sampled | Single | Multi | Shortfall |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name,_,_,_,_ in SET_SPECS:
        manifests, sheets = [], []
        for r in samples[name]:
            q = references[r["query_id"]]
            node = nodes[q["s"]]
            if len(set(q["question_texts"])) != 1 or node["node_type"] != q["Type_S"]:
                raise ValueError(f"Invalid reference question/start node: {q['query_id']}")
            if r["relation_type"] != q["relation_type"] or int(r["target_count"]) != len(q["T_q"]):
                raise ValueError("Primary/S7 reference mismatch")
            if r["bridge_multiplicity"] != ("SINGLE_BRIDGE" if len(q["B_q"])==1 else "MULTI_BRIDGE" if len(q["B_q"])>1 else "NO_BRIDGE"):
                raise ValueError("Primary/S7 multiplicity mismatch")
            manifests.append(dict(query_id=r["query_id"],relation_type=r["relation_type"],
                                  multiplicity=r["bridge_multiplicity"],ambiguity_tag=r["ambiguity_tag"],
                                  tq_size_bin=size_bin(int(r["target_count"]))))
            sheets.append(dict(query_id=r["query_id"],question_text=q["question_texts"][0],
                               start_name=node["node_name"],start_id=q["s"]))
        manifest=f"data/processed/manifests/{name}.jsonl"
        sheet=f"data/agent_inputs/{name}.jsonl"
        artifacts[manifest]=jsonl(manifests)
        artifacts[sheet]=jsonl(sheets)
        report=reports[name]
        config["sets"][name]={"target_size":report["target_size"],"size":report["sampled"],
                              "single":report["by_multiplicity"]["SINGLE_BRIDGE"],
                              "multi":report["by_multiplicity"]["MULTI_BRIDGE"],
                              "per_type_floor":report["per_type_floor"],
                              "manifest":manifest,"agent_inputs":sheet}
        lines.append(f"| {name} | {report['target_size']} | {report['sampled']} | {config['sets'][name]['single']} | {config['sets'][name]['multi']} | {report['shortfall']} |")
    for name,report in reports.items():
        lines += ["",f"## {name} — strata", "", "| Multiplicity | Relation type | Queries |", "| --- | --- | ---: |"]
        for group,types in report["strata"].items():
            lines.extend(f"| {group} | {kind} | {n} |" for kind,n in types.items())
    lines += ["", "Agent sheets contain exactly query_id, question_text, start_name and start_id.",
              "Manifest and sheet lines are ordered by query ID after selection; selection within strata uses SHA256(42 + query_id).", ""]
    artifacts["data/processed/manifests/sampling_report.md"]="\n".join(lines).encode("utf-8")
    artifacts["configs/pilot.yaml"]=yaml.safe_dump(config,sort_keys=False,allow_unicode=True).encode("utf-8")
    hashes={path:hashlib.sha256(data).hexdigest() for path,data in sorted(artifacts.items()) if path.endswith(".jsonl")}
    provenance={**provenance,"sets":reports,"frozen_manifests":hashes}
    artifacts["data/processed/manifests/sampling_provenance.json"]=(json.dumps(provenance,indent=2,sort_keys=True)+"\n").encode("utf-8")
    return artifacts,hashes


def publish(root, artifacts, hashes):
    frozen_path=root/"configs/frozen_hashes.yaml"
    frozen=read_frozen_hashes(frozen_path)
    if "manifests" in frozen and frozen["manifests"] != hashes:
        raise ValueError("Frozen sampling hashes differ; refusing resampling")
    for path,data in artifacts.items():
        dest=root/path
        placeholder=path=="configs/pilot.yaml" and dest.exists() and yaml.safe_load(dest.read_text(encoding="utf-8")) is None
        if dest.exists() and dest.read_bytes()!=data and not placeholder:
            raise FileExistsError(f"Completed sampling artifact differs: {path}")
    # Stage all bytes before publishing; a partial first publication can resume identically.
    (root/"data/processed").mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".s10-",dir=root/"data/processed") as staging:
        stage=Path(staging)
        for path,data in artifacts.items():
            temp=stage/path
            temp.parent.mkdir(parents=True,exist_ok=True)
            temp.write_bytes(data)
        for path,data in artifacts.items():
            dest=root/path
            if not dest.exists() or dest.read_bytes()!=data:
                dest.parent.mkdir(parents=True,exist_ok=True)
                (stage/path).replace(dest)
    write_once(frozen_path,"manifests",hashes)


def main():
    summary=json.loads((ROOT/"data/processed/primary_population_summary.json").read_text())
    if summary["outcome"] not in ("GREEN","YELLOW"):
        raise ValueError("S10 requires Gate D2 GREEN or YELLOW")
    if file_sha256(ROOT/"data/processed/primary_population.csv") != summary["primary_population_sha256"]:
        raise ValueError("Primary population hash mismatch")
    frozen=read_frozen_hashes(ROOT/"configs/frozen_hashes.yaml")
    if any(frozen.get(k)!=v for k,v in summary["provenance"]["frozen_inputs"].items()):
        raise ValueError("Frozen inputs differ from S9")
    for name in ("docs/frozen_pilot_protocol.md","docs/decision_rules.md"):
        if file_sha256(ROOT/name)!=summary["provenance"]["sha256"][name]:
            raise ValueError(f"S9 protocol/rules changed: {name}")
    s8=json.loads((ROOT/"results/diagnostics/query_validation_summary.json").read_text())
    for name in ("data/processed/reference_queries.parquet","data/cache/primekg_nodes.parquet"):
        if file_sha256(ROOT/name)!=s8["provenance"]["sha256"][name]:
            raise ValueError(f"S7/KG input changed: {name}")
    with (ROOT/"data/processed/primary_population.csv").open(newline="",encoding="utf-8") as stream:
        population=list(csv.DictReader(stream))
    if len(population)!=summary["N_P"] or any(r["status"]!="CONSISTENT" or r["leaky_question"]!="False" or r["saturated"]!="False" for r in population):
        raise ValueError("Invalid primary population")
    references={q["query_id"]:q for q in pq.read_table(ROOT/"data/processed/reference_queries.parquet").to_pylist()}
    nodes={str(n["node_index"]):n for n in pq.read_table(ROOT/"data/cache/primekg_nodes.parquet").to_pylist()}
    samples,reports=draw_samples(population)
    paths=["data/processed/primary_population.csv","data/processed/primary_population_summary.json",
           "data/processed/reference_queries.parquet","data/cache/primekg_nodes.parquet",
           "docs/frozen_pilot_protocol.md","docs/decision_rules.md","scripts/10_make_samples.py",
           "src/cofail_kg/data/sampling.py","src/cofail_kg/utils/frozen_hashes.py"]
    provenance={"seed":SEED,"input_queries":len(population),"base_frozen_inputs":summary["provenance"]["frozen_inputs"],
                "sha256":{p:file_sha256(ROOT/p) for p in paths},
                "git_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,check=True,text=True,capture_output=True).stdout.strip()}
    artifacts,hashes=make_artifacts(samples,reports,references,nodes,provenance)
    publish(ROOT,artifacts,hashes)
    print(json.dumps({k:{f:v for f,v in r.items() if f!="strata"} for k,r in reports.items()},indent=2))
    print("Verified/published eight JSONL artifacts; sampling hashes frozen under manifests.")


if __name__=="__main__":
    main()
