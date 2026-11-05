# S23 — Co-failure metrics (protocol §16): implementation report

**Scope.** This is offline evaluator code plus tests. It does **not** accept S22, which is still
paused under the §9.1 re-selection rule (see `docs/S22_review_packet.md`), and it does not
authorize S24 or later stages. No inference was run, and no protocol, rule, config, prompt, tool,
mapping, sample or earlier result was changed.

## Module

`src/cofail_kg/evaluation/cofailure.py`. It is evaluator-only, and no agent-facing module imports
it. It uses existing outputs only:

- the S19 `agent_metrics` row per (query, agent): §12 resolution, §13 Label A, §14.1 Label B,
  per-answer `h1`, §14.2 primary path and codes, `primary_path_max_list_size`, `list_size`;
- the S7 reference row (`s`, `A_star_q`, `B_q`, `T_q`, `relation_type`);
- the frozen per-type `R1`/`R2` and the manifest `ambiguity_tag`;
- §15 `degree_statistics`, which gives unique-neighbour degree under §3.2 and the inclusive
  same-type percentile.

It does not recompute any label, path or degree.

| Function | Protocol | Output |
|---|---|---|
| `query_cofailure(reference, mapping, ambiguity_tag, rows, degrees, agent_order)` | §16.1–§16.3 | `question` / `grounded` / `hop1_clean` / `benchmark` blocks, each with `cf3`, `cf4` and `shared_entities` (agents, degree, percentile, per-agent labels, primary paths, list sizes). Also `pcf_rel3/4`, `pcf_node3/4`, `pcf_shortcut3` with their `*_cases` (node, relation, degree, percentile, agents, per-agent contributing answers with primary path and `primary_path_max_list_size`), plus `W_Q`, `W_BH`, per-agent episode status and provenance, `technical_failure_agents` and `ambiguity_tag` |
| `pairwise_agreement(results, agent_order)` | §16.4 | The 6 unordered pairs: `numerator`, `denominator`, `agreement` (null = NA when the denominator is 0), and the query lists for both |

### How each definition is implemented

- **§16.1:** `W_iq` = resolved answers with Label A `OFF_QUESTION`, as a set per agent.
  - CF3 = some entity is in at least 3 agents' sets; CF4 = in all 4.
  - The *grounded* variant keeps an agent's entity only if its Label B ≠ `UNGROUNDED`.
    `KG_UNSUPPORTED` counts as grounded.
  - The *hop-1-clean* variant keeps it only if that answer's `h1` = 1. The agent-level `hop1_status`
    is never used for this.
  - Overlap is recomputed after each variant's filter.
- **§16.2:** `W^BH_iq` = resolved answer IDs − `A_star_q`, independent of Label A. ALT_VALID
  therefore counts here, and UNRESOLVED never does.
- **§16.3:** uses only the primary paths of `OFF_QUESTION` answers. `UNGROUNDED` and
  `KG_UNSUPPORTED` answers have no primary path, so they contribute nothing.
  - **Wrong-turn events:** step 1 with a label ∉ R1; step 2 with a label ∉ R2; the single step of a
    path whose primary codes contain `SHORTCUT`. A SHORTCUT step outside R1 is one step, so it counts
    as one event.
  - **Intermediate nodes:** every node of the primary path except its endpoints, dropping `s`, the
    answer, and members of `B_q ∪ T_q`.
  - **SHORTCUT cases:** grouped by the label of the single step from `s`.
  - Matching counts distinct agents. Repeats within one agent never add to the count.
- **§16.4:** uses the question-level `W` sets only. The denominator counts queries where both sets
  are non-empty; the numerator counts those where they intersect.

## Validation (raises `ValueError`; nothing is silently dropped)

- The agent order is 4 distinct agents.
- There is exactly one row per frozen agent: rows for a missing agent, a duplicate agent, an
  unknown agent or another query are rejected.
