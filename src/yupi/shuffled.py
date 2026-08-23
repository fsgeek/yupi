"""D8 order modes: the shuffled within-bucket channel (Part II §4).

Shuffled mode delivers each bucket of B projected records under a uniform
within-bucket permutation — a *stochastic observation kernel*, not a
projection. The likelihood of a visible sequence given the latent bucket
is m/B!, where m is the number of permutations of the latent bucket that
produce the visible sequence (duplicate records make m > 1). The filter
multiplies world-path probability by this likelihood and never assumes
uniformity over causally possible latent orders.

Ordered mode is identity serialization (likelihood 1 iff equal), so
`step_ordered_bucket` is exactly B applications of `filter.step`.

Independence discipline: this module shares with the enumerator only the
world definition (`kernel.enabled`, `records.record_of`,
`interfaces.project`); the two-path gate in tests/test_shuffled_channel.py
compares it bit-for-bit against path summation.
"""
from collections import Counter
from fractions import Fraction
from math import factorial
from typing import Dict, List, Tuple

from yupi.config import WorldConfig
from yupi.filter import Belief, ZeroProbabilityObservation, initial_belief, step
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.state import State


def multiset_key(records: List[Record]) -> Tuple:
    """Canonical hashable multiset of records (order-free identity)."""
    return tuple(sorted(Counter(records).items(), key=lambda kv: repr(kv[0])))


def channel_likelihood(latent: List[Record], visible: List[Record]) -> Fraction:
    """m / B!  with m = #permutations of `latent` equal to `visible` as a
    sequence. m = Π (multiplicity!) when the multisets agree, else 0."""
    if len(latent) != len(visible) or Counter(latent) != Counter(visible):
        return Fraction(0)
    m = 1
    for mult in Counter(latent).values():
        m *= factorial(mult)
    return Fraction(m, factorial(len(latent)))


def _expand(belief: Belief, B: int, rung: str, cfg: WorldConfig, programs):
    """All B-tick latent continuations of the belief: yields
    (projected latent bucket, prob mass, final state)."""
    frontier = [([], mass, s) for s, mass in belief.items() if mass]
    for _ in range(B):
        nxt = []
        for recs, mass, s in frontier:
            for t, p in enabled(s, cfg, programs):
                nxt.append((recs + [project(record_of(t), rung)], mass * p, t.next_state))
        frontier = nxt
    return frontier


def step_bucket(belief: Belief, visible: List[Record], rung: str,
                cfg: WorldConfig, programs) -> Belief:
    """Shuffled-mode update over one delivered bucket."""
    B = len(visible)
    unnorm: Dict[State, Fraction] = {}
    for latent, mass, s in _expand(belief, B, rung, cfg, programs):
        lik = channel_likelihood(latent, visible)
        if lik:
            unnorm[s] = unnorm.get(s, Fraction(0)) + mass * lik
    Z = sum(unnorm.values(), Fraction(0))
    if Z == 0:
        raise ZeroProbabilityObservation(f"bucket {visible!r} has probability zero")
    return {s: m / Z for s, m in unnorm.items()}


def step_ordered_bucket(belief: Belief, visible: List[Record], rung: str,
                        cfg: WorldConfig, programs) -> Belief:
    """Ordered mode: identity serialization = B per-record filter steps."""
    for r in visible:
        belief = step(belief, r, rung, cfg, programs)
    return belief


def run_buckets(cfg: WorldConfig, programs, buckets: List[List[Record]],
                rung: str, B: int, mode: str = "shuffled") -> Belief:
    if mode not in ("shuffled", "ordered"):
        raise ValueError(mode)
    f = step_bucket if mode == "shuffled" else step_ordered_bucket
    belief = initial_belief(cfg)
    for vis in buckets:
        if len(vis) != B:
            raise ValueError(f"bucket of size {len(vis)} under B={B}")
        belief = f(belief, vis, rung, cfg, programs)
    return belief
