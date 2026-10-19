import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import time
from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.tool_schemas import TOOL_SCHEMAS
from cofail_kg.agents.trace import load_episode_record

root = Path.cwd()
out = root / 'results/diagnostics/s20/ministral3/timeout-investigation'
run = root / 'results/runs/screening/primary-3060ti-20261018'
proof = json.loads((out.parent / 'official-final-integrity.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for path, value in proof['run_sha256'].items():
    assert sha(root / path) == value, path
record = load_episode_record(run / 'BH2_04425__Ministral3-8B__a1.json')
snap = json.loads((run / 'Ministral3-8B.config.json').read_text())
for path, value in snap['config']['source_sha256'].items():
    assert sha(root / path) == value, path
assert record['status'] == 'ERROR' and record['cause'] == 'CONNECTION'
assert len(record['call_log']) == 6 and record['messages'][-1]['role'] == 'tool'
options = {k: record[k] for k in ('temperature','seed','num_ctx','num_predict')}
payload = dict(model=record['model']['tag'], messages=record['messages'], tools=TOOL_SCHEMAS,
               options=options, stream=False, think=False)
(out / 'request.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
client = OllamaClient(think=False, timeout_seconds=300)
assert client.get_model_identity(payload['model']) == snap['identity']
before = client._request('GET', '/api/ps')
(out / 'before-ps.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
start = time.perf_counter()
meta = {'started_at': datetime.now(timezone.utc).isoformat(), 'original_read_timeout_seconds':120,
        'diagnostic_read_timeout_seconds':300, 'official_episode_rerun':False,
        'changed_request_fields':[], 'request_sha256':sha(out / 'request.json')}
print('Starting one diagnostic replay of the saved seventh HTTP request, read timeout 300 seconds.',flush=True)
try:
    response = client.chat(payload['model'], payload['messages'], payload['tools'], payload['options'])
    (out / 'response.json').write_text(json.dumps(response,indent=2),encoding='utf-8')
    raw = response['raw_response']
    meta.update(outcome='RESPONSE', latency_seconds=response['latency_seconds'],
                prompt_eval_count=raw.get('prompt_eval_count'), eval_count=raw.get('eval_count'),
                done_reason=raw.get('done_reason'), eval_seconds=raw.get('eval_duration',0)/1e9,
                prompt_eval_seconds=raw.get('prompt_eval_duration',0)/1e9,
                load_seconds=raw.get('load_duration',0)/1e9,
                content_characters=len(response['message'].get('content','')),
                tool_calls=len(response['tool_calls']),
                exceeded_original_read_timeout=response['latency_seconds']>120)
except Exception as error:
    meta.update(outcome='ERROR', error_type=type(error).__name__, error=str(error))
    raise
finally:
    meta.update(elapsed_seconds=time.perf_counter()-start, finished_at=datetime.now(timezone.utc).isoformat())
    for path, value in proof['run_sha256'].items():
        assert sha(root / path) == value, path
    meta['official_run_files_unchanged']=len(proof['run_sha256'])
    (out / 'replay-summary.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta,indent=2),flush=True)
