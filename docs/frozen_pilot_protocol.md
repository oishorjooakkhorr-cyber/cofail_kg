# CoFail-KG — Frozen Pilot Protocol

**Version:** 1.1 (S1 audit fixes) · **Owner:** the researcher · **Implemented by:** Claude Code (read-only for Claude)

This file is the single source of truth for every scientific definition in the project.
Claude Code implements what is written here and nothing else. The runbook
(`docs/pipeline_runbook.md`) says *when* and *how* to build each part; this file says
*what* each part must do.

---

## 0. How to read this file

### 0.1 Status tags

| Tag | Meaning |
|---|---|
| `[FROZEN]` | Decided. Changing it requires an entry in `docs/decision_log.md`. |
| `[TBD@Sx]` | Decided by the researcher at stage Sx. A recommended value may be given, but nothing that depends on it may be implemented before it is filled in. |
| `[DEFAULT]` | Used as written unless the researcher overrides it, with a decision-log entry, at or before the stage named. It becomes FROZEN when that stage is completed. |
| `[PROVISIONAL]` | Phase 2. Frozen at S29 (§21). |

### 0.2 Source tags

Every section ends with a **Source** line: **Cite** (from a paper; references in §23), **Own**
(designed here; a thesis contribution), or **Standard** (no citation needed).
✔ = checked against the paper's own page. VERIFY = confirm before citing.

### 0.3 Terms used throughout

| Term | Definition |
|---|---|
| **Row** | One BioHopR record. `row_id` = `"BH2_"` + the row's index in the pinned revision, zero-padded to 5 digits. |
| **Relation type** | BioHopR's Query:Bridge:Target type triple, read from the row's 2-hop relation field (e.g. `drug:effect/phenotype:disease`). There are 12. Each relation type has two hops. |
| **Query** | The unit of analysis: one unique pair (query entity `s`, relation type). All rows sharing them have the same question text and form one query. `query_id` = the `row_id` of its lowest-index row. |
| **Label** | A value of PrimeKG's `relation` column. All rules in this file use labels. |
| **Display label** | A value of PrimeKG's `display_relation` column. Shown to agents for information only; never used in any rule. |
| **Type_S, Type_B, Type_T** | Node types of the query entity, bridge and target, from the relation type, mapped to PrimeKG node types by the type map (§3.3). |
| **n** | Number of agents: 4 (§9.2). |
| **Episode** | One agent answering one query. |

**Source.** Own.

---

## 1. Research question and hypotheses `[FROZEN]`

**Question.** When independent LLM agents navigate the same knowledge graph (PrimeKG) to answer the
same biomedical question, do they produce the same *question-invalid* answer because they are
exposed to the same graph structure, and does modifying that shared structure reduce the
correlated failure?

- **H1 (existence, pilot).** Independent KG-grounded agents produce shared question-invalid
  answers more often than a within-query chance baseline predicts.
- **H2 (structure, pilot — descriptive).** Shared failures concentrate on identifiable structural
  features (shortcut edges, specific wrong-relation branches, off-path nodes, large fan-out) and
  are not explained only by ambiguous relation wording.
- **H3 (causal, Phase 2).** Removing or blocking the shared structural feature reduces co-failure
  more than a matched control modification does.

The pilot tests the feasibility of H1 and describes H2. H3 is pursued only if Gate D6 returns
GREEN or YELLOW (`docs/decision_rules.md`).

**Source.** Own. Motivated by Kim et al. (2025) ✔ and Kohli (2026) ✔; contrasted with CAGE-CAL
(Huang et al., 2026 ✔), which studies correlation induced by agent communication.

---

## 2. Scope `[FROZEN]`

**In the pilot:** BioHopR 2-hop questions; frozen PrimeKG; four independent agents; tool-based KG
navigation; answer and path labels; co-failure metrics; chance baselines; descriptive analysis;
decision gate.

**Not in the pilot:** graph modification, matched controls, Structural Falsifier, τ statistics,
1-hop or 3-hop questions, agent communication, voting, debate, judges, fine-tuning, closed-book runs.

**Source.** Standard.

---

## 3. Data

### 3.1 BioHopR

