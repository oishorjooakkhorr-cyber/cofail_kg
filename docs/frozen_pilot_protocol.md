# CoFail-KG — Frozen Pilot Protocol

**Version:** 1.0 (initial) · **Owner:** the researcher · **Implemented by:** Claude Code (read-only for Claude)

This file is the single source of truth for every scientific definition in the project.
Claude Code implements what is written here and nothing else. The runbook
(`docs/pipeline_runbook.md`) says *when* and *how* to build each part; this file says
*what* each part must do.

---

## 0. How to read this file

### Status tags

| Tag | Meaning |
|---|---|
| `[FROZEN]` | Decided. Changing it requires an entry in `docs/decision_log.md`. |
| `[TBD@Sx]` | Decided by the researcher at stage Sx of the runbook, from data. Claude Code must not implement anything that depends on this value before it is filled in. |
| `[DEFAULT]` | A recommended value. It becomes FROZEN when the named stage is completed, unless the researcher overrides it with a decision-log entry. |
| `[PROVISIONAL]` | Phase 2 (after the pilot gate). Revised and frozen only after the pilot. |

### Source tags

Every section ends with a **Source** line:

- **Cite:** an idea, dataset, or metric taken from a paper (full references in §23).
- **Own:** designed for this project; listed as a thesis contribution.
- **Standard:** common practice; no citation needed.
- ✔ = author/title/venue checked against the paper's own page. **VERIFY** = check before importing into Zotero.

---

## 1. Research question and hypotheses `[FROZEN]`

**Question.** When independent LLM agents navigate the same knowledge graph (PrimeKG) to answer the
same biomedical question, do they produce the same *question-invalid* answer because they are
exposed to the same graph structure, and does modifying that shared structure reduce the
correlated failure?

**Hypotheses.**

- **H1 (existence, pilot).** Independent KG-grounded agents produce shared question-invalid
  answers more often than a within-query chance baseline predicts.
- **H2 (structure, pilot — descriptive).** Shared failures concentrate on identifiable structural
  features (shortcut edges, specific wrong-relation branches, off-path high-degree nodes, large
  fan-out) and are not explained only by ambiguous relation wording.
- **H3 (causal, Phase 2).** Removing or blocking the shared structural feature reduces co-failure
  more than a matched control modification does.

The pilot tests the *feasibility* of H1 and describes H2. H3 is tested only if the pilot passes
its decision gate (`docs/decision_rules.md`, D6).

**Source.** Own. Motivated by correlated-error evidence in Kim et al. (2025) ✔ and Kohli (2026) ✔;
contrasted with CAGE-CAL, which studies correlation induced by *agent communication* rather than
by a shared external graph (Huang et al., 2026 ✔).

---

## 2. Scope `[FROZEN]`

**In the pilot:** BioHopR 2-hop questions; frozen PrimeKG; four independent agents; tool-based KG
navigation; answer and path labels; co-failure metrics; chance baselines; descriptive analysis;
decision gate.

**Not in the pilot:** any graph modification (surgery), matched controls, Structural Falsifier,
τ statistics, 1-hop or 3-hop questions, agent communication, voting, debate, judges, fine-tuning,
closed-book conditions.

**Source.** Standard (staged research design).

---

## 3. Data

### 3.1 BioHopR

| Item | Value | Status |
|---|---|---|
| Source | Hugging Face dataset `knowlab-research/BioHopR` | `[FROZEN]` |
| Revision | Dataset commit hash recorded at download | `[TBD@S2]` |
| Subset | 2-hop questions only (7,633 in the paper) | `[FROZEN]` |
| Question text given to agents | The multi-answer 2-hop question field, verbatim | `[TBD@S2]` exact field name |
| Field roles | Working hypothesis from the dataset card rows: `hop2` = query entity, `hop1` = bridge, `answer` = gold targets. **Must be verified.** | `[TBD@S5]` |

The 12 BioHopR 2-hop relation types (Query:Bridge:Target) and their counts from the paper:
Drug:Protein:Disease 3029 · Disease:Drug:Phenotype 949 · Disease:Protein:Drug 899 ·
Protein:Disease:Drug 577 · Phenotype:Disease:Drug 546 · Protein:Drug:Disease 462 ·
Disease:Drug:Protein 381 · Drug:Disease:Protein 321 · Phenotype:Drug:Disease 215 ·
Drug:Disease:Phenotype 213 · Disease:Phenotype:Drug 36 · Drug:Phenotype:Disease 5.

