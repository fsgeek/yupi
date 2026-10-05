"""Pattern-observer posteriors by PREFIX-MARGINALIZED PATH SUMMATION — the
independent validator of `yupi.pattern_filter` (learner contract v0.1,
2026-09-18). Never imports the filter; shares the world definition, the
law and Π only (the two-path firewall of `window_enumerator`).

For every endpoint T on the grid (offset U), every trajectory to the
required length is enumerated by `enumerator.paths`, the in-window suffix
is projected to the rung and patterned by Π_all, and path masses are
summed by (RESET, pattern window) → offset → (final state, binding). The
prefix records before the window are marginalized by not being matched.
"""
from fractions import Fraction
from typing import Dict, Optional, Tuple

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import next_map, project, window_map
from yupi.naming import ENTITY_ORDER, extend_binding, pattern_all
from yupi.records import Record
from yupi.window import WindowLaw, endpoint_prior


def pattern_aggregate_by_paths(cfg: WorldConfig, programs, law: WindowLaw, rung: str,
                               types=ENTITY_ORDER, prefix_len: Optional[int] = None):
    """{(reset, Πw): {U: {(S, β): law mass}}}. Full windows by default; with
    `prefix_len = k`, the first k records of every window with T − U ≥ k
    (the state is the one after the k-th window record)."""
    w_T = endpoint_prior(law)
    out: Dict[Tuple[bool, tuple], Dict[int, Dict[tuple, Fraction]]] = {}
    for T in law.endpoints():
        u = law.offset(T)
        n = T - u if prefix_len is None else prefix_len
        if T - u < n:
            continue
        for recs, prob, final in paths(cfg, programs, u + n):
            pw, binding = pattern_all(tuple(project(r, rung) for r in recs[u:u + n]), types)
            d = out.setdefault((u == 0, pw), {}).setdefault(u, {})
            d[(final, binding)] = d.get((final, binding), Fraction(0)) + w_T * prob
    return out


def next_pattern_aggregate_by_paths(cfg: WorldConfig, programs, law: WindowLaw, rung: str, types=ENTITY_ORDER):
    """{(reset, Πw): {Πr_{T+1}: law mass}} — realized next records tallied over
    trajectories to T + 1 whose window (records U+1..T) patterns to Πw; the
    next record is re-keyed through the window's binding by extend_binding.
    Dividing by the class mass gives P*(Πr | Πw) by a path that never runs
    the kernel on a posterior."""
    w_T = endpoint_prior(law)
    out: Dict[Tuple[bool, tuple], Dict[Record, Fraction]] = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, _ in paths(cfg, programs, T + 1):
            pw, binding = pattern_all(tuple(project(r, rung) for r in recs[u:T]), types)
            rho, _ = extend_binding(binding, project(recs[T], rung), types)
            d = out.setdefault((u == 0, pw), {})
            d[rho] = d.get(rho, Fraction(0)) + w_T * prob
    return out


def relay_table_by_paths(cfg: WorldConfig, programs, law: WindowLaw, base: str = "r1", types=ENTITY_ORDER,
                         rung: str = "r1R"):
    """{(reset, Πw): (mass, P*(Πr | Πw))} for FULL windows of the relay rung r1ʀ
    by path summation (relay design v0.1 §3, gate C): trajectories to T + 1, the
    window projected to `base` and relayed structurally, the next record relayed
    given that window, both re-keyed by Π_all. Never runs the kernel on a posterior.
    With `rung`, any registered window-level rung (interfaces.WINDOW_RUNGS) by its
    window and next-record maps (three-arm design v0.1 §3)."""
    wmap, nmap = window_map(rung), next_map(rung)
    w_T = endpoint_prior(law)
    joint: Dict[Tuple[bool, tuple], Dict[Record, Fraction]] = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, _ in paths(cfg, programs, T + 1):
            win = tuple(project(r, base) for r in recs[u:T])
            pw, binding = pattern_all(wmap(win), types)
            rho, _ = extend_binding(binding, nmap(win, project(recs[T], base)), types)
            d = joint.setdefault((u == 0, pw), {})
            d[rho] = d.get(rho, Fraction(0)) + w_T * prob
    out = {}
    for key, d in joint.items():
        mass = sum(d.values(), Fraction(0))
        out[key] = (mass, {r: q / mass for r, q in d.items()})
    return out
