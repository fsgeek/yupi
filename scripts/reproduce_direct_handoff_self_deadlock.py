"""Reproduce the 2026-08-20 direct-handoff self-deadlock audit finding.

This is a diagnostic witness for the kernel at commit d19ef25. It does not
repair the defect. A corrected direct-handoff implementation is expected to
produce no bad paths, at which point this historical reproducer should be
retained and a regression test should encode the corrected semantic.
"""

import json
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.programs import c0a_programs
from yupi.state import check_invariants


HORIZON = 10


def is_self_wait(state) -> bool:
    """Whether a lock owner is queued waiting for that same lock."""
    return any(
        owner is not None and owner in state.lock_wq[lock]
        for lock, owner in enumerate(state.lock_owner)
    )


def main() -> None:
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    witnesses = [
        (records, probability, state)
        for records, probability, state in paths(cfg, programs, HORIZON)
        if is_self_wait(state)
    ]
    total_mass = sum((probability for _, probability, _ in witnesses), Fraction())

    result = {
        "configuration": "C0a",
        "horizon": HORIZON,
        "bad_path_count": len(witnesses),
        "bad_path_mass": str(total_mass),
        "witnesses": [],
    }
    for records, probability, state in witnesses:
        result["witnesses"].append(
            {
                "path_probability": str(probability),
                "record_tail": [
                    {
                        "kind": record.kind,
                        "actor": record.actor,
                        "related": record.related,
                    }
                    for record in records[-3:]
                ],
                "lock_owner": list(state.lock_owner),
                "lock_wait_queues": [list(queue) for queue in state.lock_wq],
                "status": [list(status) for status in state.status],
                "reported_invariant_violations": check_invariants(state, cfg),
            }
        )

    print(json.dumps(result, indent=2, sort_keys=True))

    # These assertions pin the observed defect at the audited commit. They are
    # deliberately in a diagnostic script, not in the passing regression
    # suite. The repair should add a test for the corrected semantics.
    assert len(witnesses) == 1
    assert total_mass == Fraction(1, 8)
    _, _, witness_state = witnesses[0]
    assert check_invariants(witness_state, cfg) == []


if __name__ == "__main__":
    main()