| Item | Value | Status |
|---|---|---|
| Source | Hugging Face dataset `knowlab-research/BioHopR` | `[FROZEN]` |
| Revision | Dataset commit hash recorded at download | `[TBD@S2]` |
| Subset | 2-hop questions (7,633 rows in the paper) | `[FROZEN]` |
| Question text given to agents | The multi-answer 2-hop question field, verbatim | `[TBD@S2]` field name |
| Field roles | Working hypothesis: `hop2` = query entity, `hop1` = bridge, `answer` = gold targets. Must be verified. | `[TBD@S5]` |

The 12 relation types and their row counts in the paper: Drug:Protein:Disease 3029 ·
Disease:Drug:Phenotype 949 · Disease:Protein:Drug 899 · Protein:Disease:Drug 577 ·
Phenotype:Disease:Drug 546 · Protein:Drug:Disease 462 · Disease:Drug:Protein 381 ·
Drug:Disease:Protein 321 · Phenotype:Drug:Disease 215 · Drug:Disease:Phenotype 213 ·
Disease:Phenotype:Drug 36 · Drug:Phenotype:Disease 5.

**Source.** Cite: Kim, Abdulle & Wu (2025) ✔.

### 3.2 PrimeKG

| Item | Value | Status |
|---|---|---|
| Source | PrimeKG on Harvard Dataverse (`kg.csv`, plus node file if distributed) | `[FROZEN]` |
| Release | The release closest to BioHopR's, confirmed by the S4 Troglitazone check and Gate D1 | `[TBD@S4]` |
| Integrity | SHA256 of every raw file, stored in `data/cache/primekg_metadata.json` | `[FROZEN]` |
| Canonical node ID | PrimeKG's unique node index (expected `x_index` / `y_index`), written as a decimal string | `[TBD@S4]` confirm columns |
| Edge storage | Whether each relationship appears once or in both directions | `[TBD@S4]` |
| Edge convention | All rules treat an edge between u and v with label r as usable in either direction, unless S4 finds asymmetric directed labels (then the S4 decision-log entry defines the direction per label) | `[TBD@S4]` |
| Substitution | Never replace PrimeKG with a different or newer graph | `[FROZEN]` |

Expected check: the PrimeKG paper reports about 4.05 million relationships; about twice as many
rows means both directions are stored.

**Source.** Cite: Chandak, Huang & Zitnik (2023) ✔.

### 3.3 Type map `[TBD@S4]`

A one-to-one map from BioHopR's four types (drug, disease, gene/protein, effect/phenotype) to
PrimeKG `node_type` values. Expected to be identical strings; confirmed at S4.

**Source.** Standard.

---

## 4. Query specification (hidden from agents) `[FROZEN]`

For each query `q`:

| Symbol | Meaning |
|---|---|
| `s` | Query entity: its BioHopR name normalized to PrimeKG (§12, type filter Type_S) |
| `B*_q` | Gold bridges: the bridge names of all rows of the query, each normalized (§12, type filter Type_B) |
| `R1`, `R2` | Accepted label sets for hop 1 (Type_S–Type_B) and hop 2 (Type_B–Type_T) (§5.1) |
| `A*_q` | BioHopR gold: the union of the answer lists of all rows of the query, normalized (§12, type filter Type_T) |

**Source.** Own; terminology from Kim et al. (2025) ✔.

---

## 5. Relation mapping and ambiguity tags

### 5.1 Relation mapping `[TBD@S6]`

**Candidates.** Hop-1 candidates: every label connecting Type_S and Type_B. Hop-2 candidates:
every label connecting Type_B and Type_T. Candidate sets: every non-empty subset of a hop's
candidates. The size of a set is its number of labels.

**Validation sample.** For each relation type, order its rows by `SHA256("42" + row_id)`
ascending and take the first 30 rows whose query entity and bridge both resolve (§12). Rows that do
not resolve are counted and reported, not scored.

**Scores** (on the validation sample, one rate per candidate set):

- **Hop-1 score:** share of rows where PrimeKG has an edge between the row's `s` and its bridge
  with a label in the candidate set.
- **Hop-2 score:** share of rows where the targets reached from the row's bridge through the
  candidate set (type Type_T, excluding `s`) exactly equal the row's normalized answer list.
  A row with any gold name that cannot be normalized counts as not matching.

**Selection, per hop:** the highest score; ties broken by the smallest set; any remaining tie →
Claude Code stops and the researcher decides (decision-log entry). The mapping is chosen only from
BioHopR gold data, never from agent outputs.

Output: `results/semantics/relation_mapping.json` (frozen at Gate D1; confirmed at D2).

### 5.2 Relation-ambiguity tags `[FROZEN]` rule, computed at S6

