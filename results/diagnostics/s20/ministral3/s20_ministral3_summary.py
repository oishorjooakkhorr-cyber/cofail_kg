import csv
from collections import Counter
from datetime import datetime
import json
from pathlib import Path

from cofail_kg.agents.trace import load_episode_record
from cofail_kg.evaluation.screening import call_counts

root = Path.cwd()
out = root / 'results/diagnostics/s20/ministral3'
run = root / 'results/runs/screening/primary-3060ti-20261018'
snap = json.loads((run / 'Ministral3-8B.config.json').read_text())
rows = []
label_a = Counter()
label_b = Counter()
manual = []
for query in snap['query_ids']:
    rec = load_episode_record(run / f'{query}__Ministral3-8B__a1.json')
    met = json.loads((root / f'results/diagnostics/screening/primary-3060ti-20261018/{query}__Ministral3-8B__metrics.json').read_text())
    row = {'query_id': query, 'status': rec['status'], 'cause': rec['cause'],
        'wall_seconds': (datetime.fromisoformat(rec['timestamps']['finished_at']) - datetime.fromisoformat(rec['timestamps']['started_at'])).total_seconds(),
        **call_counts(rec), 'successful_kg_calls': sum(c['success'] for c in rec['call_log']),
        'charged_calls': met['tool_calls_used'], 'budget_exhausted': met['budget_exhausted'],
        'answers': len(met['answers']), 'supported_question_valid': sum(a['label_a'] in ('GOLD', 'GOLD_BRIDGE_EXTRA', 'ALT_VALID') and a['label_b'] == 'SUPPORTED' for a in met['answers']),
        'benchmark_precision': met['benchmark_precision'], 'benchmark_recall': met['benchmark_recall'],
        'largest_prompt': max((x for x in rec['token_counts']['prompt'] if x is not None), default=None),
        'thinking_messages': sum(bool(m.get('thinking')) for m in rec['messages'])}
    rows.append(row)
    label_a.update(a['label_a'] for a in met['answers'])
    label_b.update(a['label_b'] for a in met['answers'])
    if query in ('BH2_00461', 'BH2_03760', 'BH2_03856'):
        manual.append({'query_id': query, 'question': next(json.loads(line)['question_text'] for line in Path(snap['config']['agent_inputs']).read_text().splitlines() if json.loads(line)['query_id'] == query),
            'call_sequence': [{'tool': c['tool'], 'arguments': c['arguments'], 'success': c['success'],
                'result': c['result']} for c in rec['call_log']], 'final_output': rec['raw_final_output'],
            'answers': met['answers'], 'metrics': row})
assert len(rows) == 20
table = list(csv.DictReader((root / 'results/diagnostics/screening/screening_table.csv').open(newline='')))
model = next(r for r in table if r['agent_id'] == 'Ministral3-8B')
assert model['complete'] == 'True' and int(model['episodes_completed']) == 20
summary = {'screening_row': model, 'status_counts': dict(Counter(r['status'] for r in rows)),
    'total_answers': sum(r['answers'] for r in rows), 'label_a_counts': dict(label_a), 'label_b_counts': dict(label_b),
    'thinking_messages': sum(r['thinking_messages'] for r in rows), 'per_query': rows}
(out / 'official-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
(out / 'official-manual-inspection.json').write_text(json.dumps(manual, indent=2), encoding='utf-8')
with (out / 'official-per-query.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps({k: v for k, v in summary.items() if k != 'per_query'}, indent=2))
