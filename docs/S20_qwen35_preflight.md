# S20 Qwen3.5 9B: historical preflight and memory investigation (2026-10-18)

At this preflight checkpoint, no Qwen3.5 official screening episode or official configuration existed. The
researcher added this model as an extra candidate, retaining the original eight,
then explicitly paused official inference to investigate partial CPU placement.
After the unchanged recheck, the researcher accepted the documented placement
and authorized all 20 official queries; see the later entry in the decision log.
The observations below describe the preflight, before that authorization.

## 1. Files and scope

Evidence is in `results/diagnostics/s20/qwen35/`. Decisions are recorded in
`docs/decision_log.md`; this report records the compatibility and memory findings.
Temporary diagnostic scripts are in ignored `.venv/`. No agent, evaluator,
launcher, test, prompt, schema, configuration, data or frozen rule was changed.

Identity: `qwen3.5:9b`, Qwen lineage, 9.0B Q4_K_M, digest
`56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90`.
Local Ollama version: 0.40.4; RTX 3060 Ti, 8192 MiB VRAM.

## 2. Tests and integrity

- Unchanged full suite: **598 passed in 41.73 seconds**, no skips/deselections.
  Log: `full-suite.txt`.
- All 122 protected-file hashes and 43 previously pinned source/input hashes
  match. `integrity-preflight.json` saves hashes of all 21 existing official
  run files (20 Llama episodes plus its configuration).
- Exact installed model identity was checked before/after the synthetic tool
  exchange. Native tools are advertised by `/api/show`.
- The diagnostic used temperature=0, seed=42, num_ctx=8192,
  num_predict=4096 and think=false, with the existing 120-second request timeout.

## 3. Actual diagnostic outputs

Synthetic request: use the add tool for 2+3, then state the result.
The assistant emitted native `add` arguments `{"a":2,"b":3}` with integer
values. After the tool result `5`, it answered `The result of 2 + 3 is 5.`
Both responses had no nonempty thinking field. First response wall time was
37.665673 seconds including loading; second was 0.484875 seconds. These are
synthetic diagnostics, not screening episode times or biomedical competence.

Primary-server `/api/ps` reported:

| Quantity | Observed |
|---|---:|
| Context | 8192 |
| Loaded size | 6,402,196,107 bytes |
| Loaded size in VRAM | 5,614,044,445 bytes |
| CLI placement | 12% CPU / 88% GPU |
| Sampled total GPU usage | 7563 MiB / 8192 MiB |

Only Qwen was loaded. Windows process counters showed the inference runner as
the largest VRAM user, followed by the desktop compositor and desktop apps;
the saved counter sample is `gpu-process-memory.json`. The model includes a
5,629,109,120-byte text GGUF and a 921,704,832-byte vision projector.

An isolated Ollama server on localhost port 11435 reproduced the exact
loaded-size/VRAM values using the same binary, tag and generation settings.
It answered a synthetic `Reply with OK.` request with `OK`, with no thinking
field. Its captured loader log identifies the placement precisely:

- CUDA free memory at the fit calculation: 7088 MiB.
- Initial full-layer estimate: 5230 MiB of device memory.
- Free-memory target: 1927 MiB; reported shortfall: **70 MiB**.
- Projector worst-case reserve: 1152.01 MiB.
- User-set context 8192 retained unchanged.
- Final placement: **32/33 layers on GPU**, comprising the output layer and
  31 repeating layers. One repeating layer remains on CPU.
- CUDA model buffer 4674.33 MiB; CUDA-host model buffer 683.55 MiB;
  GPU KV cache 256 MiB; GPU recurrent-state buffer 48.16 MiB;
  GPU compute buffer 127.38 MiB.

See `ollama-memory-server.log`, particularly the fit calculation and
`offloaded 32/33 layers to GPU`. The temporary model was unloaded and the
temporary server stopped; the original server was retained.

The initial direct runner allocation probe did not inherit Ollama's CUDA loader
setup and used CPU only. Its log is retained but is **not evidence for normal
Ollama placement**. A first isolated-server attempt timed out during GPU
discovery; evidence is retained as `ollama-memory-startup-failure.*`. Adjusting
the diagnostic's server-readiness wait allowed the captured load above. No
official query was attempted, retried or saved during either diagnostic.

## 4. Interpretation and limits

The reproduced CPU placement includes a real text-layer offload, not merely the
vision projector. Freeing desktop VRAM may allow all 33 transformer/output layers
to fit with unchanged settings. The 70 MiB shortfall is a snapshot, not a
guarantee: background allocations vary, and embeddings/host buffers can remain
on the CPU even when every transformer/output layer is on GPU. A CLI percentage
alone cannot prove exact layer placement. No all-layer load has yet been tested.

No D3 quantity or pass/fail is defined for Qwen3.5 because its official 20-query
block has not started. Tool success here does not establish biomedical ability.

## 5. Unchanged recheck after closing apps

Researcher chose to close unused GPU apps, then explicitly said ready to recheck.
The repeated isolated Ollama load, using unchanged settings, again reported
32/33 layers on GPU, the same 70 MiB fitting shortfall and identical
size/size_vram values. Baseline GPU usage before loading was 926 MiB; loaded
usage was 7353 MiB. The model answered the synthetic request with `OK`, and the
temporary model/server were stopped. Logs: `memory-recheck-01/` in the evidence
directory. No official episode was run. Closing apps did not resolve placement
in this measured recheck; no further memory-setting change has been made.

## 6. Decisions and next action

The researcher approved adding Qwen3.5 9B as a ninth candidate and chose to pause
official screening for this investigation. The pending decision is whether to
accept the documented placement, investigate memory tuning in diagnostics, or
leave screening paused. No change to context, precision, model template, layer count,
memory-reserve settings or final S21 choices has been made.

## 7. Manual inspection

Inspect the two synthetic tool JSON files, `synthetic-ps.json`, and the fit/layer
lines in `ollama-memory-server.log`. Verify the unchanged official records using
`integrity-preflight.json`. Official inference remains paused pending researcher
instructions.