A hop is **ambiguous** if PrimeKG contains at least one label **not** in its accepted set
(`R1` or `R2`) that connects the same two node types. This is computed by code from PrimeKG; no
manual judgment is involved.

Tag per relation type: `NONE`, `R1_AMBIGUOUS`, `R2_AMBIGUOUS`, or `BOTH_AMBIGUOUS`.

The tags never change any answer set. They are used only to report co-failure separately for
question types with and without competing labels. Limitation (state in the thesis): the rule is
coarse; it marks a hop ambiguous even when the competing label clearly does not fit the wording.

**Source.** Own.

---

## 6. Reference sets `[FROZEN]` — computed at S7

Using the edge convention of §3.2:

- **Per-bridge targets:** `T_q(b) = { t : type(t) = Type_T, t ≠ s, and an edge (b, r, t) exists with r ∈ R2 }`
- **Valid bridges:** `B_q = { b : type(b) = Type_B, b ≠ s, an edge (s, r, b) exists with r ∈ R1, and T_q(b) is non-empty }`.
  Bridges reachable through R1 whose `T_q(b)` is empty are **dead-end bridges**; they are counted
  and reported but are not valid bridges.
- **Question-valid answers:** `T_q = ⋃ T_q(b)` over all `b` in `B_q`
- **Gold-bridge targets:** `T_q^{B*} = ⋃ T_q(b)` over all `b` in `B*_q` (computed even if a gold bridge is not in `B_q`)

`T_q` is the correctness reference: everything the question's relation pattern returns when
executed over PrimeKG. `A*_q` is kept for benchmark comparison.

**Source.** Cite: answer set obtained by executing the question's query pattern over the KG, as in
WebQSP (Yih et al., 2016, VERIFY). Departure from BioHopR's single-bridge answers: Own.

---

## 7. Query status and inclusion

### 7.1 Status labels `[FROZEN]`

**CONSISTENT** if all three hold: `s` and every gold bridge resolve; every gold bridge is in `B_q`;
and `A*_q` exactly equals `T_q^{B*}`. Consequence: for every CONSISTENT query, `A*_q ⊆ T_q`.

**INCONSISTENT** otherwise. All applicable reason codes are recorded; the **primary** reason is the
first that applies in this order: `QUERY_NOT_FOUND`, `BRIDGE_NOT_FOUND`, `GOLD_BRIDGE_NOT_VALID`
(a gold bridge resolves but is not in `B_q`), `GOLD_UNMAPPED` (a gold answer name cannot be
normalized), `GOLD_MISSING_FROM_KG` (`A*_q ∖ T_q^{B*}` non-empty), `EXTRA_TARGETS`
(`T_q^{B*} ∖ A*_q` non-empty).

**Bridge multiplicity:** `NO_BRIDGE` (B_q empty), `SINGLE_BRIDGE` (one valid bridge),
`MULTI_BRIDGE` (two or more).

**Saturation share:** size of `T_q` divided by the number of PrimeKG nodes of Type_T.
**SATURATED** if the share exceeds the threshold θ.

### 7.2 Inclusion

| Rule | Value | Status |
|---|---|---|
| Saturation threshold θ | Recommended 0.50: when nearly every node of the target type is question-valid, a wrong answer is almost impossible and the query carries no information about co-failure | `[TBD@S9]` |
| Absolute cap on the size of T_q | None; hub-heavy queries are scientifically relevant | `[FROZEN]` |
| **Primary population** | CONSISTENT ∧ not SATURATED ∧ relation type passed Gate D1 ∧ relation type passed the D2 mapping confirmation | `[FROZEN]` |
| INCONSISTENT queries | Reported in the dataset table; never sampled | `[FROZEN]` |

**Source.** Own.

---

## 8. Sampling `[FROZEN]` — executed at S10

The sampling unit is the **query**, drawn only from the primary population, seed **42**.

| Set | Size | Single / multi quota | Per-type floor | Manifest |
|---|---|---|---|---|
| Screening | 20 | 5 / 15 | 0 | `data/processed/manifests/screening.jsonl` |
| Smoke | 4 | 1 / 3 | 0 | `data/processed/manifests/smoke.jsonl` |
| Pilot | 100 | 25 / 75 `[DEFAULT]` (frozen at S10) | 1 | `data/processed/manifests/pilot.jsonl` |
| Expansion reserve | 400 | 100 / 300 | 1 | `data/processed/manifests/expansion.jsonl` |

