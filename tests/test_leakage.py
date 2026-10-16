"""S15 leakage audit, protocol §§8, 9.3, 10, 19.1. No model calls."""

import ast
import builtins
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import random
import re
import socket
from unittest.mock import Mock

import pandas as pd
import pyarrow.parquet as pq
import pytest

from cofail_kg.agents import run_agent as runner
from cofail_kg.agents.kg_env import KGEnvironment, ToolConfig
from cofail_kg.agents.prompts import P1_TEMPLATE, USER_TEMPLATE, prompt_sha256
from cofail_kg.kg.primekg_index import PrimeKGIndex
from cofail_kg.utils.frozen_hashes import read_frozen_hashes

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"query_id", "question_text", "start_name", "start_id"}
AGENT_MODULES = ("agents.kg_env", "agents.tool_schemas", "agents.prompts", "agents.run_agent")
EVALUATOR_LABELS = (
    "UNRESOLVED", "GOLD", "GOLD_BRIDGE_EXTRA", "ALT_VALID", "OFF_QUESTION",
    "NOT_APPLICABLE", "UNGROUNDED", "SUPPORTED", "PATH_INVALID", "KG_UNSUPPORTED",
    "SHORTCUT", "WRONG_RELATION_HOP1", "WRONG_BRIDGE_TYPE", "WRONG_RELATION_HOP2",
    "WRONG_TARGET_TYPE", "WRONG_HOP_COUNT",
)


def scan_surface(text, terms):
    """Protocol §19.1: literal whole words; only short *names* need manual review."""
    short = sorted({term for kind, term in terms if kind == "name" and len(term) < 4})
    hits = [(kind, term) for kind, term in terms
            if not (kind == "name" and len(term) < 4)
            and re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.IGNORECASE)]
    return hits, short


def forbidden_terms(query, spec, index):
    names = set(query["gold_bridge_names"] + query["gold_answer_names"])
    gold_ids = set(query["gold_bridges"] + query["A_star_q"])
    names.update(index.get_node(n)["name"] for n in gold_ids | set(query["B_q"]) | set(query["T_q"]))
    labels = set(spec["R1"] + spec["R2"]) | {query["relation_type"]} | set(EVALUATOR_LABELS)
    terms = [(kind, term) for kind, values in (("name", names), ("id", gold_ids), ("label", labels))
             for term in sorted(values)]
    assert all(isinstance(term, str) and term for _, term in terms), "Missing forbidden term"
    return terms


def scan_starting_line(line, row, query, spec, index):
    """Protocol §19.1(a), 2026-10-16 amendment: exempt only canonical source-name spans."""
    hits, short = scan_surface(line, forbidden_terms(query, spec, index))
    # Removing B_q leaves every term whose match must still fail, including homonyms.
    protected = forbidden_terms(query | {"B_q": []}, spec, index)
    gold = set(query["gold_bridges"] + query["A_star_q"])
    candidates = [index.get_node(n) for n in sorted(set(query["B_q"]) - gold, key=int)]
    name_start = len("Starting entity: ")
    name_end = name_start + len(row["start_name"])
    canonical = (row["start_id"] == query["s"]
                 and row["start_name"] == index.get_node(query["s"])["name"]
                 and line.startswith("Starting entity: " + row["start_name"]))
    failures, overlaps = [], []
    for kind, term in hits:
        eligible = [n for n in candidates if kind == "name"
                    and re.fullmatch(re.escape(n["name"]), term, re.IGNORECASE)
                    and not any(re.fullmatch(re.escape(t), term, re.IGNORECASE) for _, t in protected)]
        for match in re.finditer(r"(?<!\w)" + re.escape(term) + r"(?!\w)", line, re.IGNORECASE):
            span = list(match.span())
            if canonical and eligible and name_start <= span[0] and span[1] <= name_end:
                overlaps.extend(dict(term=term, node_id=n["id"], node_type=n["type"], span=span) for n in eligible)
            else:
                failures.append(dict(kind=kind, term=term, span=span))
    return failures, overlaps, short


