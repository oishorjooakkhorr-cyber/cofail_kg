import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

from cofail_kg.agents.ollama_client import OllamaClient
from cofail_kg.agents.trace import load_episode_record, record_path

root = Path.cwd()
out = root / 'results/diagnostics/s20/ministral3'
run_id = 'primary-3060ti-20261018'
agent_id = 'Ministral3-8B'
digest = '1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71'
runs_root = root / 'results/runs/screening'
baseline = json.loads((out / 'stopped-integrity-proof.json').read_text())
protected = json.loads((root / 'results/diagnostics/s20/protected-before.json').read_text())
pinned = json.loads((runs_root / run_id / 'Llama31-8B.config.json').read_text())['config']['source_sha256']
expected_files = baseline['run_sha256'].copy()
queries = [json.loads(line)['query_id'] for line in (root / 'data/agent_inputs/screening.jsonl').read_text().splitlines()]
assert len(queries) == len(set(queries)) == 20
assert len(list((runs_root / run_id).glob(f'*__{agent_id}__a1.json'))) == 16
assert baseline['episodes_remaining'] == queries[16:]
for query in queries[:16]:
    assert record_path(runs_root, run_id, query, agent_id, 1).exists()
for query in queries[16:]:
    assert not record_path(runs_root, run_id, query, agent_id, 1).exists()
saved_error = load_episode_record(record_path(runs_root, run_id, queries[15], agent_id, 1))
assert saved_error['status'] == 'ERROR' and saved_error['cause'] == 'CONNECTION'
client = OllamaClient(think=False, timeout_seconds=120)
cmd = [sys.executable, 'scripts/20_screen_models.py', '--run-id', run_id,
       '--agent-id', agent_id, '--family', 'Mistral', '--model', 'ministral-3:8b',
       '--expected-digest', digest, '--max-new', '1']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def integrity():
    for group in (expected_files, protected, pinned):
        drift = [p for p, value in group.items() if sha(root / p) != value]
        assert not drift, f'Integrity drift: {drift}'

with (out / 'continuation-journal.jsonl').open('x', encoding='utf-8') as journal:
    for index, query in enumerate(queries[16:], 17):
        integrity()
        assert client.get_model_identity('ministral-3:8b')['digest'] == digest
        existing = set((runs_root / run_id).glob(f'*__{agent_id}__a1.json'))
        print(f'START {index}/20 {query}', flush=True)
        with (out / f'continuation-{index:02d}-{query}.txt').open('x', encoding='utf-8') as console:
            result = subprocess.run(cmd, cwd=root, stdout=console, stderr=subprocess.STDOUT)
        current = set((runs_root / run_id).glob(f'*__{agent_id}__a1.json'))
        target = record_path(runs_root, run_id, query, agent_id, 1)
        row = {'index': index, 'query_id': query, 'exit_code': result.returncode,
               'checked_at': datetime.now(timezone.utc).isoformat()}
        if target.exists():
            record = load_episode_record(target)
            row.update(status=record['status'], cause=record['cause'],
                       wall_seconds=(datetime.fromisoformat(record['timestamps']['finished_at']) -
                                     datetime.fromisoformat(record['timestamps']['started_at'])).total_seconds(),
                       sha256=sha(target))
        journal.write(json.dumps(row) + '\n')
        journal.flush()
        print(json.dumps(row), flush=True)
        assert result.returncode == 0, f'STOP: nonzero launcher exit {result.returncode}'
        assert current - existing == {target}, f'STOP: wrong new records {current - existing}'
        assert record['query_id'] == query and record['agent_id'] == agent_id
        assert record['model']['digest'] == digest
        assert record['status'] != 'ERROR', f'STOP: saved ERROR {record["cause"]}'
        integrity()
        for path in (target, runs_root / run_id / f'{agent_id}.config.json'):
            key = path.relative_to(root).as_posix()
            if key in expected_files:
                assert sha(path) == expected_files[key]
            expected_files[key] = sha(path)
        assert len(current) == index
        ps = client._request('GET', '/api/ps')
        (out / f'continuation-{index:02d}-ps.json').write_text(json.dumps(ps, indent=2), encoding='utf-8')
        assert all(m['digest'] == digest and m['context_length'] == 8192 for m in ps['models'])
    integrity()
    with (out / 'official-report-only.txt').open('x', encoding='utf-8') as console:
        report = subprocess.run(cmd[:-1] + ['0'], cwd=root, stdout=console, stderr=subprocess.STDOUT)
    assert report.returncode == 0, 'Report-only invocation failed'
    integrity()
    proof = {'official_ministral_episodes': 20, 'run_files_checked': len(expected_files),
             'run_sha256': expected_files, 'protected_identities_checked': len(protected),
             'pinned_sources_checked': len(pinned), 'drift': [], 'report_only_exit': report.returncode}
    (out / 'official-final-integrity.json').write_text(json.dumps(proof, indent=2), encoding='utf-8')
    print('COMPLETE 20/20; report-only and all integrity checks passed.', flush=True)
