"""Statutory Q4 — Part II §5 / item 9: the thread DIRECTLY woken by the
first wake-causing transition in (t, t+W], by finite-horizon forward sum
over the belief-conditioned kernel.

Wake-causing transitions (statute): a COMPLETION (woken = the issuer of
the departing request, i.e. the transition's actor) or a RELEASE with a
waiter (woken = the head handed off to, the transition's `related`).
Secondary wakes (QUEUE_BLOCKED threads freed by the same completion) are
excluded. Value ∈ threads ∪ {NONE_WITHIN_W}.

Decisions recorded (day seven): (i) the sum runs the kernel forward from
the window endpoint regardless of the episode horizon T_ep — the law
governs record delivery, not world termination, and the kernel is
time-homogeneous; (ii) a completion whose issuer terminates (final
instruction) still counts as waking the issuer — the statute names "the
issuer of the departing request," not the resulting status.

Firewall: this module is the ABSORBING RECURSIVE SUM path (memoized on
(state, remaining)). Its independent partner is `forecast_paths` (explicit
continuation enumeration). They share only the world (`kernel.enabled`).
"""

from fractions import Fraction
from math import log2
from typing import Dict, Hashable, Tuple

from yupi.config import WorldConfig
from yupi.kernel import Transition, enabled
from yupi.state import State

NONE_WITHIN_W = "NONE_WITHIN_W"
Dist = Dict[Hashable, Fraction]


def woken_by(t: Transition):
    """The directly-woken thread of a transition, or None if not wake-causing."""
    if t.kind == "COMPLETION":
        return t.actor
    if t.kind == "RELEASE" and t.related is not None:
        return t.related
    return None


def q4_forward(state: State, cfg: WorldConfig, programs, W: int,
               _memo: Dict[Tuple[State, int], Dist] = None) -> Dist:
    """Exact distribution of the first directly-woken thread within W steps."""
    if _memo is None:
        _memo = {}
    key = (state, W)
    if key in _memo:
        return _memo[key]
    if W == 0:
        out = {NONE_WITHIN_W: Fraction(1)}
    else:
        out: Dist = {}
        for t, p in enabled(state, cfg, programs):
            w = woken_by(t)
            if w is not None:
                out[w] = out.get(w, Fraction(0)) + p
            else:
                for k, q in q4_forward(t.next_state, cfg, programs, W - 1, _memo).items():
                    out[k] = out.get(k, Fraction(0)) + p * q
    _memo[key] = out
    return out


def q4_mixture(belief: Dict[State, Fraction], per_state: Dict[State, Dist]) -> Dist:
    out: Dist = {}
    for s, m in belief.items():
        for k, q in per_state[s].items():
            out[k] = out.get(k, Fraction(0)) + m * q
    return out


def _H(d: Dist) -> float:
    return -sum(float(p) * log2(float(p)) for p in d.values() if p > 0)


def split_entropy(belief: Dict[State, Fraction], per_state: Dict[State, Dist]):
    """(total, irreducible, observation-gap) in bits for a belief:
    total = H(mixture); irreducible = E_belief[H(per-state)]; gap = the
    difference = I(state; answer) under the belief. Part I D1: both terms."""
    total = _H(q4_mixture(belief, per_state))
    irreducible = sum(float(m) * _H(per_state[s]) for s, m in belief.items())
    return total, irreducible, total - irreducible
