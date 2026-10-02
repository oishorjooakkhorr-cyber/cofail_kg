# CoFail-KG — Frozen Pilot Protocol

**Version:** 1.2 · **Owner:** the researcher · **Implemented by:** Claude Code (read-only for Claude)
**What changed since v1.0:** see `docs/CHANGES.md` (one page).

This file is the single source of truth for every scientific rule in the project. Claude Code
implements what is written here. The runbook (`docs/pipeline_runbook.md`) says *when* and *how*
to build each part; this file says *what* each part must do.

---

## 0. How to read this file

### 0.1 Status tags

| Tag | Meaning |
|---|---|
| `[FROZEN]` | Decided. Changing it requires an entry in `docs/decision_log.md`. |
| `[TBD@Sx]` | The **value** is filled in by the researcher at stage Sx, usually from what the code at Sx computes. Code at Sx may compute it; code at later stages that uses the value may run only after it is filled in. |
| `[DEFAULT]` | Used as written unless the researcher overrides it, with a decision-log entry, at or before the stage named. Confirmed (or changed) when that stage is completed. |
| `[PROVISIONAL]` | Phase 2. Frozen at S29 (§21). |

### 0.2 Source tags

Every section ends with a **Source** line: **Cite** (from a paper; references in §23), **Own**
(designed here; a thesis contribution), or **Standard** (no citation needed).
✔ = checked against the paper's own page. VERIFY = confirm before citing.

### 0.3 Science versus engineering `[FROZEN]`

This protocol fixes every rule that **can change a scientific result or a gate outcome**.
Engineering details that cannot (message wording beyond §10's templates, retries, file layouts,
internal data structures, performance) are decided in code, documented in docstrings, covered by
tests, and listed by Claude Code at the end of each stage as "design choices beyond the
specification" (CLAUDE.md). **Audits report only issues that could change a scientific result or a
gate outcome.**

### 0.4 Terms used throughout

| Term | Definition |
|---|---|
| **Row** | One BioHopR 2-hop record in the pinned revision. `row_id` = `"BH2_"` + the record's 0-based position among the 2-hop records as loaded at S2, zero-padded to 5 digits. |
| **Relation type** | BioHopR's Query:Bridge:Target type triple from the row's 2-hop relation field (e.g. `drug:effect/phenotype:disease`). There are 12. |
| **Query** | The unit of analysis. Rows whose query entity resolves (§12, reference policy) are grouped by **(resolved PrimeKG node `s`, relation type)**. A row whose query entity does not resolve forms its own query. `query_id` = the `row_id` of the query's lowest-index row. |
| **Label** | A value of PrimeKG's `relation` column. Every rule uses labels. |
| **Display label** | A value of PrimeKG's `display_relation` column. Shown to agents for information; never used in any rule. |
| **Type_S, Type_B, Type_T** | Node types of the query entity, bridge and target, from the relation type, mapped to PrimeKG node types (§3.3). |
| **n** | Number of agents: 4 (§9.2). |
| **Episode** | One agent answering one query once. A rerun of the same (query, agent) is a new **attempt** (§19). |
| **Primary population** | The queries eligible for sampling (§7.2). |

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
  features (shortcut edges, specific wrong-relation branches, off-path nodes, large lists) and are
  not explained only by ambiguous relation wording.
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
| Subset | 2-hop questions (7,633 in the paper) | `[FROZEN]` |
| Question text given to agents | The multi-answer 2-hop question field, verbatim | `[TBD@S2]` field name |
| Field roles | Working hypothesis: `hop2` = query entity, `hop1` = bridge, `answer` = gold targets | `[TBD@S5]` |

**Field-role verification rule `[FROZEN]` (S5).** Sample 5 rows per relation type (all if fewer),
ordered by `SHA256("42" + row_id)`. For each, test which field connects to which in PrimeKG and
which field the answers are neighbors of. The roles are accepted only if at least 95% of resolvable
sampled rows support the same roles in **every** relation type; otherwise stop and investigate.

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
| Release | Chosen at S4 (Troglitazone check). If Gate D1 later stops on a version mismatch, the release is revisited with a decision-log entry. | `[TBD@S4]` |
| Canonical node ID | PrimeKG's unique node index (expected `x_index` / `y_index`), written as a decimal string; compared numerically when ordering | `[TBD@S4]` confirm columns |
| Edge storage | Whether each relationship appears once or in both directions | `[TBD@S4]` |
| **Edge convention** | How an edge may be traversed. Default: an edge between u and v with label r can be traversed in either direction. If S4 finds labels whose meaning is directional and stored one-way, the S4 decision-log entry lists them with their allowed direction. **The same convention is used by the reference sets (§6), the tools (§10) and the trace graph (§11).** | `[TBD@S4]` |
| Substitution | Never replace PrimeKG with a different or newer graph | `[FROZEN]` |

The PrimeKG paper reports about 4.05 million relationships; about twice as many rows means both
directions are stored.

