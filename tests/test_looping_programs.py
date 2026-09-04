"""Executable controls for Part II v0.2.8 (looping programs: pc modulo the
body). Written before the implementation (2026-09-04), per the Codex review
of the proposal: the review asked for independent transition tests at every
reachable wrap site, a mixed loop/straight-line configuration, a PC_RANGE
invariant, and an exhaustive exact-zero control (no posterior mass on
pc = |P| for a looping thread). Every committed configuration is
straight-line; nothing here touches a frozen number.

Reachable wrap sites: COMPUTE, RELEASE (releasing thread), IO_ISSUE. The two
ACQUIRE advance sites (successful ACQUIRE, direct-handoff waiter) cannot
wrap because I6 forbids a body ending in ACQUIRE; they are exercised for
correctness (pc advances, no termination) rather than for wrap.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import run as filter_run
from yupi.interfaces import project
from yupi.kernel import enabled, KernelInvariantViolation
from yupi.programs import (
    COMPUTE, Loop, acquire, io, release, is_looping, validate_lock_order,
    c1_prime_programs, c1_prime_loop_programs, programs_for,
)
from yupi.state import (
    check_invariants, initial_state, RUNNABLE, TERMINATED,
)


def _cfg(n_threads, n_cpus=1, n_locks=1, n_devices=1, queue_depth=1,
         req_pool=2, p=Fraction(1, 3), eps=Fraction(1)):
    return WorldConfig(n_threads=n_threads, n_cpus=n_cpus, n_locks=n_locks,
                       n_devices=n_devices, queue_depth=queue_depth,
                       req_pool=req_pool, completion_p=p, epsilon=eps,
                       discipline="stochastic")


def _take(s, cfg, progs, pred):
    (t,) = [t for t, _ in enabled(s, cfg, progs) if pred(t)]
    return t.next_state, t


# ---- the wrapper type -------------------------------------------------------

def test_loop_body_must_be_nonempty():
    with pytest.raises(ValueError):
        Loop(())


def test_loop_is_distinct_from_its_straight_line_body():
    body = (COMPUTE, acquire(0), release(0))
    lp = Loop(body)
    assert is_looping(lp) and not is_looping(body)
    assert len(lp) == 3 and lp[1] == acquire(0) and tuple(lp) == body
    assert lp != body and hash(lp) != hash(body)      # caches keyed by programs must not collide
    assert lp == Loop(body) and hash(lp) == hash(Loop(body))


def test_validate_lock_order_applies_to_the_body():
    assert validate_lock_order((Loop((acquire(0), release(0))),))
    assert not validate_lock_order((Loop((acquire(0),)),))       # wrap would carry a lock
    assert not validate_lock_order((Loop((release(0),)),))


def test_kernel_refuses_a_looping_body_that_ends_holding_a_lock():
    cfg = _cfg(1)
    with pytest.raises(KernelInvariantViolation):
        enabled(initial_state(cfg), cfg, (Loop((acquire(0),)),))


# ---- wrap sites ---------------------------------------------------------------

def test_wrap_at_compute_returns_to_pc_zero_and_stays_runnable():
    cfg, progs = _cfg(1), (Loop((COMPUTE,)),)
    s = initial_state(cfg)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH")
    s, t = _take(s, cfg, progs, lambda t: t.kind == "STEP")
    assert s.pc == (0,) and s.status == (RUNNABLE,)
    assert TERMINATED not in s.status


def test_wrap_at_release_returns_to_pc_zero():
    cfg, progs = _cfg(1), (Loop((acquire(0), release(0))),)
    s = initial_state(cfg)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH")
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "ACQUIRE")
    assert s.pc == (1,)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH")
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "RELEASE")
    assert s.pc == (0,) and s.status == (RUNNABLE,) and s.lock_owner == (None,)


def test_wrap_at_io_issue_and_completion_wakes_runnable_not_terminated():
    cfg, progs = _cfg(1), (Loop((io(0),)),)
    s = initial_state(cfg)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH")
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "IO_ISSUE")
    assert s.pc == (0,)                       # wrapped at issue
    assert s.status[0][0] == "IO_BLOCKED"
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "COMPLETION")
    assert s.status == (RUNNABLE,)            # straight-line (io(0),) would TERMINATE here
    assert s.pc == (0,)


def test_direct_handoff_waiter_advances_past_its_acquire_without_terminating():
    # t0: acquire, compute, release (loop); t1: acquire, release (loop). One CPU.
    cfg = _cfg(2, req_pool=2)
    progs = (Loop((acquire(0), COMPUTE, release(0))), Loop((acquire(0), release(0))))
    s = initial_state(cfg)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH" and t.actor == 0)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "ACQUIRE")
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH" and t.actor == 1)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "BLOCK")
    assert s.lock_wq == ((1,),)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH" and t.actor == 0)
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "STEP")
    s, _ = _take(s, cfg, progs, lambda t: t.kind == "DISPATCH" and t.actor == 0)
    s, t = _take(s, cfg, progs, lambda t: t.kind == "RELEASE")
    assert t.related == 1                    # handoff to the waiter
    assert s.lock_owner == (1,) and s.pc == (0, 1)   # releaser wrapped; waiter past its ACQUIRE
    assert s.status[1] == RUNNABLE and TERMINATED not in s.status


# ---- invariants ------------------------------------------------------------------

def test_pc_range_flags_looping_thread_at_body_length_or_terminated():
    cfg, progs = _cfg(1), (Loop((COMPUTE,)),)
    s = initial_state(cfg)
    assert "PC_RANGE" not in check_invariants(s, cfg, progs)
    from dataclasses import replace
    assert "PC_RANGE" in check_invariants(replace(s, pc=(1,)), cfg, progs)
    assert "PC_RANGE" in check_invariants(replace(s, status=(TERMINATED,)), cfg, progs)
    # straight-line: pc == |P| is legal (final-IO-blocked or TERMINATED)
    assert "PC_RANGE" not in check_invariants(replace(s, pc=(1,), status=(TERMINATED,)), cfg, (
        (COMPUTE,),))
    assert "PC_RANGE" in check_invariants(replace(s, pc=(2,)), cfg, ((COMPUTE,),))


def test_check_invariants_without_programs_is_unchanged():
    cfg = _cfg(1)
    assert check_invariants(initial_state(cfg), cfg) == []


# ---- exhaustive exact-zero control and mixed configuration -------------------

def _reachable(cfg, progs, horizon):
    seen, frontier = set(), [initial_state(cfg)]
    while frontier:
        s = frontier.pop()
        if s in seen:
            continue
        seen.add(s)
        for t, _ in enabled(s, cfg, progs):
            frontier.append(t.next_state)
    return seen


def test_exhaustive_zero_mass_on_pc_equals_body_length_for_looping_threads():
    cfg = _cfg(2, n_cpus=1, n_locks=1, n_devices=1, queue_depth=1, req_pool=2)
    progs = (Loop((acquire(0), release(0), io(0))), Loop((COMPUTE, acquire(0), release(0))))
    for s in _reachable(cfg, progs, None):
        assert check_invariants(s, cfg, progs) == [], s
        for i in range(2):
            assert 0 <= s.pc[i] < len(progs[i]) and s.status[i] != TERMINATED
    # and by mass, at a fixed horizon: no path ends with pc == |P|
    for recs, prob, final in paths(cfg, progs, 8):
        assert all(final.pc[i] < len(progs[i]) for i in range(2))
    assert sum(p for _, p, _ in paths(cfg, progs, 8)) == Fraction(1)


def test_mixed_configuration_terminates_only_the_straight_line_thread():
    cfg = _cfg(2, n_cpus=1, n_locks=1, req_pool=2)
    progs = (Loop((acquire(0), release(0))), (acquire(0), release(0)))
    states = _reachable(cfg, progs, None)
    assert any(s.status[1] == TERMINATED for s in states)
    assert all(s.status[0] != TERMINATED for s in states)
    assert all(check_invariants(s, cfg, progs) == [] for s in states)   # I3 still active for t1


def test_filter_agrees_with_path_aggregation_on_a_looping_world():
    # two-path gate (filter vs enumerator) at a short horizon, every rung
    cfg = _cfg(2, n_cpus=1, n_locks=1, queue_depth=1, req_pool=2)
    progs = (Loop((acquire(0), release(0), io(0))), Loop((COMPUTE, acquire(0), release(0))))
    for rung in ("r0", "r1", "r2", "r3", "r4"):
        by_obs = {}
        for recs, prob, final in paths(cfg, progs, 6):
            key = tuple(project(r, rung) for r in recs)
            d = by_obs.setdefault(key, {})
            d[final] = d.get(final, Fraction(0)) + prob
        for key, d in by_obs.items():
            mass = sum(d.values(), Fraction(0))
            posterior = filter_run(cfg, progs, list(key), rung)
            assert posterior == {s: m / mass for s, m in d.items()}, (rung, key)


# ---- the looping C1′ ----------------------------------------------------------

def test_c1_prime_loop_is_the_unrolled_c1_prime_folded():
    unrolled, looped = c1_prime_programs(), c1_prime_loop_programs()
    assert len(looped) == 4 and all(is_looping(p) for p in looped)
    for u, lp in zip(unrolled, looped):
        assert len(u) % len(lp) == 0 and u == tuple(lp) * (len(u) // len(lp))
    assert programs_for("c1prime-loop") == looped
    assert not any(is_looping(p) for p in programs_for("c1"))


def test_c1_prime_loop_never_terminates_and_reaches_far_fewer_states():
    cfg = WorldConfig.c1(epsilon=Fraction(1))
    loop_states = _reachable(cfg, c1_prime_loop_programs(), None)
    assert all(TERMINATED not in s.status for s in loop_states)
    assert all(check_invariants(s, cfg, c1_prime_loop_programs()) == [] for s in loop_states)
    # the unrolled world's reachable set at tick 48 was 14370 (live census); the
    # folded world's ENTIRE reachable set must be smaller than that
    assert len(loop_states) < 14370