- A non-SUCCESS episode must have no scored answers.
- Labels must be valid values. Unresolved ⇔ `UNRESOLVED` ⇔ `NOT_APPLICABLE`.
- Label A must agree with `T_q`. `OFF_QUESTION` ∧ `SUPPORTED` is rejected, and `h1` = 1 is allowed
  only on SUPPORTED or PATH_INVALID answers.
- A primary path must be present exactly for SUPPORTED and PATH_INVALID answers, and must be a walk
  from `s` to the answer.
- Degree statistics must exist for every reported node.
- `pairwise_agreement` rejects duplicate queries.

## Tests — `tests/test_cofailure.py` (42 tests)

Every case required by the stage prompt is included, with hand-computed values:

- 4 share X → CF4 = 1, CF3 = 1. Three share X → CF4 = 0, CF3 = 1. X, X, Y, Z → 0. All different → 0.
- H1 = 0 for one of three → H1-CF3 = 0.
- One of three is UNGROUNDED → grounded CF3 = 0 while unfiltered CF3 = 1. Four share X with one
  UNGROUNDED → grounded CF3 = 1, grounded CF4 = 0.
- Shared ALT_VALID → excluded from CF^Q, included in CF^BH. UNRESOLVED never counts.
- Same wrong (node, relation) → PCF_REL3 = 1. The same relation at different source nodes does not
  match. Repeats within one agent do not count.
- Both hops violated → two events. Off-path node → PCF_NODE3 = 1. PCF_NODE excludes s, the answer,
  B_q and T_q.
- Three matching shortcut labels → PCF_SHORTCUT3 = 1. Alternative non-primary paths create no event.
- Pairwise agreement matches a hand-computed example. A pair with denominator 0 gives NA.
- Output is identical under shuffled answers and rows, and node IDs are in numeric order.
- Inclusive same-type percentile through `degree_statistics`; per-agent list sizes are kept.

Extra tests:

- KG_UNSUPPORTED counts as grounded.
- Filters recompute the overlap.
- A SHORTCUT with an accepted label is still an event.
- A PARSE_FAIL is reported and contributes nothing.
- Nine invalid-input cases are rejected.
- One end-to-end test feeds real `agent_metrics` output into `query_cofailure`.

## Real offline example (implementation exercise only)

`scripts/23_cofailure_example.py` runs on the 80 saved S22 `smoke_single_v135` metrics rows (20
screening queries) and writes `results/diagnostics/s23/smoke_single_v135_cofailure.json` (write-once).
Console output: `results/diagnostics/s23/example-console.txt`.

- Every question-level, grounded and hop-1-clean CF3 and CF4 is 0. Every PCF flag is 0.
- CF3^BH = CF4^BH = 1 on BH2_05686 and BH2_05843 (BOTH_AMBIGUOUS). All four agents share ALT_VALID
  answers there; for example, entity 14557 has degree 102 and same-type percentile 57.66.
- Pairwise: Gemma4-E4B–Granite41-8B = 1/2 = 0.5. Both had wrong answers on BH2_03881 and BH2_05366,
  and their sets intersect on BH2_05366, where they share all 30. The other five pairs have
  denominator 0 → NA.

These are screening queries from an unaccepted smoke run. They carry no scientific meaning and are
not pilot evidence.

## Exploratory comparison: Ornith15-9B in place of Qwen35-9B (researcher request, 2026-11-05)

**This is not a panel change and not S23 acceptance.** It uses screening queries only, with no
inference.

- **Script:** `scripts/23_ornith_substitution_example.py`
- **Output:** `results/diagnostics/s23/ornith_substitution_example.json` (write-once), with console
  output in `ornith-substitution-console.txt`
- **Panels:** Ministral, Gemma and Granite rows from S22 `smoke_single_v135`, plus either Qwen (S22)
  or Ornith (S20 block `ornith15-5060ti-32k-20261031`).
- **Run difference:** Ornith's episodes come from a separate S20 run. It used the same queries, P1,
  tools, evaluator and 32K f16 runtime as the three 32K agents.
- **Hash check:** all records were checked against their pinned `final-run-hashes.json` before use.