**Source.** Cite: Chandak, Huang & Zitnik (2023) ✔.

### 3.3 Type map `[TBD@S4]`

A one-to-one map from BioHopR's four types (drug, disease, gene/protein, effect/phenotype) to
PrimeKG `node_type` values. Expected to be identical strings.

### 3.4 Frozen hashes `[FROZEN]`

`configs/frozen_hashes.yaml` holds every value later checks compare against. Each entry is written
once, at its stage, and never edited:

| Key | Written at | Value |
|---|---|---|
| `biohopr_revision` | S2 | Dataset commit hash |
| `kg_fingerprint` | S4 | SHA256 of `data/cache/primekg_metadata.json` (machine-written only; it lists the SHA256 of every raw file) |
| `relation_mapping` | S6 | SHA256 of `results/semantics/relation_mapping.json` |
| `manifests` | S10 | SHA256 of each manifest and each agent-input sheet |
| `tools` | S11 | SHA256 of the tool-schema file (tool version T1) |
| `prompt` | S14 | SHA256 of the P1 template |
| `models` | S21 | Tag and digest of each frozen model |

Release details typed by the researcher (version, DOI, download date) go in
`data/cache/primekg_release.json`, which is **not** part of the fingerprint.

**Source.** Standard.

---

## 4. Query specification (hidden from agents) `[FROZEN]`

For each query `q`:

| Symbol | Meaning |
|---|---|
| `s` | The resolved query entity (§12, reference policy, type Type_S) |
| `B*_q` | Gold bridges: the bridge names of all rows of the query, each resolved (reference policy, Type_B) |
| `R1`, `R2` | Accepted label sets for hop 1 (Type_S–Type_B) and hop 2 (Type_B–Type_T) (§5.1) |
| `A*_q` | BioHopR gold: the union of the answer lists of all rows of the query, resolved (reference policy, Type_T) |
| Question text | The question field of the query's rows; must be identical across them (§7.1) |

**Source.** Own; terminology from Kim et al. (2025) ✔.

---

## 5. Relation mapping and ambiguity tags

### 5.1 Relation mapping — procedure `[FROZEN]`, result `[TBD@S6]`

**Candidates.** Hop-1 candidates: every label connecting Type_S and Type_B. Hop-2 candidates: every
label connecting Type_B and Type_T. Candidate sets: every non-empty subset of a hop's candidates;
a set's size is its number of labels. A hop with no candidates makes the relation type FAIL Gate D1.

**Validation sample.** Per relation type, order its rows by `SHA256("42" + row_id)` and take the
first 30 rows whose query entity and bridge both resolve (all such rows if fewer than 30). Fewer than
10 such rows makes the relation type FAIL Gate D1 ("insufficient validation rows").

**Scores** (per candidate set, on the validation sample):
- **Hop-1 score:** share of rows where an edge between the row's `s` and its bridge has a label in
  the set (edge convention §3.2).
- **Hop-2 score:** share of rows where the targets reached from the row's bridge through the set
  (type Type_T, excluding `s`) exactly equal the row's resolved answer list. A row with any answer
  name that does not resolve counts as not matching.

**Selection, per hop:** highest score; ties broken by the smallest set; any remaining tie is
reported as a TIE and the researcher decides (decision-log entry). The mapping is chosen only from
BioHopR gold data, never from agent outputs.

### 5.2 Relation-ambiguity tags `[FROZEN]` rule, computed at S6

A hop is **ambiguous** if PrimeKG contains at least one label **not** in its accepted set that
connects the same two node types. Computed by code; no manual judgment.

Tag per relation type: `NONE`, `R1_AMBIGUOUS`, `R2_AMBIGUOUS`, or `BOTH_AMBIGUOUS`. Tags never
change an answer set; they only split co-failure reporting. Limitation (thesis): the rule is coarse.

**Source.** Own.

---

## 6. Reference sets `[FROZEN]` — computed at S7

With the edge convention of §3.2:

- **Per-bridge targets:** `T_q(b) = { t : type(t) = Type_T, t ≠ s, edge (b, r, t) with r ∈ R2 }`
- **Valid bridges:** `B_q = { b : type(b) = Type_B, b ≠ s, edge (s, r, b) with r ∈ R1, and T_q(b) non-empty }`.
  Bridges reachable through R1 with empty `T_q(b)` are **dead ends**: counted, not valid.
- **Question-valid answers:** `T_q = ⋃ T_q(b)` over `b ∈ B_q`
- **Gold-bridge targets:** `T_q^{B*} = ⋃ T_q(b)` over `b ∈ B*_q`

`T_q` is the correctness reference. `A*_q` is kept for benchmark comparison.

**Source.** Cite: answer set obtained by executing the question's query pattern over the KG, as in
WebQSP (Yih et al., 2016, VERIFY). Departure from BioHopR's single-bridge answers: Own.

