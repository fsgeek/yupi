"""Seeded episode sampling: draw exact transitions from enabled distributions.

Implements the complete simulator for sampling episodes from the Yupana kernel's
exact probability distributions. Each episode is a sequence of (Transition, Record)
pairs, drawn deterministically from a seeded RNG. The sampler maintains exactness
by avoiding float conversions: all probability weights are Fraction values, converted
to integer numerators over a common denominator for the RNG's integer sampling.
"""

import random
from fractions import Fraction
from typing import List, Tuple

from yupi.config import WorldConfig
from yupi.kernel import Transition, enabled
from yupi.records import Record, record_of
from yupi.state import State, initial_state, TERMINATED, check_invariants


def sample_episode(
    cfg: WorldConfig,
    programs,
    horizon: int,
    seed: int
) -> List[Tuple[Transition, Record]]:
    """Sample a single episode from the Yupana world up to horizon ticks.

    Args:
        cfg: The world configuration.
        programs: The thread programs (tuple of tuples of instructions).
        horizon: Maximum number of ticks before forced termination.
        seed: Random seed for reproducibility.

    Returns:
        A list of (Transition, Record) pairs, exactly one per tick through
        `horizon` (early termination pads with absorbing IDLE records, per
        Part II §2/§3.6 — the sampler and enumerator share one episode law).

    Exactness: All probability sampling uses Fraction weights without float
    conversion. The RNG draws from integer numerators over a common denominator.
    """
    rng = random.Random(seed)
    state = initial_state(cfg)
    episode: List[Tuple[Transition, Record]] = []

    for tick in range(horizon):
        # §2/§3.6 (2026-08-20 audit fix): the episode law is exactly `horizon`
        # records; the all-TERMINATED state is an absorbing IDLE self-loop the
        # kernel emits with probability 1, so no early break — the enumerator
        # already follows this rule and the sampler must sample the same law.
        # Get the exact distribution over enabled transitions.
        transitions = enabled(state, cfg, programs)
        if not transitions:
            # No enabled transitions (shouldn't happen given IDLE fallback).
            break

        # Convert Fraction probabilities to a common denominator for exact sampling.
        probabilities = [prob for _, prob in transitions]

        # Find LCM of all denominators to establish common denominator.
        from math import gcd
        from functools import reduce

        def lcm(a, b):
            return abs(a * b) // gcd(a, b)

        # Compute LCM of all denominators.
        denominators = [p.denominator for p in probabilities]
        common_denom = reduce(lcm, denominators)

        # Convert each probability to integer numerator over common_denom.
        weights = [int(p * common_denom) for p in probabilities]

        # Draw using integer-only randrange with cumulative weights.
        # No float conversion anywhere: randrange draws from [0, total) as integers.
        total = sum(weights)
        draw = rng.randrange(total)
        cumsum = 0
        chosen_idx = 0
        for i, weight in enumerate(weights):
            cumsum += weight
            if draw < cumsum:
                chosen_idx = i
                break

        transition, _ = transitions[chosen_idx]
        record = record_of(transition)

        episode.append((transition, record))
        state = transition.next_state

    return episode
