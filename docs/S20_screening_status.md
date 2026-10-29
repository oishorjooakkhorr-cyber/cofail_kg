# Gemma new-host result — investigation 2026-10-29

**Gemma4-E4B passes D3 on RTX 5060 Ti / Ollama 0.40.12 at 16K with f16 KV.**
Fresh run gemma4-5060ti-16k-20261028: 19/20 SUCCESS, 14/20 competent,
185/185 well-formed native calls, median 10.8510705 s, no OOM/errors/timeouts.
BH2_03879 is the retained PARSE_FAIL. BH2_03762 now returns valid no_answer
but no supported answer; aggregate counts match the old full 16K block while
six outcomes change. Historical/new integrity and offline checks pass.
[New-host report](S20_gemma4_5060ti_16k.md). This separate condition neither
replaces historical acceptance nor selects the S21 panel.

# S20 screening status — 2026-10-28

**New-host result: Ministral 3 8B passes D3 on RTX 5060 Ti at 16K.** The fresh
twenty-query block uses Q4_K_M weights, unquantized f16 KV and Ollama 0.40.12.
Eighteen SUCCESS, two PARSE_FAIL, 17 competent, 179/179 well-formed native calls,
median 45.307066 s, zero OOM/errors/timeouts. This result is separate from the
3060 Ti/0.40.4 history below; it does not merge denominators or select S21.
[New-host report](S20_ministral3_5060ti_16k.md).

## Historical status — 2026-10-21

**Latest: Command R7B completed all twenty original 8K queries: D3 FAIL.**
Nineteen SUCCESS, one PARSE_FAIL, zero tool attempts, zero competent queries,
median 2.889849 s and zero OOM. Call validity is undefined (0/0), so it fails
that criterion as well as competence. [Command R7B report](S20_command_r7b_screening.md).

**Granite 4.1 16K remains stopped by the researcher during query 16.** Fifteen
outcomes are saved: six SUCCESS and nine ERROR/CONNECTION read timeouts.
Five queries have no final record (one interrupted, four unstarted). This is
not a complete D3 block: the final verdict is unassigned, although the maximum
possible SUCCESS is already 11/20 (55%), below 90%. The original Granite 4.1
8K PASS remains the qualifying evidence. [Stopped-run report](S20_granite41_16k_stopped.md).

Nine candidates have completed the twenty frozen screening queries at 8K.
Three of those candidates also have separate complete twenty-query 16K
reassessments: 240 saved outcomes across twelve full blocks. The selected
four-query Gemma diagnostic is separate and is not added to any D3 denominator.

**Current passing candidates:** Granite41-8B at 8K, Gemma4-E4B at 16K and
Qwen35-9B at 16K. **Current failing candidates:** Llama31-8B, Granite33-8B,
Granite42-8B, OLMo3-7B, Ministral3-8B and CommandR7B-7B. These are results at the recorded
settings, not a final S21 panel selection. Three passing developer families
are represented, but D3 requires four passing models; S21 remains pending.
Additional-candidate membership and D3 round accounting remain researcher
decisions under the existing rules.

## Original 8K screening — all completed candidates

All fractions use twenty queries. Call validity includes native and recorded
text-tool attempts in the denominator. Every criterion must pass D3.

| Candidate | Well-formed / attempted calls | SUCCESS | Competent | Median wall time (s) | OOM | D3 | Failed criteria |
|---|---:|---:|---:|---:|---:|---|---|
| CommandR7B-7B | 0/0 (undefined) | 19/20 | 0/20 | 2.889849 | 0 | FAIL | Call validity; competence |
| Gemma4-E4B | 149/149 | 16/20 | 11/20 | 11.9732305 | 0 | FAIL | SUCCESS |
| Granite33-8B | 0/8 | 20/20 | 0/20 | 13.597764 | 0 | FAIL | Call validity; competence |
| Granite41-8B | 217/217 | 20/20 | 14/20 | 61.3250475 | 0 | PASS | None |
| Granite42-8B | 327/327 | 17/20 | 6/20 | 120.247903 | 0 | FAIL | SUCCESS; competence |
| Llama31-8B | 0/620 | 20/20 | 0/20 | 22.132269 | 0 | FAIL | Call validity; competence |
| Ministral3-8B | 197/197 | 15/20 | 10/20 | 62.850686 | 0 | FAIL | SUCCESS |
| OLMo3-7B | 60/62 | 20/20 | 0/20 | 8.951106 | 0 | FAIL | Competence |
| Qwen35-9B | 210/210 | 18/20 | 15/20 | 26.383874 | 0 | PASS | None |