**Algorithm**, applied to each set in the order screening → smoke → pilot → reserve, each time on
the queries not yet drawn:

1. **Multiplicity quotas.** If a group (single or multi) has fewer available queries than its
   quota, take all of them and give the shortfall to the other group.
2. **Per relation type, within each multiplicity group:** give each type `min(floor, available)`;
   allocate the remaining quota in proportion to each type's remaining availability, using
   largest-remainder rounding and never exceeding availability; repeat the proportional step for
   any quota left over because of caps.
3. **Within a stratum** (relation type × multiplicity): order queries by `SHA256("42" + query_id)`
   ascending and take the first `n`.
4. Record for every sampled query: relation type, multiplicity, ambiguity tag, and its T_q size bin
   (1–10, 11–100, 101–1,000, more than 1,000; descriptive only).
5. Write `manifests.sha256` with the SHA256 of each manifest file.

**Source.** Standard (deterministic stratified sampling).

---

## 9. Agents and runtime

### 9.1 Runtime settings

| Item | Screening configuration (S20) | Final configuration (S21 onward) |
|---|---|---|
| Runtime | Ollama | Ollama |
| Temperature / seed | 0 / 42 | 0 / 42 `[FROZEN]` |
| `num_ctx` | 8192 | `[TBD@S21]` |
| Max output tokens per turn (`num_predict`) | 4096 | `[TBD@S21]` |
| Tool-call budget | 30 | `[TBD@S21]` |
| Page size | 50 | `[TBD@S21]` |
| Episode timeout | 10 minutes | `[TBD@S21]` |

The screening configuration is `[FROZEN]`; it exists so model selection does not depend on values
that are chosen from screening. Models: four, chosen by Gate D3 `[TBD@S21]`. Model identity record:
Ollama tag + digest + quantization.

### 9.2 Independence and agent count `[FROZEN]`

n = 4 agents. Changing n requires a protocol revision. Each agent runs in a fresh conversation;
no agent sees another's messages, answers or traces; no voting, debate, judge, shared memory or
shared output cache. Agents run sequentially (one model loaded at a time).

### 9.3 What the agent receives `[FROZEN]`

1. **System prompt:** a fixed text, version `P1`, frozen at S14 and reproduced in the thesis
   appendix; its SHA256 is recorded. It describes the two tools and the output format. It contains
   no BioHopR rows, no entity names, no PrimeKG labels, and no examples drawn from the data.
2. **User message:** the question text verbatim, then
   `Starting entity: <PrimeKG node name of s> (PrimeKG ID: <canonical ID of s>)`.

The question text names node types (e.g. "a effect/phenotype"); that is the task itself and is allowed.

**Never given to agents:** `R1`, `R2`, the identity of any gold bridge, `A*_q`, `T_q`, `B_q`,
evaluator labels, BioHopR's relation-type string, other agents' outputs.
**Check at S2 and S5:** no question text contains the name of any of its gold bridges.

### 9.4 Output format and parsing `[FROZEN]`

Required final reply: exactly one JSON object
`{"status": "answered", "answers": [{"id": "<ID>", "name": "<name>"}]}` or
`{"status": "no_answer", "answers": []}`.

- **Final message:** the first assistant message without native tool calls; or, once the budget is
  exhausted, the next assistant message (any tool calls in it are ignored and logged).
- **Parsing:** trim whitespace; if the whole message is one fenced code block, remove the fence.
  The remainder must parse as one JSON object with keys `status` and `answers` of the shapes above.
  Extra keys are ignored and logged. Any text outside the object makes the reply invalid.
- **One re-prompt:** if invalid, the runner sends exactly once: "Your last message was not valid
  JSON in the required format. Reply with only the JSON object." If the next reply is also invalid,
  the episode status is `PARSE_FAIL`.

### 9.5 Episode status `[FROZEN]`

| Status | Meaning |
|---|---|
| `SUCCESS` | A valid final JSON was parsed (answered or no_answer) |
| `PARSE_FAIL` | No valid JSON after the single re-prompt |
| `TIMEOUT` | The episode exceeded its wall-clock timeout |
| `ERROR` | Any other failure: runtime exception, connection failure, out-of-memory |

**Technical failure** = `PARSE_FAIL`, `TIMEOUT` or `ERROR`.

**Source.** Cite: interleaved reasoning and tool calls (ReAct, Yao et al., 2023, VERIFY). Own: rules.

