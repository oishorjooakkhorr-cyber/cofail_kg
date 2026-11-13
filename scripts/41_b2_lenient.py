"""Phase J B2 — Strict vs lenient answer key (EXPLORATORY).

Usage (from the repository root, on the PC that holds the raw run records):
    python scripts/41_b2_lenient.py --combined pilot_expansion_v1

Rule (docs/decision_log.md, entry 2026-11-12 "Plan after D7", section B2):
  Strict = the frozen labels. Lenient: wherever `indication` is in R1 or R2, `off-label use` is also
  accepted at that step (R1⁺, R2⁺); T_q⁺ and hop-1 status are recomputed with R1⁺/R2⁺, and an OFF_QUESTION
  answer in T_q⁺ is valid under the lenient key. `contraindication` is never accepted; answers whose primary
  path uses it at an indication step are counted separately (answers and queries, per agent). Report under
  both keys: CF3^Q, CF4^Q, CF3^{Q,H1} (= N), per-agent question-valid precision. Strict results remain the
  results of record.

Readings (researcher, 2026-11-13; decision log entry "B2 — Inputs and the contraindication step"):
  1. The lenient hop-1 status needs trace graphs: raw pilot_v1 / expansion_v1 records are read (never full_v1).
  2. Indication step = treat-final: second edge of a primary path with ≥ 2 edges; treat-first: first edge;
     other types: none. All retained resolved answers are counted; how many are in T_q⁺ is also reported.

Method (the frozen evaluation code, with only R1/R2 and T_q swapped):
* T_q⁺ / B_q⁺: protocol §6 construction (src/cofail_kg/evaluation/reference_sets.py): candidate bridges =
  Type_B neighbours of s through R1⁺ minus s; T_q(b) = Type_T neighbours of b through R2⁺ minus s; B_q⁺ = the
  bridges with T_q(b) non-empty; T_q⁺ = their union. With R1/R2 the same builder must reproduce the frozen
  B_q and T_q of every query (checked).
* Answers: the S16 retained answers, re-derived from the raw record exactly as agent_metrics does (parse_final
  + normalize_agent_answers); their node IDs must equal the stored metrics row's (checked).
* H1 and per-agent hop-1 status: path_labels.label_paths with {R1⁺, R2⁺}. With {R1, R2} it must reproduce
  every stored h1, Label B, primary path and hop1_status (checked).
* Lenient Label A: unchanged, except that an OFF_QUESTION answer in T_q⁺ is relabelled ALT_VALID (a
  question-valid label; G_q ⊆ T_q, so the frozen label order is respected). Label B and primary paths are
  not recomputed (B2 names only T_q⁺ and hop-1 status).
* Co-failure: cofailure.query_cofailure on the relabelled rows with reference T_q⁺ / B_q⁺ and mapping
  {R1⁺, R2⁺}. With the frozen rows it must reproduce cofailure.json's question and hop1_clean flags
  (checked). Only CF3^Q, CF4^Q, CF3^{Q,H1} (and CF4^{Q,H1}) are reported; PCF is not part of B2.
* Per-agent question-valid precision: as scripts/28_pilot_report.py table 2e — mean of the defined
  per-episode values, with the pooled value Σ question-valid / Σ resolved.

Engineering conventions (documented, not protocol):
* Both views of protocol §19.1 are written (all queries first; then without SOURCE_NAME_OVERLAP queries).
* Inputs are hash-checked (manifests and KG fingerprint against configs/frozen_hashes.yaml); outputs are
  write-once (an identical re-run is allowed). Console output is UTF-8.
* No interpretation is written.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cofail_kg.agents.run_agent import parse_final  # noqa: E402
from cofail_kg.evaluation.cofailure import query_cofailure  # noqa: E402
from cofail_kg.evaluation.normalize import normalize_agent_answers  # noqa: E402
from cofail_kg.evaluation.path_labels import label_paths  # noqa: E402

INDICATION, OFF_LABEL, CONTRA = "indication", "off-label use", "contraindication"
QUESTION_VALID = ("GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID")
HOP1 = ("H1_CLEAN", "H1_MIXED", "H1_WRONG", "H1_NONE")
KEYS = ("strict", "lenient")
VIEWS = ("all_queries", "without_source_name_overlap")
METRICS = (("CF3^Q", "question", "cf3"), ("CF4^Q", "question", "cf4"),
           ("CF3^{Q,H1}", "hop1_clean", "cf3"), ("CF4^{Q,H1}", "hop1_clean", "cf4"))
EXPLORATORY_NOTE = ("EXPLORATORY (protocol §20) — docs/decision_log.md, entry 2026-11-12 \"Plan after D7\", "
                    "section B2, with the entry 2026-11-13 \"B2 — Inputs and the contraindication step\". "
                    "Strict results remain the results of record.")


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B5 = load_script("b5_concentration", "42_b5_concentration.py")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------ the key

def lenient_labels(labels: list[str]) -> list[str]:
    """R⁺: `off-label use` added wherever `indication` is accepted; never `contraindication`."""
    out = sorted(set(labels) | ({OFF_LABEL} if INDICATION in labels else set()))
    if CONTRA in out:
        raise ValueError(f"contraindication is never accepted (labels {labels})")
    return out


def indication_step(r1: list[str], r2: list[str]) -> int | None:
    """Index of the indication edge on a primary path (reading 2): 1 for R2 ∋ indication, 0 for R1."""
    if INDICATION in r2:
        return 1
    if INDICATION in r1:
        return 0
    return None


def reference_sets(s: str, type_b: str, type_t: str, r1: list[str], r2: list[str], by_label) -> tuple[list, list]:
    """(B_q, T_q) by the §6 construction; `by_label(node, type)` -> {label: set of IDs}."""
    def reached(node, kind, labels):
        found = by_label(node, kind)
        return set().union(*(found.get(label, set()) for label in labels))

    bridges, targets = [], set()
    for b in sorted(reached(s, type_b, r1) - {s}, key=int):
        tb = reached(b, type_t, r2) - {s}
        if tb:
            bridges.append(b)
            targets |= tb
    return bridges, sorted(targets, key=int)


# ------------------------------------------------------------------------------------ per episode

def rescore_row(row: dict, record: dict | None, ref: dict, mapping: dict, kg, tq_plus: set) -> dict:
    """Lenient copy of one §15 metrics row: Label A over T_q⁺, h1 and hop1_status over {R1⁺, R2⁺}."""
    out = copy.deepcopy(row)
    if row["episode_status"] != "SUCCESS":
        return out
    answers = normalize_agent_answers(kg, parse_final(record["raw_final_output"], [])["answers"],
                                      ref["Type_T"]).answers
    if [a.node_id for a in answers] != [a["node_id"] for a in row["answers"]]:
        raise ValueError(f"{row['query_id']}/{row['agent_id']}: re-derived answers differ from the metrics row")
    strict = label_paths(answers, record, ref, mapping, kg)
    if strict["hop1_status"] != row["hop1_status"]:
        raise ValueError(f"{row['query_id']}/{row['agent_id']}: strict hop1_status not reproduced")
    for got, stored in zip(strict["answers"], row["answers"]):
        if any(got[k] != stored[k] for k in ("label_b", "h1", "primary_path")):
            raise ValueError(f"{row['query_id']}/{row['agent_id']}: strict path labels not reproduced for "
                             f"{stored['node_id']}")
    plus = {"R1": lenient_labels(mapping["R1"]), "R2": lenient_labels(mapping["R2"])}
    lenient = label_paths(answers, record, ref, plus, kg)
    out["hop1_status"] = lenient["hop1_status"]
    for a, got in zip(out["answers"], lenient["answers"]):
        a["h1"] = got["h1"]
        if a["label_a"] == "OFF_QUESTION" and a["node_id"] in tq_plus:
            a["label_a"] = "ALT_VALID"
    return out


def precision(row: dict) -> tuple[int, int] | None:
    """(question-valid, resolved) of one SUCCESS episode; None for a technical failure."""
    if row["episode_status"] != "SUCCESS":
        return None
    resolved = [a for a in row["answers"] if a["node_id"] is not None]
    return sum(a["label_a"] in QUESTION_VALID for a in resolved), len(resolved)


def contra_answers(row: dict, step: int | None, tq: set, tq_plus: set) -> list[dict]:
    """Retained resolved answers whose primary path has `contraindication` at the indication step."""
    if step is None:
        return []
    return [{"node_id": a["node_id"], "in_T_q": a["node_id"] in tq, "in_T_q_plus": a["node_id"] in tq_plus}
            for a in row["answers"]
            if a["node_id"] is not None and a.get("primary_path") and len(a["primary_path"]) > step
            and a["primary_path"][step]["label"] == CONTRA]


# ----------------------------------------------------------------------------------------- summary

def per_agent(rows: dict, agents: list[str], keep: set[str]) -> list[dict]:
    """Question-valid precision (mean of defined per-episode values and pooled) and hop-1 status counts."""
    out = []
    for agent in agents:
        mine = [r for (a, q), r in sorted(rows.items()) if a == agent and q in keep]
        pairs = [p for p in map(precision, mine) if p is not None]
        defined = [n / d for n, d in pairs if d]
        num, den = sum(n for n, d in pairs if d), sum(d for n, d in pairs if d)
        out.append({"agent_id": agent, "episodes": len(mine), "defined": len(defined),
                    "na": len(mine) - len(defined), "qv_precision_mean": sum(defined) / len(defined) if defined
                    else None, "qv_pooled_num": num, "qv_pooled_den": den,
                    "qv_precision_pooled": num / den if den else None,
                    **{h: sum(r["hop1_status"] == h for r in mine) for h in HOP1}})
    return out


def compute(data: dict, refs: dict, mapping: dict, kg, degrees: dict) -> dict:
    cof, agents = data["cofailure"], data["agents"]
    overlap = set(cof["source_name_overlap_queries"])
    by_query = {q["query_id"]: q for q in cof["queries"]}
    rows = {key: {} for key in KEYS}
    results = {key: {} for key in KEYS}
    contra, tq_info = [], {}
    for qid in sorted(by_query):
        q, ref = by_query[qid], refs[qid]
        spec = mapping[ref["relation_type"]]
        by_label = lambda node, kind: kg.neighbors_by_label(node, kind)  # noqa: E731
        bq, tq = reference_sets(ref["s"], ref["Type_B"], ref["Type_T"], spec["R1"], spec["R2"], by_label)
        if bq != list(ref["B_q"]) or tq != list(ref["T_q"]):
            raise ValueError(f"{qid}: the §6 builder does not reproduce the frozen B_q / T_q")
        plus = {"R1": lenient_labels(spec["R1"]), "R2": lenient_labels(spec["R2"])}
        bq_p, tq_p = reference_sets(ref["s"], ref["Type_B"], ref["Type_T"], plus["R1"], plus["R2"], by_label)
        if not set(tq) <= set(tq_p):
            raise ValueError(f"{qid}: T_q is not a subset of T_q⁺")
        tq_info[qid] = {"tq_size": len(tq), "tq_plus_size": len(tq_p), "bq_size": len(bq), "bq_plus_size": len(bq_p),
                        "changed": plus != {"R1": sorted(spec["R1"]), "R2": sorted(spec["R2"])}}
        ref_plus = {**ref, "B_q": bq_p, "T_q": tq_p}
        step = indication_step(spec["R1"], spec["R2"])
        strict_rows = [data["rows"][(a, qid)] for a in agents]
        lenient_rows = [rescore_row(r, data["records"].get((r["agent_id"], qid)), ref, spec, kg, set(tq_p))
                        for r in strict_rows]
        for r_s, r_l in zip(strict_rows, lenient_rows):
            got = precision(r_s)
            if got is not None and got[1] and got != (r_s["numerators"]["question_valid_precision"],
                                                       r_s["denominators"]["question_valid_precision"]):
                raise ValueError(f"{qid}/{r_s['agent_id']}: strict question-valid precision not reproduced")
            rows["strict"][(r_s["agent_id"], qid)] = r_s
            rows["lenient"][(r_l["agent_id"], qid)] = r_l
            hits = contra_answers(r_s, step, set(tq), set(tq_p))
            if hits:
                contra.append({"query_id": qid, "agent_id": r_s["agent_id"], "relation_type": ref["relation_type"],
                               "source_name_overlap": qid in overlap, "answers": hits})
        strict = query_cofailure(ref, spec, q["ambiguity_tag"], strict_rows, degrees, agents)
        for _, block, flag in METRICS:
            if strict[block][flag] != q[block][flag]:
                raise ValueError(f"{qid}: strict {block}.{flag} not reproduced from cofailure.json")
        results["strict"][qid] = strict
        results["lenient"][qid] = query_cofailure(ref_plus, plus, q["ambiguity_tag"], lenient_rows, degrees, agents)

    views = {"all_queries": set(by_query), "without_source_name_overlap": set(by_query) - overlap}
    tables = {}
    for view, keep in views.items():
        tables[view] = {
            "cofailure": {key: {label: sum(int(results[key][q][b][f]) for q in keep) for label, b, f in METRICS}
                          for key in KEYS},
            "flagged_queries": {key: {label: sorted(q for q in keep if results[key][q][b][f])
                                      for label, b, f in METRICS} for key in KEYS},
            "per_agent": {key: per_agent(rows[key], agents, keep) for key in KEYS},
            "contraindication": contra_table([c for c in contra if c["query_id"] in keep], agents),
        }
    changed = [q for q in sorted(by_query) if tq_info[q]["changed"]]
    return {"agent_order": agents, "source_name_overlap_queries": sorted(overlap), "queries": len(by_query),
            "queries_with_lenient_labels": len(changed),
            "queries_with_larger_T_q": sum(tq_info[q]["tq_plus_size"] > tq_info[q]["tq_size"] for q in changed),
            "reference_sets": tq_info, "tables": tables, "contraindication_episodes": contra}


def contra_table(contra: list[dict], agents: list[str]) -> list[dict]:
    out = []
    for agent in agents:
        mine = [c for c in contra if c["agent_id"] == agent]
        answers = [a for c in mine for a in c["answers"]]
        out.append({"agent_id": agent, "answers": len(answers), "queries": len({c["query_id"] for c in mine}),
                    "answers_in_T_q": sum(a["in_T_q"] for a in answers),
                    "answers_in_T_q_plus": sum(a["in_T_q_plus"] for a in answers)})
    return out


# -------------------------------------------------------------------------------------------- output

def _f(x) -> str:
    return "NA" if x is None else f"{x:.3f}"


def summary_csv(result: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["view", "section", "key", "item", "value"])
    for view in VIEWS:
        t = result["tables"][view]
        for key in KEYS:
            for label, value in t["cofailure"][key].items():
                w.writerow([view, "cofailure", key, label, value])
            for r in t["per_agent"][key]:
                for k in ("episodes", "defined", "na", "qv_precision_mean", "qv_pooled_num", "qv_pooled_den",
                          "qv_precision_pooled", *HOP1):
                    w.writerow([view, f"per_agent:{r['agent_id']}", key, k,
                                f"{r[k]:.6f}" if isinstance(r[k], float) else ("" if r[k] is None else r[k])])
        for r in t["contraindication"]:
            for k in ("answers", "queries", "answers_in_T_q", "answers_in_T_q_plus"):
                w.writerow([view, f"contraindication:{r['agent_id']}", "strict paths", k, r[k]])
    return buf.getvalue()


def to_markdown(result: dict, provenance: dict) -> str:
    out = ["# B2 — Strict vs lenient answer key (EXPLORATORY)\n", f"{EXPLORATORY_NOTE}\n",
           f"Produced by `scripts/41_b2_lenient.py` at commit `{provenance['git_commit']}` (tracked files clean: "
           f"{provenance['git_tracked_clean']}). Runs: " + ", ".join(f"`{r}`" for r in provenance["runs"]) +
           ". Latest attempts.\n",
           f"Lenient key: `off-label use` accepted wherever `indication` is (R1⁺, R2⁺); `contraindication` never. "
           f"{result['queries_with_lenient_labels']} of {result['queries']} queries have a changed key; "
           f"{result['queries_with_larger_T_q']} of them have T_q⁺ larger than T_q.\n"]
    titles = {"all_queries": "All queries",
              "without_source_name_overlap": "Without SOURCE_NAME_OVERLAP queries (" +
              ", ".join(result["source_name_overlap_queries"]) + "; protocol §19.1)"}
    n = 1
    for view in VIEWS:
        t = result["tables"][view]
        out.append(f"## Table {n} — Co-failure, {titles[view]}\n")
        n += 1
        out.append("| Metric | Strict (of record) | Lenient | Strict-only queries | Lenient-only queries |")
        out.append("|---|---|---|---|---|")
        for label, _, _ in METRICS:
            s_q, l_q = set(t["flagged_queries"]["strict"][label]), set(t["flagged_queries"]["lenient"][label])
            out.append(f"| {label} | {t['cofailure']['strict'][label]} | {t['cofailure']['lenient'][label]} | "
                       f"{', '.join(sorted(s_q - l_q)) or '—'} | {', '.join(sorted(l_q - s_q)) or '—'} |")
        out.append("\nCF3^{Q,H1} = N.\n")
        out.append(f"## Table {n} — Per-agent question-valid precision and hop-1 status, {titles[view]}\n")
        n += 1
        out.append("| Agent | Key | QV precision: mean (defined / NA) | Pooled | H1_CLEAN | H1_MIXED | H1_WRONG | "
                   "H1_NONE |")
        out.append("|---|---|---|---|---|---|---|---|")
        for i, agent in enumerate(result["agent_order"]):
            for key in KEYS:
                r = t["per_agent"][key][i]
                out.append(f"| {agent} | {key} | {_f(r['qv_precision_mean'])} ({r['defined']} / {r['na']}) | "
                           f"{_f(r['qv_precision_pooled'])} ({r['qv_pooled_num']}/{r['qv_pooled_den']}) | "
                           f"{r['H1_CLEAN']} | {r['H1_MIXED']} | {r['H1_WRONG']} | {r['H1_NONE']} |")
        out.append("")
        out.append(f"## Table {n} — `contraindication` at an indication step, {titles[view]}\n")
        n += 1
        out.append("| Agent | Answers | Queries | Of the answers: in T_q | in T_q⁺ |")
        out.append("|---|---|---|---|---|")
        for r in t["contraindication"]:
            out.append(f"| {r['agent_id']} | {r['answers']} | {r['queries']} | {r['answers_in_T_q']} | "
                       f"{r['answers_in_T_q_plus']} |")
        out.append("")
    out.append("Indication step: treat-final, the second edge of a primary path with ≥ 2 edges; treat-first, the "
               "first edge. Per-episode contraindication detail and per-query T_q / T_q⁺ sizes: `b2.json`.\n")
    return "\n".join(out)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--combined", required=True, help="results/combined/<id> (e.g. pilot_expansion_v1)")
    ap.add_argument("--out", default="results/exploratory/b2")
    args = ap.parse_args(argv)

    frozen = yaml.safe_load((ROOT / "configs/frozen_hashes.yaml").read_text(encoding="utf-8"))
    kg_meta = ROOT / "data/cache/primekg_metadata.json"
    if sha256_file(kg_meta) != frozen["kg_fingerprint"]:
        raise ValueError(f"KG fingerprint {sha256_file(kg_meta)} != frozen {frozen['kg_fingerprint']}")
    comb_dir = ROOT / "results/combined" / args.combined
    components = json.loads((comb_dir / "components.json").read_text(encoding="utf-8"))["components"]
    manifest_inputs = {}
    for run_id in sorted(components):
        rel = f"data/processed/manifests/{components[run_id]['manifest']}.jsonl"
        digest = sha256_file(ROOT / rel)
        if frozen["manifests"].get(rel) != digest:
            raise ValueError(f"{rel}: SHA256 {digest} != frozen {frozen['manifests'].get(rel)} (protocol §3.4)")
        manifest_inputs[components[run_id]["manifest"]] = {"path": rel, "sha256": digest, "run_id": run_id}
    if sorted(components) != ["expansion_v1", "pilot_v1"]:
        raise ValueError(f"B2 reads only pilot_v1 and expansion_v1, got {sorted(components)}")

    report = load_script("s28_report", "28_pilot_report.py")
    launcher = load_script("screening_launcher", "20_screen_models.py")
    data = report.load_combined(args.combined)
    refs, _targets, mapping, _status, kg, degrees = launcher.load_evaluator()
    result = compute(data, refs, mapping, kg, degrees)

    commit, clean = B5.git_state()
    cof_path = comb_dir / "cofailure.json"
    provenance = {"git_commit": commit, "git_tracked_clean": clean, "combined_id": args.combined,
                  "runs": sorted(components),
                  "inputs": {"cofailure": {"path": cof_path.relative_to(ROOT).as_posix(),
                                           "sha256": sha256_file(cof_path)},
                             "relation_mapping": sha256_file(ROOT / "results/semantics/relation_mapping.json"),
                             "kg_fingerprint": frozen["kg_fingerprint"], "manifests": manifest_inputs}}
    out_dir = ROOT / args.out
    payload = {"stage": "B2", "status": "EXPLORATORY", "note": EXPLORATORY_NOTE, "provenance": provenance,
               **result}
    B5.write_once(out_dir / "b2.json", json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    B5.write_once(out_dir / "b2_summary.csv", summary_csv(result))
    md = to_markdown(result, provenance)
    B5.write_once(out_dir / "b2_report.md", md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