---

## 7. Query status and inclusion

### 7.1 Status labels `[FROZEN]`

**CONSISTENT** if all hold:
1. `s` resolves;
2. all rows of the query have identical question text;
3. every gold bridge resolves and is in `B_q`;
4. every gold answer name resolves;
5. `A*_q` exactly equals `T_q^{B*}`.

Consequence: for every CONSISTENT query, `A*_q ⊆ T_q`.

**INCONSISTENT** otherwise. Reason codes, defined below, are all recorded; the **primary** reason
is the first applicable in this order. If `QUERY_NOT_FOUND` applies, the codes that need `s`
(`GOLD_BRIDGE_NOT_VALID`, `GOLD_MISSING_FROM_KG`, `EXTRA_TARGETS`) are recorded as `NA`.

| Code | Applies when |
|---|---|
| `QUERY_NOT_FOUND` | The query entity name does not resolve |
| `QUESTION_TEXT_MISMATCH` | The query's rows do not all have identical question text |
| `BRIDGE_NOT_FOUND` | Some gold bridge name does not resolve |
| `GOLD_BRIDGE_NOT_VALID` | Some gold bridge resolves but is not in `B_q` |
| `GOLD_UNMAPPED` | Some gold answer name does not resolve |
| `GOLD_MISSING_FROM_KG` | `A*_q ∖ T_q^{B*}` is non-empty |
| `EXTRA_TARGETS` | `T_q^{B*} ∖ A*_q` is non-empty |

**Bridge multiplicity:** `NO_BRIDGE` (B_q empty), `SINGLE_BRIDGE` (one), `MULTI_BRIDGE` (two or more).

**LEAKY_QUESTION** (an exclusion flag): the question text contains, as a case-insensitive whole
word or phrase, the name of a gold bridge or of a gold answer at least 4 characters long.

**Saturation share** = size of `T_q` / number of PrimeKG nodes of Type_T. **SATURATED** if above θ.

### 7.2 Inclusion

| Rule | Value | Status |
|---|---|---|
| Saturation threshold θ | Recommended 0.50 | `[TBD@S9]` |
| Absolute cap on the size of T_q | None (hub-heavy queries are relevant) | `[FROZEN]` |
| **Primary population** | CONSISTENT ∧ not SATURATED ∧ not LEAKY_QUESTION ∧ relation type passed Gate D1 ∧ relation type confirmed or UNCONFIRMABLE in Gate D2 step 1 | `[FROZEN]` |
| INCONSISTENT and LEAKY_QUESTION queries | Reported in the dataset table; never sampled | `[FROZEN]` |

**Source.** Own.

---

## 8. Sampling `[FROZEN]` — executed at S10

The sampling unit is the **query**, drawn only from the primary population, seed **42**.

| Set | Target size | Single / multi quota | Per-type floor (within each multiplicity group) |
|---|---|---|---|
| Screening | 20 | 5 / 15 | 0 |
| Smoke | 4 | 1 / 3 | 0 |
| Pilot | 100 | 25 / 75 `[DEFAULT]`, confirmed at S10 | 1 |
| Expansion reserve | up to 400 | 100 / 300 | 1 |

**Algorithm**, applied to each set in the order screening → smoke → pilot → reserve, each time on
the queries not yet drawn:

1. **Multiplicity quotas.** If one group has fewer available queries than its quota, take all of
   them and give the shortfall to the other group. If both groups together have fewer than the
   target size, the set contains all remaining queries; record the shortfall.
2. **Relation types, within each multiplicity group.** Give each type `min(floor, available)`.
   Allocate the rest in proportion to each type's remaining availability using largest-remainder
   rounding (equal remainders broken by relation-type name, ascending), never exceeding
   availability; repeat for any quota left over because of caps.
3. **Within a stratum** (relation type × multiplicity): order queries by `SHA256("42" + query_id)`
   ascending and take the first `n`.
4. Record for each sampled query: relation type, multiplicity, ambiguity tag, T_q size bin
   (1–10, 11–100, 101–1,000, over 1,000; descriptive only).

**Outputs.**
- Manifests (evaluation side): `data/processed/manifests/<set>.jsonl`.
- **Agent-input sheets** (agent side): `data/agent_inputs/<set>.jsonl`, one line per query with
  exactly four fields: `query_id`, `question_text`, `start_name` (PrimeKG node name of `s`),
  `start_id`. Nothing else.
- SHA256 of every manifest and sheet in `configs/frozen_hashes.yaml` (§3.4).

**Source.** Standard (deterministic stratified sampling).

---

## 9. Agents and runtime

### 9.1 Runtime settings

