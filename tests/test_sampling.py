import hashlib

import pytest

from cofail_kg.data.sampling import allocate_types, draw_samples, size_bin


def rows(single=100, multi=100):
    return [dict(query_id=f"q{i:04d}", relation_type="a" if i%2 else "b",
                 bridge_multiplicity="SINGLE_BRIDGE" if i<single else "MULTI_BRIDGE",
                 ambiguity_tag="NONE", target_count=10) for i in range(single+multi)]


def test_largest_remainder_ties_floor_and_capacity():
    assert allocate_types({"b":5,"a":5},1,0) == {"a":1,"b":0}
    assert allocate_types({"a":10,"b":20},8,1) == {"a":3,"b":5}
    assert allocate_types({"a":1,"b":100},100,1) == {"a":1,"b":99}
    with pytest.raises(ValueError,match="floor"):
        allocate_types({"a":5,"b":5},1,1)


def test_sizes_disjointness_quota_transfer_and_shortfall():
    samples, report = draw_samples(rows(4,30), [("first",10,5,5,0),("second",30,10,20,0)])
    assert len(samples["first"]) == 10 and len(samples["second"]) == 24
    assert report["first"]["by_multiplicity"] == {"SINGLE_BRIDGE":4,"MULTI_BRIDGE":6}
    assert report["second"]["shortfall"] == 6
    assert not ({r["query_id"] for r in samples["first"]}&{r["query_id"] for r in samples["second"]})


def test_hash_order_and_reversed_input_are_identical():
    source=rows(50,0)
    selected, report=draw_samples(source,[("one",5,5,0,0)])
    assert (selected,report)==draw_samples(list(reversed(source)),[("one",5,5,0,0)])
    for kind,n in [("a",3),("b",2)]:
        expected=sorted([r for r in source if r["relation_type"]==kind],
                        key=lambda r:hashlib.sha256(("42"+r["query_id"]).encode()).hexdigest())[:n]
        assert {r["query_id"] for r in selected["one"] if r["relation_type"]==kind}=={r["query_id"] for r in expected}


def test_floors_within_each_multiplicity_group_and_empty_input():
    samples, report=draw_samples(rows(30,30),[("pilot",8,4,4,1)])
    assert all(n>=1 for group in report["pilot"]["strata"].values() for n in group.values())
    empty, report=draw_samples([],[("empty",4,1,3,0)])
    assert empty["empty"]==[] and report["empty"]["shortfall"]==4


@pytest.mark.parametrize("n,label",[(1,"1–10"),(10,"1–10"),(11,"11–100"),(100,"11–100"),
                                    (101,"101–1,000"),(1000,"101–1,000"),(1001,"over 1,000")])
def test_size_bin_boundaries(n,label):
    assert size_bin(n)==label


def test_invalid_population_fails():
    with pytest.raises(ValueError,match="Duplicate"):
        draw_samples([rows()[0]]*2)
    bad=rows(1,0)
    bad[0]["bridge_multiplicity"]="NO_BRIDGE"
    with pytest.raises(ValueError,match="multiplicity"):
        draw_samples(bad)


def test_artifact_schema_byte_identical_rerun_and_frozen_hashes(tmp_path):
    import importlib.util
    import json
    from pathlib import Path
    from cofail_kg.utils.frozen_hashes import read_frozen_hashes,write_once
    path=Path(__file__).resolve().parents[1]/"scripts/10_make_samples.py"
    spec=importlib.util.spec_from_file_location("s10",path)
    script=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    source=rows(600,600)
    selected,reports=draw_samples(source)
    references={r["query_id"]:dict(query_id=r["query_id"],s="1",Type_S="kind",
        question_texts=["Name all targets"],relation_type=r["relation_type"],T_q=[str(i) for i in range(10)],
        B_q=["2"] if r["bridge_multiplicity"]=="SINGLE_BRIDGE" else ["2","3"]) for r in source}
    nodes={"1":{"node_type":"kind","node_name":"Source"}}
    artifacts,hashes=script.make_artifacts(selected,reports,references,nodes,{})
    assert (artifacts,hashes)==script.make_artifacts(selected,reports,references,nodes,{})
    for name in selected:
        sheet=[json.loads(line) for line in artifacts[f"data/agent_inputs/{name}.jsonl"].splitlines()]
        manifest=[json.loads(line) for line in artifacts[f"data/processed/manifests/{name}.jsonl"].splitlines()]
        assert all(set(r)=={"query_id","question_text","start_name","start_id"} for r in sheet)
        assert all(set(r)=={"query_id","relation_type","multiplicity","ambiguity_tag","tq_size_bin"} for r in manifest)
        assert [r["query_id"] for r in sheet]==[r["query_id"] for r in manifest]
    frozen=tmp_path/"configs/frozen_hashes.yaml"
    write_once(frozen,"existing","preserve")
    (tmp_path/"configs/pilot.yaml").write_text("# placeholder\n")
    script.publish(tmp_path,artifacts,hashes)
    before={p:(tmp_path/p).read_bytes() for p in artifacts}
    frozen_before=frozen.read_bytes()
    script.publish(tmp_path,artifacts,hashes)
    assert frozen.read_bytes()==frozen_before
    assert read_frozen_hashes(frozen)=={"existing":"preserve","manifests":hashes}
    assert before=={p:(tmp_path/p).read_bytes() for p in artifacts}
    with pytest.raises(ValueError,match="Frozen"):
        script.publish(tmp_path,artifacts,{"changed":"hash"})
    changed={**artifacts,"data/processed/manifests/sampling_report.md":b"changed"}
    with pytest.raises(FileExistsError,match="differs"):
        script.publish(tmp_path,changed,hashes)
