"""Windowed posteriors by PREFIX-MARGINALIZED PATH SUMMATION (validator).

The independent second path for the windowed gate: enumerate every full
episode trajectory to each length-compatible endpoint T (via
`enumerator.paths` — brute force, no recursive belief update), project the
in-window suffix, keep paths matching the observed window, and sum kept
path probabilities by (offset, final state). The prefix records before the
window are marginalized by simply not being matched — the sum over full
paths IS the prefix marginalization.

This module never imports `window_filter`; the only sharing is the world
definition and the law/result structures in `window`. It exists so
`filter_window` can be validated bit-for-bit, exactly as `enumerator`
validates `filter`.
"""

from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.records import Record
from yupi.window import Belief, WindowLaw, WindowPosterior


def posterior_by_window_paths(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    obs_seq: List[Record],
    rung: str,
    reset_observed: bool,
) -> WindowPosterior:
    """Exact joint posterior over (U, S_T) by exhaustive path summation.

    The uniform endpoint prior is a constant across compatible components
    and cancels in normalization; within a component the kept-path masses
    are exact Fractions, so equality with the filter path is bit-for-bit.
    """
    n = len(obs_seq)
    raw: Dict[int, Belief] = {}
    for T, u in law.compatible_endpoints(n, reset_observed):
        totals: Belief = {}
        for recs, prob, final in paths(cfg, programs, T):
            projected = [project(r, rung) for r in recs[u:]]
            if projected != list(obs_seq):
                continue
            totals[final] = totals.get(final, Fraction(0)) + prob
        if totals:
            raw[u] = totals

    grand = sum(
        (m for totals in raw.values() for m in totals.values()), Fraction(0)
    )
    components: Dict[int, Tuple[Fraction, Belief]] = {}
    for u, totals in raw.items():
        mass = sum(totals.values(), Fraction(0))
        components[u] = (
            mass / grand,
            {s: m / mass for s, m in totals.items()},
        )
    return WindowPosterior(components=components)