| Metric (20 queries) | Frozen panel (with Qwen) | With Ornith |
|---|---|---|
| CF3 / CF4, question level | 0 / 0 | 0 / 0 |
| CF3 / CF4, grounded | 0 / 0 | 0 / 0 |
| CF3 / CF4, hop-1-clean | 0 / 0 | 0 / 0 |
| CF3^BH / CF4^BH | 2 / 2 | 2 / 1 |
| All PCF flags | 0 | 0 |
| Pairwise, Gemma–Granite | 1/2 = 0.5 | 1/2 = 0.5 |
| Pairwise, Granite–fourth agent | 0/0 (NA) | 0/2 = 0.0 (BH2_03762, BH2_03991) |
| Other pairs with the fourth agent | NA | NA |
| Fourth agent's failed episodes | 2 PARSE_FAIL (BH2_03879, BH2_03991) | 1 ERROR/RUNTIME (BH2_03879), 1 PARSE_FAIL (BH2_03881) |
| Queries where the fourth agent has OFF_QUESTION answers | 1 (BH2_03760) | 10 |

Observations:

- **Ornith answers the start entity.** In 7 of Ornith's 10 queries with OFF_QUESTION answers, the
  only wrong answer is the start entity `s` itself, which is consistent with the S20 report.
- **No shared errors.** None of Ornith's wrong answers is shared with two other agents, so no CF3
  case appears.
- **Why CF4^BH falls.** On BH2_05686, Ornith gave none of the 14 shared ALT_VALID answers. Its only
  answer was `s`.
- **Low power.** With question-level CF3 = 0 in both panels, these 20 screening queries cannot
  separate the two panels on the primary metric.

## Researcher questions (implementation proceeds on the literal reading; tell me if it should change)

1. **Technical failures in §16.** A PARSE_FAIL, TIMEOUT or ERROR episode has no resolved answers, so
   it contributes an empty `W`. With one failed agent, CF4 cannot be 1 on that query. Such a query
   still enters CF3, and the pair's §16.4 denominator excludes it naturally. §16 does not say whether
   queries with failed episodes should be excluded or reported separately. The code keeps all
   queries and reports `technical_failure_agents` per query, so either convention can be applied
   later without recomputation. **Decision needed:** keep all queries, or exclude or flag queries
   with a failed episode?
2. **Wrong-turn events on paths that are not length 2.** Read literally, §16.3 gives:
   - a length-1 path to a non-Type_T node whose label ∉ R1 produces an event (step 1);
   - for a path of length ≥ 3, only steps 1 and 2 are checked;
   - a length-0 path (answer = s) produces none.

   **Confirm** that this literal reading is intended.
3. **SOURCE_NAME_OVERLAP (§19.1a).** Every §16 metric must also be reported with these queries
   excluded. The per-query output supports this filter, but it is applied at reporting time (S27),
   which is not built here.

## Design choices beyond the specification

| Choice | Class |
|---|---|
| Input is the S19 row unchanged plus the S7 reference row, mapping, tag and degrees | routine engineering |
| Within-agent sets (duplicates count once); counts are of distinct agents | routine engineering (follows §16 wording) |
| Failed episodes contribute empty sets; status passed through, not altered (question 1) | routine engineering, pending researcher confirmation |
| Shared-entity and PCF evidence lists only items reaching ≥ 3 agents | routine engineering |
| SHORTCUT is detected from the stored §14.2 primary codes | routine engineering (reuse) |
| A SHORTCUT step with a label ∉ R1 is one event, not two | routine engineering (same step) |
| PCF list-size evidence is the per-answer `primary_path_max_list_size`, with no cross-agent aggregation | routine engineering |
| Strict validation that raises on inconsistent inputs | routine engineering |
| Numeric node ordering; agents in frozen order; pairs in `itertools.combinations` order | routine engineering |
| §16.4 pairwise agreement | possible literature method; already attributed in the protocol to Kim et al. (2025), adapted to answer sets |
| All other §16 metrics | protocol's own definitions (Own) |