| Item | Screening configuration (S20) `[FROZEN]` | Final configuration (S21 on) |
|---|---|---|
| Runtime | Ollama | Ollama |
| Temperature / seed | 0 / 42 | 0 / 42 `[FROZEN]` |
| `num_ctx` | 8192 | `[TBD@S21]` |
| Max output tokens per turn (`num_predict`) | 4096 | `[TBD@S21]` |
| Tool-call budget | 30 | `[TBD@S21]` |
| Page size | 50 | `[TBD@S21]` |
| Episode timeout | 10 minutes | `[TBD@S21]` |

**Rules for choosing the final values `[FROZEN]` (applied at S21):**
- `num_ctx`: the smallest power of 2 that is ≥ 8192 and ≥ 1.25 × the largest prompt token count
  seen for the chosen models. Because screening caps context at 8192, if any chosen model's largest
  screening prompt count exceeds 0.8 × 8192, rerun 5 screening queries for that model with
  `num_ctx` 16384 and use those counts. The value must run without out-of-memory errors.
- Page size: 50; 25 if the chosen `num_ctx` cannot fit in memory.
- Budget: 2 × the median tool calls of the chosen models in screening, bounded to 20–40; if more
  than 20% of their screening episodes hit the budget, use the next value up to 40.
- `num_predict`: at least 25 tokens × the 90th percentile of BioHopR answer-list size (S3),
  rounded up to a power of 2, at least 4096.
- Timeout: 3 × the slowest chosen model's median screening episode time, at least 10 minutes.

Models: four, chosen by Gate D3 `[TBD@S21]`, recorded by tag, digest and quantization.

**Re-selection `[FROZEN]`:** if S22 shows any episode with prompt tokens above 90% of `num_ctx`, or
any OUT_OF_MEMORY error, the final values are chosen again with the same rules, using the S22
measurements in place of the screening ones. Allowed only before S26; logged.

### 9.2 Independence and agent count `[FROZEN]`

n = 4. Changing n requires a protocol revision. Each episode is a fresh conversation; no agent
sees another's messages, answers or traces; no voting, debate, judge, shared memory or shared
output cache. Runs proceed one model at a time, in agent order, through the manifest's query order.

### 9.3 What the agent receives `[FROZEN]`

Agent-facing code reads only the agent-input sheet (§8) and the PrimeKG index.

1. **System prompt:** the template `P1` `[TBD@S14]` (text approved by the researcher at S14 and
   reproduced in the thesis appendix). It describes the two tools and the output format and may
   contain the placeholders `{PAGE_SIZE}` and `{BUDGET}`, filled from the configuration. It contains
   no BioHopR rows, entity names, PrimeKG labels, or examples drawn from the data. **Prompt version**
   = `P1` + SHA256 of the template; the filled-in values are recorded with the tool configuration.
2. **User message:** the question text verbatim, then
   `Starting entity: <start_name> (PrimeKG ID: <start_id>)`.

The question text names node types (e.g. "a effect/phenotype"); that is the task and is allowed.
**Never given to agents:** `R1`, `R2`, the identity of any gold bridge, `A*_q`, `T_q`, `B_q`,
evaluator labels, BioHopR's relation-type string, other agents' outputs.

### 9.4 Output format and parsing `[FROZEN]`

Required final reply: one JSON object with `"status"` (`"answered"` or `"no_answer"`) and
`"answers"`, a list of objects each with `"id"` (string or integer) and `"name"` (string).

- **Final message:** the first assistant message without native tool calls; or, after the budget
  message, the next assistant message (any tool calls in it are ignored and logged).
- **Parsing:** trim whitespace; if the whole message is one fenced code block (with or without a
  language tag such as `json`), remove the fence. The remainder must parse as one JSON object of
  the shape above; any text outside it makes the reply invalid. Extra keys, at any level, are
  ignored and logged.
- `"answered"` with an empty list is valid (zero answers). `"no_answer"` with items is valid; the
  items are ignored and logged.
- **One re-prompt:** if invalid, the runner sends exactly once: "Your last message was not valid
  JSON in the required format. Reply with only the JSON object." If the next reply is also invalid:
  `PARSE_FAIL`.

### 9.5 Episode status `[FROZEN]`

If several apply, the first in this order is recorded:

| Order | Status | Meaning |
|---|---|---|
| 1 | `TIMEOUT` | The episode exceeded its wall-clock timeout at any point |
| 2 | `ERROR` | Any other failure; a `cause` field records `OUT_OF_MEMORY`, `CONNECTION`, `RUNTIME` or `OTHER` (detection method decided in code at S13) |
| 3 | `PARSE_FAIL` | No valid JSON after the single re-prompt |
| 4 | `SUCCESS` | A valid final reply was parsed |

**Technical failure** = `TIMEOUT`, `ERROR` or `PARSE_FAIL`.

**TEXT_TOOL_CALL:** an assistant message without native tool calls whose text contains
`inspect_entity` or `get_neighbors` immediately followed by `(`, or a JSON object whose `"name"`
(or `"function"`) value is one of these tool names. Such text is never executed; it is logged.

**Source.** Cite: interleaved reasoning and tool calls (ReAct, Yao et al., 2023, VERIFY). Own: rules.

