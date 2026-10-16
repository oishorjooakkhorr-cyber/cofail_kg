"""S14 protocol §9 mocked episodes on the tiny S4 graph; no Ollama required."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
from unittest.mock import Mock

import pytest

from test_primekg_index import cache, index
from test_primekg_prepare import raw_graph
from cofail_kg.agents import run_agent as runner
from cofail_kg.agents.ollama_client import OllamaError
from cofail_kg.agents.prompts import P1_TEMPLATE, USER_TEMPLATE, prompt_sha256
from cofail_kg.agents.trace import load_episode_record


def response(content='', calls=None):
    message = {'role': 'assistant', 'content': content, 'thinking': 'synthetic thinking'}
    if calls:
        message['tool_calls'] = calls
    return {'message': message, 'tool_calls': calls or [], 'raw_response': {'message': message},
            'prompt_eval_count': 12, 'eval_count': 6, 'latency_seconds': .001}


def call(name='inspect_entity', **args):
    return {'id': 'c1', 'function': {'name': name, 'arguments': args}}


@pytest.fixture
def episode(tmp_path, index, monkeypatch):
    query = {'query_id': 'Q1', 'question_text': 'Find an entity.', 'start_id': '10', 'start_name': 'Alpha'}
    sheet = tmp_path / 'screening.jsonl'
    sheet.write_text(json.dumps(query)+'\n', encoding='utf-8')
    config = {'run_id': 's14-test', 'agent_inputs': str(sheet), 'cache_dir': 'unused',
              'runs_root': str(tmp_path / 'runs'), 'temperature': 0, 'seed': 42,
              'num_ctx': 8192, 'num_predict': 4096, 'page_size': 50, 'budget': 30,
              'timeout_seconds': 10, 'request_timeout_seconds': 7,
              'base_url': 'http://127.0.0.1:11434', 'kg_fingerprint': 'a'*64,
              'biohopr_revision': 'test-revision', 'git_commit': 'test-dirty',
              'tool_schema_sha256': 'b'*64,
              'agent_inputs_sha256': hashlib.sha256(sheet.read_bytes()).hexdigest(),
              'draft_prompt': True}
    agent = {'agent_id': 'A1', 'tag': 'tiny:test', 'digest': 'test-digest',
             'quantization': 'Q4_K_M', 'think': True}
    client = Mock()
    monkeypatch.setattr(runner, 'PrimeKGIndex', lambda _: index)
    monkeypatch.setattr(runner, 'OllamaClient', Mock(return_value=client))

    def run(replies):
        client.chat.side_effect = replies
        path = runner.run_episode('Q1', agent, config)
        return load_episode_record(path)
    return run, client, config, agent


def test_templates_are_exact_runbook_text():
    book = (Path(__file__).parents[1] / 'docs/pipeline_runbook.md').read_text(encoding='utf-8')
    section = book.split('## S14 — Agent prompt and runner', 1)[1]
    blocks = section.split('```text\n')
    assert P1_TEMPLATE == blocks[1].split('\n```', 1)[0]
    assert USER_TEMPLATE == blocks[2].split('\n```', 1)[0]
    assert prompt_sha256() == hashlib.sha256(P1_TEMPLATE.encode()).hexdigest()


def test_normal_episode_and_thinking_preserved(episode):
    run, client, config, _ = episode
    record = run([response(calls=[call(entity_id='10')]), response(
        '{"status":"answered","answers":[{"id":"10","name":"Alpha"}]}')])
    assert record['status'] == 'SUCCESS'
    assert record['appeared_entities'] == ['10']
    assert record['attempt'] == 1
    assert record['call_log'][0]['success']
    assert record['messages'][1]['content'] == 'Find an entity.\nStarting entity: Alpha (PrimeKG ID: 10)'
    assert record['messages'][2]['thinking'] == 'synthetic thinking'
    raw = next(e for e in record['log_events'] if e['event'] == 'CHAT_RESPONSE')
    assert raw['raw_response']['message']['thinking'] == 'synthetic thinking'
    assert record['token_counts'] == {'prompt': [12, 12], 'completion': [6, 6]}
    assert client.chat.call_count == 2
    with pytest.raises(FileExistsError):
        run([])
    assert client.chat.call_count == 2


@pytest.mark.parametrize('text,expected', [
    ('```json\n{"status":"answered","answers":[{"id":2,"name":"Beta"}]}\n```', 2),
    ('{"status":"answered","answers":[]}', None),
    ('{"status":"no_answer","answers":[{"id":"2","name":"Beta"}]}', None),
])
def test_parsing_fences_integer_ids_empty_and_no_answer_items(episode, text, expected):
    run, _, _, _ = episode
    record = run([response(text)])
    assert record['status'] == 'SUCCESS'
    parsed = next(e['parsed'] for e in record['log_events'] if e['event'] == 'FINAL_PARSED')
    assert (parsed['answers'][0]['id'] if parsed['answers'] else None) == expected


def test_extra_keys_are_logged_and_ignored(episode):
    run, _, _, _ = episode
    record = run([response('{"status":"answered","extra":1,"answers":[{"id":2,"name":"B","x":3}]}')])
    assert record['status'] == 'SUCCESS'
    assert any(e['event'] == 'EXTRA_KEYS' for e in record['log_events'])


@pytest.mark.parametrize('second,status', [
    ('{"status":"answered","answers":[]}', 'SUCCESS'), ('still invalid', 'PARSE_FAIL')])
def test_exactly_one_fixed_reprompt(episode, second, status):
    run, client, _, _ = episode
    record = run([response('invalid'), response(second)])
    assert record['status'] == status
    assert client.chat.call_count == 2
    assert {'role': 'user', 'content': runner.REPROMPT} in record['messages']


def test_budget_exhaustion_and_ignored_final_calls(episode):
    run, client, config, _ = episode
    config['budget'] = 1
    record = run([
        response(calls=[call(entity_id='10'), call(entity_id='2'), call(entity_id='30')]),
        response('{"status":"answered","answers":[]}', calls=[call(entity_id='40')])])
    assert record['status'] == 'SUCCESS'
    assert client.chat.call_count == 2
    assert record['appeared_entities'] == ['10']
    assert len(record['call_log']) == 2
    assert record['call_log'][-1]['result'] == runner.BUDGET_EXHAUSTED
    assert len(record['ignored_tool_calls']) == 2


@pytest.mark.parametrize('text', [
    'inspect_entity(10)', 'get_neighbors(10, "x")',
    '{"name":"inspect_entity","arguments":{}}',
    'prefix {"function":"get_neighbors"} suffix'])
def test_text_tool_calls_are_detected_never_executed(episode, text):
    run, _, _, _ = episode
    record = run([response(text), response('{"status":"no_answer","answers":[]}')])
    assert record['status'] == 'SUCCESS'
    assert record['call_log'] == []
    assert any(e['event'] == 'TEXT_TOOL_CALL' for e in record['log_events'])


@pytest.mark.parametrize('cause', ['OUT_OF_MEMORY', 'CONNECTION', 'RUNTIME', 'OTHER'])
def test_error_cause_is_preserved(episode, cause):
    run, _, _, _ = episode
    record = run([OllamaError(cause, 'synthetic failure')])
    assert record['status'] == 'ERROR' and record['cause'] == cause


def test_timeout_during_reprompt_has_precedence(episode):
    run, _, config, _ = episode
    config['timeout_seconds'] = .03

    def replies(*args):
        if replies.count == 0:
            replies.count += 1
            return response('bad JSON')
        time.sleep(.08)
        raise OllamaError('CONNECTION', 'late timeout')
    replies.count = 0
    record = run(replies)
    assert record['status'] == 'TIMEOUT' and record['cause'] is None


def test_agent_sheet_rejects_extra_fields_before_model_call(episode):
    run, client, config, _ = episode
    sheet = Path(config['agent_inputs'])
    data = json.loads(sheet.read_text()) | {'gold_answer': 'forbidden'}
    sheet.write_text(json.dumps(data)+'\n')
    config['agent_inputs_sha256'] = hashlib.sha256(sheet.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='four'):
        run([])
    client.chat.assert_not_called()


def test_sheet_hash_mismatch_stops_before_model_call(episode):
    run, client, config, _ = episode
    config['agent_inputs_sha256'] = '0'*64
    with pytest.raises(ValueError, match='hash'):
        run([])
    client.chat.assert_not_called()


@pytest.mark.parametrize('text', [
    '[]', 'null', '{"status":"answered","answers":{}}',
    '{"status":"answered","answers":[{"id":true,"name":"B"}]}',
    '{"status":"answered","answers":[{"id":2,"name":null}]}',
    'prefix {"status":"answered","answers":[]}',
    '{"status":"answered","answers":[]} trailing',
    '{"status":"answered","answers":[],"extra":NaN}',
])
def test_invalid_final_shapes_are_rejected(text):
    with pytest.raises(ValueError):
        runner.parse_final(text, [])


@pytest.mark.parametrize('text', [
    '```\n{"status":"answered","answers":[]}\n```',
    ' ```json\r\n{"status":"answered","answers":[]}\r\n``` ',
])
def test_whole_fences_without_tag_and_with_crlf(text):
    assert runner.parse_final(text, []) == {'status': 'answered', 'answers': []}


def test_ignored_keys_and_no_answer_items_keep_evidence():
    events = []
    parsed = runner.parse_final(
        '{"status":"no_answer","answers":[{"id":2,"name":"B","extra":3}],"x":4}', events)
    assert parsed == {'status': 'no_answer', 'answers': []}
    assert events == [
        {'event': 'EXTRA_KEYS', 'details': [
            {'location': 'final', 'keys': ['x']}, {'location': 'answers[0]', 'keys': ['extra']}]},
        {'event': 'NO_ANSWER_ITEMS_IGNORED', 'items': [{'id': 2, 'name': 'B'}]},
    ]


@pytest.mark.parametrize('text,expected', [
    ('get_neighbors (10)', False), ('We can use inspect_entity.', False),
    ('{"function":{"name":"get_neighbors","arguments":{}}}', True),
    ('{"name":"different"}', False),
])
def test_text_tool_detection_boundaries(text, expected):
    assert runner.text_tool_call(text) is expected


def test_reprompt_cannot_reopen_tool_execution(episode):
    run, client, _, _ = episode
    record = run([response('invalid'), response('invalid', calls=[call(entity_id='10')])])
    assert record['status'] == 'PARSE_FAIL'
    assert record['call_log'] == []
    assert record['ignored_tool_calls'] == [call(entity_id='10')]
    assert client.chat.call_count == 2


def test_tool_errors_consume_budget_and_only_one_final_turn_follows(episode):
    run, client, config, _ = episode
    config['budget'] = 1
    record = run([response(calls=[call('unknown')]), response(calls=[call(entity_id='10')]),
                  response('{"status":"no_answer","answers":[]}')])
    assert record['status'] == 'SUCCESS'
    assert [entry['result'] for entry in record['call_log']] == [
        'Error: unknown tool unknown.', runner.BUDGET_EXHAUSTED]
    assert client.chat.call_count == 3


def test_malformed_native_call_is_saved_as_error(episode):
    run, _, _, _ = episode
    record = run([response(calls=[{'function': {'name': 'inspect_entity', 'arguments': 'bad'}}])])
    assert record['status'] == 'ERROR' and record['cause'] == 'OTHER'
    assert record['call_log'] == []
    assert record['log_events'][-1]['type'] == 'ValueError'


def test_deadline_wins_over_valid_final_and_preserves_late_response(episode, monkeypatch):
    run, client, config, _ = episode
    clock = [100.0]
    monkeypatch.setattr(runner.time, 'monotonic', lambda: clock[0])

    def reply(*args):
        assert 0 < client.timeout_seconds <= config['timeout_seconds']
        clock[0] += config['timeout_seconds'] + 1
        return response('{"status":"no_answer","answers":[]}')

    record = run(reply)
    assert record['status'] == 'TIMEOUT' and record['cause'] is None
    assert record['raw_final_output'] == '{"status":"no_answer","answers":[]}'
    assert record['token_counts']['completion'] == [6]


def test_duplicate_sheet_query_is_rejected(episode):
    run, client, config, _ = episode
    sheet = Path(config['agent_inputs'])
    sheet.write_bytes(sheet.read_bytes() * 2)
    config['agent_inputs_sha256'] = hashlib.sha256(sheet.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='Duplicate'):
        run([])
    client.chat.assert_not_called()


def test_approved_prompt_required_after_draft_review(episode):
    run, client, config, _ = episode
    config['draft_prompt'] = False
    with pytest.raises(ValueError, match='Approved prompt hash'):
        run([])
    client.chat.assert_not_called()
    config['prompt_sha256'] = prompt_sha256()
    assert run([response('{"status":"no_answer","answers":[]}')])['status'] == 'SUCCESS'


def test_conversations_are_independent_and_leftover_temp_is_not_completed(episode):
    run, client, config, _ = episode
    leftover = Path(config['runs_root']) / config['run_id'] / '.Q1__A1__a1.json.leftover.tmp'
    leftover.parent.mkdir(parents=True)
    leftover.write_text('unfinished')
    first = run([response('{"status":"no_answer","answers":[]}')])
    config['run_id'] = 'second-run'
    second = run([response('{"status":"no_answer","answers":[]}')])
    assert first['messages'] == second['messages']
    assert len(client.chat.call_args.args[1]) == 2
    assert leftover.read_text() == 'unfinished'


def test_thinking_only_token_limit_replies_preserve_evidence_and_fail_parsing(episode):
    run, client, _, _ = episode
    reply = response('')
    reply['eval_count'] = 4096
    reply['raw_response'].update(done=True, done_reason='length', eval_count=4096)
    record = run([deepcopy(reply), deepcopy(reply)])
    assert record['status'] == 'PARSE_FAIL' and record['raw_final_output'] == ''
    assert record['call_log'] == [] and record['trace_graph'] == []
    assert record['token_counts']['completion'] == [4096, 4096]
    responses = [e['raw_response'] for e in record['log_events'] if e['event'] == 'CHAT_RESPONSE']
    assert [r['done_reason'] for r in responses] == ['length', 'length']
    assert all(r['message']['thinking'] == 'synthetic thinking' for r in responses)
    assert client.chat.call_count == 2