BioHopR defines a 2-hop gold answer as all nodes reachable *through the bridge node* of that row.
This protocol keeps that list as a secondary reference (`A*_q`) but defines correctness through
the question's relation pattern (§6).

**Source.** Cite: Kim, Abdulle & Wu (2025) ✔.

### 3.2 PrimeKG

| Item | Value | Status |
|---|---|---|
| Source | PrimeKG release on Harvard Dataverse (edge file `kg.csv`, plus node file if distributed) | `[FROZEN]` |
| Release | The release closest to the one BioHopR was built from; confirmed empirically by the S5/S6 reproduction rate | `[TBD@S4]` |
| Integrity | SHA256 of every raw file, recorded in `data/cache/primekg_metadata.json` | `[FROZEN]` |
| Canonical node ID | PrimeKG's unique node index (expected column `x_index`/`y_index`) — source IDs (`x_id`) are *not* unique across sources | `[TBD@S4]` confirm columns |
| Edge storage | Whether each relationship appears once or in both directions in `kg.csv` | `[TBD@S4]` |
| Substitution | Never replace PrimeKG with a newer graph (e.g., a successor KG) | `[FROZEN]` |

Expected check: the PrimeKG paper reports about 4.05 million relationships. If `kg.csv` has roughly
twice as many rows, relationships are stored in both directions.

**Source.** Cite: Chandak, Huang & Zitnik (2023) ✔.

---

## 4. Query specification (hidden from agents) `[FROZEN]`

For each 2-hop query `q`, the evaluator derives:

| Symbol | Meaning |
|---|---|
| `s` | Query entity (PrimeKG canonical ID) |
| `b*` | BioHopR gold bridge (PrimeKG canonical ID) |
| `R1`, `R2` | Sets of PrimeKG relation labels accepted for hop 1 and hop 2 (from §5) |
| `Type_B`, `Type_T` | Required bridge and target node types |
| `A*_q` | BioHopR gold answers, normalized to PrimeKG IDs (§12 rules applied to names) |

None of these are ever shown to an experimental agent (§9.3).

**Source.** Own (formalization); BioHopR's query/bridge/target terminology (Kim et al., 2025 ✔).

---

## 5. Relation mapping and ambiguity tags

### 5.1 BioHopR → PrimeKG relation mapping `[TBD@S6]`

For each of the 12 BioHopR relation pairs:

1. List every PrimeKG relation label (and display label) that connects the required node types
   for hop 1 and for hop 2.
2. For each candidate label set, compute on a validation sample (up to 30 rows per pair, seed 42)
   how often `T_q^{b*}` (computed with that set, §6) exactly equals `A*_q`.
3. **Selection rule:** choose the smallest label set with the highest exact-reproduction rate.
   If two different sets tie, or the best rate is below the D1 threshold, Claude Code stops and the
   researcher decides (decision-log entry).
4. The mapping is chosen **only** from BioHopR gold data — never from agent outputs.

Output: `results/semantics/relation_mapping.json` (frozen at Gate D1).

### 5.2 Relation-ambiguity tags `[TBD@S6]`

A hop is **ambiguous** when the question's natural-language wording for that hop could reasonably
refer to a PrimeKG relation label *outside* the accepted set (`R1` or `R2`) that connects the same
node types. Examples of the kind of case this captures: wording like "related to a phenotype"
when PrimeKG separates phenotype-present from phenotype-absent edges; "treats" when PrimeKG
separates indication from off-label use.

Procedure (done before any agent is run):

1. Claude Code lists, per hop, all PrimeKG labels connecting the relevant types, with the
   question template wording.
2. The researcher fills `results/semantics/ambiguity_judgments.csv`, marking each non-accepted
   label as `PLAUSIBLE` or `NOT_PLAUSIBLE` for the wording.
3. Tag per relation pair: `NONE`, `R1_AMBIGUOUS`, `R2_AMBIGUOUS`, or `BOTH_AMBIGUOUS`.
4. Optional robustness: a second rater (e.g., supervisor) repeats step 2 blind; disagreements are
   logged and resolved before S10.

**Source.** Own.

---

## 6. Reference sets `[FROZEN]` (definitions) — computed at S7