---

## 10. KG environment (tools) `[FROZEN]` design — built at S11

**`inspect_entity(entity_id)`** → ID, name, type, and for each label touching the entity: the label,
its display label(s), neighbor node type(s), and the number of unique neighbors.

**`get_neighbors(entity_id, relation, neighbor_type=None, page=1)`** → neighbors through that label
(each with ID, name, type, display label), plus `total_count`, `page`, `page_size`, `has_more`.
A `direction` argument exists only if §3.2 lists directional labels `[TBD@S4]`.

Tool descriptions (wording of the tool schemas, version `T1`) `[TBD@S11]`: neutral; they describe
what each tool does and never mention BioHopR relations, relation types or answers.

| Rule | Value |
|---|---|
| Graph scope | Full frozen PrimeKG, all node types, using the edge convention of §3.2. Reads only the PrimeKG index (and, in Phase 2 only, an overlay file of edge identities to hide). |
| Name search | None |
| Label ordering | Alphabetical by label |
| Neighbor ordering | Ascending numeric canonical ID |
| Page size, budget | From the configuration (§9.1) |
| Truncation | Never silent; `total_count` and `has_more` always returned |
| Empty results | A label with zero neighbors (or a filter matching none) returns page 1 with `total_count` 0 — a successful call |
| Successful call | Any call returning without an error |
| Error templates (count toward the budget) | `Error: unknown entity ID <arg>.` · `Error: entity <id> has no relation <arg>.` · `Error: unknown neighbor_type <arg>.` · `Error: page must be an integer from 1 to <m>.` · `Error: missing argument <name>.` · `Error: unknown tool <name>.` |
| Budget exhausted | `Tool budget exhausted. Give your final answer now.` |
| Error principle | Error and budget messages echo only the agent's own arguments; they never mention accepted labels or types. |
| Logging | Every call: arguments, all returned IDs, page, `total_count`, timing |

In Phase 2, counts and lists are computed after hiding overlay edges, so the agent sees a consistent
graph.

**Source.** Cite: function-based graph tools for LLMs, including neighbor listing and counting
(Graph-CoT, Jin et al., 2024 ✔ title/venue); relation-then-entity exploration (Think-on-Graph,
Sun et al., 2024, VERIFY). Own: pagination, ordering, budget, no-search rule.

---

## 11. Trace and trace graph `[FROZEN]`

Every episode stores all messages, all tool calls with arguments and complete results, timings,
token counts, and the reproducibility fields of §19.

**Trace graph `TG_i`:** for every successful `get_neighbors(u, r, …)` call, a directed edge
`u → v` with label `r` for each neighbor `v` on the returned page, oriented as the agent traversed
it under the §3.2 edge convention. An edge is identified by (u, r, v); its **creation index** is
the index of the first successful call that returned it. Nothing else adds edges.

**Appeared:** entity `x` appeared if any successful call returned it, as a neighbor or as the
subject of `inspect_entity`.

**Source.** Cite: path-level traces (KG-TRACES, arXiv 2506.00783 ✔ title). Own: construction rules.

---

## 12. Normalization `[FROZEN]`

Two policies, because reference names and agent answers need different handling.

**Reference policy** (query entity, gold bridges, gold answers; with the filter type given in §4):
an exact name match after lower-casing, Unicode NFKC normalization and whitespace collapsing,
considering **only nodes of the filter type**. Exactly one → that node; none or several →
unresolved.

