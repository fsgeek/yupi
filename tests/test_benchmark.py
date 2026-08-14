"""Tests for the D4 budget benchmark harness (src/yupi/benchmark.py).

The harness prices the two posterior paths on this hardware BEFORE any
observability curve is computed (Part I D4/D9 precedence rule): filter.step
wall-clock and peak memory as functions of support size, and enumerator
path throughput as a function of horizon. States for pricing come from
deterministic BFS over world reachability — no observations, no posteriors,
so no observability information leaks ahead of the budget freeze.

Witness/control discipline (C0c's Riemann-C.6 rule): the dynamometer world
must be witnessed large enough to price big supports (cap is hit), and the
control is C0a, whose reachable space exhausts below the same cap — the
world where big-support pricing provably cannot work.
"""

from fractions import Fraction

from yupi.benchmark import (
    EnumPrice,
    FilterPrice,
    choose_observation,
    dyno_config,
    dyno_programs,
    make_belief,
    price_enumerator,
    price_filter_step,
    reachable_states,
)
from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import step
from yupi.kernel import enabled
from yupi.programs import c0a_programs, validate_lock_order
from yupi.state import check_invariants, initial_state


CAP_LARGE = 10**6


def test_reachable_states_starts_at_initial_and_is_deterministic():
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    first = reachable_states(cfg, programs, cap=200)
    second = reachable_states(cfg, programs, cap=200)
    assert first == second
    assert first[0] == initial_state(cfg)


def test_reachable_states_distinct_and_invariant_clean():
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    states = reachable_states(cfg, programs, cap=200)
    assert len(states) == len(set(states))
    for s in states:
        assert check_invariants(s, cfg) == []


def test_reachable_states_exhausts_small_world_below_cap():
    # Control world: C0a's reachable space is finite and small; BFS must
    # terminate below the cap and the returned set must be closed under
    # the world's own transitions.
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    states = reachable_states(cfg, programs, cap=CAP_LARGE)
    assert len(states) < CAP_LARGE
    universe = set(states)
    for s in states:
        for t, _ in enabled(s, cfg, programs):
            assert t.next_state in universe


def test_reachable_states_respects_cap():
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    states = reachable_states(cfg, programs, cap=5)
    assert len(states) == 5


def test_dyno_world_is_valid_and_large():
    # Witness: the dynamometer world must be big enough to price large
    # supports — BFS hits the cap instead of exhausting. Its programs must
    # honor the I6 lock-order discipline like any Yupana workload.
    cfg = dyno_config()
    programs = dyno_programs()
    assert validate_lock_order(programs)
    cap = 20_000
    states = reachable_states(cfg, programs, cap=cap)
    assert len(states) == cap
    for s in states[:100]:
        assert check_invariants(s, cfg) == []


def test_make_belief_uniform_exact():
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    states = reachable_states(cfg, programs, cap=7)
    belief = make_belief(states)
    assert len(belief) == 7
    assert all(mass == Fraction(1, 7) for mass in belief.values())
    assert sum(belief.values(), Fraction(0)) == Fraction(1)


def test_choose_observation_yields_nonzero_likelihood_step():
    cfg = dyno_config()
    programs = dyno_programs()
    states = reachable_states(cfg, programs, cap=50)
    belief = make_belief(states)
    obs = choose_observation(belief, cfg, programs, rung="r1")
    posterior = step(belief, obs, "r1", cfg, programs)
    assert len(posterior) >= 1


def test_price_filter_step_reports_consistent_counts():
    cfg = dyno_config()
    programs = dyno_programs()
    states = reachable_states(cfg, programs, cap=50)
    belief = make_belief(states)
    price = price_filter_step(belief, cfg, programs, rung="r1", repeats=2)
    assert isinstance(price, FilterPrice)
    assert price.support_in == 50
    assert price.support_out >= 1
    # every support state offers at least one transition, so expansion
    # touches at least as many transitions as states
    assert price.transitions_expanded >= price.support_in
    assert price.wall_s > 0
    assert price.peak_mem_bytes > 0


def test_price_enumerator_counts_paths_exactly():
    cfg = WorldConfig.c0a()
    programs = c0a_programs()
    price = price_enumerator(cfg, programs, horizon=3)
    assert isinstance(price, EnumPrice)
    assert price.horizon == 3
    assert price.n_paths == len(paths(cfg, programs, 3))
    assert price.wall_s > 0
