"""S25 audit double-check (offline, read-only): independent re-derivation of answer normalization, Label A,
Label B, H1, the primary path and reason codes, for every answer of every smoke_panel episode.

Deliberately does NOT import anything from cofail_kg (no evaluation, trace or normalization code). It
rebuilds TG_i and "appeared" from the raw call_log (protocol §11), normalizes the raw final output (§12
agent policy), and applies §13, §14.1, §14.2 (full total order) and §14.3 from the protocol text. It
then compares with (1) results/runs/smoke_panel/audit_sheet.csv and (2) the saved per-episode metrics.

This supplements the researcher's D4 manual audit; it does not replace it.
Writes label_checks.json and walkthrough/<episode>.md next to this file.
"""
from collections import defaultdict, deque
import csv
import json
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "results/runs/smoke_panel"
HERE = Path(__file__).parent
WALK = HERE / "walkthrough"


def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text)).lower()).strip()


def parse_final(raw):
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def main():
    refs = {q["query_id"]: q for q in pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()}
    mapping = json.loads((ROOT / "results/semantics/relation_mapping.json").read_text(encoding="utf-8"))["per_type"]
    nodes = pd.read_parquet(ROOT / "data/cache/primekg_nodes.parquet", columns=["node_index", "node_type", "node_name"])
    ids = nodes["node_index"].astype(str).tolist()
    ntype = dict(zip(ids, nodes["node_type"]))
    nname = dict(zip(ids, nodes["node_name"]))
    by_name = defaultdict(list)
    for i, name in zip(ids, nodes["node_name"]):
        by_name[norm(name)].append(i)

    sheet = defaultdict(dict)
    sheet_path = RUN / "audit_sheet.csv"  # absent for runs without panel analysis (e.g. exploratory runs)
    for row in (csv.DictReader(sheet_path.open(encoding="utf-8")) if sheet_path.exists() else []):
        sheet[row["episode"]][row["answer_id"]] = row

    WALK.mkdir(exist_ok=True)
    results, problems = [], []
    for rec_path in sorted(RUN.glob("BH2_*__a*.json")):
        episode = rec_path.stem
        record = json.loads(rec_path.read_text(encoding="utf-8"))
        q, agent = record["query_id"], record["agent_id"]
        metric_path = RUN / "analysis/metrics" / agent / f"{q}.json"
        metric = json.loads(metric_path.read_text(encoding="utf-8")) if metric_path.exists() else None
        if record["status"] != "SUCCESS":
            results.append({"episode": episode, "status": record["status"], "checked": False})
            continue
        ref = refs[q]
        r1, r2 = set(mapping[ref["relation_type"]]["R1"]), set(mapping[ref["relation_type"]]["R2"])
        s, tb, tt = str(ref["s"]), ref["Type_B"], ref["Type_T"]
        a_star, g_q, t_q = set(map(str, ref["A_star_q"])), set(map(str, ref["G_q"])), set(map(str, ref["T_q"]))

        # §11 trace graph and appearance, from the raw call log.
        appeared, edge_ci = set(), {}
        for ci, call in enumerate(record["call_log"]):
            if not call["success"]:
                continue
            if call["tool"] == "inspect_entity":
                appeared.add(str(call["result"]["id"]))
            elif call["tool"] == "get_neighbors":
                u, r = str(call["arguments"]["entity_id"]), call["arguments"]["relation"]
                for item in call["result"]["items"]:
                    v = str(item["id"])
                    appeared.add(v)
                    edge_ci.setdefault((u, r, v), ci)
        out = defaultdict(list)
        for (u, r, v), ci in edge_ci.items():
            out[u].append((r, v, ci))

        # Cross-check our TG_i against the record's stored trace_graph (creation-index convention).
        stored = {(e["u"], e["label"], e["v"]): e["creation_index"] for e in record["trace_graph"]}
        tg_match = set(stored) == set(edge_ci)
        ci_offset = {stored[k] - edge_ci[k] for k in stored if k in edge_ci}

        # §12 agent policy.
        submitted = parse_final(record["raw_final_output"]).get("answers", [])
        resolved, seen = [], set()
        for idx, item in enumerate(submitted):
            node, how = None, None
            raw_id = item.get("id") if isinstance(item, dict) else None
            if raw_id is not None and str(raw_id).strip() in ntype:
                node, how = str(raw_id).strip(), "ID"
            else:
                name = norm(item.get("name", "")) if isinstance(item, dict) else norm(item)
                cands = by_name.get(name, [])
                typed = [c for c in cands if ntype[c] == tt]
                if len(typed) == 1:
                    node, how = typed[0], "NAME_TYPE_T"
                elif tt == "disease" and not [c for c in cands if ntype[c] == "disease"] and \
                        len([c for c in by_name.get(norm(name + " (disease)"), []) if ntype[c] == "disease"]) == 1:
                    node, how = [c for c in by_name[norm(name + " (disease)")] if ntype[c] == "disease"][0], "NAME_SUFFIX"
                elif len(cands) == 1:
                    node, how = cands[0], "NAME_ANY_TYPE"
                else:
                    how = "UNRESOLVED_AMBIGUOUS" if cands else "UNRESOLVED_NO_MATCH"
            key = node if node is not None else f"UNRESOLVED#{idx}"
            if node is not None and node in seen:
                continue
            seen.add(key)
            resolved.append((idx, node, how))

        bridges = sorted({v for (u, r, v) in edge_ci if u == s and r in r1 and v != s and ntype.get(v) == tb}, key=int)

        def shortest_paths(x):
            """All shortest directed s->x paths (edge lists). Length 0 when x == s."""
            if x == s:
                return [[]]
            dist, dq = {s: 0}, deque([s])
            while dq:
                u = dq.popleft()
                for _, v, _ in out[u]:
                    if v not in dist:
                        dist[v] = dist[u] + 1
                        dq.append(v)
            if x not in dist:
                return []
            paths = []

            def walk(u, acc):
                if u == x:
                    paths.append(list(acc))
                    return
                for r, v, ci in out[u]:
                    if dist.get(v) == dist[u] + 1 and dist[v] <= dist[x]:
                        acc.append((u, r, v, ci))
                        walk(v, acc)
                        acc.pop()
            walk(s, [])
            return paths

        def codes(path, x):
            n, c = len(path), set()
            if n == 1 and ntype[x] == tt:
                c.add("SHORTCUT")
            if n == 2:
                if path[0][1] not in r1:
                    c.add("WRONG_RELATION_HOP1")
                if ntype[path[0][2]] != tb:
                    c.add("WRONG_BRIDGE_TYPE")
                if path[1][1] not in r2:
                    c.add("WRONG_RELATION_HOP2")
            if n >= 1 and ntype[x] != tt:
                c.add("WRONG_TARGET_TYPE")
            if n != 2 and not (n == 1 and ntype[x] == tt):
                c.add("WRONG_HOP_COUNT")
            return c

        def simple_paths_le3(x):
            found = [[]] if x == s else []

            def dfs(u, acc, visited):
                if len(acc) == 3:
                    return
                for r, v, ci in out[u]:
                    if v in visited:
                        continue
                    acc.append((u, r, v, ci))
                    if v == x:
                        found.append(list(acc))
                    else:
                        visited.add(v)
                        dfs(v, acc, visited)
                        visited.discard(v)
                    acc.pop()
            dfs(s, [], {s})
            return found

        metric_by_idx = {a["submitted_index"]: a for a in metric["answers"]} if metric else {}
        ep_rows = []
        for idx, x, how in resolved:
            if x is None:
                la = lb = "UNRESOLVED"
                lb = "NOT_APPLICABLE"
                h1, prim, pcodes, allcodes, support = 0, None, [], [], []
            else:
                la = ("GOLD" if x in a_star else "GOLD_BRIDGE_EXTRA" if x in g_q
                      else "ALT_VALID" if x in t_q else "OFF_QUESTION")
                support = [b for b in bridges for r, v, _ in out[b] if v == x and r in r2 and x != s and ntype[x] == tt]
                sps = shortest_paths(x)
                if x not in appeared:
                    lb = "UNGROUNDED"
                elif support:
                    lb = "SUPPORTED"
                elif sps:
                    lb = "PATH_INVALID"
                else:
                    lb = "KG_UNSUPPORTED"
                prim = None
                if sps:
                    prim = min(sps, key=lambda p: (len(p), max((e[3] for e in p), default=-1),
                                                   [(int(e[0]), e[1]) for e in p]))
                pcodes = sorted(codes(prim, x)) if lb == "PATH_INVALID" and prim is not None else []
                allcodes = sorted(set().union(*[codes(p, x) for p in simple_paths_le3(x)])) if lb == "PATH_INVALID" else []
                h1 = 0
                if lb in ("SUPPORTED", "PATH_INVALID") and x != s:
                    for b in bridges:
                        if b == x:
                            continue
                        reach, stack = {b}, [b]
                        while stack:
                            for _, v, _ in out[stack.pop()]:
                                if v != s and v not in reach:
                                    reach.add(v)
                                    stack.append(v)
                        if x in reach:
                            h1 = 1
                            break
            prim_str = " ; ".join(f"{u} -{r}-> {v}" for u, r, v, _ in prim) if prim else ""
            mine = {"label_a": la, "label_b": lb, "h1": h1, "primary_path": prim_str,
                    "primary_reason_codes": pcodes, "reason_codes": allcodes}
            saved = metric_by_idx.get(idx)
            diffs = []
            if saved is None:
                diffs.append("missing in saved metrics")
            else:
                if saved.get("node_id") not in (x, None) or (x is None and saved.get("node_id")):
                    diffs.append(f"node_id {saved.get('node_id')} != {x}")
                for k in ("label_a", "label_b", "h1"):
                    if saved.get(k) != mine[k]:
                        diffs.append(f"{k} saved={saved.get(k)} mine={mine[k]}")
                sp = " ; ".join(f"{e['u']} -{e['label']}-> {e['v']}" for e in (saved.get("primary_path") or []))
                if sp != prim_str:
                    diffs.append(f"primary_path saved=[{sp}] mine=[{prim_str}]")
                if sorted(saved.get("primary_reason_codes") or []) != pcodes:
                    diffs.append(f"primary_reason_codes saved={saved.get('primary_reason_codes')} mine={pcodes}")
                if sorted(saved.get("reason_codes") or []) != allcodes:
                    diffs.append(f"reason_codes saved={saved.get('reason_codes')} mine={allcodes}")
            sheet_row = sheet.get(episode, {}).get(x) if x else None
            if episode in sheet and x:
                if sheet_row is None:
                    diffs.append("answer missing from audit sheet")
                else:
                    if sheet_row["label_A"] != la or sheet_row["label_B"] != lb:
                        diffs.append(f"sheet labels {sheet_row['label_A']}/{sheet_row['label_B']} != {la}/{lb}")
                    if sheet_row["primary_path"] != prim_str:
                        diffs.append(f"sheet primary_path [{sheet_row['primary_path']}] != [{prim_str}]")
            row = {"episode": episode, "submitted_index": idx, "submitted": submitted[idx], "normalized_by": how,
                   "answer_id": x, "answer_name": nname.get(x), "answer_type": ntype.get(x),
                   "in_A_star_q": x in a_star, "in_G_q": x in g_q, "in_T_q": x in t_q, "appeared": x in appeared,
                   "supporting_bridges": sorted(set(support), key=int)[:5], "mine": mine, "diffs": diffs,
                   "in_audit_sheet": sheet_row is not None}
            ep_rows.append(row)
            if diffs:
                problems.append(row)
        if episode in sheet:
            extra = set(sheet[episode]) - {x for _, x, _ in resolved if x}
            for e in sorted(extra):
                problems.append({"episode": episode, "answer_id": e, "diffs": ["in audit sheet but not a resolved answer"]})
        results.append({"episode": episode, "status": record["status"], "checked": True, "tg_matches_stored": tg_match,
                        "creation_index_offset_vs_stored": sorted(ci_offset), "answers": ep_rows})

        if episode in sheet:
            lines = [f"# {episode}", "",
                     f"- Relation type: `{ref['relation_type']}`; start s = {s} ({nname[s]}, {ntype[s]})",
                     f"- Type_B = {tb}; Type_T = {tt}; R1 = {sorted(r1)}; R2 = {sorted(r2)}",
                     f"- |A*_q| = {len(a_star)}, |G_q| = {len(g_q)}, |T_q| = {len(t_q)}",
                     f"- Successful calls: {sum(c['success'] for c in record['call_log'])}; TG_i edges: {len(edge_ci)}",
                     f"- R1 bridges reached from s (Type_B): {len(bridges)} -> {bridges[:20]}{' ...' if len(bridges) > 20 else ''}",
                     "", "| # | answer | name | type | A*_q | T_q | appeared | bridge used | Label A | Label B | agrees |",
                     "|---|---|---|---|---|---|---|---|---|---|---|"]
            for r in ep_rows:
                lines.append(f"| {r['submitted_index']} | {r['answer_id']} | {r['answer_name']} | {r['answer_type']} | "
                             f"{'yes' if r['in_A_star_q'] else 'no'} | {'yes' if r['in_T_q'] else 'no'} | "
                             f"{'yes' if r['appeared'] else 'no'} | {', '.join(r['supporting_bridges'][:2]) or '-'} | "
                             f"{r['mine']['label_a']} | {r['mine']['label_b']} | {'yes' if not r['diffs'] else 'NO: ' + '; '.join(r['diffs'])} |")
            (WALK / f"{episode}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (HERE / "label_checks.json").write_text(json.dumps({"episodes": results, "problems": problems}, indent=2) + "\n",
                                            encoding="utf-8")
    checked = [a for e in results if e.get("checked") for a in e["answers"]]
    print(f"episodes={len(results)} checked={sum(bool(e.get('checked')) for e in results)} answers={len(checked)} "
          f"audit_rows_checked={sum(a['in_audit_sheet'] for a in checked)} problems={len(problems)}")
    for e in results:
        if e.get("checked"):
            print(e["episode"], "TG match", e["tg_matches_stored"], "ci offset", e["creation_index_offset_vs_stored"])
    for p in problems[:30]:
        print("PROBLEM", p["episode"], p.get("answer_id"), p["diffs"])


if __name__ == "__main__":
    main()
