import hashlib
import json
from pathlib import Path

from cofail_kg.agents.tool_schemas import TOOL_SCHEMAS, TOOL_VERSION
from cofail_kg.utils.frozen_hashes import read_frozen_hashes


def test_t1_source_bytes_match_the_frozen_identity():
    root = Path(__file__).resolve().parents[1]
    source = root / "src/cofail_kg/agents/tool_schemas.py"
    frozen = read_frozen_hashes(root / "configs/frozen_hashes.yaml")
    assert hashlib.sha256(source.read_bytes()).hexdigest() == frozen["tools"]


def test_ollama_function_contract_has_only_the_two_protocol_tools():
    assert TOOL_VERSION == "T1"
    assert json.loads(json.dumps(TOOL_SCHEMAS)) == TOOL_SCHEMAS
    assert [tool["type"] for tool in TOOL_SCHEMAS] == ["function", "function"]
    inspect, neighbors = [tool["function"] for tool in TOOL_SCHEMAS]
    assert [inspect["name"], neighbors["name"]] == ["inspect_entity", "get_neighbors"]
    assert inspect["parameters"]["required"] == ["entity_id"]
    assert set(inspect["parameters"]["properties"]) == {"entity_id"}
    assert neighbors["parameters"]["required"] == ["entity_id", "relation"]
    props = neighbors["parameters"]["properties"]
    assert set(props) == {"entity_id", "relation", "neighbor_type", "page"}
    assert props["page"]["type"] == "integer" and props["page"]["default"] == 1
    assert props["neighbor_type"]["type"] == "string"
    for function in (inspect, neighbors):
        assert function["parameters"]["type"] == "object"
        assert function["description"]
        for prop in function["parameters"]["properties"].values():
            assert prop["description"]
            assert "enum" not in prop


def test_descriptions_do_not_embed_dataset_or_evaluator_hints():
    text = json.dumps(TOOL_SCHEMAS).lower()
    for forbidden in ("biohopr", "gold", "bridge", "answer", "drug_protein",
                      "disease_protein", "relation_type", "data/processed", "direction"):
        assert forbidden not in text
