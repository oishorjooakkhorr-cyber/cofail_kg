import importlib.util
import json
from datetime import datetime
from pathlib import Path
import subprocess

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.run_agent import run_episode
from cofail_kg.agents.trace import load_episode_record, record_path
from cofail_kg.evaluation.agent_metrics import agent_metrics
from cofail_kg.evaluation.screening import call_counts
from cofail_kg.kg.prepare import file_hash

root = Path.cwd()
out = root / 'results/diagnostics/s20/ministral3/offbook-20261019T075024Z'
run_id = 'ministral3-bh204425-diagnostic-20261019T075024Z'
query_id = 'BH2_04425'
original = root / 'results/runs/screening/primary-3060ti-20261018'
snapshot = json.loads((original / 'Ministral3-8B.config.json').read_text())
proof = json.loads((out.parent / 'official-final-integrity.json').read_text())
protected = json.loads((root / 'results/diagnostics/s20/protected-before.json').read_text())
expected = {**proof['run_sha256'], **protected, **snapshot['config']['source_sha256']}
for path in (root / 'results/diagnostics/screening').rglob('*'):
    if path.is_file():
        expected[path.relative_to(root).as_posix()] = file_hash(path)
for path, value in expected.items():
    assert file_hash(root / path) == value, path
(out / 'integrity-before.json').write_text(json.dumps(expected,indent=2),encoding='utf-8')
client = OllamaClient(think=False, timeout_seconds=120)
identity = client.get_model_identity('ministral-3:8b')
assert identity == snapshot['identity']
config = snapshot['config'].copy()
commit = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
dirty = bool(subprocess.check_output(['git','status','--porcelain'],text=True))
config.update(run_id=run_id, runs_root=str(root / 'results/runs/diagnostic'),
              request_timeout_seconds=600, git_commit=commit+('-dirty' if dirty else ''))
config['source_sha256'] = {**config['source_sha256'], Path(__file__).relative_to(root).as_posix():file_hash(Path(__file__))}
agent = snapshot['agent'].copy()
target = record_path(config['runs_root'],run_id,query_id,agent['agent_id'],1)
assert not target.exists()
spec = importlib.util.spec_from_file_location('s14_diagnostic_launcher', root / 'scripts/14_run_episode.py')
s14 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s14)
s14.check_persistence(Path(config['runs_root']))
manifest = {'diagnostic_only':True,'excluded_from_official_screening':True,
            'original_record':str(original / f'{query_id}__Ministral3-8B__a1.json'),
            'changes_from_screening':{'request_timeout_seconds':{'from':120,'to':600}},
            'query_id':query_id,'identity':identity,'agent':agent,'config':config}
(out / 'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(f'START one complete diagnostic episode: {query_id}; request cap 600 s, episode cap 600 s.',flush=True)
path = run_episode(query_id,agent,config)
record = load_episode_record(path)
assert client.get_model_identity(agent['tag']) == identity
assert record['run_id']==run_id and record['query_id']==query_id
assert record['model']['digest']==identity['digest']
assert len([p for p in Path(config['runs_root']).joinpath(run_id).glob('*.json')])==1
# Evaluator references are loaded only after the independent episode finishes.
spec = importlib.util.spec_from_file_location('s20_diagnostic_evaluator',root / 'scripts/20_screen_models.py')
s20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s20)
refs,targets,mapping,status,kg,degrees = s20.load_evaluator()
query = refs[query_id]
metrics = agent_metrics(record,query,mapping[query['relation_type']],targets[query_id],kg,degrees,
                        consistent=status[query_id]=='CONSISTENT')
(out / 'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
for key,value in expected.items():
    assert file_hash(root / key)==value,key
summary = {'diagnostic_only':True,'record_path':str(path),'record_sha256':file_hash(path),
           'status':record['status'],'cause':record['cause'],
           'wall_seconds':(datetime.fromisoformat(record['timestamps']['finished_at'])-datetime.fromisoformat(record['timestamps']['started_at'])).total_seconds(),
           **call_counts(record),'tool_calls_used':metrics['tool_calls_used'],
           'answer_items':len(metrics['answers']),
           'supported_question_valid':sum(a['label_a'] in ('GOLD','GOLD_BRIDGE_EXTRA','ALT_VALID') and a['label_b']=='SUPPORTED' for a in metrics['answers']),
           'largest_prompt':max(record['token_counts']['prompt'],default=None),
           'official_run_files_unchanged':len(proof['run_sha256']),
           'total_protected_files_unchanged':len(expected),'official_screening_unchanged':True,
           'final_output':record['raw_final_output']}
(out / 'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(out / 'after-ps.json').write_text(json.dumps(client._request('GET','/api/ps'),indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='final_output'},indent=2),flush=True)
