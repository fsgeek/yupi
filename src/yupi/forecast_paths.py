"""Statutory Q4 by EXPLICIT CONTINUATION ENUMERATION — the independent
partner of `forecast.q4_forward` behind the forward-sum firewall.

Unrolls every W-step continuation from a state (no absorption, no memo),
multiplies probabilities along the path, and tags each full-length path
by the first wake-causing transition found scanning forward (or
NONE_WITHIN_W). Shares only the world (`kernel.enabled`) and the
statute's `woken_by` predicate — the predicate is world definition (what
counts as a wake), not computation.
"""

from fractions import Fraction
from typing import Dict, Hashable, List

from yupi.config import WorldConfig
from yupi.forecast import NONE_WITHIN_W, woken_by
from yupi.kernel import Transition, enabled
from yupi.state import State


def q4_by_paths(state: State, cfg: WorldConfig, programs, W: int) -> Dict[Hashable, Fraction]:
    out: Dict[Hashable, Fraction] = {}

    def recurse(s: State, prob: Fraction, trail: List[Transition], remaining: int):
        if remaining == 0:
            tag = NONE_WITHIN_W
            for t in trail:
                w = woken_by(t)
                if w is not None:
                    tag = w
                    break
            out[tag] = out.get(tag, Fraction(0)) + prob
            return
        for t, p in enabled(s, cfg, programs):
            recurse(t.next_state, prob * p, trail + [t], remaining - 1)

    recurse(state, Fraction(1), [], W)
    return out