---

## 10. KG environment (tools) `[FROZEN]` design — built at S11

**`inspect_entity(entity_id)`** → ID, name, type, and for each label touching the entity: the label,
its display label(s), neighbor node type(s), and the number of unique neighbors.

**`get_neighbors(entity_id, relation, neighbor_type=None, page=1)`** → neighbors through that label
(ID, name, type, display label), plus `total_count`, `page`, `page_size`, `has_more`. A `direction`
argument is added only if §3.2 finds asymmetric directed labels.

| Rule | Value |
|---|---|
| Graph scope | Full frozen PrimeKG, all node types; reads only the PrimeKG index (and, in Phase 2 only, an overlay file listing edges to hide) |
| Name search | None; agents start from the given ID |
| Label ordering | Alphabetical by label |
| Neighbor ordering | Ascending numeric canonical ID |
| Page size, budget | From configuration (§9.1) |
| Truncation | Never silent: `total_count` and `has_more` always returned |
| Successful call | Any call that returns without an error, including empty results |
| Error messages (fixed templates; count toward the budget) | `Error: unknown entity ID <arg>.` · `Error: entity <id> has no relation <arg>.` · `Error: page <n> is out of range (1–<m>).` |
| Budget exhausted | `Tool budget exhausted. Give your final answer now.` |
| Logging | Every call: arguments, all returned IDs, page, `total_count`, timing |

In Phase 2, counts and lists are computed after hiding overlay edges, so the agent sees a
consistent graph. The overlay file contains only edge identities, never labels such as R1/R2,
answers or evaluation results.

**Source.** Cite: function-based graph tools for LLMs, including neighbor listing and counting
(Graph-CoT, Jin et al., 2024 ✔ title/venue); relation-then-entity exploration (Think-on-Graph,
Sun et al., 2024, VERIFY). Own: pagination, ordering, budget, no-search rule.

---

## 11. Trace and trace graph `[FROZEN]`

Every episode stores all messages, all tool calls with arguments and complete results, timings,
token counts, and the reproducibility fields of §19.

**Trace graph `TG_i`:** for every successful `get_neighbors(u, r, …)` call, a directed edge
`(u, r, v)` for each neighbor `v` on the returned page. Each edge records the index of the tool call
that created it. Nothing else adds edges.

**Appeared:** entity `x` appeared if any successful tool call returned it (as a neighbor, or as the
subject of `inspect_entity`).

**Source.** Cite: path-level traces (KG-TRACES, arXiv 2506.00783 ✔ title). Own: construction rules.

---

## 12. Normalization `[FROZEN]`

Applied to agent answers (type filter Type_T) and to BioHopR names (type filter as stated in §4):

1. **ID:** an ID given as a string or an integer is compared, after whitespace trimming, to the
   canonical decimal-string IDs. A match → that node. If the given name differs from the node's
   name, log `NAME_ID_MISMATCH` (the ID wins).
2. **Name:** otherwise, exact match after lower-casing, Unicode NFKC normalization and whitespace
   collapsing. One node → that node. Several → the unique node of the filter type, if exactly one;
   otherwise `UNRESOLVED (AMBIGUOUS_NAME)`.
3. Otherwise `UNRESOLVED (NO_MATCH)`.

Duplicates within one agent's answers are removed after normalization. No fuzzy or embedding
matching. (BioHopR's own evaluation used BioLORD-2023 embeddings at τ = 0.9 for free-text answers;
agents here copy IDs from tool output.)

**Source.** Own; contrast with Kim et al. (2025) ✔ and Remy et al. (2023) ✔.

---

## 13. Label A — answer status `[FROZEN]`

Computed only for primary-population queries. Each predicted entity `x` gets exactly one label;
the first matching rule wins:

| Priority | Label | Rule |
|---|---|---|
| 1 | `UNRESOLVED` | Normalization failed |
| 2 | `GOLD` | `x ∈ A*_q` |
| 3 | `GOLD_BRIDGE_EXTRA` | `x ∈ T_q^{B*}` and `x ∉ A*_q`. Always empty for CONSISTENT queries; any occurrence indicates a bug. |
| 4 | `ALT_VALID` | `x ∈ T_q` and `x ∉ T_q^{B*}` |
| 5 | `OFF_QUESTION` | `x ∉ T_q` (includes `x = s`) |