**Agent policy** (each item of an agent's answer list):
1. **ID:** a string or integer, whitespace-trimmed, equal to a canonical ID → that node. If the given
   name differs from the node's name, log `NAME_ID_MISMATCH` (the ID wins).
2. **Name:** otherwise, exact match as above. If exactly one matching node has type Type_T → that
   node. Else, if exactly one node matches in total (of any type) → that node (it will be labeled
   by §13–14, typically OFF_QUESTION with WRONG_TARGET_TYPE). Otherwise `UNRESOLVED (AMBIGUOUS_NAME)`.
3. Otherwise `UNRESOLVED (NO_MATCH)`.

Duplicates within one agent's answers are removed after normalization. No fuzzy or embedding
matching. (BioHopR's evaluation used BioLORD-2023 embeddings at τ = 0.9 for free-text answers;
agents here copy IDs from tool output.)

**Source.** Own; contrast with Kim et al. (2025) ✔ and Remy et al. (2023) ✔.

---

## 13. Label A — answer status `[FROZEN]`

Computed only for primary-population queries. First matching rule wins:

| Priority | Label | Rule |
|---|---|---|
| 1 | `UNRESOLVED` | Normalization failed |
| 2 | `GOLD` | `x ∈ A*_q` |
| 3 | `GOLD_BRIDGE_EXTRA` | `x ∈ T_q^{B*}` and `x ∉ A*_q` — always empty for CONSISTENT queries; any occurrence is a bug |
| 4 | `ALT_VALID` | `x ∈ T_q` and `x ∉ T_q^{B*}` |
| 5 | `OFF_QUESTION` | `x ∉ T_q` (includes `x = s`) |

**Question-valid** = GOLD, GOLD_BRIDGE_EXTRA or ALT_VALID; for primary-population queries this is
exactly `x ∈ T_q`.

**Source.** Own.

---

## 14. Label B — path status, reason codes, hop-1 status `[FROZEN]`

### 14.1 Label B

`UNRESOLVED` answers get `NOT_APPLICABLE`. Otherwise, the first matching rule wins:

| Priority | Label | Rule |
|---|---|---|
| 1 | `UNGROUNDED` | `x` never appeared |
| 2 | `SUPPORTED` | `TG_i` contains `s –r1→ b –r2→ x` with r1 ∈ R1, type(b) = Type_B, b ≠ s, r2 ∈ R2, type(x) = Type_T, x ≠ s |
| 3 | `PATH_INVALID` | `x` appeared, `TG_i` has a directed path from `s` to `x` (the length-0 path counts when x = s), and rule 2 does not hold |
| 4 | `KG_UNSUPPORTED` | `x` appeared, but `TG_i` has no path from `s` to `x` |

**Invariant (tested):** no answer is both `OFF_QUESTION` and `SUPPORTED`. It holds because the trace
graph and `T_q` use the same edge convention (§3.2) and a SUPPORTED path uses real PrimeKG edges with
accepted labels. (A SUPPORTED path's bridge is never a dead end, since it reaches x.)

### 14.2 Primary path and reason codes (`PATH_INVALID` only)

**Primary path:** among all directed paths from `s` to `x` in `TG_i`, the first by this total order:
(1) fewer edges; (2) smaller largest creation index among its edges; (3) lexicographically smaller
sequence of (numeric node ID, label) pairs along the path.

**Codes**, assigned for the primary path and separately as the union over all simple paths of
length ≤ 3:

| Code | Condition on a path |
|---|---|
| `SHORTCUT` | Length 1 and type(x) = Type_T |
| `WRONG_RELATION_HOP1` | Length 2 and first label ∉ R1 |
| `WRONG_BRIDGE_TYPE` | Length 2 and middle node type ≠ Type_B |
| `WRONG_RELATION_HOP2` | Length 2 and second label ∉ R2 |
| `WRONG_TARGET_TYPE` | Length ≥ 1 and type(x) ≠ Type_T |
| `WRONG_HOP_COUNT` | Length other than 2, except that a length-1 path to a Type_T node is coded `SHORTCUT` instead |

### 14.3 Hop-1 status

**Per answer:** `H1(x, i) = 1` if `TG_i` contains an edge `s → b` with label in R1 and
type(b) = Type_B, where `b ≠ x` lies on a path from `s` to `x`. Otherwise 0 (always 0 for
UNGROUNDED, KG_UNSUPPORTED and NOT_APPLICABLE). H1 = 1 implies the answer is grounded.

**Per agent:** from successful `get_neighbors` calls issued on `s`, by label only (neighbor_type
filters ignored): `H1_CLEAN` (all in R1), `H1_MIXED` (some in R1), `H1_WRONG` (none in R1),
`H1_NONE` (no such call). The agent **found R1** if H1_CLEAN or H1_MIXED.

**Source.** Own. Motivation for tracking ungrounded answers: Zhou et al. (2025b) ✔ title.

---

## 15. Per-agent metrics `[FROZEN]`

Undefined values (division by zero) are `NA`, excluded from averages, and counted.

| Metric | Definition |
|---|---|
| Label counts | Counts of every Label A and Label B value; reason-code frequencies (primary path and all paths) |
| Question-valid precision | question-valid answers / resolved answers |
| OFF_QUESTION rate | OFF_QUESTION answers / resolved answers |
| UNRESOLVED rate | unresolved answers / all answers |
| UNGROUNDED rate | UNGROUNDED answers / resolved answers |
| Benchmark P / R / F1 | Against `A*_q` (secondary) |
| Hop-1 status | §14.3 |
| Bridges explored | Members of `B_q` on which the agent made a successful `get_neighbors` call |
| Explored-bridge rank | For an explored bridge b: its position in the first successful `get_neighbors(s, r, …)` result with r ∈ R1 that contained it, = (page − 1) × page size + position on the page (1-based); `NA` if never so returned |
| Bridge-conditional recall | For each explored valid bridge b: answers in `T_q(b)` / size of `T_q(b)` |
| Early stop | The agent answered with at least one entity from page 1 of a list whose `has_more` was true and never requested page 2 of that same (entity, label, neighbor_type) list |
| FIRST_SEEN_PAGE | Per answer: the page of the first `get_neighbors` result containing it; `INSPECT` if it appeared only as an `inspect_entity` subject; `NEVER` if it never appeared |
| List size (fan-out) | Per answer: `total_count` of the list in which it first appeared; per PCF case: the largest `total_count` along the primary path |
| Effort | Pages requested, tool calls used, budget-exhausted flag, TEXT_TOOL_CALL count, episode status |
| Degree | Unique neighbors of a node over all labels, under the §3.2 edge convention |
| Degree percentile | 100 × share of PrimeKG nodes of the same type whose degree is ≤ this node's degree |

**Source.** Standard (precision/recall/F1); Own (the rest).

---

## 16. Co-failure metrics `[FROZEN]`

### 16.1 Answer level (primary)

`W_iq` = agent i's resolved answers labeled `OFF_QUESTION` on query q.

- **CF4^Q(q) = 1** if some entity is in `W_iq` for all 4 agents.
- **CF3^Q(q) = 1** if some entity is in `W_iq` for at least 3 agents.
- **Grounded variants:** an entity counts for agent i only if its Label B for agent i is not `UNGROUNDED`.
- **Hop-1-clean variants (CF3^{Q,H1}, CF4^{Q,H1}):** an entity counts for agent i only if `H1(x, i) = 1`.

### 16.2 Benchmark comparison (secondary)

`W^BH_iq` = resolved answers ∖ `A*_q`; **CF3^BH** and **CF4^BH** as in 16.1.

### 16.3 Path level (secondary)

- **Wrong-turn events** of an `OFF_QUESTION` answer: every step `(u, r)` on its primary path whose
  label violates the specification at that position — step 1 with label ∉ R1, step 2 with label
  ∉ R2, or the single step of a `SHORTCUT` path. A path yields 0, 1 or 2 events.
- **PCF_REL3 / PCF_REL4 (q) = 1** if the same `(u, r)` event occurs for ≥ 3 / all 4 agents.
- **PCF_NODE3 / PCF_NODE4 (q) = 1** if an intermediate node `v` (not `s`, not the answer) that is
  not in `B_q ∪ T_q` lies on the primary path of an `OFF_QUESTION` answer for ≥ 3 / all 4 agents.
- **PCF_SHORTCUT3 (q) = 1** if ≥ 3 agents have an `OFF_QUESTION` answer whose primary path is a
  `SHORTCUT` from `s` through the same label.
- For every PCF case: node(s), degree, degree percentile, label(s), list size, ambiguity tag.

### 16.4 Pairwise error agreement

For agents i and j: among queries where both `W_iq` and `W_jq` are non-empty, the share where they
intersect; `NA` if there are none; the denominator is always reported. Adapted from the "agreement
when both are wrong" measure of Kim et al. (2025) to answer sets.

**Source.** Cite: Kim et al. (2025) ✔ for 16.4. Own for the rest.

---

## 17. Chance baselines `[FROZEN]`

**Pool** for agent i on query q: `C_iq` = entities that appeared in agent i's tool outputs, with
type Type_T, not in `T_q`, not `s`.

Each null comes with its own **observed set** and **observed total**, always restricted the same way
as its pool, so like is compared with like:

| Null | Pool | Observed set for agent i | Observed total |
|---|---|---|---|
| **N1** (uniform) | `C_iq` | `W'_iq` = members of `W_iq` that appeared and have type Type_T | `O_N1` = number of queries where some entity is in `W'_iq` for ≥ 3 agents |
| **N1-H1** (hop-1-clean) | `C_iq` restricted to entities with `H1(x, i) = 1` | `W'_iq` restricted to `H1(x, i) = 1` | `O_H1`, counted the same way |
| **N2** (ordering) | `C_iq` restricted to entities that appeared on page 1 of any `get_neighbors` list the agent opened | `W'_iq` restricted the same way | `O_N2`, counted the same way |

In every row the observed set is a subset of the pool, so the draw is always possible.

**Procedure.** In each trial, every agent (in ascending agent order) draws, without replacement,
as many entities as its observed set contains, uniformly from its pool (pool sorted by numeric ID;
NumPy `Generator.choice`). Compute "≥ 3 agents share an entity" per query and sum over queries.
10,000 trials. Random numbers: NumPy `Generator(PCG64)` from `SeedSequence([42, h, v])`, where `h` =
the first 8 hex digits of `SHA256(query_id)` read as an integer and `v` = 1, 2, 3 for N1, N1-H1, N2.
The same is done for the 4-agent version. Report per query the null probability and, in aggregate,
the observed total, the null mean, median and 95th percentile, and
`p = (1 + #{trials with null total ≥ observed total}) / (1 + 10,000)`.

**"Observed exceeds null"** means the observed total is above that null's 95th percentile.
**The gate comparison (D6, D7) is `O_H1` against N1-H1**, matching the gate's case count, which
uses hop-1-clean co-failure.

**Required test:** if all agents give the same single wrong answer while each saw 200 other wrong
candidates of Type_T, the N1 probability of a shared answer is below 0.01.

**Source.** Own. Context: comparison with an independent-voting null in Kohli (2026) ✔.

---

## 18. Decision rules

All gates (D1–D8), thresholds and precedence are in `docs/decision_rules.md`, frozen before the
data each gate judges exists.

**Source.** Cite: pre-registration (Nosek et al., 2018, VERIFY).

---

## 19. Reproducibility `[FROZEN]`

**Every episode record includes:** query ID, agent ID, attempt number, model tag + digest +
quantization, temperature, seed, `num_ctx`, `num_predict`, prompt version, tool configuration (T1,
page size, budget, ordering rule, tool-schema SHA256, filled-in prompt values), KG fingerprint,
BioHopR revision, git commit, timestamps, full trace, raw final output, episode status (and cause).

**Runs.**
- An episode is **completed** once its record exists with any status (§9.5). Resuming a run never
  reruns completed episodes.
- Records are write-once.
- **Reruns** (only through Gate D6/D7 HOLD, a Gate D4 FAIL, or the code-change rule below): a new run ID; for each (query, agent), analysis uses
  the latest attempt; every attempt is kept; `E` is computed on latest attempts.
- **Code changes during a run:** stop the run first. Episodes completed under the earlier commit are
  used only if a decision-log entry explains why the fix cannot have affected them; otherwise they
  are rerun under the new commit as new attempts.
- Raw data files are never modified.

### 19.1 Verification tests (used by Gate D4)

| Test | Definition |
|---|---|
| **Leakage test** | Run on the screening and smoke queries. (a) The system prompt and the starting-entity line contain none of: R1/R2 labels, gold bridge or gold answer names or IDs, names of other `B_q` or `T_q` members, the relation-type string, evaluator label names — matched case-insensitively as whole words, names shorter than 4 characters listed for manual review instead. (b) Agent-facing modules import nothing from `cofail_kg.evaluation` and open no files except the agent-input sheet and the PrimeKG cache. (c) Each agent-input sheet line has exactly the four fields of §8. (d) For 10 random (entity, label) pairs, tool output equals the index exactly. |
| **Reconstruction check** | For every episode, rebuilding `TG_i` from the stored raw tool results gives exactly the stored trace graph. |
| **Kill-and-resume test** | Interrupt at about half the episodes and restart; the final set equals manifest × agents, with no duplicates and none missing. |
| **Audit selection** | Per agent: among its SUCCESS episodes with at least one answer, ordered by `SHA256("42" + query_id + agent_id)`, the first containing an OFF_QUESTION answer (if any) and the first not already chosen. If an agent has fewer than 2 such episodes, all of them are chosen. |

**Source.** Standard.

---

## 20. Change control `[FROZEN]`

Implementation fixes that change no definition here: allowed, noted in `progress.md`. Any change to
a frozen item: a dated `decision_log.md` entry stating what, why, and what data had been seen.
Changes made after seeing pilot results are reported as exploratory.

**Source.** Standard.

---

## 21. Phase 2 — intervention design `[PROVISIONAL]`, frozen at S29

Frozen at S29, after Gate D6 and before the expansion run, using what the pilot showed (logged as
frozen after seeing pilot data). Fan-out is analyzed descriptively (§15) and is not an
intervention mechanism.

- **Valid route:** a path `s → b → t` in the (modified) graph with r1 ∈ R1, b ∈ B_q, r2 ∈ R2, t ∈ T_q.
- **Mechanisms:** `SHORTCUT`, `WRONG_TURN_HOP1` and `WRONG_TURN_HOP2` (§16.3 wrong-turn events at
  step 1 and step 2, on primary paths of any length — distinct from the length-2 reason codes of
  §14.2), and `OFF_PATH_NODE` (from §16.3 PCF_NODE).
- **Candidate:** a CONSISTENT pilot or expansion **query** with CF3^{Q,H1} = 1, or a PCF event shared
  by ≥ 3 agents, whose shared feature can be blocked while at least one valid route remains. If a
  query has several features, the one shared by the most agents is used (ties: the earliest on the
  primary paths). Candidates and cases are counted **in queries**.
- **Surgery:** a query-local overlay (§10): hide specific edges `(u, r, v)`, or hide label `r` at
  node `u`. Never remove the only valid bridge.
- **Branch degree** of label r at node u: number of unique neighbors of u through r.
- **Matched control:** same mechanism, same hop position, same label where possible, degree (or
  branch degree) within ±25% (else nearest), not used by any agent in the original run, removal
  leaves a valid route. If none exists: treatment-only exploratory.
- **Outcomes:** CF3/CF4 before vs after; PCF before vs after; recovery = share of agents whose
  answers become question-valid; change in no-answer rate (not recovery); **displacement** per
  agent: `VALID_RELATION`, `SAME_WRONG_RELATION_OTHER_NEIGHBOR`, `OTHER_WRONG`, `NO_ANSWER`.
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
