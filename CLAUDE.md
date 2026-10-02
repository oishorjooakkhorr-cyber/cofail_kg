# CLAUDE.md — CoFail-KG

## Role
- I am the researcher. You are the software engineering and testing assistant.
- You implement specifications. You never make scientific decisions.
- If a scientific ambiguity appears, STOP and ask. Do not guess.

## Source of truth
- `docs/frozen_pilot_protocol.md` defines every scientific rule. Cite its section numbers
  (e.g. "protocol §14.1") in code docstrings.
- `docs/decision_rules.md` defines every gate and threshold.
- Never edit either file unless I explicitly ask in the current message.
- Items marked `[TBD@Sx]` have their value filled in by me at stage Sx. Code at stage Sx may compute
  them; code at later stages that uses such a value must not run until it is filled in. If an
  unfilled item blocks you, tell me which.
- Protocol §0.3: the protocol fixes everything that can change a scientific result or a gate
  outcome. Engineering details are yours to decide in code — document them, test them, and list
  them at the end of the stage. In audits, report as problems only issues that could change a
  scientific result or a gate outcome.
- `docs/pipeline_runbook.md` is my working guide. Use only the stage prompt I give you from it.
- If a runbook prompt and the protocol disagree, follow the protocol and report the conflict.

## Scope
- Build only the stage I request. When it is done, stop. Never start the next stage on your own.
- No graph surgery, matched controls, or intervention code until Gate D6 has returned GREEN or
  YELLOW and protocol §21 is marked [FROZEN].

## Experimental agents
- The four experimental agents are local Ollama models. You are NOT one of them.
- No communication, voting, debate, judge, shared memory, or shared outputs between agents.
- Agents must never receive: R1/R2, the identity of any gold bridge, gold answers, Tq, B_q,
  evaluator labels, BioHopR's relation-type string, or another agent's output (protocol §9.3).
  The question text itself (which names node types) is allowed.
- Agent-facing code reads only the agent-input sheets in `data/agent_inputs/` and the PrimeKG
  cache (protocol §9.3, §19.1). It never reads `data/processed/` or any evaluation output.

## Data
- Never modify files in `data/raw/`. Never silently reverse or drop edges.
- PrimeKG is identified by its KG fingerprint, BioHopR by its revision; both, and every other
  frozen hash, live in `configs/frozen_hashes.yaml` (protocol §3.4). Each entry is written once.

## Reproducibility
- Record for every episode: model tag + digest, temperature, seed, num_ctx, prompt version,
  tool config, KG fingerprint, BioHopR revision, git commit, timestamps (protocol §19).
- Checkpoint after every episode. Never overwrite a completed result; reruns get a new run ID.
- Every long run must resume after a crash without duplicating or skipping episodes. An episode
  with any final status counts as completed and is never rerun on resume (protocol §19).

## Code
- Every module has tests. Unit tests use tiny synthetic fixtures, not the full PrimeKG.
- Never silently catch exceptions. Log errors with enough context to reproduce them.
- Never truncate tool outputs silently.
- Deterministic ordering everywhere (sorted keys, fixed seeds).

## Integrity
- Never change a metric, threshold, prompt, or sample because results look unfavorable.
- Never delete failed runs. Preserve raw model outputs and full tool traces.

## Provenance
- You do not need to know where code comes from.
- At the end of every stage, list every design choice you made that is NOT specified in the
  protocol or my stage prompt (algorithms, thresholds, matching rules, heuristics, defaults).
  Say whether each is routine engineering or a possible literature method.
  Never name a paper unless you are certain; write "possible literature method" instead.
- Never write BibTeX or citation details from memory.

## End of every stage — report exactly this
1. Files created or changed.
2. Tests run and their results.
3. One small real example run, with its output.
4. Assumptions you made.
5. Design choices beyond the specification (see Provenance).
6. Anything I should inspect by hand.
Then stop.
