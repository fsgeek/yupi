"""`window_filter.state_marginal_at` is a pure function of (cfg, programs, t)
and was recomputed from reset for every compatible offset of every window
(profile 2026-09-04 at (40,4,2), looping C1′: 14.7 of 17 s per window). An
exact cross-call cache must return bit-identical beliefs and must not call
the kernel again for a t it has already reached. Written before the cache."""
from fractions import Fraction

import pytest

from yupi import window_filter
from yupi.config import WorldConfig
from yupi.programs import c1_programs, c1_prime_loop_programs
from yupi.window_filter import state_marginal_at, marginal_cache_clear


def _fresh(cfg, progs, t):
    """Reference: the uncached forward marginal, computed here."""
    from yupi.kernel import enabled
    from yupi.state import initial_state
    belief = {initial_state(cfg): Fraction(1)}
    for _ in range(t):
        nxt = {}
        for s, m in belief.items():
            for tr, p in enabled(s, cfg, progs):
                nxt[tr.next_state] = nxt.get(tr.next_state, Fraction(0)) + m * p
        belief = nxt
    return belief


@pytest.mark.parametrize("progs_fn", [c1_programs, c1_prime_loop_programs])
@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_cached_marginal_is_bit_identical(progs_fn, eps):
    marginal_cache_clear()
    cfg, progs = WorldConfig.c1(epsilon=eps), progs_fn()
    for t in (0, 3, 7, 12, 5):          # out of order: the cache must serve t=5 from t=12's prefix
        assert state_marginal_at(cfg, progs, t) == _fresh(cfg, progs, t)


def test_cache_does_not_call_the_kernel_for_a_reached_t(monkeypatch):
    marginal_cache_clear()
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    ref = state_marginal_at(cfg, progs, 10)
    def boom(*a, **k):
        raise AssertionError("kernel called for a cached t")
    monkeypatch.setattr(window_filter, "enabled", boom)
    assert state_marginal_at(cfg, progs, 10) == ref
    assert state_marginal_at(cfg, progs, 4) == _fresh(cfg, progs, 4)
    with pytest.raises(AssertionError):
        state_marginal_at(cfg, progs, 11)     # beyond the reached t: must compute (and here, fail)


def test_cache_is_keyed_by_config_and_programs():
    marginal_cache_clear()
    a = state_marginal_at(WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), 6)
    b = state_marginal_at(WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), 6)
    c = state_marginal_at(WorldConfig.c1(epsilon=Fraction(1)), c1_prime_loop_programs(), 6)
    assert a != b and a != c
    assert a == _fresh(WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), 6)


def test_returned_belief_is_not_the_cache_object():
    marginal_cache_clear()
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    b = state_marginal_at(cfg, progs, 5)
    b[next(iter(b))] = Fraction(0)            # a caller mutating its copy must not poison the cache
    assert state_marginal_at(cfg, progs, 5) == _fresh(cfg, progs, 5)