**Question-valid** = `GOLD`, `GOLD_BRIDGE_EXTRA` or `ALT_VALID`; for primary-population queries
this is exactly `x ∈ T_q`.

**Source.** Own.

---

## 14. Label B — path status, reason codes, hop-1 status `[FROZEN]`

### 14.1 Label B

`UNRESOLVED` answers get `NOT_APPLICABLE`. Otherwise, the first matching rule wins:

| Priority | Label | Rule |
|---|---|---|
| 1 | `UNGROUNDED` | `x` never appeared |
| 2 | `SUPPORTED` | `TG_i` contains `s –r1→ b –r2→ x` with r1 ∈ R1, type(b) = Type_B, b ≠ s, r2 ∈ R2, type(x) = Type_T, x ≠ s |
| 3 | `PATH_INVALID` | `x` appeared, `TG_i` has a directed path from `s` to `x` (including the length-0 path when x = s), and rule 2 does not hold |
| 4 | `KG_UNSUPPORTED` | `x` appeared, but `TG_i` has no path from `s` to `x` |

**Invariant (tested):** no answer is both `OFF_QUESTION` and `SUPPORTED`. A SUPPORTED path uses real
PrimeKG edges with accepted labels, so its endpoint is in `T_q` by definition.

### 14.2 Reason codes (`PATH_INVALID` only)

**Primary path:** the shortest directed path from `s` to `x` in `TG_i` (breadth-first, any length).
Ties: the path whose last edge was created by the lowest tool-call index; then the
lexicographically smallest sequence of node IDs.

**Codes** are assigned for the primary path and, separately, for the union over all simple paths of
length ≤ 3:

| Code | Condition on a path |
|---|---|
| `SHORTCUT` | Length 1 and type(x) = Type_T |
| `WRONG_RELATION_HOP1` | Length 2 and first label ∉ R1 |
| `WRONG_BRIDGE_TYPE` | Length 2 and middle node type ≠ Type_B |
| `WRONG_RELATION_HOP2` | Length 2 and second label ∉ R2 |
| `WRONG_TARGET_TYPE` | Any length ≥ 1 and type(x) ≠ Type_T |
| `WRONG_HOP_COUNT` | Length 0 (x = s), or length ≥ 3 |

### 14.3 Hop-1 status

**Per answer:** `H1(x, i) = 1` if `TG_i` contains an edge `(s, r, b)` with r ∈ R1 and
type(b) = Type_B such that `b` lies on a path from `s` to `x`; otherwise 0 (always 0 for UNGROUNDED,
KG_UNSUPPORTED and NOT_APPLICABLE).

**Per agent:** based only on successful `get_neighbors` calls issued on `s`, judged by label only
(neighbor_type filters ignored): `H1_CLEAN` (all labels in R1), `H1_MIXED` (some in R1),
`H1_WRONG` (none in R1), `H1_NONE` (no such call). The agent **found R1** if H1_CLEAN or H1_MIXED.

**Source.** Own. Motivation for tracking ungrounded answers: Zhou et al. (2025b) ✔ title.

---

## 15. Per-agent metrics `[FROZEN]`

Undefined values (division by zero) are recorded as `NA`, excluded from averages, and counted.

- Counts of every Label A and Label B value; reason-code frequencies (primary path and all paths).
- **Question-valid precision** = question-valid answers / resolved answers.
- **OFF_QUESTION, UNRESOLVED, UNGROUNDED rates** (per resolved or per total answers, as labeled).
- **Benchmark precision / recall / F1** against `A*_q` (secondary).
- **Hop-1 status** (§14.3).
- **Bridges explored:** members of `B_q` on which the agent made a successful `get_neighbors` call.
- **Bridge rank** of an explored bridge `b`: its position in the first successful
  `get_neighbors(s, r, …)` result with r ∈ R1 that contained it, counted as
  `(page − 1) × page_size + position on the page` (1-based). `NA` if `b` was never returned by such a call.
- **Bridge-conditional recall** for each explored valid bridge `b`: answers in `T_q(b)` / size of `T_q(b)`.
- **Early stop:** the agent answered with at least one entity from page 1 of a list whose `has_more`
  was true, and never requested page 2 of that same (entity, label, neighbor_type) list.
- **FIRST_SEEN_PAGE** per answer: the page number of the first `get_neighbors` result containing it;
  `INSPECT` if it appeared only as an `inspect_entity` subject; `NEVER` if it never appeared.
