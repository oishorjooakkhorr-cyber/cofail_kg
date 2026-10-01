# Provenance Tracker — CoFail-KG

Where every idea, dataset, metric and tool comes from. Update at the end of each stage (Claude
Code lists "design choices beyond the specification"; you decide whether they need a row).

**Type:** `DATA` · `DESIGN` (idea re-implemented) · `METRIC` · `CODE` (copied/adapted code) ·
`SOFTWARE` · `BACKGROUND` (related work only) · `OWN` (thesis contribution) · `STANDARD` (no citation)

**Citation status:** ✔ = checked against the paper's own page during planning · VERIFY = confirm
before citing · then `IN ZOTERO` → `CITED` as you go.

---

## 1. Stage-by-stage

| Stage | Component | Borrowed | Source | Type | Status |
|---|---|---|---|---|---|
| S0 | Coding assistant | — | Claude Code (Anthropic) | SOFTWARE | disclosure |
| S1 | Frozen protocol and gates before data | Pre-registration practice | Nosek et al. (2018), PNAS | BACKGROUND | VERIFY |
| S2–S3 | Dataset, templates, relation types | Data | Kim, Abdulle & Wu (2025), BioHopR, Findings of ACL 2025 | DATA | ✔ |
| S4 | Knowledge graph | Data | Chandak, Huang & Zitnik (2023), PrimeKG, Scientific Data 10:67 | DATA | ✔ |
| S5–S6 | Field-role verification; mapping by gold reproduction (hop-1 and hop-2 scores); mechanical ambiguity rule | — | — | OWN | — |
| S7 | Answer set = execute the question's relation pattern over the KG | Evaluation convention | Yih et al. (2016), WebQSP, ACL 2016 | DESIGN | VERIFY |
| S7 | Departure from BioHopR's single-bridge answer definition | Contrast | Kim et al. (2025) §3.1 | DATA | ✔ |
| S7–S9 | Query grouping; consistency check; mapping confirmation; saturation rule | — | — | OWN | — |
| S10 | Stratified deterministic sampling | — | — | STANDARD | — |
| S11 | Function-based graph tools incl. neighbor listing and neighbor counts | Tool interface | Jin et al. (2024), Graph-CoT, Findings of ACL 2024 | DESIGN | ✔ title/venue · VERIFY authors |
| S11 | Relation-then-entity exploration | Agent design | Sun et al. (2024), Think-on-Graph, ICLR 2024 | DESIGN | VERIFY |
| S11 | Pagination, ordering, budget, no search tool | — | — | OWN | — |
| S12 | Path-level reasoning traces | Trace idea | KG-TRACES, arXiv:2506.00783 | DESIGN | ✔ title · VERIFY authors |
| S12 | Trace-graph rules | — | — | OWN | — |
| S13 | Local model serving | — | Ollama | SOFTWARE | cite repo/docs |
| S14 | Reason → tool call → observation loop | Agent loop | Yao et al. (2023), ReAct, ICLR 2023 | DESIGN | VERIFY |
| S14 | System prompt P1, parsing and re-prompt rules | — | — | OWN | — |
| S16 | Exact-ID/name normalization (no embeddings) | Contrast with BioHopR's BioLORD matching | Remy et al. (2023), BioLORD-2023; Kim et al. (2025) §4.3 | BACKGROUND | ✔ |
| S17 | Label A | — | — | OWN | — |
| S18 | Label B, reason codes, hop-1 status | — | — | OWN | — |
| S18 | Why track ungrounded answers | Motivation | Zhou et al. (2025b), What Breaks KG-based RAG?, arXiv:2508.08344 | BACKGROUND | ✔ title · VERIFY authors |
| S19 | Precision / recall / F1 | — | — | STANDARD | — |
| S19 | Bridge rank, early stop, bridge-conditional recall | — | — | OWN | — |
| S20–S21 | Each experimental model | Models | Technical report or model card of each frozen model | SOFTWARE | fill at S21 |
| S23 | Pairwise "agree when both wrong" | Metric, adapted to answer sets | Kim, Garg, Peng & Garg (2025), ICML, PMLR 267 | METRIC | ✔ |
| S23 | CF3/CF4 (Q, grounded, H1), PCF_REL, PCF_NODE, PCF_SHORTCUT | — | — | OWN | — |
| S24 | Within-query Monte Carlo nulls N1, N2 | — | — | OWN | — |
| S24 | Context: panels vs independent-voting null | Background | Kohli (2026), Nine Judges, arXiv:2605.29800 | BACKGROUND | ✔ |
| S25 | Checkpoint/resume, write-once | — | — | STANDARD | — |
| D1–D8 | Feasibility gates | — | — | OWN | — |