- **Valid bridges:** `B_q = { b : type(b) = Type_B, b ≠ s, and PrimeKG has an edge (s, r, b) with r ∈ R1 }`
- **Per-bridge targets:** `T_q(b) = { t : type(t) = Type_T, t ≠ s, and PrimeKG has an edge (b, r, t) with r ∈ R2 }`
- **Question-valid answers:** `T_q = ⋃_{b ∈ B_q} T_q(b)`
- **Gold-bridge targets:** `T_q^{b*} = T_q(b*)`
- **BioHopR gold:** `A*_q`

`T_q` is the correctness reference: it is everything the question's relation pattern returns when
executed over PrimeKG. `A*_q` is kept for benchmark comparison only.

"Edge (u, r, v)" follows the edge-storage convention confirmed at S4. If PrimeKG stores both
directions, an edge between u and v with label r counts in either direction.

**Source.** Cite: answer set defined by executing the question's query pattern over the KG, as in
WebQSP (Yih et al., 2016, VERIFY). Departure from BioHopR's single-bridge answer definition is
Own and must be stated in the thesis.

---

## 7. Query status and inclusion

### 7.1 Status labels `[FROZEN]`

| Label | Rule |
|---|---|
| `CONSISTENT` | `A*_q` (normalized) exactly equals `T_q^{b*}` |
| `INCONSISTENT` | Otherwise, with one reason code: `QUERY_NOT_FOUND`, `BRIDGE_NOT_FOUND`, `GOLD_UNMAPPED` (a gold name cannot be normalized), `GOLD_MISSING_FROM_KG` (gold ∖ `T_q^{b*}` non-empty), `EXTRA_TARGETS` (`T_q^{b*}` ∖ gold non-empty) |
| `SINGLE_BRIDGE` | B_q has exactly one member |
| `MULTI_BRIDGE` | B_q has two or more members |
| `SATURATED` | `T_q` contains more than a threshold share of all PrimeKG nodes of `Type_T` (see 7.2) |

### 7.2 Inclusion rules

| Rule | Value | Status |
|---|---|---|
| Primary population | `CONSISTENT` ∧ not `SATURATED` ∧ relation pair passed Gate D1 | `[FROZEN]` |
| Saturation threshold | `[DEFAULT]` 50% of all `Type_T` nodes. Rationale: when almost every node of the target type is question-valid, an `OFF_QUESTION` answer is nearly impossible, so the query carries no information about co-failure. | `[TBD@S9]` |
| Absolute size cap on the size of `T_q` | None by default. Add only if S3/S9 show a technical need; hub-heavy queries are scientifically interesting and should not be removed for convenience. | `[TBD@S9]` |
| `INCONSISTENT` queries | Reported in the dataset table; not sampled for the pilot | `[FROZEN]` |

**Source.** Own.

---

## 8. Sampling `[FROZEN]` procedure — executed at S10

| Set | Size | Use |
|---|---|---|
| Screening | 20 | Model screening (S20) and single-agent smoke test (S22) |
| Smoke | 4 | Four-agent panel smoke test (S25) |
| Pilot | 100 | The pilot (S27) |
| Expansion reserve | 400 | Added only if Gate D6 allows expansion to 500 |

All sets are disjoint and drawn from the primary population with seed **42**.

**Allocation.**

1. Strata = relation pair × bridge multiplicity (`SINGLE_BRIDGE` / `MULTI_BRIDGE`).
2. Pilot target mix `[DEFAULT]`: 25% `SINGLE_BRIDGE`, 75% `MULTI_BRIDGE`, capped by availability.
3. Across relation pairs: proportional to the primary-population share, with a floor of
   `min(3, available)` per pair; rounding by largest remainder.
4. Within a stratum: order candidates by `SHA256(str(seed) + query_id)` ascending and take the first
   `n` — deterministic and independent of file order.
5. Draw order: screening → smoke → pilot → expansion reserve, each excluding earlier draws.
6. Record ambiguity tag and `|T_q|` bin for every sampled query (descriptive; not stratified).

**Source.** Standard (stratified deterministic sampling).

---

## 9. Agents and runtime

### 9.1 Models and runtime settings

