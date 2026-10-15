"""S9 primary population (protocol §7.2) and ordered D2 step-3 feasibility rules."""

import math
from collections import Counter


def feasibility(n, k):
    if n < 150:
        return "RED"
    if n >= 650 and k >= 5:
        return "GREEN"
    return "YELLOW"


def build_population(records, pass_types, confirmation, theta):
    if theta is None or not math.isfinite(theta) or not 0 <= theta <= 1:
        raise ValueError("A frozen numeric theta in [0, 1] is required")
    if set(pass_types) - set(confirmation):
        raise ValueError("Missing D2 mapping confirmation")
    if len({r["query_id"] for r in records}) != len(records):
        raise ValueError("Duplicate query IDs")
    population, exclusions = [], Counter()
    for r in sorted(records, key=lambda r: r["query_id"]):
        share = r["saturation_share"]
        if not math.isfinite(share) or not 0 <= share <= 1:
            raise ValueError("Invalid saturation share")
        flags = {"inconsistent": r["status"] != "CONSISTENT",
                 "saturated": share > theta, "leaky_question": r["leaky_question"],
                 "not_d1_pass": r["relation_type"] not in pass_types,
                 "not_confirmed_or_unconfirmable": confirmation.get(r["relation_type"]) not in ("CONFIRMED", "UNCONFIRMABLE")}
        exclusions.update({key: int(value) for key, value in flags.items()})
        if not any(flags.values()):
            population.append({**r, "theta": theta, "saturated": False,
                               "mapping_confirmation": confirmation[r["relation_type"]]})
    by_type = {}
    for kind in sorted(pass_types):
        group = [r for r in population if r["relation_type"] == kind]
        by_type[kind] = {"queries": len(group), "by_multiplicity": dict(sorted(Counter(r["bridge_multiplicity"] for r in group).items()))}
    n, k = len(population), sum(v["queries"] >= 20 for v in by_type.values())
    return population, {"theta": theta, "input_queries": len(records), "N_P": n, "K": k,
                        "outcome": feasibility(n,k), "excluded_queries": len(records)-n,
                        "exclusion_counts": dict(sorted(exclusions.items())),
                        "exclusion_counts_may_overlap": True, "by_type": by_type,
                        "by_multiplicity": dict(sorted(Counter(r["bridge_multiplicity"] for r in population).items()))}
