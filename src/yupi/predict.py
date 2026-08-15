"""Predictive-state targets — Part II §5, "P-next" and "P-horizon".

- p_next(state, rung): the Bayes-optimal next-RECORD distribution as the
  observer at `rung` sees it — project(record_of(t), rung) over the
  kernel's enabled transitions. One step; no recursion.
- next_kinds(state, m): distribution of the next m EVENT_KINDs (record
  kinds; COMPLETION mapped to IO_COMPLETE). Fixed-length recursion.
- time_to_wake(state, W): distribution of the step index (1..W) of the
  first wake-causing transition, or NONE_WITHIN_W. First-event recursion.
- next_complete_lineage(state, W): lineage (request id) of the first
  IO_COMPLETE within W, or NONE_WITHIN_W. First-event recursion. "Where
  exposed": meaningful to an r4 observer; computed on the state.

`first_event` generalizes forecast.q4_forward: absorb(t, k) returns a
tag (absorb) or None (continue). Firewall: this module is the RECURSIVE
side; `predict_paths` is the explicit-enumeration partner. Shared: the
world (kernel.enabled, records, interfaces) and forecast.woken_by.
Belief-level mixtures use forecast.q4_mixture / split_entropy unchanged.
"""

from fractions import Fraction
from typing import Callable, Dict, Hashable, Optional, Tuple

from yupi.config import WorldConfig
from yupi.forecast import NONE_WITHIN_W, woken_by
from yupi.interfaces import project
from yupi.kernel import Transition, enabled
from yupi.records import record_of
from yupi.state import State

Dist = Dict[Hashable, Fraction]


def p_next(state: State, cfg: WorldConfig, programs, rung: str) -> Dist:
    out: Dist = {}
    for t, p in enabled(state, cfg, programs):
        r = project(record_of(t), rung)
        out[r] = out.get(r, Fraction(0)) + p
    return out


def first_event(state: State, cfg: WorldConfig, programs, W: int,
                absorb: Callable[[Transition, int], Optional[Hashable]],
                _memo: Dict = None, _k: int = 1) -> Dist:
    """Distribution of absorb(t, k) at the first step k ≤ W where it is
    not None; NONE_WITHIN_W otherwise. Memo keyed on (state, W, k)."""
    if _memo is None:
        _memo = {}
    key = (state, W, _k)
    if key in _memo:
        return _memo[key]
    if W == 0:
        out = {NONE_WITHIN_W: Fraction(1)}
    else:
        out: Dist = {}
        for t, p in enabled(state, cfg, programs):
            tag = absorb(t, _k)
            if tag is not None:
                out[tag] = out.get(tag, Fraction(0)) + p
            else:
                for k2, q in first_event(t.next_state, cfg, programs, W - 1,
                                         absorb, _memo, _k + 1).items():
                    out[k2] = out.get(k2, Fraction(0)) + p * q
    _memo[key] = out
    return out


def _wake_time(t: Transition, k: int):
    return k if woken_by(t) is not None else None


def _complete_lineage(t: Transition, k: int):
    return t.lineage if t.kind == "COMPLETION" else None


def time_to_wake(state, cfg, programs, W, _memo=None) -> Dist:
    return first_event(state, cfg, programs, W, _wake_time, _memo)


def next_complete_lineage(state, cfg, programs, W, _memo=None) -> Dist:
    return first_event(state, cfg, programs, W, _complete_lineage, _memo)


def next_kinds(state: State, cfg: WorldConfig, programs, m: int,
               _memo: Dict = None) -> Dist:
    """Distribution over tuples of the next m record kinds."""
    if _memo is None:
        _memo = {}
    key = (state, m)
    if key in _memo:
        return _memo[key]
    if m == 0:
        out = {(): Fraction(1)}
    else:
        out: Dist = {}
        for t, p in enabled(state, cfg, programs):
            k = record_of(t).kind
            for rest, q in next_kinds(t.next_state, cfg, programs, m - 1, _memo).items():
                tup = (k,) + rest
                out[tup] = out.get(tup, Fraction(0)) + p * q
    _memo[key] = out
    return out
