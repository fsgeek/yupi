"""Independent exhaustive trajectory enumerator (Part II §6, brute-force validator).

Computes posteriors by BRUTE-FORCE PATH SUMMATION over the full trajectory
tree: depth-first unrolling of every stochastic choice `enabled()` offers,
to exactly `horizon` ticks, followed by summing/filtering/normalizing path
probabilities. No recursive belief update anywhere in this module -- that is
the point. This module exists to be compared bit-for-bit against a
separately implemented recursive filter (`filter.py`, future task); sharing
any belief-propagation logic with that module would defeat the validation
this enumerator is for. The only shared consumption is `yupi.kernel.enabled`,
`yupi.records.record_of`, `yupi.interfaces.project`, and
`yupi.state.initial_state` -- the world definition itself, not any filtering
algorithm.

Episodes are NOT stopped early at all-TERMINATED: per Part II §3.6, a
terminated world still offers an IDLE self-loop with probability 1, so
unrolling continues to `horizon` regardless, keeping every path the same
length and carrying probability mass through the self-loop correctly.
"""

from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.state import State, initial_state
from yupi.interfaces import project


def paths(
    cfg: WorldConfig, programs, horizon: int
) -> List[Tuple[List[Record], Fraction, State]]:
    """Enumerate every trajectory to `horizon` by depth-first unrolling.

    Returns a list of (latent record sequence, exact path probability, final
    state) triples, one per distinct path through the full stochastic
    transition tree. Probabilities across the returned list sum to exactly
    Fraction(1) (enabled() always returns a distribution summing to 1, so
    the tree's leaves at any fixed depth partition the full probability
    mass).
    """
    results: List[Tuple[List[Record], Fraction, State]] = []

    def recurse(state: State, prob: Fraction, recs: List[Record], remaining: int) -> None:
        if remaining == 0:
            results.append((recs, prob, state))
            return
        for transition, p in enabled(state, cfg, programs):
            recurse(
                transition.next_state,
                prob * p,
                recs + [record_of(transition)],
                remaining - 1,
            )

    recurse(initial_state(cfg), Fraction(1), [], horizon)
    return results


def posterior_by_paths(
    cfg: WorldConfig, programs, obs_seq: List[Record], rung: str
) -> Dict[State, Fraction]:
    """Exact posterior over final states given an observed record sequence.

    Brute force: enumerate all paths to horizon = len(obs_seq), keep those
    whose per-tick projection at `rung` equals `obs_seq` exactly, sum kept
    path probabilities by final state, and normalize by the total kept
    probability mass (the exact probability of observing `obs_seq` at all).
    """
    horizon = len(obs_seq)
    all_paths = paths(cfg, programs, horizon)

    totals: Dict[State, Fraction] = {}
    total_mass = Fraction(0)
    for recs, prob, final in all_paths:
        projected = [project(r, rung) for r in recs]
        if projected != obs_seq:
            continue
        totals[final] = totals.get(final, Fraction(0)) + prob
        total_mass += prob

    return {state: p / total_mass for state, p in totals.items()}