- Pages requested, tool calls used, budget-exhausted flag, episode status.
- **Degree** of a node (used in §16): number of unique neighbors over all labels, edges taken in
  either direction; **degree percentile**: among PrimeKG nodes of the same type.

**Source.** Standard (precision/recall/F1); Own (the rest).

---

## 16. Co-failure metrics `[FROZEN]`

### 16.1 Answer level (primary)

`W_iq` = agent i's resolved answers labeled `OFF_QUESTION` on query q.

- **CF4^Q(q) = 1** if some entity is in `W_iq` for all 4 agents.
- **CF3^Q(q) = 1** if some entity is in `W_iq` for at least 3 agents.
- **Grounded:** an entity counts for agent i only if its Label B for agent i is not `UNGROUNDED`.
- **Hop-1-clean (CF3^{Q,H1}, CF4^{Q,H1}):** an entity counts for agent i only if
  `H1(x, i) = 1` (which implies it is grounded).

### 16.2 Benchmark comparison (secondary)

`W^BH_iq` = resolved answers ∖ `A*_q`; **CF3^BH** and **CF4^BH** as in 16.1.

### 16.3 Path level (secondary)

- **Wrong-turn events** of an `OFF_QUESTION` answer: every step `(u, r)` on its primary path whose
  label violates the specification at that position — step 1 with label ∉ R1, step 2 with label
  ∉ R2, or the single step of a `SHORTCUT` path. A path can yield 0, 1 or 2 events. Paths whose
  only problems are types or hop count yield no wrong-turn event.
- **PCF_REL3 / PCF_REL4 (q) = 1** if the same `(u, r)` event occurs for ≥ 3 / all 4 agents.
- **PCF_NODE3 / PCF_NODE4 (q) = 1** if an *intermediate* node `v` (not `s`, not the answer) that is
  not in `B_q ∪ T_q` lies on the primary path of an `OFF_QUESTION` answer for ≥ 3 / all 4 agents.
- **PCF_SHORTCUT3 (q) = 1** if ≥ 3 agents have an `OFF_QUESTION` answer whose primary path is a
  `SHORTCUT` from `s` through the same label.
- For every PCF case record: the node(s), degree, degree percentile, label(s), ambiguity tag.

### 16.4 Pairwise error agreement

For agents i and j: among queries where both `W_iq` and `W_jq` are non-empty, the share where they
intersect. `NA` if there are no such queries; the denominator is always reported. Adapted from the
"agreement when both are wrong" measure of Kim et al. (2025) to answer sets.

**Source.** Cite: Kim et al. (2025) ✔ for 16.4. Own for the rest.

---

## 17. Chance baselines `[FROZEN]`

**Pools.** For agent i on query q:
`C_iq` = entities that appeared in agent i's tool outputs, with type Type_T, not in `T_q`, not `s`.

**Observed sets.** `W'_iq` = members of `W_iq` that appeared in tool outputs and have type Type_T;
`k_iq` = its size. Then `W'_iq ⊆ C_iq`.

**N1 (uniform null).** In each trial, every agent draws `k_iq` distinct entities uniformly from
`C_iq`; compute CF3 and CF4 on the drawn sets.

**N1-H1 (hop-1-clean null).** Same, with both the pool and the observed set restricted to entities
with `H1(x, i) = 1`.

**N2 (ordering sensitivity).** Same as N1, with both the pool and the observed set restricted to
entities that appeared on **page 1** of any `get_neighbors` list the agent opened (so the draw is
always possible). This asks whether agreement exceeds what first-page exposure alone would produce.

**Procedure.** 10,000 trials. Random numbers: NumPy `Generator(PCG64)` from
`SeedSequence([42, h])`, where `h` = the first 8 hex digits of `SHA256(query_id)` read as an integer,
so results do not depend on query order. Report per query the null probability; in aggregate,
the observed total `O`, the null totals' mean, median and 95th percentile, and
`p = (1 + #{trials with null total ≥ O}) / (1 + 10,000)`. **"Observed exceeds null"** means `O`
is above the null 95th percentile.

**Required test:** if all agents give the same single wrong answer while each saw 200 other wrong
candidates of Type_T, the N1 probability of CF3 is below 0.01.

**Source.** Own. Context: comparison with an independent-voting null in Kohli (2026) ✔.

---

## 18. Decision rules

All gates (D1–D8), thresholds and precedence are in `docs/decision_rules.md`, frozen before the
data each gate judges exists.

