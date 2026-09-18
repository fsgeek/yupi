"""Naming bridge (Part II v0.2.9, proposed 2026-09-12, ENACTED 2026-09-13):
the equality-pattern projection Π, the surface renaming σ, and the
corpus-track state quotient. Exact; no kernel rule reads any of this. The
lemma that makes Π sufficient for the corpus process is executable in
tests/test_naming_bridge.py (threads) and
tests/test_naming_bridge_all_types.py (all four entity types, 2026-09-18);
the corpus-track producer is scripts/c1_corpus_track.py (thread-only Π —
its numbers are lower bounds on the four-type pattern observer's
uncertainty, learner contract v0.1 §2.1). Firewall: imports the record
schema and the interface constant only."""
from __future__ import annotations

import itertools
from typing import Tuple

from yupi.interfaces import MASKED
from yupi.records import Record


def _is_thread_field(v):
    return v is not None and v != MASKED


def rename(rec: Record, sigma) -> Record:
    """Surface record: thread fields through the episode's injection σ."""
    return Record(kind=rec.kind,
                  actor=sigma[rec.actor] if _is_thread_field(rec.actor) else rec.actor,
                  obj=rec.obj,
                  related=sigma[rec.related] if _is_thread_field(rec.related) else rec.related,
                  lineage=rec.lineage)


def pattern(window):
    """Equality pattern: thread fields relabeled by first appearance (actor
    before related within a record); returns (pattern window, order), where
    order[k] is the original label of pattern index k."""
    idx, order, out = {}, [], []
    def lab(v):
        if not _is_thread_field(v):
            return v
        if v not in idx:
            idx[v] = len(order); order.append(v)
        return idx[v]
    for r in window:
        a = lab(r.actor); rel = lab(r.related)
        out.append(Record(kind=r.kind, actor=a, obj=r.obj, related=rel, lineage=r.lineage))
    return tuple(out), tuple(order)



UNSEEN = "?"


def quotient(state, binding, cfg, with_pc=True, with_cursor=True):
    """The state re-expressed in the window's names — the corpus-track
    state (v0.2.9 §2, amended per the Codex read of 2026-09-12 [rv-4] [rv-5]).

    Named threads keep their fields under their pattern index. Unnamed
    threads are canonicalized: their fields, and every reference to them,
    are written under anonymous labels a0, a1, … chosen as the
    lexicographically least representation over all orderings of the
    unnamed threads, so relational structure among anonymous threads
    (which anonymous thread owns a lock, which waits, whether two
    references are the same thread) is kept while their structural
    identity is not. A field the kernel never writes under the
    configuration is excluded: the round-robin cursor is constant at
    ε = 1 (Part II §1, v0.2.6) and mapping it through the binding would
    inject binding entropy into the state ([rv-5]); at ε < 1 it is live
    and is mapped like any other thread reference. Program role is not a
    field of the state and is deliberately absent: which program a named
    thread runs is the binding's business, so role uncertainty lives in
    H(S, β | q, w), not in q.

    `with_pc=False` drops the program counters (2026-09-13): pc is written
    by the kernel and is state, but its value is meaningful only relative
    to the thread's program, which is the binding's business — so pc is a
    second coordinate (after the cursor) through which role can enter q.
    `with_cursor=False` also drops the cursor where it is live (ε < 1); at
    ε = 1 it is excluded regardless. Three forms are reported; none is
    claimed as "the content", and differences between them are conditional
    contributions, not shares (the coordinates may interact)."""
    n = len(state.pc)
    named = {t: k for k, t in enumerate(binding)}
    unnamed = [t for t in range(n) if t not in named]
    best = None
    for perm in itertools.permutations(unnamed):
        lab = dict(named)
        for j, t in enumerate(perm):
            lab[t] = f"a{j}"
        nm = lambda t: (lab[t] if t is not None else None)
        pcv = (lambda t: state.pc[t]) if with_pc else (lambda t: None)
        rep = (tuple((pcv(t), state.status[t]) for t in binding),
               tuple((pcv(t), state.status[t]) for t in perm),
               tuple(sorted(str(nm(t)) for t in state.running)),
               tuple(str(nm(o)) for o in state.lock_owner),
               tuple(tuple(str(nm(t)) for t in q) for q in state.lock_wq),
               tuple(tuple((str(nm(t)), r) for t, r in q) for q in state.dev_q),
               (str(nm(state.rr_cursor)) if (cfg.epsilon < 1 and with_cursor) else None))
        if best is None or rep < best:
            best = rep
    return best




