"""Content-rung observation projections for the Yupana record layer.

Implements Part II §4 of docs/yupana-m1-part2-semantics-draft.md.
Projection table (content rungs):
  r0 (kind-only):      kind only, actor/obj/related/lineage → MASKED
                       (exploratory extension below the statutory ladder,
                       2026-09-03; not a Part II rung unless enacted)
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
        rung: One of "r0" (exploratory), "r1", "r2", "r3", "r4".

    Returns:
        A new Record with fields masked according to the rung definition.

    Raises:
        ValueError: If rung is not one of the known rung names.
    """
    if rung not in ("r0", "r1", "r2", "r3", "r4"):
        raise ValueError(f"Unknown rung name: {rung!r}")

    # r0: kind only (exploratory, below the statutory ladder)
    if rung == "r0":
        return Record(
            kind=record.kind,
            actor=MASKED,
            obj=MASKED,
            related=MASKED,
            lineage=MASKED,
        )

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


# ---- the relay rung r1ʀ (docs/relay-intervention-design-v0.1.md §2, 2026-09-30) ----
#
# A WINDOW-level interface, not a per-record projection: record t's OBJECT
# slot (which r1 masks) carries the KIND of the most recent earlier record
# in the same window with the same actor as t; None (rendered NONE) when the
# actor has no earlier record in the window or t has no actor. Its values
# are `Lit` — literal kind names, not entities — so Π_all and the renamings
# pass them through untouched (yupi.naming). Name in code and on disk: "r1R".

from dataclasses import dataclass as _dataclass


@_dataclass(frozen=True)
class Lit:
    """A literal value in an entity slot: a KIND name the naming layer never renames."""
    kind: str


RELAY_RUNGS = {"r1R": "r1"}          # window-level rung -> the per-record rung it relays


def _check_r1(rec: Record) -> None:
    if not (rec.obj == MASKED and rec.related == MASKED and rec.lineage == MASKED):
        raise ValueError(f"relay applies to r1-projected records only, got {rec!r}")


def relay_next(window, rec: Record) -> Record:
    """The r1ʀ form of r1 record `rec` following the r1 records `window`."""
    _check_r1(rec)
    val = None
    if rec.actor is not None:
        for prev in reversed(window):
            if prev.actor == rec.actor:
                val = Lit(prev.kind)
                break
    return Record(kind=rec.kind, actor=rec.actor, obj=val, related=MASKED, lineage=MASKED)


def relay_window(window) -> tuple:
    """r1 records of one window -> r1ʀ records (window-local: uses records 1..t only)."""
    window = tuple(window)
    out = []
    last = {}
    for rec in window:
        _check_r1(rec)
        val = Lit(last[rec.actor]) if rec.actor is not None and rec.actor in last else None
        out.append(Record(kind=rec.kind, actor=rec.actor, obj=val, related=MASKED, lineage=MASKED))
        if rec.actor is not None:
            last[rec.actor] = rec.kind
    return tuple(out)


def drop_relay(window) -> tuple:
    """Inverse of relay_window: r1ʀ records -> r1 records."""
    return tuple(Record(kind=r.kind, actor=r.actor, obj=MASKED, related=r.related, lineage=r.lineage)
                 for r in window)


def project_window(records, rung: str) -> tuple:
    """Project a window's latent records: per record for r0–r4, then the relay for r1R."""
    base = RELAY_RUNGS.get(rung)
    if base is None:
        return tuple(project(r, rung) for r in records)
    return relay_window(tuple(project(r, base) for r in records))
