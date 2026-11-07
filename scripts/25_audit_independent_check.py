"""Independent re-derivation of Label A / Label B for the §19.1 audit episodes of a panel run.

Purpose: a bug check of the evaluator before Gate D4 (researcher request, 2026-11-07). It is written
from the protocol text only and deliberately imports NOTHING from `cofail_kg` (no evaluator,
normalizer, path-labelling or reference-set code). It rebuilds every input from the raw files:

* `data/raw/kg.csv`             — nodes (index, type, name) and edges, either direction (§3.2)
* `data/raw/BioHopR.json`       — row `n` of query `BH2_n`: query entity, bridge, answer names (§4)
* `results/semantics/relation_mapping.json` — frozen R1, R2 and construction per relation type (§5)
* the episode records           — call log (trace graph §11), FINAL_PARSED answers (§9.4)

and recomputes, per audit-sheet row: s, B*_q, B_q, T_q, G_q, A*_q (§6, §12 reference policy), agent
normalization (§12 agent policy), the trace graph and "appeared" (§11), Label A (§13), Label B
(§14.1) and the primary path (§14.2). `data/processed/reference_queries.parquet` is read only to
compare its sets with the recomputed ones.

Output:
* `<run>/analysis/independent_audit_check.csv` — every audit row with code and independent labels;
* `<run>/analysis/independent_audit_check.json` — summary and set comparisons;
* with `--fill`, the empty `my_label_A`, `my_label_B`, `notes` cells of `<run>/audit_sheet.csv` are
  filled with the independent labels (machine columns checked unchanged; filled cells refused).

Usage: python scripts/25_audit_independent_check.py --run-id smoke_panel [--fill]
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict, deque
import io
import json
from pathlib import Path
import sys
import unicodedata

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MACHINE = ("episode", "answer_id", "label_A", "label_B", "primary_path")
MINE = ("my_label_A", "my_label_B", "notes")
WHO = "Independent re-derivation by Claude from raw KG/BioHopR/traces, not a human audit"


def norm(text: str) -> str:
    """§12 reference policy: lower-case, NFKC, collapse internal whitespace, trim."""
    return " ".join(unicodedata.normalize("NFKC", str(text).lower()).split())


class KG:
    def __init__(self, path: Path):
        cols = ["relation", "x_index", "x_type", "x_name", "y_index", "y_type", "y_name"]
        df = pd.read_csv(path, usecols=cols, dtype=str, keep_default_na=False)
        self.type, self.name = {}, {}
        for side in ("x", "y"):
            part = df[[f"{side}_index", f"{side}_type", f"{side}_name"]].drop_duplicates()
            for idx, typ, name in part.itertuples(index=False):
                if idx in self.type and (self.type[idx], self.name[idx]) != (typ, name):
                    raise ValueError(f"node {idx} has two type/name values")
                self.type[idx], self.name[idx] = typ, name
        self.by_name = defaultdict(list)
        for idx in sorted(self.type, key=int):
            self.by_name[norm(self.name[idx])].append(idx)
        self.adj = defaultdict(set)  # node -> {(label, neighbour)}, either direction (§3.2)
        for rel, x, y in df[["relation", "x_index", "y_index"]].itertuples(index=False):
            self.adj[x].add((rel, y))
            self.adj[y].add((rel, x))

    def resolve_reference(self, name: str, typ: str):
        """§12 reference policy with the disease-suffix retry."""
        hits = [i for i in self.by_name.get(norm(name), []) if self.type[i] == typ]
        if len(hits) == 1:
            return hits[0]
        if not hits and typ == "disease":
            hits = [i for i in self.by_name.get(norm(norm(name) + " (disease)"), []) if self.type[i] == typ]
            if len(hits) == 1:
                return hits[0]
        return None

    def resolve_agent(self, item: dict, type_t: str):
        """§12 agent policy: ID, then name (Type_T, disease retry, any-type unique), else unresolved."""
        raw_id = item.get("id")
        if isinstance(raw_id, (str, int)) and not isinstance(raw_id, bool):
            key = str(raw_id).strip()
            if key in self.type:
                return key
        name = item.get("name")
        if not isinstance(name, str):
            return None
        hits = self.by_name.get(norm(name), [])
        typed = [i for i in hits if self.type[i] == type_t]
        if len(typed) == 1:
            return typed[0]
        if not hits and type_t == "disease":
            retry = [i for i in self.by_name.get(norm(norm(name) + " (disease)"), []) if self.type[i] == type_t]
            if len(retry) == 1:
                return retry[0]
        if not typed and len(hits) == 1:
            return hits[0]
        return None

    def step(self, node: str, labels, typ: str):
        return {v for r, v in self.adj.get(node, ()) if r in labels and self.type[v] == typ}


def reference_sets(kg: KG, rows: list[dict], mapping: dict) -> dict:
    """§4 and §6 for one query, from its BioHopR rows."""
    first = rows[0]
    if len({r["hop2_question_multi"] for r in rows}) != 1:
        raise ValueError("rows of one query have different question texts")
    type_s, type_b = first["relation_hop2"].split(":")[0], first["relation_hop2"].split(":")[1]
    type_t = first["target_type"]
    rel = mapping[first["relation_hop2"]]
    r1, r2 = set(rel["R1"]), set(rel["R2"])
    s = kg.resolve_reference(first["hop2"], type_s)
    gold_b = {kg.resolve_reference(r["hop1"], type_b) for r in rows} - {None}
    targets = lambda b: {t for t in kg.step(b, r2, type_t) if t != s}  # noqa: E731
    reach = {b for b in kg.step(s, r1, type_b) if b != s}
    b_q = {b for b in reach if targets(b)}
    t_q = set().union(*(targets(b) for b in b_q)) if b_q else set()
    t_gold = set().union(*(targets(b) for b in gold_b)) if gold_b else set()
    a_star = {kg.resolve_reference(n, type_t) for r in rows for n in r["answer"]} - {None}
    g_q = t_gold if rel["construction"] == "BRIDGE" else t_q
    return {"s": s, "type_s": type_s, "type_b": type_b, "type_t": type_t, "R1": r1, "R2": r2,
            "construction": rel["construction"], "gold_bridges": gold_b, "B_q": b_q, "T_q": t_q,
            "G_q": g_q, "A_star_q": a_star}


def trace_graph(record: dict):
    """§11: edges (u, r, v) from successful get_neighbors pages; appeared entities."""
    edges, appeared = {}, set()
    for index, call in enumerate(record["call_log"]):
        if not call["success"]:
            continue
        if call["tool"] == "inspect_entity":
            appeared.add(str(call["result"]["id"]))
        elif call["tool"] == "get_neighbors":
            u, r = str(call["arguments"]["entity_id"]).strip(), call["arguments"]["relation"]
            for item in call["result"]["items"]:
                v = str(item["id"])
                appeared.add(v)
                edges.setdefault((u, r, v), index)
    return edges, appeared


def primary_path(edges: dict, s: str, x: str):
    """§14.2: shortest, then smaller largest creation index, then smaller (id, label) sequence."""
    if x == s:
        return []
    out = defaultdict(list)
    for (u, r, v), idx in edges.items():
        out[u].append((r, v, idx))
    dist, queue = {s: 0}, deque([s])
    while queue:
        u = queue.popleft()
        for _, v, _ in out[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    if x not in dist:
        return None
    best = None

    def walk(u, path):
        nonlocal best
        if u == x:
            key = (max(e[3] for e in path), [(int(e[0]), e[1]) for e in path])
            if best is None or key < best[0]:
                best = (key, list(path))
            return
        for r, v, idx in out[u]:
            if dist.get(v) == dist[u] + 1 and dist[v] <= dist[x]:
                path.append((u, r, v, idx))
                walk(v, path)
                path.pop()

    walk(s, [])
    return best[1]


def labels(kg: KG, ref: dict, edges: dict, appeared: set, x):
    if x is None:
        return "UNRESOLVED", "NOT_APPLICABLE", None
    if x in ref["A_star_q"]:
        a = "GOLD"
    elif x in ref["G_q"]:
        a = "GOLD_BRIDGE_EXTRA"
    elif x in ref["T_q"]:
        a = "ALT_VALID"
    else:
        a = "OFF_QUESTION"
    path = primary_path(edges, ref["s"], x) if x in appeared else None
    if x not in appeared:
        b = "UNGROUNDED"
    else:
        s = ref["s"]
        supported = x != s and kg.type[x] == ref["type_t"] and any(
            u == s and r1 in ref["R1"] and b_ != s and kg.type[b_] == ref["type_b"]
            and any((b_, r2, x) in edges for r2 in ref["R2"])
            for (u, r1, b_) in edges)
        b = "SUPPORTED" if supported else ("PATH_INVALID" if path is not None else "KG_UNSUPPORTED")
    return a, b, path


def render(path) -> str:
    if path is None:
        return ""
    if not path:
        return "(length 0: answer is s)"
    return " ; ".join(f"{u} -{r}-> {v}" for u, r, v, _ in path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--fill", action="store_true", help="fill the empty my_label_* cells")
    parser.add_argument("--dry-run", action="store_true", help="print the comparison, write nothing")
    args = parser.parse_args(argv)
    run = ROOT / "results" / "runs" / args.run_id
    sheet_path = run / "audit_sheet.csv"
    sheet_text = sheet_path.read_bytes().decode("utf-8")  # bytes: keep the CRLF line endings
    sheet = list(csv.DictReader(io.StringIO(sheet_text)))

    kg = KG(ROOT / "data" / "raw" / "kg.csv")
    biohopr = json.loads((ROOT / "data" / "raw" / "BioHopR.json").read_text(encoding="utf-8"))
    mapping = json.loads((ROOT / "results" / "semantics" / "relation_mapping.json")
                         .read_text(encoding="utf-8"))["per_type"]
    stored = pd.read_parquet(ROOT / "data" / "processed" / "reference_queries.parquet").set_index("query_id")

    summary = {"run_id": args.run_id, "who": WHO, "queries": {}, "episodes": {}, "rows": len(sheet),
               "label_A_agree": 0, "label_B_agree": 0, "path_agree": 0, "disagreements": []}
    refs, cache = {}, {}
    out_rows = []
    for row in sheet:
        episode = row["episode"]
        query_id, agent_id, _ = episode.split("__")
        if query_id not in refs:
            row_ids = list(stored.loc[query_id, "row_ids"])
            q_rows = [biohopr[int(r.split("_")[1])] for r in row_ids]
            # Independent grouping check: every BioHopR row with the same question belongs to the query.
            same = sorted(f"BH2_{i:05d}" for i, r in enumerate(biohopr)
                          if r["hop2_question_multi"] == q_rows[0]["hop2_question_multi"]
                          and r["relation_hop2"] == q_rows[0]["relation_hop2"] and r["hop2"] == q_rows[0]["hop2"])
            ref = reference_sets(kg, q_rows, mapping)
            compare = {k: sorted(ref[k], key=int) == sorted(map(str, stored.loc[query_id, k]), key=int)
                       for k in ("B_q", "T_q", "G_q", "A_star_q", "gold_bridges")}
            compare["s"] = ref["s"] == str(stored.loc[query_id, "s"])
            compare["row_grouping"] = same == sorted(row_ids)
            compare["question_text"] = sorted({r["hop2_question_multi"] for r in q_rows}) == sorted(
                stored.loc[query_id, "question_texts"])
            summary["queries"][query_id] = {"construction": ref["construction"], "R1": sorted(ref["R1"]),
                                            "R2": sorted(ref["R2"]), "sizes": {k: len(ref[k]) for k in
                                            ("B_q", "T_q", "G_q", "A_star_q")}, "matches_stored": compare}
            refs[query_id] = ref
        ref = refs[query_id]
        if episode not in cache:
            record = json.loads((run / f"{episode}.json").read_text(encoding="utf-8"))
            if record["status"] != "SUCCESS":
                raise ValueError(f"{episode}: audit episode is not SUCCESS")
            edges, appeared = trace_graph(record)
            stored_edges = {(e["u"], e["label"], e["v"]): e["creation_index"] for e in record["trace_graph"]}
            bad_edges = sorted(f"{u}-{r}-{v}" for u, r, v in edges if (r, v) not in kg.adj.get(u, set()))
            parsed = [e for e in record["log_events"] if e.get("event") == "FINAL_PARSED"]
            if len(parsed) != 1:
                raise ValueError(f"{episode}: expected one FINAL_PARSED event")
            answers, seen = [], set()
            for item in parsed[0]["parsed"]["answers"]:
                x = kg.resolve_agent(item, ref["type_t"])
                key = x if x is not None else ("unresolved", json.dumps(item, sort_keys=True))
                if key not in seen:  # §12: duplicates removed after normalization
                    seen.add(key)
                    answers.append((x, item))
            cache[episode] = {"edges": edges, "appeared": appeared, "answers": answers}
            summary["episodes"][episode] = {
                "trace_graph_matches_record": edges == stored_edges,
                "appeared_matches_record": appeared == set(map(str, record["appeared_entities"])),
                "edges_not_in_primekg": bad_edges, "answers_after_normalization": len(answers),
                "audit_rows": sum(r["episode"] == episode for r in sheet)}
        info = cache[episode]
        answer_id = row["answer_id"]
        x = None if answer_id.startswith("unresolved:") else answer_id
        if x is not None and x not in {a for a, _ in info["answers"]}:
            raise ValueError(f"{episode}: sheet answer {answer_id} not among independently normalized answers")
        a, b, path = labels(kg, ref, info["edges"], info["appeared"], x)
        rendered = render(path)
        ok_a, ok_b, ok_p = a == row["label_A"], b == row["label_B"], rendered == row["primary_path"]
        summary["label_A_agree"] += ok_a
        summary["label_B_agree"] += ok_b
        summary["path_agree"] += ok_p
        if not (ok_a and ok_b and ok_p):
            summary["disagreements"].append({"episode": episode, "answer_id": answer_id,
                                             "code": [row["label_A"], row["label_B"], row["primary_path"]],
                                             "independent": [a, b, rendered]})
        note = "agrees with code" if ok_a and ok_b and ok_p else "DISAGREES with code (see JSON)"
        out_rows.append({**{k: row[k] for k in MACHINE}, "independent_label_A": a,
                         "independent_label_B": b, "independent_primary_path": rendered,
                         "agree_A": ok_a, "agree_B": ok_b, "agree_path": ok_p, "note": note})
    # Every independently normalized answer of each audit episode must appear on the sheet.
    for episode, info in cache.items():
        if len(info["answers"]) != summary["episodes"][episode]["audit_rows"]:
            summary["disagreements"].append({"episode": episode, "issue": "answer count differs from sheet",
                                             "independent": len(info["answers"]),
                                             "sheet": summary["episodes"][episode]["audit_rows"]})

    analysis = run / "analysis"
    if not args.dry_run:  # write-once outputs
        with open(analysis / "independent_audit_check.csv", "x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(out_rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(out_rows)
        with open(analysis / "independent_audit_check.json", "x", encoding="utf-8", newline="\n") as handle:
            json.dump(summary, handle, indent=2, sort_keys=True)
            handle.write("\n")

    if args.fill and not args.dry_run:
        if any(row[k] for row in sheet for k in MINE):
            raise ValueError("audit sheet already has my_label_* / notes values; refusing to overwrite")
        for row, mine in zip(sheet, out_rows):
            assert all(row[k] == mine[k] for k in MACHINE)
            row["my_label_A"], row["my_label_B"] = mine["independent_label_A"], mine["independent_label_B"]
            row["notes"] = f"{WHO}; {mine['note']}"
        buffer = io.StringIO()
        ending = "\r\n" if "\r\n" in sheet_text else "\n"  # keep the sheet's own line ending
        writer = csv.DictWriter(buffer, fieldnames=list(sheet[0]), lineterminator=ending)
        writer.writeheader()
        writer.writerows(sheet)
        reread = list(csv.DictReader(io.StringIO(buffer.getvalue())))
        original = list(csv.DictReader(io.StringIO(sheet_text)))
        assert [[r[k] for k in MACHINE] for r in reread] == [[r[k] for k in MACHINE] for r in original]
        sheet_path.write_text(buffer.getvalue(), encoding="utf-8", newline="")

    print(json.dumps({k: summary[k] for k in ("rows", "label_A_agree", "label_B_agree", "path_agree")}))
    print(json.dumps(summary["queries"], indent=1))
    print(json.dumps(summary["episodes"], indent=1))
    print(f"disagreements: {len(summary['disagreements'])}")
    for d in summary["disagreements"][:20]:
        print(json.dumps(d))
    return 0 if not summary["disagreements"] else 1


if __name__ == "__main__":
    sys.exit(main())
