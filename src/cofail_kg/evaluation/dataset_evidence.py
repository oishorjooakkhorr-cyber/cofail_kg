"""S9 part 1: D2 steps 1–2 evidence, protocol §7.2; never compute step 3."""

import numpy as np

THRESHOLDS = (.30, .50, .70, .90)


def decision_evidence(records, pass_types):
    """Return confirmation, saturation distribution and threshold-sensitivity tables.

    Saturation uses all consistent queries in confirmed/unconfirmable types,
    including S6 sample queries and leakage flags, as the S9 part-1 prompt requires.
    """
    pass_types = sorted(pass_types)
    if {r["relation_type"] for r in records} - set(pass_types):
        raise ValueError("S8 contains a non-PASS relation type")
    if len({r["query_id"] for r in records}) != len(records):
        raise ValueError("Duplicate S8 query IDs")
    confirmation = []
    for kind in pass_types:
        group = [r for r in records if r["relation_type"] == kind]
        unseen = [r for r in group if not r["contains_s6_validation_row"]]
        n = len(unseen)
        consistent = sum(r["status"] == "CONSISTENT" for r in unseen)
        confirmation.append(dict(
            relation_type=kind, total_queries=len(group), s6_overlap_queries=len(group)-n,
            confirmation_queries=n, consistent_queries=consistent, inconsistent_queries=n-consistent,
            consistent_share=consistent/n if n else None,
            confirmation_status="UNCONFIRMABLE" if not n else "CONFIRMED" if 5*consistent >= 4*n else "UNCONFIRMED"))
    admitted = {r["relation_type"] for r in confirmation if r["confirmation_status"] != "UNCONFIRMED"}
    consistent_rows = [r for r in records if r["status"] == "CONSISTENT" and r["relation_type"] in admitted]
    distribution, sensitivity = [], []
    for kind in ["ALL", *sorted(admitted)]:
        shares = [r["saturation_share"] for r in consistent_rows if kind == "ALL" or r["relation_type"] == kind]
        if any(not np.isfinite(x) or not 0 <= x <= 1 for x in shares):
            raise ValueError("Invalid saturation share")
        percentiles = np.percentile(shares, [50, 90, 95, 99], method="linear").tolist() if shares else [None]*4
        distribution.append(dict(relation_type=kind, queries=len(shares),
                                 **dict(zip(("p50", "p90", "p95", "p99"), percentiles)),
                                 max=max(shares) if shares else None))
        for theta in THRESHOLDS:
            excluded = sum(x > theta for x in shares)
            sensitivity.append(dict(relation_type=kind, theta=theta, queries=len(shares),
                                    excluded_queries=excluded, excluded_share=excluded/len(shares) if shares else None,
                                    remaining_after_saturation=len(shares)-excluded,
                                    entire_type_removed=kind != "ALL" and bool(shares) and excluded == len(shares)))
    return confirmation, distribution, sensitivity
