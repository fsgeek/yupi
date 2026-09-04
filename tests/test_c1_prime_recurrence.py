"""Recurrence in C1′ (unrolled), pinned for the looping exit-law freeze
(`docs/looping-exit-law-freeze-v0.1.md` §3): P(some thread has ACQUIRED the
same lock twice) by tick t, exact forward marginal. Ticks 16 and 24 only
(the 32/40/48 values in the note were computed the same way; a 48-tick
marginal is a minute per ε and is not re-run here)."""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.programs import c1_prime_programs
from yupi.state import initial_state


def second_acquire_index(program):
    seen = {}
    for i, ins in enumerate(program):
        if ins[0] == "ACQUIRE":
            seen[ins[1]] = seen.get(ins[1], 0) + 1
            if seen[ins[1]] == 2:
                return i
    return None


def recurrence(eps, ticks):
    progs = c1_prime_programs()
    thr = [second_acquire_index(p) for p in progs]
    cfg = WorldConfig.c1(epsilon=eps)
    dist = {initial_state(cfg): Fraction(1)}
    out = {}
    for t in range(1, max(ticks) + 1):
        nxt = {}
        for s, m in dist.items():
            for tr, p in enabled(s, cfg, progs):
                nxt[tr.next_state] = nxt.get(tr.next_state, Fraction(0)) + m * p
        dist = nxt
        if t in ticks:
            out[t] = sum(m for s, m in dist.items() if any(s.pc[i] > thr[i] for i in range(4)))
    return out


def test_second_acquire_indices():
    assert [second_acquire_index(p) for p in c1_prime_programs()] == [3, 4, 4, 4]


@pytest.mark.parametrize("eps,t16,t24", [(Fraction(1), 0.0085, 0.1177), (Fraction(1, 2), 0.0004, 0.0257)])
def test_recurrence_is_rare_before_tick_24(eps, t16, t24):
    r = recurrence(eps, (16, 24))
    assert round(float(r[16]), 4) == t16 and round(float(r[24]), 4) == t24
    assert 0 < r[16] < r[24] < Fraction(1, 5)
