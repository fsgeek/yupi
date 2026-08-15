"""Explicit-enumeration partners for `predict` — the other side of the
forward-sum firewall. Every W-step continuation unrolled, probability
multiplied along the path, functional read off the full trail."""

from fractions import Fraction
from typing import Dict, Hashable, List

from yupi.config import WorldConfig
from yupi.forecast import NONE_WITHIN_W, woken_by
from yupi.kernel import Transition, enabled
from yupi.records import record_of
from yupi.state import State


def _trails(state: State, cfg: WorldConfig, programs, W: int):
    out: List[tuple] = []

    def rec(s, prob, trail, remaining):
        if remaining == 0:
            out.append((trail, prob))
            return
        for t, p in enabled(s, cfg, programs):
            rec(t.next_state, prob * p, trail + [t], remaining - 1)

    rec(state, Fraction(1), [], W)
    return out


def time_to_wake_by_paths(state, cfg, programs, W) -> Dict[Hashable, Fraction]:
    out: Dict[Hashable, Fraction] = {}
    for trail, prob in _trails(state, cfg, programs, W):
        tag = NONE_WITHIN_W
        for i, t in enumerate(trail):
            if woken_by(t) is not None:
                tag = i + 1
                break
        out[tag] = out.get(tag, Fraction(0)) + prob
    return out


def next_complete_lineage_by_paths(state, cfg, programs, W) -> Dict[Hashable, Fraction]:
    out: Dict[Hashable, Fraction] = {}
    for trail, prob in _trails(state, cfg, programs, W):
        tag = NONE_WITHIN_W
        for t in trail:
            if t.kind == "COMPLETION":
                tag = t.lineage
                break
        out[tag] = out.get(tag, Fraction(0)) + prob
    return out


def next_kinds_by_paths(state, cfg, programs, m) -> Dict[Hashable, Fraction]:
    out: Dict[Hashable, Fraction] = {}
    for trail, prob in _trails(state, cfg, programs, m):
        tup = tuple(record_of(t).kind for t in trail)
        out[tup] = out.get(tup, Fraction(0)) + prob
    return out