def overlap_record(split, row, query, matches, index):
    return dict(flag="SOURCE_NAME_OVERLAP", split=split, query_id=row["query_id"],
                relation_type=query["relation_type"], start_id=row["start_id"], start_name=row["start_name"],
                matches=matches, gold_bridges=[{k: index.get_node(n)[k] for k in ("id", "name", "type")}
                                              for n in query["gold_bridges"]],
                bq_size=len(query["B_q"]), tq_size=len(query["T_q"]))


def read_sheet(path):
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row = json.loads(line)
        assert isinstance(row, dict) and set(row) == FIELDS, f"{path}:{line_number}: exactly four fields required"
        assert all(isinstance(v, str) and v.strip() for v in row.values())
        assert re.fullmatch(r"0|[1-9][0-9]*", row["start_id"])
        rows.append(row)
    assert rows and len({r["query_id"] for r in rows}) == len(rows), "Empty/duplicate query sheet"
    return rows


def inspect_source(source, module):
    """Follow static imports and inventory I/O sites; dynamic imports fail closed."""
    tree, imports, sites = ast.parse(source), set(), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                base = importlib.util.resolve_name("." * node.level + base, module.rpartition(".")[0])
            imports.add(base)
            imports.update(base + "." + alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            assert name.split(".")[-1] not in {"__import__", "import_module"}, f"Dynamic import: {module}:{node.lineno}"
            if name.split(".")[-1] in {"open", "read_text", "read_bytes", "read_parquet", "read_csv",
                                          "load_episode_record", "read_frozen_hashes", "file_hash"}:
                sites.append({"module": module, "line": node.lineno, "call": ast.unparse(node)})
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.replace("\\", "/")
            assert not any(s in value for s in ("data/processed/", "results/semantics/")), f"Evaluator path: {module}:{node.lineno}"
    assert not any(n == "cofail_kg.evaluation" or n.startswith("cofail_kg.evaluation.") for n in imports), f"evaluation import: {module}"
    return imports, sites


def inspect_modules(package, entries):
    pending = ["cofail_kg." + name for name in entries]
    visited, sites = set(), []
    while pending:
        module = pending.pop()
        if module in visited:
            continue
        parts = module.split(".")[1:]
        path = package.joinpath(*parts).with_suffix(".py")
        if not path.is_file():
            path = package.joinpath(*parts, "__init__.py")
        if not path.is_file():
            continue
        visited.add(module)
        imports, calls = inspect_source(path.read_text(encoding="utf-8"), module)
        sites.extend(calls)
        pending.extend(n for n in imports if n.startswith("cofail_kg."))
        pending.extend(".".join(module.split(".")[:i]) for i in range(1, len(module.split("."))))
    return {"modules": sorted(visited), "io_sites": sorted(sites, key=lambda s: (s["module"], s["line"]))}


@contextmanager
def guarded_agent_io(monkeypatch, directories, files):
    """Guard application I/O entry points, including pathlib and pandas native Parquet."""
    directories, files = [p.resolve() for p in directories], {p.resolve() for p in files}
    reads = []

    def check(path):
        assert isinstance(path, (str, bytes, os.PathLike)), f"Forbidden agent file object: {path!r}"
        resolved = Path(os.fsdecode(path)).resolve()
        assert resolved in files or any(resolved.is_relative_to(d) for d in directories), f"Forbidden agent read: {resolved}"
        reads.append(str(resolved))

    def wrap_open(original):
        def guarded(path, mode="r", *args, **kwargs):
            check(path)
            assert not any(c in mode for c in "wax+"), f"Forbidden agent write: {path}"
            return original(path, mode, *args, **kwargs)
        return guarded

    original_os_open, original_parquet = os.open, pd.read_parquet

    def os_open(path, flags, *args, **kwargs):
        check(path)
        assert not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC), f"Forbidden agent write: {path}"
        return original_os_open(path, flags, *args, **kwargs)

    def parquet(path, *args, **kwargs):
        check(path)
        return original_parquet(path, *args, **kwargs)

    def no_network(*args, **kwargs):
        raise AssertionError("Network/model calls prohibited during S15")

    with monkeypatch.context() as patch:
        patch.setattr(builtins, "open", wrap_open(builtins.open))
        patch.setattr(io, "open", wrap_open(io.open))
        patch.setattr(os, "open", os_open)
        patch.setattr(pd, "read_parquet", parquet)
        patch.setattr(socket.socket, "connect", no_network)
        patch.setattr(socket.socket, "connect_ex", no_network)
        yield reads


