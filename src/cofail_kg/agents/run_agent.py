"""One independent episode, native tools and write-once trace (protocol §9, §11, §19).

The launcher supplies provenance/configuration. This module reads only the agent
sheet and PrimeKG cache; evaluator data never enters its conversation or imports.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import time

from cofail_kg.agents.kg_env import BUDGET_EXHAUSTED, KGEnvironment, ToolConfig
from cofail_kg.agents.ollama_client import OllamaClient, OllamaError
from cofail_kg.agents.prompts import P1_TEMPLATE, USER_TEMPLATE, PROMPT_VERSION, prompt_sha256
from cofail_kg.agents.tool_schemas import TOOL_SCHEMAS, TOOL_VERSION
from cofail_kg.agents.trace import make_episode_record, record_path, save_episode_record
from cofail_kg.kg.primekg_index import PrimeKGIndex

REPROMPT = ("Your last message was not valid JSON in the required format. "
            "Reply with only the JSON object.")


def _reject_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def parse_final(text, events):
    """Parse §9.4 only; normalization and scientific labels belong to later stages."""
    if not isinstance(text, str):
        raise ValueError("Final content must be text")
    text = text.strip()
    fence = re.fullmatch(r"```[^\r\n`]*\r?\n(.*?)\r?\n```", text, re.DOTALL)
    if fence:
        text = fence[1]
    value = json.loads(text, parse_constant=_reject_constant)
    if (not isinstance(value, dict) or value.get("status") not in ("answered", "no_answer")
            or not isinstance(value.get("answers"), list)):
        raise ValueError("Expected status and answers list")
    answers = []
    extras = []
    if keys := sorted(set(value) - {"status", "answers"}):
        extras.append({"location": "final", "keys": keys})
    for position, item in enumerate(value["answers"]):
        if (not isinstance(item, dict) or type(item.get("id")) not in (str, int)
                or not isinstance(item.get("name"), str)):
            raise ValueError("Each answer needs a string/integer id and string name")
        answers.append({"id": item["id"], "name": item["name"]})
        if keys := sorted(set(item) - {"id", "name"}):
            extras.append({"location": f"answers[{position}]", "keys": keys})
    if extras:
        events.append({"event": "EXTRA_KEYS", "details": extras})
    if value["status"] == "no_answer" and answers:
        events.append({"event": "NO_ANSWER_ITEMS_IGNORED", "items": answers})
        answers = []
    return {"status": value["status"], "answers": answers}


def text_tool_call(text):
    """Recognize §9.5 text calls, including JSON objects embedded in prose."""
    if not isinstance(text, str):
        return False
    names = ("inspect_entity", "get_neighbors")
    if re.search(r"(?:inspect_entity|get_neighbors)\(", text):
        return True
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            value, _ = decoder.raw_decode(text[match.start():])
        except ValueError:
            continue
        if any(value.get(key) in names for key in ("name", "function")):
            return True
    return False


def _query(query_id, config):
    data = Path(config["agent_inputs"]).read_bytes()
    if hashlib.sha256(data).hexdigest() != config["agent_inputs_sha256"]:
        raise ValueError("Agent-input sheet hash mismatch")
    found = None
    seen = set()
    for line in data.decode("utf-8").splitlines():
        row = json.loads(line)
        if (not isinstance(row, dict)
                or set(row) != {"query_id", "question_text", "start_name", "start_id"}):
            raise ValueError("Agent-input rows must contain exactly four allowed fields")
        if any(not isinstance(value, str) or not value.strip() for value in row.values()):
            raise ValueError("Agent-input fields must be nonempty strings")
        if not re.fullmatch(r"0|[1-9][0-9]*", row["start_id"]):
            raise ValueError("Agent-input start_id must be a canonical numeric ID")
        if row["query_id"] in seen:
            raise ValueError("Duplicate query_id in agent-input sheet")
        seen.add(row["query_id"])
        if row["query_id"] == query_id:
            found = row
    if found is None:
        raise ValueError(f"Query {query_id!r} not found in agent-input sheet")
    return found


def run_episode(query_id, agent_config, run_config):
    """Run attempt 1 (§9.2–§9.5); any existing final record prevents another run.

    `draft_prompt=True` is for S14 review only; other callers must supply the
    approved `prompt_sha256`. `think` is always explicit in agent_config.
    """
    config = run_config
    target = record_path(config["runs_root"], config["run_id"], query_id,
                         agent_config["agent_id"], 1)
    if target.exists():
        raise FileExistsError(f"Episode already exists, refusing to overwrite: {target}")
    template_hash = prompt_sha256()
    if config.get("draft_prompt") is not True and config.get("prompt_sha256") != template_hash:
        raise ValueError("Approved prompt hash required outside S14 draft review")
    timeout = config["timeout_seconds"]
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout_seconds must be finite and positive")
    tool_config = ToolConfig(page_size=config["page_size"], budget=config["budget"])
    client = OllamaClient(timeout_seconds=config["request_timeout_seconds"],
                          think=agent_config["think"], base_url=config["base_url"])
    query = _query(query_id, config)
    system = P1_TEMPLATE.replace("{PAGE_SIZE}", str(tool_config.page_size)).replace(
        "{BUDGET}", str(tool_config.budget))
    # Substitute once: question text containing placeholder-like text stays verbatim.
    user = USER_TEMPLATE.format(QUESTION=query["question_text"], START_NAME=query["start_name"],
                                START_ID=query["start_id"])
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    events = [{"event": "EPISODE_CONFIG", "think": agent_config["think"],
               "draft_prompt": config.get("draft_prompt") is True,
               "agent_inputs_sha256": config["agent_inputs_sha256"],
               "source_sha256": config.get("source_sha256", {}),
               "timeout_seconds": timeout, "request_timeout_seconds": config["request_timeout_seconds"]}]
    ignored = []
    counts = {"prompt": [], "completion": []}
    options = {key: config[key] for key in ("temperature", "seed", "num_ctx", "num_predict")}
    started_at = datetime.now(timezone.utc).isoformat()
    fields = dict(run_id=config["run_id"], query_id=query_id, agent_id=agent_config["agent_id"],
                  attempt=1, model={key: agent_config[key] for key in ("tag", "digest", "quantization")},
                  **options, prompt_version=f"{PROMPT_VERSION}:{template_hash}",
                  tool_config={"tool_version": TOOL_VERSION, "page_size": tool_config.page_size,
                               "budget": tool_config.budget, "ordering_rule": "numeric-id",
                               "tool_schema_sha256": config["tool_schema_sha256"],
                               "prompt_values": {"PAGE_SIZE": tool_config.page_size,
                                                 "BUDGET": tool_config.budget}},
                  kg_fingerprint=config["kg_fingerprint"], biohopr_revision=config["biohopr_revision"],
                  git_commit=config["git_commit"], timestamps={"started_at": started_at,
                                                             "finished_at": started_at},
                  messages=messages, call_log=[], token_counts=counts, raw_final_output=None,
                  status="ERROR", cause="OTHER", ignored_tool_calls=ignored, log_events=events)
    make_episode_record(**fields)  # Validate provenance before any expensive work/model call.
    deadline = time.monotonic() + timeout
    environment = None
    final_turn = False
    reprompted = False

    def check_time():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Episode wall-clock timeout")
        return remaining

    try:
        environment = KGEnvironment(PrimeKGIndex(config["cache_dir"]), tool_config)
        while True:
            client.timeout_seconds = min(config["request_timeout_seconds"], check_time())
            response = client.chat(agent_config["tag"], deepcopy(messages),
                                   deepcopy(TOOL_SCHEMAS), options)
            message = deepcopy(response["message"])
            messages.append(message)
            events.append({"event": "CHAT_RESPONSE", "message_index": len(messages) - 1,
                           "raw_response": deepcopy(response["raw_response"]),
                           "latency_seconds": response["latency_seconds"]})
            counts["prompt"].append(response["prompt_eval_count"])
            counts["completion"].append(response["eval_count"])
            calls = response["tool_calls"]
            content = message.get("content", "")
            if not calls or final_turn:
                fields["raw_final_output"] = content if isinstance(content, str) else None
            check_time()
            if not calls and text_tool_call(content):
                events.append({"event": "TEXT_TOOL_CALL", "message_index": len(messages) - 1,
                               "content": content})
            if calls and not final_turn:
                for position, call in enumerate(calls):
                    check_time()
                    function = call.get("function") if isinstance(call, dict) else None
                    if (not isinstance(function, dict) or not isinstance(function.get("name"), str)
                            or not isinstance(function.get("arguments"), dict)):
                        raise ValueError("Malformed native tool call; expected name and argument object")
                    result = environment.call(function["name"], function["arguments"])
                    reply = {"role": "tool", "tool_name": function["name"],
                             "content": result if isinstance(result, str) else json.dumps(result)}
                    if "id" in call:
                        reply["tool_call_id"] = call["id"]
                    messages.append(reply)
                    if result == BUDGET_EXHAUSTED:
                        ignored.extend(deepcopy(calls[position + 1:]))
                        final_turn = True
                        break
                continue
            ignored.extend(deepcopy(calls))
            try:
                parsed = parse_final(content, events)
            except ValueError as error:
                events.append({"event": "PARSE_ERROR", "message": str(error),
                               "message_index": len(messages) - 1})
                if reprompted:
                    fields.update(status="PARSE_FAIL", cause=None)
                    break
                messages.append({"role": "user", "content": REPROMPT})
                reprompted = final_turn = True
            else:
                events.append({"event": "FINAL_PARSED", "parsed": parsed})
                fields.update(status="SUCCESS", cause=None)
                break
    except Exception as error:
        events.append({"event": "ERROR", "type": type(error).__name__, "message": str(error),
                       "http_status": getattr(error, "status_code", None),
                       "response_text": getattr(error, "response_text", None)})
        fields.update(status="ERROR", cause=error.cause if isinstance(error, OllamaError) else "OTHER")
    if time.monotonic() >= deadline:
        fields.update(status="TIMEOUT", cause=None)
    fields["call_log"] = environment.call_log if environment is not None else []
    fields["timestamps"]["finished_at"] = datetime.now(timezone.utc).isoformat()
    return save_episode_record(make_episode_record(**fields), config["runs_root"])
