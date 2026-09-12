"""EXPERIMENT (2026-09-12, scratch): the window-process recursion with every
shared object interned and the kernel memoized per state. Same arithmetic,
same dictionary; the only changes are object identity and call count.
Gate: agg and mass_T equal (==) to yupi.window_process at the same law."""
from fractions import Fraction
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.records import record_of
from yupi.state import initial_state
from yupi.window import endpoint_prior


def window_law_aggregate_interned(cfg, programs, law, rung, stats=None, mass_T=True):
    L = law.L
    w_T = endpoint_prior(law)
    endpoints = set(law.endpoints())
    states = {}                       # State value -> canonical object
    kern = {}                         # canonical State -> [(tr, canonical next, canonical projected record, p)]
    proj = {}                         # id(tr) -> projected canonical record (tr pinned via kern)
    recs = {}                         # projected Record value -> canonical
    def canon_state(s):
        c = states.get(s)
        if c is None:
            states[s] = s; c = s
        return c
    def moves(s):
        m = kern.get(s)
        if m is None:
            m = []
            for tr, p in enabled(s, cfg, programs):
                r = project(record_of(tr), rung)
                r = recs.setdefault(r, r)
                m.append((canon_state(tr.next_state), r, p))
            kern[s] = m
        return m
    s0 = canon_state(initial_state(cfg))
    dist = {(s0, ()): Fraction(1)}
    agg = {}
    mT = {} if (stats is not None and mass_T) else None
    if stats is not None:
        stats["pairs_per_tick"] = []; stats["states_per_tick"] = []
        if mT is not None: stats["mass_T"] = mT
    for t in range(1, law.T_ep + 1):
        nxt = {}
        wins = {}                     # per-tick window intern: same window from different states shares one tuple
        for (s, buf), mass in dist.items():
            for ns, r, p in moves(s):
                nb = buf + (r,)
                if len(nb) > L:
                    nb = nb[-L:]
                nb = wins.setdefault(nb, nb)
                key = (ns, nb)
                nxt[key] = nxt.get(key, Fraction(0)) + mass * p
        dist = nxt
        del wins
        if stats is not None:
            stats["pairs_per_tick"].append(len(dist))
            stats["states_per_tick"].append(len({s for s, _ in dist}))
        if t in endpoints:
            reset = t <= L
            for (s, buf), mass in dist.items():
                d = agg.setdefault((reset, buf), {})
                d[s] = d.get(s, Fraction(0)) + w_T * mass
                if mT is not None:
                    e = mT.setdefault((reset, buf), {})
                    e[t] = e.get(t, Fraction(0)) + w_T * mass
    if stats is not None:
        stats["max_pairs"] = max(stats["pairs_per_tick"])
        stats["max_states"] = max(stats["states_per_tick"])
        stats["n_windows"] = len(agg)
        stats["n_distinct_states"] = len(states); stats["n_distinct_records"] = len(recs)
    return agg


def project_interned(fine, fine_mT, rungs):
    """Coarser rungs from the r4 aggregate, projected records interned so a
    coarse window is one tuple over shared records."""
    out, outT = {}, {}
    for r in rungs:
        if r == "r4":
            out[r] = fine; outT[r] = fine_mT; continue
        recs = {}
        coarse, coarse_mT = {}, {}
        for (reset, win), joint in fine.items():
            key = (reset, tuple(recs.setdefault(pr, pr) for pr in (project(x, r) for x in win)))
            d = coarse.setdefault(key, {})
            for s, m in joint.items():
                d[s] = d.get(s, Fraction(0)) + m
            if fine_mT is not None:
                e = coarse_mT.setdefault(key, {})
                for T, m in fine_mT[(reset, win)].items():
                    e[T] = e.get(T, Fraction(0)) + m
        out[r] = coarse; outT[r] = coarse_mT if fine_mT is not None else None
    return out, outT