| Item | Value | Status |
|---|---|---|
| Number of agents | 4 | `[FROZEN]` |
| Runtime | Ollama (local) | `[FROZEN]` |
| Models | Four models passing Gate D3, from ≥ 3 distinct families (prefer 4) | `[TBD@S21]` |
| Model identity record | Ollama tag + model digest + quantization | `[FROZEN]` |
| Temperature | 0 | `[FROZEN]` |
| Seed | 42 for every model | `[FROZEN]` |
| Context length (`num_ctx`) | From screening token counts and VRAM | `[TBD@S21]` |
| Max output tokens per turn | From S3 answer-size statistics | `[TBD@S21]` |
| Tool-call budget per episode | — | `[TBD@S21]` |
| Wall-clock timeout per episode | — | `[TBD@S21]` |

### 9.2 Independence `[FROZEN]`

Each agent runs in its own fresh conversation. No agent sees another agent's messages, answers,
or traces. No voting, debate, judge, shared memory, or shared cache of model outputs. Agents run
sequentially (one model loaded at a time).

### 9.3 What the agent receives `[FROZEN]`

1. A system prompt containing: tool descriptions, output-format rules, and the rule
   "answer using entities you found with the tools".
2. A user message containing **only**: the BioHopR multi-answer 2-hop question text (verbatim) and
   `Starting entity: <name> (PrimeKG ID: <id>)`.

The agent **never** receives: `R1`, `R2`, `Type_B`, the gold bridge, gold answers, `T_q`,
any evaluator label, the relation-pair name, or any other agent's output.

### 9.4 Output format `[FROZEN]`

The final assistant message must be exactly one JSON object:

```json
{"status": "answered", "answers": [{"id": "<PrimeKG ID>", "name": "<entity name>"}]}
```

or `{"status": "no_answer", "answers": []}`.