## 2. Phase 2 (after the pilot)

| Component | Borrowed | Source | Type | Status |
|---|---|---|---|---|
| Counterfactual deletion logic | Explaining predictions by removing graph parts | Ying et al. (2019), GNNExplainer, NeurIPS; Lucic et al. (2022), CF-GNNExplainer, AISTATS | DESIGN | VERIFY |
| Deletion baselines | Random triple deletion vs reasoning-path disruption | Zhou, Zhu et al. (2025a), arXiv:2504.05163 | DESIGN | ✔ |
| Component perturbations | Node/edge-level perturbation of KG inputs | Balanos et al. (2025), KGRAG-Ex, arXiv:2507.08443 | DESIGN | ✔ |
| Root-cause validation | Counterfactual validation vs propagated symptoms | LIDL, arXiv:2601.05539 | DESIGN | VERIFY |
| Degree-only baseline for nomination | Centrality vs learned evidence | Knowledge-Based Zero-Replay Debugging, arXiv:2606.14805 | DESIGN | ✔ title · VERIFY authors |
| Matched controls, displacement categories | — | — | OWN | — |

## 3. Related work only

| Source | Role | Status |
|---|---|---|
| Huang et al. (2026), CAGE-CAL, arXiv:2605.30653 | Closest work: counterfactual graphs for correlated failure, but on the agent communication graph | ✔ |
| Kohli (2026), Nine Judges | Heterogeneous panels behave like ~2 independent voters | ✔ |
| Kim et al. (2025), Correlated Errors in LLMs | Shared errors across 350+ models | ✔ |
| Su et al. (2025), KGARevion, ICLR 2025 | LLM agent verifying triples against PrimeKG (not traversal) | ✔ |
| Self-consistency; Multi-Agent Debate; Mixture-of-Agents | The independence assumption being tested | VERIFY |
| MAST; ErrorProbe | Agent-internal failure diagnosis | VERIFY |
| GraphTracer, arXiv:2510.10581 | Perturbing high-degree / high-betweenness trace nodes | VERIFY |
| "Learning to Deceive KG-Augmented Models", arXiv:2010.12872 | KG perturbations that preserve accuracy | VERIFY |
| TRAIL, arXiv:2508.04474 | Retrieval bias toward hub entities | VERIFY |

## 4. Own contributions (claim these; run a literature search on each before claiming)

- Re-deriving BioHopR answers for KG-grounded agents (T_q), with CONSISTENT/INCONSISTENT validation
- Relation-ambiguity tags frozen before any agent run
- Two-label evaluation (answer status × path status) with trace-based reason codes and hop-1 status
- Co-failure at answer level (CF, incl. hop-1-clean) and path level (PCF_REL, PCF_NODE, PCF_SHORTCUT)
- Within-query chance baselines, including the ordering-sensitivity null
- Pre-registered feasibility gates for a multi-agent KG study
- (Phase 2) Matched-control structural surgery with displacement analysis

## 5. External code log

| Our file | Repo URL | Commit | License | What was adapted | Date |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

## 6. AI-assistance log (for the thesis disclosure)

| Stage | Tool | What it did | What I did |
|---|---|---|---|
| Planning | ChatGPT, Claude | Discussed design options | Made and froze all design decisions |
| S0 | Claude Code | Created skeleton | Specified, reviewed, committed |