def compare_neighbors(index, env, entity, label):
    expected = [{k: n[k] for k in ("id", "name", "type", "display_labels")}
                for n in index.neighbors(entity, label)]
    pages = max(1, (len(expected) + 49) // 50)
    for page in range(1, pages + 1):
        actual = env.get_neighbors(entity, label, page=page)
        assert actual == dict(items=expected[(page - 1) * 50:page * 50], total_count=len(expected),
                              page=page, page_size=50, has_more=page < pages), (entity, label, page)
    return {"entity": entity, "label": label, "neighbors": len(expected), "pages": pages}


def test_matcher_detects_leaks_and_reports_short_names():
    terms = [("name", "Alpha (beta)"), ("name", "ACE"), ("id", "12"),
             ("label", "r"), ("label", "OFF_QUESTION")]
    hits, short = scan_surface("ALPHA (BETA); 12 r off_question ACE", terms)
    assert hits == [("name", "Alpha (beta)"), ("id", "12"),
                    ("label", "r"), ("label", "OFF_QUESTION")]
    assert short == ["ACE"]
    assert scan_surface("xAlpha (beta)y 312 zr OFF_QUESTION_suffix", terms)[0] == []


@pytest.mark.parametrize("role,key", [("name", "gold_bridge_names"),
                                    ("name", "gold_answer_names"),
                                    ("id", "gold_bridges"), ("id", "A_star_q")])
def test_vocabulary_includes_each_gold_source(role, key):
    query = {"gold_bridge_names": [], "gold_answer_names": [], "gold_bridges": [],
             "A_star_q": [], "B_q": [], "T_q": [], "relation_type": "a:b:c"}
    query[key] = ["1234" if role == "id" else "Raw Alias"]
    index = Mock()
    index.get_node.return_value = {"name": "Canonical Name"}
    terms = forbidden_terms(query, {"R1": ["first"], "R2": ["second"]}, index)
    assert (role, query[key][0]) in terms
    assert ("label", "first") in terms and ("label", "second") in terms
    assert ("label", "a:b:c") in terms
    assert ("label", "OFF_QUESTION") in terms
    if role == "id":
        assert ("name", "Canonical Name") in terms


def test_vocabulary_includes_other_bridge_and_target_names():
    query = dict(gold_bridge_names=[], gold_answer_names=[], gold_bridges=[], A_star_q=[],
                 B_q=["1"], T_q=["2"], relation_type="a:b:c")
    index = Mock()
    index.get_node.side_effect = lambda n: {"name": {"1": "Other Bridge", "2": "Other Target"}[n]}
    terms = forbidden_terms(query, {"R1": [], "R2": []}, index)
    assert ("name", "Other Bridge") in terms and ("name", "Other Target") in terms


@pytest.fixture
def overlap_case():
    row = dict(query_id="synthetic", question_text="Unchanged question.", start_id="100",
               start_name="Folic acid deficiency")
    nodes = {"100": dict(id="100", name=row["start_name"], type="disease"),
             "101": dict(id="101", name="Folic acid", type="drug"),
             "102": dict(id="102", name="Gold bridge", type="drug"),
             "103": dict(id="103", name="Gold answer", type="phenotype"),
             "104": dict(id="104", name="Other target", type="phenotype")}
    query = dict(s="100", gold_bridge_names=["Gold bridge"], gold_answer_names=["Gold answer"],
                 gold_bridges=["102"], A_star_q=["103"], B_q=["101", "102"], T_q=["103", "104"],
                 relation_type="a:b:c")
    index = Mock()
    index.get_node.side_effect = lambda n: nodes[n]
    return row, query, {"R1": ["first"], "R2": ["second"]}, index, nodes


def test_overlap_exempts_only_canonical_non_gold_bridge_span(overlap_case):
    row, query, spec, index, _ = overlap_case
    line = f"Starting entity: {row['start_name']} (PrimeKG ID: 100)"
    failures, flags, short = scan_starting_line(line, row, query, spec, index)
    assert failures == [] and short == []
    assert len(flags) == 1 and flags[0]["node_id"] == "101"
    assert flags[0]["span"] == [17, 27]
    # The question deliberately lacks the canonical name; no question-text condition exists.
    assert row["start_name"] not in row["question_text"]


def test_overlap_repeated_outside_name_still_fails(overlap_case):
    row, query, spec, index, _ = overlap_case
    line = f"Starting entity: {row['start_name']} (PrimeKG ID: 100); FOLIC ACID"
    failures, flags, _ = scan_starting_line(line, row, query, spec, index)
    assert len(flags) == 1 and len(failures) == 1
    assert failures[0]["span"] == [line.rindex("FOLIC"), len(line)]


@pytest.mark.parametrize("role", ["gold_bridges", "A_star_q", "T_q", "gold_bridge_names", "gold_answer_names"])
def test_overlap_never_exempts_gold_or_target(overlap_case, role):
    row, query, spec, index, _ = overlap_case
    query[role].append("Folic acid" if role.endswith("names") else "101")
    failures, flags, _ = scan_starting_line(f"Starting entity: {row['start_name']}", row, query, spec, index)
    assert failures and not flags


def test_overlap_target_homonym_still_fails(overlap_case):
    row, query, spec, index, nodes = overlap_case
    nodes["104"]["name"] = "FOLIC ACID"
    failures, flags, _ = scan_starting_line(f"Starting entity: {row['start_name']}", row, query, spec, index)
    assert failures and not flags


@pytest.mark.parametrize("term", ["103", "first", "second", "a:b:c", "OFF_QUESTION"])
def test_overlap_never_exempts_id_or_label(overlap_case, term):
    row, query, spec, index, nodes = overlap_case
    row["start_name"] = nodes["100"]["name"] = term + " condition"
    nodes["101"]["name"] = term
    failures, flags, _ = scan_starting_line(f"Starting entity: {row['start_name']}", row, query, spec, index)
    assert failures and not flags


def test_overlap_requires_canonical_name(overlap_case):
    row, query, spec, index, _ = overlap_case
    row["start_name"] += " modified"
    failures, flags, _ = scan_starting_line(f"Starting entity: {row['start_name']}", row, query, spec, index)
    assert failures and not flags


def test_overlap_short_names_remain_manual_review(overlap_case):
    row, query, spec, index, nodes = overlap_case
    row["start_name"] = nodes["100"]["name"] = "ACE condition"
    nodes["101"]["name"] = "ACE"
    failures, flags, short = scan_starting_line(f"Starting entity: {row['start_name']}", row, query, spec, index)
    assert not failures and not flags and short == ["ACE"]


def test_overlap_allows_entire_name_shared_by_distinct_nodes(overlap_case):
    row, query, spec, index, nodes = overlap_case
    row["start_name"] = nodes["100"]["name"] = nodes["101"]["name"] = "Ewing sarcoma"
    failures, flags, _ = scan_starting_line(f"Starting entity: {row['start_name']}", row, query, spec, index)
    assert not failures and len(flags) == 1
    assert flags[0]["span"] == [17, 30]


def test_sheet_rejects_extra_fields(tmp_path):
    sheet = tmp_path / "sheet.jsonl"
    row = dict(query_id="Q", question_text="Question", start_name="Start", start_id="1")
    sheet.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert read_sheet(sheet) == [row]
    sheet.write_text(json.dumps(row | {"R1": ["secret"]}) + "\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="four fields"):
        read_sheet(sheet)


@pytest.mark.parametrize("source", [
    "import cofail_kg.evaluation.normalize as x",
    "from cofail_kg.evaluation import normalize",
    "from cofail_kg import evaluation",
    "from ..evaluation import normalize",
    "__import__('cofail_kg.evaluation')",
    "import importlib; importlib.import_module('cofail_kg.evaluation')",
    "open('data/processed/reference_queries.parquet')",
])
def test_source_checker_rejects_forbidden_access(source):
    with pytest.raises(AssertionError):
        inspect_source(source, "cofail_kg.agents.fake")


def test_source_checker_follows_local_imports(tmp_path):
    package = tmp_path / "cofail_kg"
    package.mkdir()
    (package / "entry.py").write_text("from cofail_kg import helper\n")
    (package / "helper.py").write_text("import cofail_kg.evaluation\n")
    with pytest.raises(AssertionError, match="evaluation"):
        inspect_modules(package, ["entry"])


@pytest.mark.parametrize("method", ["builtin", "path", "os", "parquet"])
def test_read_guard_rejects_evaluator_files(tmp_path, monkeypatch, method):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    secret = tmp_path / "reference.txt"
    secret.write_text("secret")
    with guarded_agent_io(monkeypatch, [allowed], []) as reads:
        with pytest.raises(AssertionError, match="Forbidden agent"):
            if method == "builtin":
                builtins.open(secret)
            elif method == "path":
                secret.read_text()
            elif method == "os":
                os.open(secret, os.O_RDONLY)
            else:
                pd.read_parquet(secret)
    assert not reads


def test_neighbor_checker_detects_changed_output():
    index = Mock()
    index.neighbors.return_value = [dict(id="1", name="One", type="gene", display_labels=["r"])]
    env = Mock()
    env.get_neighbors.return_value = dict(items=[], total_count=1, page=1, page_size=50, has_more=False)
    with pytest.raises(AssertionError):
        compare_neighbors(index, env, "0", "r")


def test_neighbor_checker_checks_later_pages_and_metadata():
    expected = [dict(id=str(n), name=str(n), type="gene", display_labels=["r"]) for n in range(51)]
    index = Mock()
    index.neighbors.return_value = expected
    env = Mock()
    replies = [dict(items=expected[:50], total_count=51, page=1, page_size=50, has_more=True),
               dict(items=expected[50:], total_count=51, page=2, page_size=50, has_more=False)]
    env.get_neighbors.side_effect = replies
    assert compare_neighbors(index, env, "0", "r")["pages"] == 2
    for key, bad in (("items", []), ("total_count", 50), ("page", 1), ("page_size", 49), ("has_more", True)):
        env.get_neighbors.side_effect = [replies[0], replies[1] | {key: bad}]
        with pytest.raises(AssertionError):
            compare_neighbors(index, env, "0", "r")


def test_guard_allows_sheet_read_but_denies_writes_and_network(tmp_path, monkeypatch):
    sheet = tmp_path / "sheet.jsonl"
    sheet.write_text("allowed", encoding="utf-8")
    with guarded_agent_io(monkeypatch, [], [sheet]) as reads:
        assert sheet.read_text(encoding="utf-8") == "allowed"
        with pytest.raises(AssertionError, match="write"):
            sheet.write_text("changed")
        with socket.socket() as sock:
            with pytest.raises(AssertionError, match="Network/model"):
                sock.connect(("127.0.0.1", 1))
    assert reads and sheet.read_text(encoding="utf-8") == "allowed"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def audit_inputs():
    frozen = read_frozen_hashes(ROOT / "configs/frozen_hashes.yaml")
    assert prompt_sha256() == frozen["prompt"]
    assert sha256(ROOT / "src/cofail_kg/agents/tool_schemas.py") == frozen["tools"]
    assert sha256(ROOT / "data/cache/primekg_metadata.json") == frozen["kg_fingerprint"]
    mapping_path = ROOT / "results/semantics/relation_mapping.json"
    assert sha256(mapping_path) == frozen["relation_mapping"]
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    assert mapping["frozen"] is True and mapping["d1"]["outcome"] == "PROCEED"
    summary = json.loads((ROOT / "data/processed/reference_summary.json").read_text(encoding="utf-8"))
    for key, frozen_key in (("biohopr_revision", "biohopr_revision"), ("kg_fingerprint", "kg_fingerprint"),
                            ("relation_mapping_sha256", "relation_mapping")):
        assert summary["provenance"][key] == frozen[frozen_key]
    for key in ("biohopr_revision", "kg_fingerprint"):
        assert mapping["provenance"][key] == frozen[key]
    sheets = {}
    for path in sorted((ROOT / "data/agent_inputs").glob("*.jsonl")):
        assert sha256(path) == frozen["manifests"][path.relative_to(ROOT).as_posix()]
        sheets[path.stem] = read_sheet(path)
    assert set(sheets) == {"screening", "smoke", "pilot", "expansion"}
    assert len(sheets["screening"]) == 20 and len(sheets["smoke"]) == 4
    refs = pq.read_table(ROOT / "data/processed/reference_queries.parquet").to_pylist()
    references = {q["query_id"]: q for q in refs}
    assert len(references) == len(refs)
    for split in sorted(sheets):
        path = ROOT / f"data/processed/manifests/{split}.jsonl"
        assert sha256(path) == frozen["manifests"][path.relative_to(ROOT).as_posix()]
        manifest = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert [q["query_id"] for q in manifest] == [q["query_id"] for q in sheets[split]]
        for row, selected in zip(sheets[split], manifest):
            q = references[row["query_id"]]
            assert q["s"] == row["start_id"] and row["question_text"] in q["question_texts"]
            assert q["relation_type"] == selected["relation_type"]
            assert not q["unresolved_names"]
    paths = [ROOT / "configs/frozen_hashes.yaml", mapping_path,
             ROOT / "data/processed/reference_queries.parquet",
             ROOT / "data/processed/reference_summary.json"]
    paths.extend(ROOT / name for name in frozen["manifests"])
    print("S15_PREFLIGHT=" + json.dumps({"hashes": {p.relative_to(ROOT).as_posix(): sha256(p) for p in paths},
                                        "frozen": frozen, "sheet_counts": {k: len(v) for k, v in sheets.items()}}, sort_keys=True))
    return frozen, mapping, sheets, references


@pytest.fixture(scope="module")
def audited_index(audit_inputs):
    with pytest.MonkeyPatch.context() as patch:
        with guarded_agent_io(patch, [ROOT / "data/cache"], []) as reads:
            index = PrimeKGIndex(ROOT / "data/cache")
    print("S15_CACHE_READS=" + json.dumps(sorted(set(reads))))
    return index


class InitialMessagesCaptured(BaseException):
    """Escape the runner's Exception handler before inference or episode saving."""


def capture_initial_messages(query_id, config, agent, index, monkeypatch):
    captured = []

    def capture(tag, messages, tools, options):
        captured.extend(deepcopy(messages))
        raise InitialMessagesCaptured

    client = Mock()
    client.chat.side_effect = capture
    with monkeypatch.context() as patch:
        patch.setattr(runner, "OllamaClient", Mock(return_value=client))
        # The real cache constructor is separately exercised under the same I/O guard.
        patch.setattr(runner, "PrimeKGIndex", lambda path: index)
        patch.setattr(runner, "save_episode_record", lambda *a: pytest.fail("S15 must not save episodes"))
        with guarded_agent_io(patch, [ROOT / "data/cache"], [Path(config["agent_inputs"])]) as reads:
            with pytest.raises(InitialMessagesCaptured):
                runner.run_episode(query_id, agent, config)
        assert client.chat.call_count == 1
    return captured, sorted(set(reads))


def test_a_real_screening_and_smoke_messages(audit_inputs, audited_index, monkeypatch, tmp_path):
    frozen, mapping, sheets, references = audit_inputs
    failures, short_names, evidence, overlaps = [], [], [], []
    for split in ("screening", "smoke"):
        sheet = ROOT / f"data/agent_inputs/{split}.jsonl"
        config = dict(run_id="s15-message-only", runs_root=str(tmp_path / "runs"), agent_inputs=str(sheet),
                      agent_inputs_sha256=sha256(sheet), cache_dir=str(ROOT / "data/cache"),
                      prompt_sha256=frozen["prompt"], page_size=50, budget=30, temperature=0, seed=42,
                      num_ctx=8192, num_predict=4096, timeout_seconds=600, request_timeout_seconds=60,
                      base_url="http://127.0.0.1:1", tool_schema_sha256=frozen["tools"],
                      kg_fingerprint=frozen["kg_fingerprint"], biohopr_revision=frozen["biohopr_revision"],
                      git_commit="S15-test-only-no-episode")
        agent = dict(agent_id="S15-test", tag="fake:no-model", digest="not-a-real-model",
                     quantization="not-applicable", think=False)
        for row in sheets[split]:
            q = references[row["query_id"]]
            spec = mapping["per_type"][q["relation_type"]]
            assert spec["d1_status"] == "PASS" and not spec["excluded"]
            assert audited_index.get_node(row["start_id"])["name"] == row["start_name"]
            messages, reads = capture_initial_messages(row["query_id"], config, agent, audited_index, monkeypatch)
            assert messages == [dict(role="system", content=P1_TEMPLATE.replace("{PAGE_SIZE}", "50").replace("{BUDGET}", "30")),
                                dict(role="user", content=USER_TEMPLATE.format(QUESTION=row["question_text"],
                                                                              START_NAME=row["start_name"], START_ID=row["start_id"]))]
            terms = forbidden_terms(q, spec, audited_index)
            starting_line = messages[1]["content"][len(row["question_text"]) + 1:]
            hits, _ = scan_surface(messages[0]["content"], terms)
            failures.extend(dict(split=split, query_id=row["query_id"], surface="system", kind=k, term=t) for k, t in hits)
            line_failures, matches, short = scan_starting_line(starting_line, row, q, spec, audited_index)
            failures.extend(dict(split=split, query_id=row["query_id"], surface="starting_entity", **f) for f in line_failures)
            if matches:
                overlaps.append(overlap_record(split, row, q, matches, audited_index))
            short_names.extend(dict(split=split, query_id=row["query_id"], name=n,
                                    present_in_system=bool(scan_surface(messages[0]["content"], [("id", n)])[0]),
                                    present_in_starting_line=bool(scan_surface(starting_line, [("id", n)])[0])) for n in short)
            evidence.append(dict(split=split, query_id=row["query_id"], terms=len(terms), reads=reads, messages=messages))
    assert not (tmp_path / "runs").exists()
    print("S15_A=" + json.dumps(dict(queries=len(evidence), failures=failures, overlaps=overlaps,
                                    short_names=short_names, captures=evidence), sort_keys=True))
    print("EXACT SYSTEM MESSAGE:\n" + evidence[0]["messages"][0]["content"])
    print("EXACT USER MESSAGE:\n" + evidence[0]["messages"][1]["content"])
    print("SHORT NAMES FOR MANUAL REVIEW:\n" + json.dumps(short_names, indent=2))
    assert not failures, failures
    assert [(q["split"], q["query_id"]) for q in overlaps] == [("screening", "BH2_04007")]


def test_a_all_524_source_name_overlaps(audit_inputs, audited_index):
    _, mapping, sheets, references = audit_inputs
    overlaps, failures, short_names, type_counts, split_counts = [], [], [], {}, {}
    system = P1_TEMPLATE.replace("{PAGE_SIZE}", "50").replace("{BUDGET}", "30")
    for split, rows in sorted(sheets.items()):
        split_counts[split] = dict(rows=len(rows), flagged=0)
        for row in rows:
            q = references[row["query_id"]]
            spec = mapping["per_type"][q["relation_type"]]
            assert spec["d1_status"] == "PASS" and not spec["excluded"]
            counts = type_counts.setdefault(q["relation_type"], dict(rows=0, flagged=0))
            counts["rows"] += 1
            line = f"Starting entity: {row['start_name']} (PrimeKG ID: {row['start_id']})"
            hits, matches, short = scan_starting_line(line, row, q, spec, audited_index)
            failures.extend(dict(split=split, query_id=row["query_id"], surface="starting_entity", **f) for f in hits)
            system_hits, _ = scan_surface(system, forbidden_terms(q, spec, audited_index))
            failures.extend(dict(split=split, query_id=row["query_id"], surface="system", kind=k, term=t) for k, t in system_hits)
            if matches:
                overlaps.append(overlap_record(split, row, q, matches, audited_index))
                counts["flagged"] += 1
                split_counts[split]["flagged"] += 1
            short_names.extend(dict(split=split, query_id=row["query_id"], name=n,
                                    present_in_system=bool(scan_surface(system, [("id", n)])[0]),
                                    present_in_starting_line=bool(scan_surface(line, [("id", n)])[0])) for n in short)
    report = dict(rows=sum(len(rows) for rows in sheets.values()), flagged_queries=overlaps, failures=failures,
                  per_split=split_counts, per_relation_type=type_counts, short_names=short_names)
    print("S15_SOURCE_NAME_OVERLAP=" + json.dumps(report, sort_keys=True))
    assert report["rows"] == 524 and not failures, failures
    # Expected audit findings only; query IDs never participate in the exemption rule.
    assert {(q["split"], q["query_id"], m["node_id"]) for q in overlaps for m in q["matches"]} == {
        ("screening", "BH2_04007", "14678"), ("pilot", "BH2_05778", "29749"),
        ("expansion", "BH2_05971", "33562"), ("expansion", "BH2_06099", "33562"),
    }
    assert len(overlaps) == 4


def test_b_agent_import_isolation():
    report = inspect_modules(ROOT / "src/cofail_kg", AGENT_MODULES)
    assert all("cofail_kg." + name in report["modules"] for name in AGENT_MODULES)
    print("S15_B=" + json.dumps(report, sort_keys=True))


def test_c_all_agent_sheet_fields(audit_inputs):
    sheets = audit_inputs[2]
    print("S15_C=" + json.dumps({name: len(rows) for name, rows in sheets.items()}, sort_keys=True))
    assert sum(map(len, sheets.values())) == 524


def test_d_ten_real_neighbor_pairs(audited_index, monkeypatch):
    edges = audited_index._edges
    pairs = pd.concat([edges[[side, "relation"]].rename(columns={side: "entity"})
                       for side in ("x_index", "y_index")]).drop_duplicates().sort_values(["entity", "relation"])
    population = [(str(entity), str(label)) for entity, label in pairs.itertuples(index=False, name=None)]
    chosen = random.Random(42).sample(population, 10)
    reports = []
    with guarded_agent_io(monkeypatch, [ROOT / "data/cache"], []):
        for entity, label in chosen:
            count = len(audited_index.neighbors(entity, label))
            env = KGEnvironment(audited_index, ToolConfig(page_size=50, budget=max(30, (count + 49) // 50)))
            reports.append(compare_neighbors(audited_index, env, entity, label))
    assert len(set(chosen)) == 10
    print("S15_D=" + json.dumps(dict(seed=42, population=len(population), pairs=reports), sort_keys=True))
