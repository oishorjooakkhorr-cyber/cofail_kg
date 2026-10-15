# S11 — KG environment and T1 tool schemas

Completed on 2026-10-15. **Researcher approved wording B and authorized the S11 commit.**
The exact schema source SHA256 is frozen under `tools`. No experimental model was run
and S12 has not started. The protocol and decision rules are unchanged.

## 1. Files created or changed

- `src/cofail_kg/agents/kg_env.py`: `ToolConfig`, `KGEnvironment`, the two public
  tools, a restricted dispatcher, call budget and full in-memory call log.
- `src/cofail_kg/agents/tool_schemas.py`: approved T1 function definitions, wording B.
- `tests/test_kg_env.py`: 40 synthetic tests, including fresh-process isolation.
- `tests/test_tool_schemas.py`: schema/neutrality checks and frozen-source identity check.
- `configs/frozen_hashes.yaml`: write-once `tools` SHA256; prior entries preserved.
- `results/diagnostics/s11_tools.json`: real screening-entity verification,
  complete inspection and page results, timings, configuration and source hashes.
- `.gitattributes`: preserve exact schema source bytes for protocol §3.4 hashing.
- `docs/S11_implementation.md`, `docs/progress.md`, `docs/decision_log.md`: implementation
  report and approval/completion status.

No dependencies were added. The existing S4 index supplies all graph operations;
the agent environment reads no files itself and has no evaluator dependency.

## 2. Tests run and results

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_kg_env.py tests/test_tool_schemas.py -q
# 43 passed (including the final frozen-identity check)
.\venv\Scripts\python.exe -m pytest -q
# 228 passed (185 existing + 43 S11)
```

Tests were first run before their modules existed and failed at import. The implemented
environment then passed 28 initial cases, followed by all 42 S11 cases. Coverage includes:

- Exact identity fields; alphabetical labels; unique counts and all display labels.
- Numeric neighbor ordering, reciprocal/duplicate edges, self-loops, reverse traversal,
  pages 1+2, last page, type filtering and successful empty page 1.
- All six protocol §10 error templates, strict integer pages, malformed field values,
  missing arguments, unknown tools and direct-call defaults.
- Errors consume budget; exhausted responses take precedence over argument errors;
  every subsequent exhausted attempt remains logged. Zero budget is supported.
- Full copied arguments/results, success flags, UTC timestamps and elapsed time.
- Configuration validation and refusal of an outgoing-only index.
- In a fresh interpreter, an audit hook rejects imports of `cofail_kg.evaluation`
  and file access under `data/processed/` or `results/`, including transitive imports
  and reads. Importing both modules, loading a synthetic cache and exercising both
  tools succeeds with that guard active.
- The two function definitions serialize to JSON, expose only the specified
  parameters, contain no accepted-label/type enumerations and no evaluator hints.

Review experiment: reversed `has_more`'s comparison in memory, then ran the pagination
test. It failed on the first page as expected. Disk source was never mutated. This
was an intentional test-strength check, not an unresolved test failure.

Finalization adds a source-byte identity check, which failed before `tools` was
written. The approved descriptions were compared exactly with option B before
freezing. The write-once operation preserved all earlier hash values; repeating
the same freeze was a byte-preserving no-op.

## 3. Small real example and output

Selected screening query `BH2_02033`, start ID `19601` (MYO-029), directly from the
frozen agent-input sheet. Selected the first alphabetical relation with more than
50 neighbors that fits within the screening budget; this tests multiple pages without
using evaluator information. Verified the sheet SHA256 and KG metadata fingerprint
against `configs/frozen_hashes.yaml` before loading.

```python
from cofail_kg.agents.kg_env import KGEnvironment, ToolConfig
from cofail_kg.kg.primekg_index import PrimeKGIndex

