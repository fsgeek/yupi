"""Window-law aggregation by FORWARD RECURSION OVER (STATE, LAST-L WINDOW).

The third exact path in the instrument, built 2026-09-03 so that the window
law can be evaluated at horizons where path enumeration is impossible
(`c1-prime-pilot-note-v0.1.md`): the ceilings producers aggregate every
full path by (reset observed, projected in-window suffix) → law mass over
final states; this module produces the identical dictionary by carrying
the joint law of (S_t, last-L projected records) forward one tick at a
time, applying the endpoint prior at each grid point. Memory is the number
of distinct (state, window) pairs at a tick — bounded by reachable states
× distinct windows, independent of the horizon — instead of the number of
paths, which is exponential in it.

Firewall: this module imports neither `window_filter` (recursive mixture
filtering per observed window) nor `window_enumerator` / `enumerator`
(brute-force path summation). Sharing is the world definition
(`kernel.enabled`, `records`, `interfaces`, `state`) and the law structure
in `window`. Its gate is exact equality with the path aggregation at
horizons where both exist (`tests/test_window_process.py`), the same
relation `filter` bears to `enumerator`.

Exact rationals throughout.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Optional, Tuple

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.state import State, initial_state
from yupi.window import WindowLaw, endpoint_prior

WindowKey = Tuple[bool, Tuple[Record, ...]]
Aggregate = Dict[WindowKey, Dict[State, Fraction]]


def window_law_aggregate(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    rung: str,
    stats: Optional[dict] = None,
) -> Aggregate:
    """Law mass over final states per (reset_observed, projected window),
    for every endpoint on the law's grid — the dictionary the ceilings
    producers build from `paths`, without the paths.

    reset_observed is True iff the endpoint T ≤ L (offset U = 0), in which
    case the window is the whole trace (length T); otherwise the window is
    the last L records and the reset is not in view. Windows of different
    lengths never share a key, so the endpoint mixture happens exactly as
    in the path aggregation.
    """
    L = law.L
    w_T = endpoint_prior(law)
    endpoints = set(law.endpoints())
    dist: Dict[Tuple[State, Tuple[Record, ...]], Fraction] = {
        (initial_state(cfg), ()): Fraction(1)
    }
    agg: Aggregate = {}
    if stats is not None:
        stats["pairs_per_tick"] = []
    for t in range(1, law.T_ep + 1):
        nxt: Dict[Tuple[State, Tuple[Record, ...]], Fraction] = {}
        for (s, buf), mass in dist.items():
            for tr, p in enabled(s, cfg, programs):
                r = project(record_of(tr), rung)
                nb = buf + (r,)
                if len(nb) > L:
                    nb = nb[-L:]
                key = (tr.next_state, nb)
                nxt[key] = nxt.get(key, Fraction(0)) + mass * p
        dist = nxt
        if stats is not None:
            stats["pairs_per_tick"].append(len(dist))
        if t in endpoints:
            reset = t <= L
            for (s, buf), mass in dist.items():
                d = agg.setdefault((reset, buf), {})
                d[s] = d.get(s, Fraction(0)) + w_T * mass
    if stats is not None:
        stats["max_pairs"] = max(stats["pairs_per_tick"])
        stats["n_windows"] = len(agg)
    return agg


def window_law_aggregates(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    rungs=("r0", "r1", "r2", "r3", "r4"),
    stats: Optional[dict] = None,
) -> Dict[str, Aggregate]:
    """The aggregate for every requested rung from ONE recursion at r4.

    r4 refines every other rung (each rung only masks fields), so a coarser
    rung's aggregate is the r4 aggregate with keys re-projected and masses
    merged. Same output as calling `window_law_aggregate` per rung, at the
    cost of a single r4 recursion (gate: tests/test_window_process.py).
    """
    fine = window_law_aggregate(cfg, programs, law, "r4", stats)
    out: Dict[str, Aggregate] = {}
    for r in rungs:
        if r == "r4":
            out[r] = fine
            continue
        coarse: Aggregate = {}
        for (reset, win), joint in fine.items():
            key = (reset, tuple(project(x, r) for x in win))
            d = coarse.setdefault(key, {})
            for s, m in joint.items():
                d[s] = d.get(s, Fraction(0)) + m
        out[r] = coarse
    return out
