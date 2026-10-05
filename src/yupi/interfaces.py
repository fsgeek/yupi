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
    """Inverse of relay_window (and of every registered window map): OBJECT slot -> MASKED."""
    return tuple(Record(kind=r.kind, actor=r.actor, obj=MASKED, related=r.related, lineage=r.lineage)
                 for r in window)


# ---- the decoy r1ᴅ and the self-copy r1ꜱ (docs/three-arm-design-v0.1.md §2, 2026-10-05) ----
#
# Window-level rungs over r1 like the relay, value in the same OBJECT slot, as a Lit:
#   r1D: record t's OBJECT = KIND of record t − 1 in the window; None for the first record.
#   r1S: record t's OBJECT = KIND of record t.
# Neither carries binding content. Both are window-local, injective (drop_relay
# inverts them) and literal under Π_all.

def decoy_next(window, rec: Record) -> Record:
    """The r1ᴅ form of r1 record `rec` following the r1 records `window`."""
    _check_r1(rec)
    val = Lit(window[-1].kind) if len(window) else None
    return Record(kind=rec.kind, actor=rec.actor, obj=val, related=MASKED, lineage=MASKED)


def decoy_window(window) -> tuple:
    """r1 records of one window -> r1ᴅ records (window-local: record t uses record t − 1)."""
    window = tuple(window)
    return tuple(decoy_next(window[:i], rec) for i, rec in enumerate(window))


def self_copy_next(window, rec: Record) -> Record:
    """The r1ꜱ form of r1 record `rec` (the window is not consulted)."""
    _check_r1(rec)
    return Record(kind=rec.kind, actor=rec.actor, obj=Lit(rec.kind), related=MASKED, lineage=MASKED)


def self_copy_window(window) -> tuple:
    """r1 records of one window -> r1ꜱ records."""
    return tuple(self_copy_next((), rec) for rec in window)


# The registry of window-level rungs: name -> (base per-record rung, window map,
# next-record map). The window map takes base records of one window to the rung's
# records; the next-record map takes (base window, next base record) to the rung's
# next record and equals the last step of the window map. RELAY_RUNGS above is kept
# as it was (r1R only) for callers that predate the registry.
WINDOW_RUNGS = {
    "r1R": ("r1", relay_window, relay_next),
    "r1D": ("r1", decoy_window, decoy_next),
    "r1S": ("r1", self_copy_window, self_copy_next),
}


def base_rung(rung: str) -> str:
    """The per-record rung a window-level rung is built on; a per-record rung is its own base."""
    return WINDOW_RUNGS[rung][0] if rung in WINDOW_RUNGS else rung


def window_map(rung: str):
    """The window map of a registered window-level rung (KeyError otherwise)."""
    return WINDOW_RUNGS[rung][1]


def next_map(rung: str):
    """The next-record map of a registered window-level rung (KeyError otherwise)."""
    return WINDOW_RUNGS[rung][2]


def project_window(records, rung: str) -> tuple:
    """Project a window's latent records: per record for r0–r4, then the window map
    for a window-level rung (r1R, r1D, r1S)."""
    if rung not in WINDOW_RUNGS:
        return tuple(project(r, rung) for r in records)
    base, wmap, _ = WINDOW_RUNGS[rung]
    return wmap(tuple(project(r, base) for r in records))
