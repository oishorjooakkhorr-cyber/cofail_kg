# S6 — Researcher-authorized exclusion of the two remaining failed types

Decision date: 2026-10-13. Status: **both types are now EXCLUDED from the current primary analysis**.

Authorization: “okay u may exclude them for the time being but the report be detailed why they were excluded”.
This decision follows the investigation saved at commit `4819ee8`. It supersedes the
pending-disposition statements in that historical investigation, without changing its evidence.

“For the time being” records the researcher's intent to retain these types for possible later
review. Their current status is EXCLUDED, with no expiry or automatic re-admission. No raw
records, candidate scores, or exploratory findings are deleted. This is exclusion of two
relation types (36 and 215 dataset rows), not deletion of selected unfavorable validation rows.

## Rule applied

Protocol §5.1 requires exact reference-set reproduction; §5.3 adopts one construction per
relation type. D1 requires at least ten validation rows, available labels, hop-1 and hop-2
scores of at least 90%, and a passing S5 field-role outcome. D1 permits investigation of
field roles, edge storage and release for up to two working days, then exclusion if failure
remains. The investigation completed without a permitted repair; the allowance is not a
requirement to wait two full days after the checks finish.

| Requirement | disease:effect/phenotype:drug | effect/phenotype:drug:disease |
|---|---:|---:|
| Rows in the pinned dataset | 36 | 215 |
| Validation rows (minimum 10) | 30 — meets requirement | 30 — meets requirement |
| Original S5 field-role gate | PASS (5/5 supporting) | PASS (5/5 supporting) |
| Candidate labels available for both hops | Yes | Yes |
| Hop 1 (required 27/30) | 30/30 — PASS | 30/30 — PASS |
| Best BRIDGE hop 2 (required 27/30) | 3/30 (10%) — FAIL | 26/30 (86.67%) — FAIL |
| Best UNION hop 2 (required 27/30) | 3/30 (10%) — FAIL | 20/30 (66.67%) — FAIL |
| Final disposition | EXCLUDED | EXCLUDED |

The reason code for each is `HOP2_REPRODUCTION_BELOW_THRESHOLD`. Neither is excluded for
too few rows or failure of the original S5 gate. All available query/bridge pairs resolve
(36/36 and 215/215). The protocol's cap explains the 30-row samples; zero validation rows
were skipped and all sampled reference answers resolved. Original prescribed samples were retained.

## 1. Why disease → phenotype → drug is excluded

The diagnostic R1 is `disease_phenotype_positive`. The only available R2 label is
`drug_effect`. It reproduces only three of the thirty reference sets under either construction.
Every sampled query has one valid phenotype bridge, so BRIDGE and UNION produce identical
sets. In all 27 failures the graph reaches every reference drug plus additional drugs.

Examples from the prescribed validation order:

| Row | Query and stored bridge | Reference drugs | Reached drugs | Extra | Missing |
|---|---|---:|---:|---:|---:|
| BH2_06128 | pleural empyema → Pleural effusion | 44 | 111 | 67 | 0 |
| BH2_06120 | microcephaly-intellectual disability-phalangeal and neurological anomalies syndrome → Intellectual disability | 14 | 20 | 6 | 0 |