Parsing rule: if the final message is not valid JSON of this shape, the runner sends **exactly one**
fixed re-prompt ("Your last message was not valid JSON in the required format. Reply with only the
JSON object.") The re-prompt is identical for every model and logged. If the second reply also
fails, the episode is `PARSE_FAIL` (a technical failure, counted in Gate D6's E).

**Source.** Standard (tool-using agent loop: ReAct, Yao et al., 2023, VERIFY); Own (format rules).

---

## 10. KG environment (tools) `[FROZEN]` design — built at S11

Agents access PrimeKG only through two functions. The environment reads the frozen PrimeKG index;
it never reads evaluation files.

**`inspect_entity(entity_id)`** → entity ID, name, type, and the list of relations touching it; for
each relation: label, neighbor node type(s), and neighbor count.

**`get_neighbors(entity_id, relation, neighbor_type=None, page=1)`** → the neighbors of that
entity through that relation: for each neighbor its ID, name and type; plus `total_count`, `page`,
`page_size`, `has_more`. (A `direction` argument is added only if S4 shows PrimeKG stores
asymmetric directed edges — `[TBD@S4]`.)

| Rule | Value |
|---|---|
| Graph scope | Full frozen PrimeKG, all node types |
| Name search tool | None. The agent starts from the given entity ID; entity linking is not part of the task. |
| Neighbor counts in `inspect_entity` | Shown |
| Relation ordering | Alphabetical by label |
| Neighbor ordering | Ascending canonical node ID (neutral, fixed; its shared effect is measured, §15) |
| Page size | `[TBD@S21]` |
| Truncation | Never silent: `total_count` and `has_more` always returned |
| Invalid input | Structured error message returned to the agent; counts toward the budget |
| Budget exhausted | Structured message: "Tool budget exhausted. Give your final answer now." |
| Logging | Every call, arguments, full returned IDs, page, `total_count`, timing |

**Source.** Cite: function-based graph interaction for LLMs, including a neighbor-listing and a
degree/count function, adapted from Graph-CoT (Jin et al., 2024 ✔ title/venue; authors VERIFY);
relation-then-entity exploration as in Think-on-Graph (Sun et al., 2024, VERIFY). Own: pagination,
ordering, budget, no-search rule.

---

## 11. Trace and trace graph `[FROZEN]`

Every episode stores a trace: all messages, all tool calls with arguments and complete results,
timings, token counts, model identity, seed, prompt version, PrimeKG hash, git commit.

**Trace graph `TG_i`** for agent `i` on query `q`: for every successful `get_neighbors(u, r, ...)`
call, add a directed edge `(u, r, v)` for each neighbor `v` **on the returned page**. Nothing else
adds edges. All path statements in §14 are about paths in `TG_i`.

**Appeared in tool output:** entity `x` appeared if it was returned by any tool call (as a
neighbor, or as the subject of a successful `inspect_entity`).

**Source.** Cite: path-level reasoning traces (KG-TRACES, arXiv 2506.00783 ✔ title; authors VERIFY).
Own: trace-graph construction rules.

---

## 12. Answer normalization `[FROZEN]`

For each item in the agent's `answers` list, in order:

1. If `id` is a valid PrimeKG canonical ID → that node. If the given `name` differs from the
   node's name, log `NAME_ID_MISMATCH` (the ID wins).
2. Else, exact name match after lower-casing, Unicode NFKC normalization and whitespace collapsing:
   exactly one node → that node; several nodes → the unique one of type `Type_T` if exactly one
   exists; otherwise `UNRESOLVED (AMBIGUOUS_NAME)`.
3. Else `UNRESOLVED (NO_MATCH)`.

Duplicates within one agent's answer set are removed after normalization. No fuzzy or embedding
matching in the pilot: agents copy IDs from tool output, so matching decisions are rarely needed,
and every extra matching rule is a researcher degree of freedom. (BioHopR itself used embedding
similarity with BioLORD-2023 at τ = 0.9 because its models answered in free text without a KG.)

The same rules normalize BioHopR gold names to `A*_q` (with `Type_T` as the type filter).

**Source.** Own; contrast with BioHopR's evaluation (Kim et al., 2025 ✔; Remy et al., 2023 ✔).

---

## 13. Label A — answer status `[FROZEN]`

Each resolved predicted entity `x` gets exactly one label; the first matching rule wins:

| Priority | Label | Rule |
|---|---|---|
| 1 | `UNRESOLVED` | Normalization failed (§12) |
| 2 | `GOLD` | `x ∈ A*_q` |
| 3 | `GOLD_BRIDGE_EXTRA` | `x ∈ T_q^{b*}` and `x ∉ A*_q` (a dataset/KG discrepancy; empty for CONSISTENT queries) |
| 4 | `ALT_VALID` | `x ∈ T_q` and `x ∉ T_q^{b*}` |
| 5 | `OFF_QUESTION` | `x` is a PrimeKG node and `x ∉ T_q` |

**Question-valid** = `GOLD` ∪ `GOLD_BRIDGE_EXTRA` ∪ `ALT_VALID`. `ALT_VALID` is never an error.

**Source.** Own.

---

## 14. Label B — path status, reason codes, hop-1 status `[FROZEN]`

### 14.1 Label B (first matching rule wins)

| Priority | Label | Rule |
|---|---|---|
| 1 | `UNGROUNDED` | `x` never appeared in any tool output in this episode |
| 2 | `SUPPORTED` | `TG_i` contains `s –r1→ b –r2→ x` with `r1 ∈ R1`, `type(b) = Type_B`, `b ≠ s`, `r2 ∈ R2`, `type(x) = Type_T`, `x ≠ s` |
| 3 | `PATH_INVALID` | `x` appeared, `TG_i` contains at least one directed path from `s` to `x`, but none satisfies rule 2 |
| 4 | `KG_UNSUPPORTED` | `x` appeared, but `TG_i` contains no path from `s` to `x` (the agent reached `x` through an entity ID it did not obtain from the query entity's neighborhood) |

A trace that follows valid relations, e.g. query disease → (accepted hop-1 relation) → drug →
(accepted hop-2 relation) → phenotype, is `SUPPORTED`.

### 14.2 Reason codes (for `PATH_INVALID` only)

Examine all simple paths from `s` to `x` in `TG_i` of length ≤ 3. For each path, assign every code
that applies; record the union across paths and the codes of the **primary path** (shortest;
ties broken by earliest tool call).

| Code | Condition on a path |
|---|---|
| `SHORTCUT` | Length 1 and `type(x) = Type_T` |
| `WRONG_RELATION_HOP1` | Length 2 and first relation ∉ `R1` |
| `WRONG_BRIDGE_TYPE` | Length 2 and middle node type ≠ `Type_B` |
| `WRONG_RELATION_HOP2` | Length 2 and second relation ∉ `R2` |
| `WRONG_TARGET_TYPE` | Any length and `type(x) ≠ Type_T` |
| `WRONG_HOP_COUNT` | Length ≥ 3 (or no path of length ≤ 3 exists) |

### 14.3 Hop-1 status

**Per answer:** `H1(x, i) = 1` if `TG_i` contains an edge `(s, r, b)` with `r ∈ R1`,
`type(b) = Type_B`, and `b` lies on some path from `s` to `x`. Otherwise 0 (always 0 for
`UNGROUNDED` and `KG_UNSUPPORTED`).

**Per agent (for Gate D6):** based on all `get_neighbors` calls issued on `s`:
`H1_CLEAN` (all use relations in `R1`), `H1_MIXED` (some in `R1`, some not), `H1_WRONG` (at least
one call, none in `R1`), `H1_NONE` (no call on `s`). An agent **found R1** if `H1_CLEAN` or
`H1_MIXED`.

**Source.** Own. Motivation for tracking ungrounded answers: KG-RAG systems benefit from textual
entity labels in ways that suggest reliance on memorized knowledge (Zhou et al., 2025b,
arXiv 2508.08344 ✔ title; authors VERIFY).

---

## 15. Per-agent metrics `[FROZEN]`

For each agent and query:

- Counts of every Label A and Label B class; reason-code frequencies (all paths and primary path).
- **Question-valid precision** = question-valid answers / resolved answers.
- **OFF_QUESTION rate**, **UNRESOLVED rate**, **UNGROUNDED rate**.
- **Benchmark precision / recall / F1** against `A*_q` (secondary; for comparison with BioHopR).
- **Hop-1 status** (§14.3).
- **Bridges explored:** members of `B_q` on which the agent called `get_neighbors`.
- **Bridge rank:** position of each explored bridge in the list returned from `s` (to measure
  ordering effects).
- **Bridge-conditional recall** for each explored valid bridge `b`: |answers ∩ `T_q(b)`| / |`T_q(b)`|
  (diagnostic only).
- **Early stop:** the agent answered with items from page 1 of a list whose `has_more` was true and
  never requested page 2 of that list.
- **FIRST_SEEN_PAGE** for every answer; pages requested; tool calls used; budget-exhausted flag.

**Source.** Standard (precision/recall/F1); Own (the rest).

---

## 16. Co-failure metrics `[FROZEN]`

### 16.1 Answer-level (primary)

`W_iq` = agent `i`'s resolved answers labeled `OFF_QUESTION` on query `q`.

- **CF4^Q(q) = 1** if some entity is in `W_iq` for all four agents.
- **CF3^Q(q) = 1** if some entity is in `W_iq` for at least three agents.
- **Grounded variants:** same, using only entities whose Label B ≠ `UNGROUNDED`.
- **Hop-1-clean variants:** **CF3^{Q,H1}(q) = 1** if some entity `x` is in `W_iq` for at least three
  agents **and** `H1(x, i) = 1` for each of those agents; **CF4^{Q,H1}** likewise for all four.
- `UNRESOLVED` answers never enter any `W`.

### 16.2 Benchmark comparison (secondary)

`W^BH_iq` = resolved answers ∖ `A*_q`. **CF3^BH**, **CF4^BH** defined as in 16.1. The difference
between CF^BH and CF^Q shows how many apparent benchmark co-failures are valid alternative answers.

### 16.3 Path-level (secondary: *how* agents failed)

- **Wrong-turn event:** on the primary path of an `OFF_QUESTION` answer, the step `(u, r)` whose
  relation violates the specification (a `WRONG_RELATION_HOP1`, `WRONG_RELATION_HOP2`, or
  `SHORTCUT` step).
- **PCF_REL3 / PCF_REL4 (q) = 1** if the same `(u, r)` wrong-turn event occurs for ≥ 3 / 4 agents.
- **PCF_NODE3 / PCF_NODE4 (q) = 1** if some node `v ∉ {s} ∪ B_q ∪ T_q` lies on the primary path of
  an `OFF_QUESTION` answer for ≥ 3 / 4 agents (an off-path node shared by the failures).
- **PCF_SHORTCUT3 (q) = 1** if ≥ 3 agents have an `OFF_QUESTION` answer whose primary path is a
  `SHORTCUT` from `s` via the same relation.
- For every PCF case, record the node(s), their PrimeKG degree and degree percentile, the
  relation(s), and the query's ambiguity tag.

### 16.4 Pairwise error agreement

For each pair of agents `(i, j)`: among queries where both `W_iq` and `W_jq` are non-empty, the
fraction where `W_iq ∩ W_jq ≠ ∅`. This adapts the "agreement when both are wrong" measure of
Kim et al. (2025) from single answers to answer sets; state the adaptation in the thesis.

**Source.** Cite: Kim et al. (2025) ✔ for 16.4. Own for 16.1–16.3.

---

## 17. Chance baselines `[FROZEN]`

Purpose: estimate how much agreement on wrong answers would occur if each agent picked its wrong
answers at random from the wrong candidates it actually saw.

**Candidate pool** for agent `i` on query `q`:
`C_iq = { x : x appeared in agent i's tool outputs, type(x) = Type_T, x ∉ T_q, x ≠ s }`.

**Observed quantity** (restricted to what the null can model):
`W'_iq = { x ∈ W_iq : Label B(x) ≠ UNGROUNDED and type(x) = Type_T }`, `k_iq = |W'_iq|`.
By construction `W'_iq ⊆ C_iq`. Ungrounded and wrong-type shared answers are reported separately.

**Null N1 (uniform).** In each of 10,000 trials (seed 42), every agent draws `k_iq` distinct
entities uniformly from `C_iq`; compute CF3 on the drawn sets. Per query: null probability of CF3.
Aggregate: observed total `O = Σ_q CF3(W')`; null totals `N_t` summed across queries within each
trial; report null mean, median, 95th percentile, and exceedance
`p = (1 + #{t : N_t ≥ O}) / (1 + 10,000)`. **"Observed exceeds null"** means `O` > null 95th percentile.
The same is computed for the hop-1-clean subset and for CF4.

**Null N2 (ordering sensitivity).** Same as N1, but each `C_iq` is restricted to entities that
appeared on **page 1** of the lists the agent opened. All agents see identical first pages, so N2
approximates agreement produced by shared ordering alone. If observed agreement exceeds N1 but not
N2, the result is reported as "consistent with an ordering effect".

Test requirement: when all agents give the same single wrong answer but each saw many other wrong
candidates, the null probability must be low (the null must not reproduce agreement by construction).

**Source.** Own (Monte Carlo null). Context: Kohli (2026) ✔ compares panels against an
independent-voting (Condorcet) null.

---

## 18. Decision rules

All gates (D1–D8), thresholds and precedence are in `docs/decision_rules.md`. They are frozen
before the data they judge is seen.

**Source.** Cite: pre-registration of analysis decisions (Nosek et al., 2018, VERIFY).

---

## 19. Reproducibility `[FROZEN]`

- Every episode record includes: query ID, agent ID, model tag + digest, temperature, seed,
  `num_ctx`, prompt version, tool configuration, PrimeKG SHA256, BioHopR revision, git commit,
  timestamps, full trace, raw final output, parse status.
- Results are write-once: a completed episode file is never overwritten; reruns write new files
  with a new run ID.
- Long runs checkpoint after every episode and resume without duplicating completed episodes.
- Raw data files are never modified.

**Source.** Standard.

---

## 20. Change control `[FROZEN]`

- Implementation bug fixes that do not change any definition here: allowed; note in `progress.md`.
- Any change to this file after its section is frozen: requires a dated entry in
  `docs/decision_log.md` stating what, why, and whether any data had been seen.
- Changes made after seeing pilot results are labeled **exploratory** in the thesis.

**Source.** Standard.

---

## 21. Phase 2 — intervention design `[PROVISIONAL]`

Revised and frozen after Gate D6/D7. Recorded now so the pilot collects what Phase 2 needs.

- **Candidate rule:** `CONSISTENT` query ∧ CF3^{Q,H1} = 1 ∧ a PCF event identifies a specific
  shared structural feature (edge, relation branch at a node, or off-path node) ∧ blocking it
  leaves at least one `SUPPORTED` route to `T_q`.
- **Surgery:** implemented as a query-local *overlay* in the tool layer (the original PrimeKG files
  are never modified): remove specific edges `(u, r, v)`, or hide relation `r` at node `u`.
  Never delete the only valid bridge.
- **Matched control:** a feature of the same kind at the same hop position, same relation label
  where possible, degree within ±25% (else nearest), not used by any agent in the original run,
  whose removal also leaves a valid route. If none exists, the case is treatment-only exploratory.
- **Outcomes:** CF3/CF4 before vs after; PCF before vs after; recovery = share of agents whose
  answers become question-valid; abstention (no-answer) change, which is not recovery;
  **displacement** — where each agent goes after treatment: `VALID_RELATION`,
  `SAME_WRONG_RELATION_OTHER_NEIGHBOR` (evidence the error was semantic), `OTHER_WRONG`,
  `NO_ANSWER`.
- **Effect:** ΔCF = CF_before − CF_after; τ_CF = ΔCF_treatment − ΔCF_control.

**Source.** Cite: counterfactual deletion to explain predictions (GNNExplainer, Ying et al., 2019,
VERIFY; CF-GNNExplainer, Lucic et al., 2022, VERIFY); random vs reasoning-path deletion baselines
(Zhou et al., 2025a ✔); component-level KG perturbation (Balanos et al., 2025 ✔); counterfactual
validation of root causes (LIDL, arXiv 2601.05539, VERIFY); centrality vs learned evidence
(arXiv 2606.14805 ✔ title, VERIFY authors). Own: matched-control design and displacement categories.

---

## 22. Optional, not part of the design

A closed-book comparison (same models, same questions, no tools) may be run later as an
exploratory follow-up. It is not a planned condition and is reported as exploratory if run.

---

## 23. References

✔ = checked against the paper's own page during planning. VERIFY = confirm before citing.
Import every entry into Zotero from the official page; never type BibTeX by hand.

- Balanos, G., Chasanis, E., Skianis, K., & Pitoura, E. (2025). *KGRAG-Ex: Explainable Retrieval-Augmented Generation with Knowledge Graph-based Perturbations.* arXiv:2507.08443. ✔
- Chandak, P., Huang, K., & Zitnik, M. (2023). *Building a knowledge graph to enable precision medicine.* Scientific Data, 10(1), 67. ✔
- Huang, J., Li, M., Li, Z., Kwon, S., Yu, H., & Zhang, C. (2026). *Counterfactual Graph for Multi-Agent LLM Calibration* (CAGE-CAL). arXiv:2605.30653. ✔
- Jin, B., et al. (2024). *Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs.* Findings of ACL 2024. ✔ title/venue · VERIFY authors
- Kim, E. M., Garg, A., Peng, K., & Garg, N. (2025). *Correlated Errors in Large Language Models.* ICML 2025, PMLR 267:30038–30066. ✔
- Kim, Y., Abdulle, Y., & Wu, H. (2025). *BioHopR: A Benchmark for Multi-Hop, Multi-Answer Reasoning in Biomedicine.* Findings of ACL 2025 (arXiv:2505.22240). ✔
- Kohli, G. (2026). *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels.* arXiv:2605.29800. ✔
- KG-TRACES: *Knowledge Graph-constrained Trajectory Reasoning Attribution and Chain Explanation Supervision.* arXiv:2506.00783. ✔ title · VERIFY authors
- *Knowledge-Based Zero-Replay Debugging of Multi-Agent LLM Traces.* arXiv:2606.14805. ✔ title · VERIFY authors
- LIDL. arXiv:2601.05539. VERIFY title and authors
- Lucic, A., et al. (2022). *CF-GNNExplainer: Counterfactual Explanations for Graph Neural Networks.* AISTATS 2022. VERIFY
- Nosek, B. A., et al. (2018). *The preregistration revolution.* PNAS. VERIFY
- Remy, F., Demuynck, K., & Demeester, T. (2023). *BioLORD-2023: Semantic textual representations fusing LLM and clinical knowledge graph insights.* arXiv:2311.16075. ✔
- Sun, J., et al. (2024). *Think-on-Graph: Deep and Responsible Reasoning of Large Language Model on Knowledge Graph.* ICLR 2024. VERIFY
- Yao, S., et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023. VERIFY
- Yih, W., et al. (2016). *The Value of Semantic Parse Labeling for Knowledge Base Question Answering.* ACL 2016. VERIFY
- Ying, R., et al. (2019). *GNNExplainer: Generating Explanations for Graph Neural Networks.* NeurIPS 2019. VERIFY
- Zhou, D., Zhu, Y., et al. (2025a). *Evaluating Knowledge Graph Based Retrieval Augmented Generation Methods under Knowledge Incompleteness.* arXiv:2504.05163. ✔
- Zhou, D., et al. (2025b). *What Breaks Knowledge Graph based RAG? Benchmarking and Empirical Insights into Reasoning under Incomplete Knowledge.* arXiv:2508.08344. ✔ title · VERIFY authors
- Software: Ollama (cite repository/documentation); each experimental model (cite its technical report or model card).