Source: [original screening table](../results/diagnostics/screening/screening_table.csv).
It contains the original 8K blocks, not the separate 16K reassessments.

## Complete 16K reassessments — original history retained

These three full blocks use the researcher-authorized context amendment and
unchanged D3 thresholds. They do not combine old successes with selected reruns.

| Candidate | Well-formed / attempted calls | SUCCESS | Competent | Median wall time (s) | OOM | D3 | Failed criteria |
|---|---:|---:|---:|---:|---:|---|---|
| Gemma4-E4B | 181/181 | 19/20 | 14/20 | 16.2779325 | 0 | PASS | None |
| Qwen35-9B | 263/263 | 19/20 | 13/20 | 56.839506 | 0 | PASS | None |
| Ministral3-8B | 167/167 | 12/20 | 12/20 | 168.0803425 | 0 | FAIL | SUCCESS |

Sources: [16K report](S20_full_16k_reassessment.md) and
[acceptance artifact](../results/diagnostics/s20/full-16k-20261020/acceptance.json).
Granite 4.1 has a separate stopped 15/20 16K block, excluded from this table
of complete reassessments. No 16K result is claimed for the other four candidates.

## Failure history and interpretation

- [Command R7B](S20_command_r7b_screening.md): nineteen outputs parsed,
  one array-shaped final output failed parsing, no tool attempts occurred and
  no query was competent. Undefined 0/0 call validity does not pass D3.
- [Llama 3.1](S20_llama_screening.md): all twenty outputs parsed, but none of
  620 tool attempts met the frozen schema and no query was competent.
- [Granite 3.3](S20_granite33_screening.md): all twenty outputs parsed, but
  there were zero native calls, eight text-tool attempts and no competent query.
- [Granite 4.2](S20_granite42_screening.md): three preserved request-timeout
  errors reduced SUCCESS to 85%; competence was 30%. Both criteria fail.
- [OLMo 3](S20_olmo3_screening.md): all twenty outputs parsed and call validity
  passed, but no query had a supported question-valid answer.
- [Ministral 3](S20_ministral3_screening.md): the 8K block retained four parse
  failures and one request-timeout error. The separate 16K block retained eight
  request-timeout errors; SUCCESS remained below 90% in both blocks.
- [Gemma 4](S20_gemma4_screening.md): its original 8K block failed with four
  parse failures. Its complete 16K block passes with one parse failure retained.
- [Qwen3.5](S20_qwen35_screening.md): passes at both contexts, with two parse
  failures retained at 8K and one at 16K. Competence decreased from 15/20 to
  13/20; a larger context did not improve every metric.
- [Granite 4.1](S20_granite41_screening.md): its 2026-10-21 8K block passes all
  five criteria: twenty SUCCESS, no errors/timeouts/parse failures, fourteen
  competent queries and 217/217 well-formed native calls. Of 568 submitted
  answer items, 525 were question-valid and supported; 43 were
  OFF_QUESTION/PATH_INVALID. Its earlier deferred status is superseded. Its
  later 16K test was stopped at 15/20 with nine request-timeout errors; the
  incomplete 16K evidence does not supersede the completed 8K PASS.

SUCCESS means valid final JSON, including a valid `no_answer`; it does not mean
correctness. Competence requires at least one question-valid, SUPPORTED answer
on a query and is not answer-level accuracy or exhaustive recall. Thresholds
remain call validity >=90%, SUCCESS >=90%, competence >=40%, median wall time
<=300 seconds and zero ERROR/OUT_OF_MEMORY episodes. See [D3](decision_rules.md).

This update adds the researcher-authorized complete Command R7B block.
All earlier rows and failed outcomes are preserved; no failed result was
retried, metric definition changed, protocol amended or S21 configuration frozen.
Older dated reports and decision entries remain history.