These counts apply to both constructions. Complete named sets and canonical IDs are in the
[original investigation report](../s6_remaining_investigation/report.md#named-validation-examples).
There is no alternative R2 subset or construction that removes the extras. Allowing containment
would change the scientific acceptance rule after observing results, so it is not a repair
under the current protocol. The evidence proves a set mismatch; it does not establish why
the upstream reference lists are smaller, nor that the additional drugs are graph errors.

## 2. Why phenotype → drug → disease is excluded

The diagnostic R1 is `drug_effect`; the best R2 is `indication`. All seven nonempty subsets
of `contraindication`, `indication` and `off-label use` were checked:

| R2 subset | BRIDGE exact matches | UNION exact matches |
|---|---:|---:|
| contraindication | 0/30 | 0/30 |
| indication | 26/30 | 20/30 |
| off-label use | 0/30 | 0/30 |
| contraindication + indication | 3/30 | 1/30 |
| contraindication + off-label use | 0/30 | 0/30 |
| indication + off-label use | 14/30 | 10/30 |
| all three labels | 3/30 | 1/30 |

The best construction is one row short of 27/30. Being close does not satisfy the fixed gate.
Its failures have two distinct explanations in the observed evidence:

1. **Construction mixture:** 17 rows match both constructions, nine match BRIDGE only, and
   three match UNION only. UNION recovers missing reference diseases in the three UNION-only
   rows, but adds extra diseases in the nine BRIDGE-only rows. No one construction reaches 90%.
2. **Node identity:** the remaining row, BH2_05027, matches neither. Neuropathic arthropathy
   has one valid drug bridge, Methylprednisolone. The reference and reached sets both have
   118 diseases, sharing 117. The reference resolves to `acute lymphoblastic leukemia`
   (35852; MONDO_grouped, source ID 3541_870), while the graph reaches
   `acute lymphoblastic leukemia (disease)` (33621; MONDO, source ID 4967).

For the identity conflict, the raw reference has a trailing space. Frozen §12 trims it and
finds the exact-name node 35852. The suffix retry applies only when there is no exact disease
match, so it correctly does not fire. No tested R2 subset reaches 35852 through the valid
bridge. The evidence establishes no resolver implementation bug or authorization to merge
these distinct IDs. Similar names alone are insufficient. Changing resolution to prefer
the connected node would change the identity rule using the desired path outcome.

Two other illustrative rows: BH2_05081 (Thyroid follicular adenoma → Pergolide) has four
reference diseases; BRIDGE reaches two with two missing, while UNION reaches exactly four.
BH2_04897 (Agoraphobia → Fluvoxamine) has nine reference diseases; BRIDGE reaches three with
six missing, while UNION reaches exactly nine. Full named sets, the BRIDGE-only example,
and BH2_05027 are preserved in the linked investigation report.

Choosing whichever construction matches the reference on each row would cover 29/30.
That is an exploratory, reference-informed diagnostic, not an independently validated
selector. It cannot qualify the type under §5.3. Likewise, hypothetically replacing the
conflicting reference ID could make BRIDGE 27/30, but no such identity correction has been
justified or applied. Neither counterfactual changes the exclusion decision.

## Checks completed before exclusion

- **Reproduction:** original S6 samples and per-type results reproduced exactly; every R2
  subset was evaluated under both constructions on all 60 sampled rows.
- **Field roles:** all type fields agree. A separate support check on the S6 samples supports
  30/30 and 29/30 respectively; BH2_05027 explains the latter conflict. This larger-sample
  diagnostic does not replace or retroactively fail the original S5 gate.
- **Edge storage:** a scan of all 8,100,498 raw edges reproduced the selected-R1 bridge sets
  and every candidate's target sets. Outgoing-only, incoming-only and cached either-direction
  results agree for the inspected paths. No orientation or cache defect explains the failures.
- **Release:** raw SHA256s match frozen metadata; its fingerprint matches the frozen value;
  raw MD5s match the publisher checksums recorded at S4. Pinned BioHopR revision and loader
  integrity checks pass. These checks verify local release integrity, not upstream author intent.

Full machine-readable evidence: [evidence.json](../s6_remaining_investigation/evidence.json),
[mixtures.csv](../s6_remaining_investigation/mixtures.csv), and
[identity_check.json](../s6_remaining_investigation/identity_check.json).

## Consequences and retained boundaries

All three failing types are now formally excluded: these two account for 251 rows, and the
previously excluded five-row type brings the total to 256. The five-row type's tied labels
remain unresolved. No R2 or construction is adopted for any excluded type, and no mapping
or hash is frozen. S7 has not started.

Recomputed global D1 is **PROCEED: 9/12 types, 7,377/7,633 rows (96.65%)**. It still exceeds
the required six types and 70% coverage. Exclusions do not reduce the denominators. These
are dataset-row coverage figures, not a claim about final S9 population size or measured
agent cofailure. No agent episodes were run for this decision.

Future reconsideration requires an explicit researcher decision and a documented basis
consistent with the frozen rules. Any proposed rule change after seeing these results must
be identified as such, with its exploratory status and affected downstream quantities made
explicit. “For the time being” does not waive the gate or authorize automatic re-admission.

## Record and verification

Current status is recorded in [the exclusion registry](../relation_type_exclusions.json)
and [recomputed D1](../d1_after_exclusion.json). Copies of the previous registry and D1
reports are in [previous](previous/d1_after_exclusion.md). The original investigation and
S6 calculation artifacts are unchanged. The decision log has a new entry; old entries remain.

This update changes status and documentation only. The investigation's full test suite
passed 119 tests; it was not rerun for this metadata-only decision. Assertions recomputed
D1 using the existing evaluator, verified that exactly the three FAIL types are excluded,
checked that the five-row exclusion is unchanged, and verified protected scientific and
investigation files by SHA256. See [verification.json](verification.json).

Assumption: current frozen rules remain authoritative. Routine engineering choices: keep
a cumulative current registry, archive its previous state, and add this dated decision
report instead of overwriting the completed investigation. No new scientific method,
threshold or identity rule. Manual review focus: the two distinct leukemia IDs and the
limits of the 29/30 construction-mixture result.
