"""Canonical record layer: exact mapping from kernel transitions to observable records.

Implements Part II §4 of docs/yupana-m1-part2-semantics-draft.md. Each Transition
produces exactly one Record with the EVENT_KIND, ACTOR, OBJECT, RELATED, and
LINEAGE fields. The special case is the kernel's COMPLETION kind, which maps to
the record schema's IO_COMPLETE EVENT_KIND.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from yupi.kernel import Transition


@dataclass(frozen=True)
class Record:
    """One observable record: the immutable canonical form of a transition.

    kind: one of COMPLETION, DISPATCH, STEP, ACQUIRE, BLOCK, RELEASE,
          IO_ISSUE, IDLE, or IO_COMPLETE (the mapped form of COMPLETION).
    actor: the transitioning thread id, or None (IDLE has no actor).
    obj: ("LOCK", l) or ("DEV", d), or None when the transition kind has
         no natural object (e.g. STEP, DISPATCH, IDLE).
    related: current owner (on BLOCK for a lock), woken thread (on RELEASE),
             or None.
    lineage: request id (completion / IO_ISSUE), or None.
    """

    kind: str
    actor: Optional[int]
    obj: Optional[Tuple[str, int]]
    related: Optional[int]
    lineage: Optional[int]


def record_of(t: Transition) -> Record:
    """Convert a Transition to a Record, mapping COMPLETION → IO_COMPLETE.

    Maps all fields field-for-field from the Transition, with the single
    exception that the kernel's COMPLETION kind is mapped to the record
    schema's IO_COMPLETE EVENT_KIND.

    Args:
        t: The Transition to convert.

    Returns:
        A Record with the mapped kind and all other fields copied directly.
    """
    kind = t.kind
    if kind == "COMPLETION":
        kind = "IO_COMPLETE"

    return Record(
        kind=kind,
        actor=t.actor,
        obj=t.obj,
        related=t.related,
        lineage=t.lineage,
    )
