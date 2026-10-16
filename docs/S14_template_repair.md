# S14 template repair and repeat — 2026-10-16

The authorized single repeat finished **SUCCESS**, after the existing one allowed
JSON re-prompt. All four native tool calls succeeded; the final 21 ID/name pairs
exactly match the returned disease neighbors. This is a successful execution and
format check, not gold-answer scoring or proof of reliable non-thinking behavior.

## Files and repair

- `configs/qwen3_s14.Modelfile`: reproducible diagnostic template, based on the
  installed `qwen3:4b`. Tool definitions use `{{ json .Function }}`; the assistant
  prefix immediately closes the thinking block when thinking is explicitly false.
- `scripts/14_run_episode.py`: `--diagnostic-model` selects the separate installed
  variant while retaining the original default and recording the actual identity.
- `tests/test_run_episode_script.py`: regression verifies model selection, exact
  identity passed to the runner, and before/after identity evidence.
- README, progress log, decision log and the earlier diagnostic report link this
  result and correct the earlier assumption about switchable thinking.

Installed tag: `cofail-qwen3:4b-templatefix`.
Digest: `188b1ed1a40c5a0e9c2b0a23cbb057cc1e7db1129395bec24ea082a7974155cd`.
The original model is unchanged. Creation reused the existing weights, model
metadata, parameters and capabilities; no download occurred. The two intended
template expression changes were checked against the original before creation.

## Tests and runtime checks

The new regression failed before implementation on the unrecognized model option.
After implementation, the full host suite passed **352 tests in 10.24 seconds**,
with no skips or exclusions. `git diff --check` passed (line-ending warnings only).
Two render-only requests verified that both tool definitions parse as JSON with
the expected names, descriptions, parameter types/properties and required fields.
The false prefix ends in `<think>\n</think>`; the true prefix ends in `<think>`.
These requests generated no tokens. Runtime rendering does not preserve every
JSON-schema annotation (such as minimum/default); tool-side validation remains
unchanged, and frozen T1 source was not edited.

## One real example and output

```powershell
.\.venv\Scripts\python.exe scripts/14_run_episode.py --run-id s14-templatefix-20261016 --think false --diagnostic-num-predict 6144 --diagnostic-model cofail-qwen3:4b-templatefix
```

Same first screening query: `BH2_00461`. Context 8192, output cap 6144,
temperature 0, seed 42, page size 50, budget 30, episode timeout 600 s.
Runtime: **101.511760 s**. Model identity was stable before and after.

| Measure | Previous unmodified template | Repaired diagnostic variant |
| --- | --- | --- |
| Final status | PARSE_FAIL | SUCCESS |
| Successful native tool calls | 4 | 4 |
| Returned disease entries | 21 | 21 |
| Final JSON re-prompts | 1, still invalid | 1, valid |
| Runtime (seconds) | 174.107482 | 101.511760 |
| Sampled total GPU peak (MiB) | 4714 | 4742 |
| Maximum prompt tokens | 7295 | 7196 |

Both runs requested thinking false. Completion tokens in this repeat were
5505, 1478, 306, 481, 751, 444; every response ended with `stop`, not the output cap.
The first final attempt still contained reasoning and failed strict parsing.
The unchanged fixed re-prompt produced standalone JSON, with status `answered`.
No prefix stripping or parser relaxation was used. One pair of runs cannot
establish a general success rate or attribute all differences to one expression.

The graph route was `14097 --drug_protein--> 111 (TTR) --disease_protein--> 21 diseases`.
All four saved tool results were compared with the researcher inspection CLI.
The final answer list matches the complete returned disease list, including
Finnish type amyloidosis, AL amyloidosis, anxiety disorder and ATTRV122I amyloidosis.
The complete JSON is in the episode record; this list is illustrative, not a
medical interpretation or evaluation of BioHopR answer accuracy.

GPU: RTX 3060 Ti, 8192 MiB. Across 99 samples, total usage peaked at 4742 MiB
(4.63 GiB). Ollama reported the entire model on GPU, context length 8192. Sampling
does not guarantee the instantaneous peak. No OOM occurred.

Record: `results/runs/s14-templatefix-20261016/BH2_00461__S14-qwen3-4b__a1.json`.
SHA256: `e56f8ab710a056656f78676e28527fc34ee951617103c76fdb144ff34fb83d53`.
Both prior failed records retain their original SHA256 hashes.

## Corrected assumption and remaining limitation

The installed tag is misleading if treated as the original switchable Qwen3-4B.
Its GGUF metadata says `general.finetune=Thinking`, `general.version=2507`, and
links the license to Qwen3-4B-Thinking-2507. Qwen's
[official model card](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)
states that this version supports only thinking mode. The original unconditional
thinking prefix is consistent with that model's intended mode. The earlier claim
that a missing false branch alone explains the unwanted reasoning was incomplete.

The repair demonstrably fixes malformed tool serialization. The added false branch
changes the rendered prefix, but cannot make these thinking-only weights reliably
behave as a non-thinking model: reasoning remained in assistant content in this run.
The saved variant is a diagnostic artifact, not a validated experimental default.

For a genuine non-thinking example, a researcher-authorized model choice is still
needed: the original [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) supports mode
switching, while [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
is explicitly non-thinking. Verify the actual weights, template and quantization
under the new tag before testing it. Neither replacement has been installed or
benchmarked here; this result does not justify increasing context again.

## Engineering choices and manual review

Routine engineering choices: a separate local model tag preserves the original;
an explicit diagnostic CLI option preserves default behavior; render-only checks
validate serialization before generation; one-second GPU sampling records capacity.
The diagnostic retained the previously authorized false/6144/8192 settings. No new
scientific threshold, prompt, parser, frozen setting or experimental model was chosen.

Inspect the complete final answer and preceding rejected reply in the record,
the Thinking-2507 identity, and whether to approve/freeze P1. No S15 work, gold
scoring, additional episode, model download, commit or full pilot was performed.

Evidence under `results/diagnostics/`: `s14_templatefix_install.json`,
`s14_templatefix_render_validation.json`, `s14_templatefix_suite.txt`,
`s14_templatefix_console.txt`, `s14_templatefix_gpu.json`,
`s14_templatefix_verification.json`, and `s14-templatefix-20261016_identity.json`.
