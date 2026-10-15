"""Deterministic disjoint query sampling, protocol §8; evaluator-only metadata."""

import hashlib
from collections import Counter

SEED = 42
GROUPS = ("SINGLE_BRIDGE", "MULTI_BRIDGE")
SET_SPECS = (("screening",20,5,15,0), ("smoke",4,1,3,0),
             ("pilot",100,25,75,1), ("expansion",400,100,300,1))


def allocate_types(available, quota, floor):
    """Apply per-type floors then largest remainders on remaining availability (§8.2)."""
    available = dict(sorted(available.items()))
    if quota < 0 or quota > sum(available.values()) or floor < 0 or any(n < 0 for n in available.values()):
        raise ValueError("Invalid allocation capacity/quota")
    allocation = {kind:min(floor,n) for kind,n in available.items()}
    if sum(allocation.values()) > quota:
        raise ValueError("Per-type floor exceeds group quota; protocol requires researcher clarification")
    left = quota-sum(allocation.values())
    capacity = {kind:n-allocation[kind] for kind,n in available.items()}
    total = sum(capacity.values())
    if left:
        division = {kind:divmod(left*n,total) for kind,n in capacity.items()}
        for kind,(base,_) in division.items():
            allocation[kind] += base
        remainder_slots = quota-sum(allocation.values())
        order = sorted((kind for kind in capacity if allocation[kind]<available[kind]),
                       key=lambda kind:(-division[kind][1],kind))
        for kind in order[:remainder_slots]:
            allocation[kind] += 1
    return allocation


def size_bin(n):
    if n < 1:
        raise ValueError("Sampled queries must have at least one valid target")
    return "1–10" if n<=10 else "11–100" if n<=100 else "101–1,000" if n<=1000 else "over 1,000"


def draw_samples(records, specs=SET_SPECS):
    if len({r["query_id"] for r in records}) != len(records):
        raise ValueError("Duplicate population query IDs")
    if any(r["bridge_multiplicity"] not in GROUPS for r in records):
        raise ValueError("Invalid primary-population multiplicity")
    remaining = {r["query_id"]:r for r in records}
    samples, reports = {}, {}
    for name,target,single,multi,floor in specs:
        if single+multi != target:
            raise ValueError("Multiplicity quotas must sum to target size")
        available = {g:sum(r["bridge_multiplicity"]==g for r in remaining.values()) for g in GROUPS}
        quotas = {g:min(n,available[g]) for g,n in zip(GROUPS,(single,multi))}
        left = target-sum(quotas.values())
        for g in GROUPS:
            extra = min(left,available[g]-quotas[g])
            quotas[g] += extra
            left -= extra
        chosen, strata = [], {}
        for group in GROUPS:
            members = [r for r in remaining.values() if r["bridge_multiplicity"]==group]
            allocation = allocate_types(Counter(r["relation_type"] for r in members),quotas[group],floor)
            strata[group] = allocation
            for kind,n in allocation.items():
                candidates = sorted((r for r in members if r["relation_type"]==kind),
                                    key=lambda r:(hashlib.sha256((str(SEED)+r["query_id"]).encode()).hexdigest(),r["query_id"]))
                chosen.extend(candidates[:n])
        chosen.sort(key=lambda r:r["query_id"])
        for r in chosen:
            del remaining[r["query_id"]]
        samples[name] = chosen
        reports[name] = {"target_size":target,"sampled":len(chosen),"shortfall":target-len(chosen),
                         "requested_quotas":dict(zip(GROUPS,(single,multi))),
                         "by_multiplicity":quotas,"per_type_floor":floor,"strata":strata}
    return samples,reports
