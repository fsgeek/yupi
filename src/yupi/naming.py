"""Naming bridge (Part II v0.2.9 PROPOSAL, 2026-09-12; not enacted): the
equality-pattern projection Π, the surface renaming σ, and the corpus-track
state quotient. Exact; no kernel rule reads any of this. The lemma that
makes Π sufficient for the corpus process is executable in
tests/test_naming_bridge.py; the corpus-track producer is
scripts/c1_corpus_track.py. Firewall: imports the record schema and the
interface constant only."""
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