# ---- Π over all four entity types (learner contract v0.1 §2.1, 2026-09-18) ----
#
# The corpus renames threads, locks, devices and request ids per episode
# (design v0.1 §3); `pattern`/`rename` above cover threads only, and every
# corpus-track artifact produced with them holds the other three types
# canonical (a thread-naming lower bound on the pattern observer's
# uncertainty). `pattern_all` is the joint equality pattern: first-appearance
# relabeling per entity type, actor before related within a record, obj
# keeping its kind tag. The binding is a 4-tuple of orders in ENTITY order
# (thread, lock, device, request); binding[0] equals `pattern`'s order.
# Lemma: tests/test_naming_bridge_all_types.py.

ENTITY_ORDER = ("thread", "lock", "device", "request")


def rename_all(rec: Record, sigma: dict) -> Record:
    """Surface record under per-type injections: sigma[type][structural] -> token.
    MASKED and None survive; obj keeps its ("LOCK"|"DEV", ·) tag."""
    def th(v):
        return sigma["thread"][v] if _is_thread_field(v) else v
    if _is_thread_field(rec.obj):
        tag, i = rec.obj
        obj = (tag, sigma["lock"][i] if tag == "LOCK" else sigma["device"][i])
    else:
        obj = rec.obj
    lin = sigma["request"][rec.lineage] if _is_thread_field(rec.lineage) else rec.lineage
    return Record(kind=rec.kind, actor=th(rec.actor), obj=obj, related=th(rec.related), lineage=lin)


def extend_binding(binding, rec: Record, types=ENTITY_ORDER):
    """One step of Π_all: (pattern record, extended binding). A field whose
    entity is already bound keeps its pattern index; a fresh entity of a
    renamed type takes the next index of its type (actor before related
    within a record) and the binding grows; a type not in `types`, MASKED
    and None pass through. pattern_all is the fold of this over a window,
    and the pattern filter's likelihood is [extend_binding(β, r)[0] == ρ]."""
    orders = [list(o) for o in binding]

    def lab(et, v):
        if not _is_thread_field(v) or et not in types:
            return v
        o = orders[ENTITY_ORDER.index(et)]
        if v in o:
            return o.index(v)
        o.append(v)
        return len(o) - 1

    a = lab("thread", rec.actor)
    if _is_thread_field(rec.obj):
        tag, i = rec.obj
        obj = (tag, lab("lock" if tag == "LOCK" else "device", i))
    else:
        obj = rec.obj
    rel = lab("thread", rec.related)
    lin = lab("request", rec.lineage)
    return Record(kind=rec.kind, actor=a, obj=obj, related=rel, lineage=lin), tuple(tuple(o) for o in orders)


def pattern_all(window, types=ENTITY_ORDER):
    """Joint equality pattern over the entity types in `types` (default all
    four): returns (pattern window, binding) with binding = (thread order,
    lock order, device order, request order); order[k] is the structural
    index of pattern index k. A type not in `types` is left structural and
    its order is empty — the observer for whom that type is NOT renamed
    knows its identities, so its pattern is the identity.
    pattern_all(w, ("thread",)) has pattern(w)'s window and order."""
    binding = ((), (), (), ())
    out = []
    for r in window:
        pr, binding = extend_binding(binding, r, types)
        out.append(pr)
    return tuple(out), binding
