"""Witness tests for the 2026-08-20 direct-handoff audit findings.

Statute anchors: Part II §3.3 (RELEASE: the woken head "acquires ownership
immediately and becomes RUNNABLE" — its ACQUIRE is complete, so its pc must
advance at handoff), §3.5 (direct handoff), §3.6/§2 (episodes are exactly
T_ep records; the terminal state is an absorbing IDLE self-loop), I6 (no
deadlock state reachable). Written failing against the defective kernel
(commit 47b4019 era), per the audit's reproduction.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.kernel import enabled
from yupi.programs import c0a_programs, c0b_programs, c1_programs, validate_lock_order
from yupi.simulator import sample_episode
from yupi.state import check_invariants, initial_state, TERMINATED


def _self_wait(state):
    return any(
        owner is not None and owner in state.lock_wq[lock]
        for lock, owner in enumerate(state.lock_owner)
    )


def _first_self_wait_transition(cfg, programs, horizon):
    """Walk every path; return a (state_before, transition) pair whose next
    state self-waits, or None."""
    frontier = [(initial_state(cfg), Fraction(1))]
    for _ in range(horizon):
        nxt = []
        for s, p in frontier:
            for t, q in enabled(s, cfg, programs):
                if _self_wait(t.next_state):
                    return s, t
                nxt.append((t.next_state, p * q))
        frontier = nxt
    return None


def test_handoff_advances_woken_pc_past_acquire():
    """After a RELEASE handoff, the woken thread's pc has moved past its
    ACQUIRE (statute: it acquired immediately)."""
    cfg, programs = WorldConfig.c0a(), c0a_programs()
    seen_handoff = False
    frontier = [initial_state(cfg)]
    seen = set()
    for _ in range(12):
        nxt = []
        for s in frontier:
            for t, _ in enabled(s, cfg, programs):
                if t.kind == "RELEASE" and t.related is not None:
                    seen_handoff = True
                    woken = t.related
                    ns = t.next_state
                    instr = programs[woken][ns.pc[woken]] if ns.pc[woken] < len(programs[woken]) else None
                    assert not (instr is not None and instr[0] == "ACQUIRE" and t.obj == ("LOCK", instr[1])), (
                        "woken thread's pc still points at the ACQUIRE it was handed"
                    )
                if t.next_state not in seen:
                    seen.add(t.next_state)
                    nxt.append(t.next_state)
        frontier = nxt
    assert seen_handoff, "no handoff reached — witness vacuous"


def test_no_self_wait_reachable_c0a_horizon_12():
    """Exact enumeration: no endpoint state to horizon 12 has a lock owner
    queued on its own lock (audit: mass 1/8 at T=10, 11/32 at T=12)."""
    cfg, programs = WorldConfig.c0a(), c0a_programs()
    for T in (10, 12):
        bad = sum((p for _, p, f in paths(cfg, programs, T) if _self_wait(f)), Fraction(0))
        assert bad == 0, f"self-wait mass {bad} at T={T}"


def test_no_self_wait_reachable_c1_first_contamination_tick():
    cfg, programs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    bad = sum((p for _, p, f in paths(cfg, programs, 11) if _self_wait(f)), Fraction(0))
    assert bad == 0, f"self-wait mass {bad} at T=11 (audit measured 1/384 at 11–12)"


def test_no_self_wait_transition_anywhere_c0a():
    assert _first_self_wait_transition(WorldConfig.c0a(), c0a_programs(), 12) is None


def test_check_invariants_flags_self_wait():
    """I6 (deadlock): an owner queued on its own lock must be reported."""
    from dataclasses import replace
    from yupi.state import lock_blocked
    cfg, programs = WorldConfig.c0a(), c0a_programs()
    s = initial_state(cfg)
    # Synthesize the audit's bad state shape: thread 0 owns lock 0 AND waits on it.
    bad = replace(
        s,
        lock_owner=(0,) + s.lock_owner[1:],
        lock_wq=((0,),) + s.lock_wq[1:],
        status=(lock_blocked(0),) + s.status[1:],
        running=s.running - {0},
    )
    assert "I6" in check_invariants(bad, cfg)


def test_sample_episode_emits_exactly_horizon_records():
    """Statute §2: exactly T_ep transition records, absorbing IDLE tail
    (audit: sample_episode returned 11 of 40 for this seed)."""
    cfg, programs = WorldConfig.c0b("fifo"), c0b_programs()
    episode = sample_episode(cfg, programs, 40, 0)
    assert len(episode) == 40
    # Once all threads terminate, every remaining record is IDLE.
    terminated_at = None
    for i, (t, r) in enumerate(episode):
        if all(st == TERMINATED for st in t.next_state.status) and terminated_at is None:
            terminated_at = i
        if terminated_at is not None and i > terminated_at:
            assert r.kind == "IDLE"
    assert terminated_at is not None and terminated_at < 39


def test_validate_lock_order_rejects_unreleased_lock():
    """Finding 10: a program ending while holding a lock is outside the
    declared machine (I3/I6) and must be rejected."""
    assert not validate_lock_order(((("ACQUIRE", 0),),))