env = KGEnvironment(PrimeKGIndex(), ToolConfig(page_size=50, budget=30))
entity = env.inspect_entity("19601")
first = env.get_neighbors("19601", "drug_drug")
print(entity["id"], entity["name"], entity["type"])
print(first["total_count"], first["has_more"], [n["id"] for n in first["items"][:5]])
# 19601 MYO-029 drug
# 329 True ['14058', '14147', '14211', '14235', '14270']
```

All seven pages had sizes `[50, 50, 50, 50, 50, 50, 29]`, totaling 329 distinct IDs
in ascending numeric order. The last page had `has_more=False`; the last five IDs
were `21199, 21200, 21201, 21202, 21203`. Inspection plus all pages used eight calls.
Every returned item, including name, type and display labels, matched:

```powershell
.\venv\Scripts\python.exe scripts/inspect_kg.py neighbors 19601 --relation drug_drug
```

Full evidence is saved in `results/diagnostics/s11_tools.json`. This is a graph-tool
check, not a model episode or an answer evaluation. That original evidence remains
unchanged and records the earlier draft schema hash. Finalization changed only
schema wording/documentation, not the verified graph environment; the approved
schema identity is the `tools` hash below and in `configs/frozen_hashes.yaml`.

## 4. Assumptions

- S4's frozen either-direction traversal remains authoritative (protocol §3.2).
- Screening uses page size 50 and budget 30 (§9.1). They are explicitly passed via
  `ToolConfig`; no final S21 values have been chosen or frozen.
- Each environment belongs to one sequential episode. The future runner will pass
  decoded argument objects to `env.call(name, arguments)` and keep evaluator data
  out of the agent process (§9.3). Parsing model messages belongs to later stages.
- The researcher's explicit instruction, "okay lock B, and commit", approves option
  B and authorizes freezing its source hash and committing S11. Existing parameter
  descriptions remain unchanged.

## 5. Design choices beyond the specification

All choices below are routine engineering; no new literature method, scientific
threshold or answer-selection rule was introduced.

- Use a frozen dataclass with explicit configuration values. Validate page size as
  a positive integer and budget as a nonnegative integer; reject booleans.
- Return successful results as dictionaries and exact protocol errors as strings.
  Inspection uses `relations`; each relation retains S4's `neighbor_count`,
  `neighbor_types` and `display_labels` field names. Neighbor items also retain
  `display_labels` as a list, preserving multiple display labels for one neighbor.
- Project node output down to ID/name/type; source identifiers and source metadata
  are not part of the specified tool output.
- Delegate counts, uniqueness, ordering and traversal to the verified S4 index.
  Determine valid node types from its metadata, including globally known types with
  no neighbors at the current entity. A missing relation is an error; an existing
  relation filtered to zero neighbors is a successful empty page.
- Check budget, tool name, required argument presence, entity, relation, type, then
  page in that order. Missing required arguments are checked in signature order.
  Explicit null required values are present but invalid. Page strings, floats and
  booleans are not coerced; an empty result still has exactly one valid page.
- The dispatcher uses only declared arguments. Extra object keys have no effect and
  remain in the log; they do not become additional tool capabilities. The schema
  uses ordinary object properties without an extra-key rejection policy. The runner
  must supply a decoded argument object; raw JSON parsing is not part of S11.
- Track charged calls separately from the log length. After budget exhaustion,
  append every attempted call while leaving the charged count at the budget.
- Copy arguments and results into the log so later caller mutations cannot alter
  trace evidence. Record UTC ISO timestamps and monotonic elapsed seconds. Complete
  results retain every returned ID and all pagination fields.
- Unexpected infrastructure exceptions are recorded as internal errors and re-raised,
  rather than inventing a new model-visible error template or silently continuing.
- Reject non-frozen outgoing-only traversal at environment construction. No overlay
  or intervention functionality is implemented in S11.
- Use a constant list of JSON-compatible function dictionaries in the envelope
  documented by [Ollama](https://docs.ollama.com/capabilities/tool-calling), checked
  2026-10-15. Wording B was subsequently approved and its source hash frozen.
- Preserve schema source bytes with a narrowly scoped Git attribute so Windows
  checkout conversion cannot change its future frozen identity.

## 6. Hand inspection and approval

Review the complete approved wording B below and the real call log. The descriptions
state tool behavior without suggesting a relation, node type, path or answer.

**inspect_entity**

> Return an entity’s ID, name, and type, followed by relation summaries ordered
> alphabetically by label. Each summary includes display labels, neighbor types,
> and a unique neighbor count.

**get_neighbors**

> Return unique neighbors for the specified entity and relation label in ascending
> numeric ID order, optionally filtered by neighbor type. Each item includes ID, name,
> type, and display labels. Return total_count, page, page_size, and has_more.

Parameter descriptions (unchanged, also part of the frozen T1 wording):

| Parameter | Description |
|---|---|
| `entity_id` (both tools) | Canonical entity ID. |
| `relation` | Relation label. |
| `neighbor_type` | Optional neighbor node type; omit to include all types. |
| `page` | Page number, starting at 1. Defaults to 1. |

Approved 2026-10-15. SHA256 of the exact `tool_schemas.py` bytes, written with the
existing `write_once` helper under `tools` in `configs/frozen_hashes.yaml`:

`fe95093be50073aca922360645240d4410737fb39f11061aa1f5f2df0a8b0bab`

S11 is complete. S12 requires a separate researcher request.
