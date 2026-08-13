"""Content-rung observation projections for the Yupana record layer.

Implements Part II §4 of docs/yupana-m1-part2-semantics-draft.md.
Projection table (content rungs):
  r1 (actor-only):     kind + actor only, obj/related/lineage → MASKED
  r2 (+object):        kind + actor + obj, related/lineage → MASKED
  r3 (+related):       kind + actor + obj + related, lineage → MASKED
  r4 (+lineage):       all fields preserved (no masking)

Semantics: None (a field absent in the latent record) survives projection as None,
distinct from MASKED (a field suppressed by the interface rung).
"""

from typing import Union
from yupi.records import Record

MASKED = "MASKED"


def project(record: Record, rung: str) -> Record:
    """Project a record to a specified content rung.

    Args:
        record: The Record to project.
        rung: One of "r1", "r2", "r3", "r4".

    Returns:
        A new Record with fields masked according to the rung definition.

    Raises:
        ValueError: If rung is not one of the known rung names.
    """
    if rung not in ("r1", "r2", "r3", "r4"):
        raise ValueError(f"Unknown rung name: {rung!r}")

    # r1: kind + actor only
    if rung == "r1":
        return Record(
            kind=record.kind,
            actor=record.actor,
            obj=MASKED,
            related=MASKED,
            lineage=MASKED,
        )

    # r2: kind + actor + obj (related/lineage masked)
    if rung == "r2":
        return Record(
            kind=record.kind,
            actor=record.actor,
            obj=record.obj,
            related=MASKED,
            lineage=MASKED,
        )

    # r3: kind + actor + obj + related (lineage masked)
    if rung == "r3":
        return Record(
            kind=record.kind,
            actor=record.actor,
            obj=record.obj,
            related=record.related,
            lineage=MASKED,
        )

    # r4: all fields (no masking)
    return record