**Source.** Cite: pre-registration (Nosek et al., 2018, VERIFY).

---

## 19. Reproducibility `[FROZEN]`

Every episode record includes: query ID, agent ID, model tag + digest + quantization, temperature,
seed, `num_ctx`, `num_predict`, **prompt version** (`P1` + SHA256 of the system prompt and user
template), **tool configuration** (tool version `T1`, page size, budget, ordering rule, SHA256 of
the tool schema file), **KG fingerprint** (SHA256 of `primekg_metadata.json`, which itself lists the
SHA256 of every raw file), BioHopR revision, git commit, timestamps, full trace, raw final output,
episode status.

Results are write-once; reruns use a new run ID. Long runs checkpoint after every episode and resume
without duplicating or skipping episodes. Raw data files are never modified.

### 19.1 Verification tests (used by Gate D4)

| Test | Definition |
|---|---|
| **Leakage test** | For every screening query: the system prompt and user message contain none of R1/R2 labels, gold bridge names or IDs, gold answer names or IDs, or the relation-type string; the agent-facing modules import nothing from `cofail_kg.evaluation` and open no file under `data/processed/`; for 10 random (entity, label) pairs, tool output equals the index exactly. |
| **Reconstruction check** | For every episode, rebuilding `TG_i` from the stored raw tool results gives exactly the stored trace graph. |
| **Kill-and-resume test** | The run is interrupted at about half its episodes and restarted; the final set of episodes equals the manifest × agents, with no duplicates and no missing pairs. |
| **Audit selection** | 2 episodes per agent: among that agent's SUCCESS episodes with at least one answer, ordered by `SHA256("42" + query_id + agent_id)`, the first one containing an OFF_QUESTION answer (if any) and the first one not already chosen. |

**Source.** Standard.

---

## 20. Change control `[FROZEN]`

Implementation fixes that change no definition here: allowed, noted in `progress.md`. Any change to
a frozen item: dated `decision_log.md` entry stating what, why, and what data had been seen. Changes
made after seeing pilot results are reported as exploratory.

**Source.** Standard.

---

## 21. Phase 2 — intervention design `[PROVISIONAL]`, frozen at S29

Frozen at S29, after Gate D6 and before the expansion run (S30), using what the pilot showed. That
freeze happens after pilot data is seen and is logged as such.

- **Valid route:** a path `s → b → t` in the (modified) graph with r1 ∈ R1, b ∈ B_q, r2 ∈ R2, t ∈ T_q.
- **Mechanism** of a candidate: the category of its shared structure — `SHORTCUT`,
  `WRONG_RELATION_HOP1`, `WRONG_RELATION_HOP2`, or `OFF_PATH_NODE` (from §16.3 events).
- **Candidate rule:** CONSISTENT query ∧ CF3^{Q,H1} = 1 or a PCF event shared by ≥ 3 agents ∧ the
  shared feature can be blocked while at least one valid route remains.
- **Surgery:** a query-local overlay (§10): hide specific edges `(u, r, v)`, or hide label `r` at
  node `u`. Never remove the only valid bridge.
- **Branch degree** of label r at node u: the number of unique neighbors of u through r.
- **Matched control:** a feature of the same mechanism at the same hop position, same label where
  possible, degree (or branch degree) within ±25% (else nearest), not used by any agent in the
  original run, whose removal also leaves a valid route. If none exists, the case is
  treatment-only exploratory.
- **Outcomes:** CF3/CF4 before vs after; PCF before vs after; recovery = share of agents whose
  answers become question-valid; change in no-answer rate (not recovery); **displacement** per agent:
  `VALID_RELATION`, `SAME_WRONG_RELATION_OTHER_NEIGHBOR`, `OTHER_WRONG`, `NO_ANSWER`.
- **Effect:** ΔCF = CF_before − CF_after; τ_CF = ΔCF_treatment − ΔCF_control.

**Source.** Cite: counterfactual deletion (GNNExplainer, Ying et al., 2019; CF-GNNExplainer,
Lucic et al., 2022 — VERIFY); deletion baselines (Zhou et al., 2025a ✔); component perturbation
(Balanos et al., 2025 ✔); root-cause validation (LIDL, VERIFY); centrality baseline
(arXiv 2606.14805 ✔ title). Own: matched controls, displacement.

---

## 22. Optional, not part of the design

A closed-book comparison may be run later as an exploratory follow-up.

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
