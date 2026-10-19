import json
from pathlib import Path
import subprocess
from cofail_kg.agents.ollama_client import OllamaClient

out = Path('results/diagnostics/s20/granite33')
client = OllamaClient(think=False, timeout_seconds=120)
identity = client.get_model_identity('granite3.3:8b')
assert identity['digest'] == 'fd429f23b90980ed1bef53b990894e7b0199331f6ae90c5650240a7d5b70f1f7'
options = dict(temperature=0, seed=42, num_ctx=8192, num_predict=4096)
tools = [{'type': 'function', 'function': {'name': 'add', 'description': 'Add two integers.',
    'parameters': {'type': 'object', 'properties': {'a': {'type': 'integer'},
    'b': {'type': 'integer'}}, 'required': ['a', 'b']}}}]
messages = [{'role': 'user', 'content': 'Use the add tool to calculate 2 + 3, then state the result.'}]
first = client.chat(identity['tag'], messages, tools, options)
(out / 'synthetic-tool-call.json').write_text(json.dumps(first, indent=2), encoding='utf-8')
assert not first['message'].get('thinking'), 'Thinking was not disabled'
calls = first['tool_calls']
assert len(calls) == 1 and calls[0]['function']['name'] == 'add', calls
args = calls[0]['function']['arguments']
assert type(args) is dict and type(args.get('a')) is int and type(args.get('b')) is int, args
assert args == {'a': 2, 'b': 3}, args
messages.extend([first['message'], {'role': 'tool', 'tool_name': 'add', 'content': '5'}])
second = client.chat(identity['tag'], messages, tools, options)
(out / 'synthetic-tool-result.json').write_text(json.dumps(second, indent=2), encoding='utf-8')
assert not second['message'].get('thinking'), 'Thinking was not disabled'
assert not second['tool_calls'] and '5' in second['message'].get('content', ''), second['message']
ps = client._request('GET', '/api/ps')
(out / 'synthetic-ps.json').write_text(json.dumps(ps, indent=2), encoding='utf-8')
gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv,noheader'], text=True)
(out / 'synthetic-gpu.txt').write_text(gpu, encoding='utf-8')
assert client.get_model_identity(identity['tag']) == identity
print(json.dumps({'identity': identity, 'first_message': first['message'], 'final_message': second['message'], 'ps': ps, 'gpu': gpu}, indent=2))
