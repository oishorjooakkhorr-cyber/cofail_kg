"""S13: two synthetic chat calls, never a biomedical episode or Gate D3 decision."""

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path

import yaml

from cofail_kg.agents.ollama_client import OllamaClient, OllamaError


ROOT = Path(__file__).resolve().parents[1]
OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 4096}
ADD = {"type": "function", "function": {
    "name": "add", "description": "Add two integers.",
    "parameters": {"type": "object", "properties": {
        "a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="qwen3:4b", help="Diagnostic model only (default: qwen3:4b)")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/ollama.yaml")
    parser.add_argument("--output", type=Path, help="Optional new JSON evidence file; never overwritten")
    args = parser.parse_args(argv)
    if args.output and args.output.exists():
        raise FileExistsError(args.output)
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    client = OllamaClient(timeout_seconds=config["request_timeout_seconds"],
                          think=config["think"], base_url=config["base_url"])
    report = {"stage": "S13", "model_requested": args.model, "options": OPTIONS,
              "transport": config, "started_at": datetime.now(timezone.utc).isoformat(),
              "native_tool_call": False}
    code = 1
    try:
        identity = client.get_model_identity(args.model)
        report["identity_before"] = identity
        if "tools" not in identity["capabilities"]:
            raise OllamaError("RUNTIME", "Test model does not advertise tools capability")
        for name, text, tools in (
            ("plain", "Reply with a short greeting.", []),
            ("tool", "Use the add tool to calculate 2 + 3.", [ADD]),
        ):
            messages = [{"role": "user", "content": text}]
            report[name + "_request"] = {"messages": messages, "tools": tools}
            report[name] = client.chat(identity["tag"], messages, tools, OPTIONS)
        report["native_tool_call"] = any(
            isinstance(call, dict) and isinstance(call.get("function"), dict)
            and call["function"].get("name") == "add" for call in report["tool"]["tool_calls"])
        report["identity_after"] = client.get_model_identity(identity["tag"])
        if report["identity_after"] != identity:
            raise OllamaError("RUNTIME", "Model identity changed during diagnostic")
        code = 0 if report["native_tool_call"] else 1
    except OllamaError as exc:
        report["error"] = {"cause": exc.cause, "message": str(exc),
                           "status_code": exc.status_code, "response_text": exc.response_text}
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(text, end="")
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(text)
    return code


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
