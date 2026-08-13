"""Exact recursive Bayes filter (Part II §6, independent measurement path).

Computes posteriors by RECURSIVE BELIEF UPDATE -- belief in, observation in,
belief out -- carrying a full distribution over states forward one
observation at a time. No enumeration of trajectories anywhere in this
module: at each step only the current belief's support is expanded one tick
via `enabled()`, filtered against the single observed record, and collapsed
back into a new belief over states. This module exists to be compared
bit-for-bit against the independent brute-force path-summation enumerator
(`enumerator.py`, Task 7); sharing any of the enumerator's logic would defeat
that validation, so the only shared consumption is `yupi.kernel.enabled`,
`yupi.records.record_of`, `yupi.interfaces.project`, and
`yupi.state.initial_state` -- the world definition itself, not any
posterior-computation algorithm. `yupi.enumerator` is never imported here.

Fraction only, no floats: every belief value and every normalization is
exact rational arithmetic.
"""

from fractions import Fraction
from typing import Dict, List

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.state import State, initial_state

Belief = Dict[State, Fraction]


class ZeroProbabilityObservation(Exception):
    """Raised when an observation has probability zero under the current belief."""


def initial_belief(cfg: WorldConfig) -> Belief:
    """The point-mass belief on the world's initial state."""
    return {initial_state(cfg): Fraction(1)}


def step(belief: Belief, obs: Record, rung: str, cfg: WorldConfig, programs) -> Belief:
    """One recursive Bayes update: belief in, observation in, belief out.

    b'(s') proportional to sum over s of b(s) * sum of p for (t, p) in
    enabled(s) with project(record_of(t), rung) == obs and t.next_state == s'.

    Imported here rather than at module scope to keep `interfaces.project`
    off this module's top-level import list until it is actually needed --
    `project` is applied to each candidate transition's record, matched
    against the already-projected `obs` the caller supplies.
    """
    from yupi.interfaces import project

    unnormalized: Belief = {}
    for s, mass in belief.items():
        if mass == 0:
            continue
        for t, p in enabled(s, cfg, programs):
            if project(record_of(t), rung) != obs:
                continue
            contribution = mass * p
            s_next = t.next_state
            unnormalized[s_next] = unnormalized.get(s_next, Fraction(0)) + contribution

    total = sum(unnormalized.values(), Fraction(0))
    if total == 0:
        raise ZeroProbabilityObservation(
            f"observation {obs!r} has probability zero under the current belief"
        )

    return {s: mass / total for s, mass in unnormalized.items()}


def run(cfg: WorldConfig, programs, obs_seq: List[Record], rung: str) -> Belief:
    """Fold `step` over an observation sequence, starting from the initial belief."""
    belief = initial_belief(cfg)
    for obs in obs_seq:
        belief = step(belief, obs, rung, cfg, programs)
    return belief
