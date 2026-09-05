"""Enumerator-side aggregation for the statutory producers, one entry point
(2026-09-04): per rung, the law mass over final states per
(reset_observed, projected window) and its per-endpoint split — from path
aggregation (the committed method, `enumerator.paths`) or from the
window-process recursion (`window_process.window_law_aggregates`: one r4
pass, every coarser rung projected). The two agree exactly wherever both
run (tests/test_aggregation.py); the recursion reaches horizons the path
enumerator cannot. Firewall: this module is enumerator-side only and
imports no filter code; the filter-side gate is applied by the caller.
"""
from fractions import Fraction
from typing import Dict, Tuple

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_process import window_law_aggregates

Aggregate = Dict[Tuple[bool, tuple], Dict[object, Fraction]]
MassT = Dict[Tuple[bool, tuple], Dict[int, Fraction]]


def aggregate_by_rung(cfg: WorldConfig, programs, law: WindowLaw, rungs, mode: str) -> Dict[str, Tuple[Aggregate, MassT]]:
    """{rung: (agg, mass_T)}: agg[(reset, window)][state] = law mass;
    mass_T[(reset, window)][T] = law mass generated at endpoint T."""
    rungs = tuple(rungs)
    if mode == "paths":
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, programs, T) for T in law.endpoints()}
        out = {}
        for rung in rungs:
            agg: Aggregate = {}
            mT: MassT = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
                    e = mT.setdefault(key, {})
                    e[T] = e.get(T, Fraction(0)) + w_T * prob
            out[rung] = (agg, mT)
        return out
    if mode == "window":
        stats: dict = {}
        aggs = window_law_aggregates(cfg, programs, law, rungs, stats)
        return {rung: (aggs[rung], stats["mass_T_by_rung"][rung]) for rung in rungs}
    raise ValueError(f"unknown aggregation mode {mode!r} (paths | window)")
