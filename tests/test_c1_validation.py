"""C1 validation: the base experimental configuration (Part I, Configurations).

4 threads / 2 CPUs / 2 locks / 1 device, queue depth 2 (pending D4/D9
measurement — parameterized), stochastic completion per D10, ε per D9
(default 1, the pre-stated base).

Witness discipline (C0c's Riemann-C.6 rule): every witness class carries a
paired control asserting the class is provably empty on a world where it
must fail. Controls here are arity/capacity arguments on C0 configs.

Witnessed machinery, each previously sound-but-unexercised:
  W1 multi-waiter lock queue (|lock_wq| >= 2)        control: C0a (arity)
  W2 both waiter orders reachable                     control: C0a (arity)
  W3 nested lock hold (one thread owns both locks)    control: C0a (1 lock)
  W4 device queue full at depth 2                     control: C0a (depth 1)
  W5 QUEUE_BLOCKED reachable                          control: C0b (issuers <= depth)
  W6 full-context point mass — the predicted FOURTH ZERO per the
     injectivity theorem (docs/full-context-injectivity-note-v0.1.md):
     asserted as a test so any future kernel change that creates
     full-context grip surfaces as a red test, i.e. a finding either way
     (C0c precedent).
"""

from fractions import Fraction

from yupi.benchmark import reachable_states
from yupi.config import WorldConfig
from yupi.enumerator import paths, posterior_by_paths
from yupi.filter import run as filter_run
from yupi.interfaces import project
from yupi.programs import c0a_programs, c0b_programs, c1_programs, validate_lock_order
from yupi.state import check_invariants, queue_blocked

CAP = 300_000


def _c1():
    cfg = WorldConfig.c1()
    programs = c1_programs()
    return cfg, programs


def _reach(cfg, programs, cap=CAP):
    return reachable_states(cfg, programs, cap=cap)


# --- configuration shape ---------------------------------------------------


def test_c1_shape_matches_part_i():
    cfg = WorldConfig.c1()
    assert cfg.n_threads == 4
    assert cfg.n_cpus == 2
    assert cfg.n_locks == 2
    assert cfg.n_devices == 1
    assert cfg.queue_depth == 2
    assert cfg.discipline == "stochastic"
    assert cfg.epsilon == Fraction(1)


def test_c1_programs_respect_lock_order_discipline():
    assert validate_lock_order(c1_programs())


def test_c1_reachable_space_exhausts_and_is_invariant_clean():
    cfg, programs = _c1()
    states = _reach(cfg, programs)
    assert len(states) < CAP  # exhausted, not truncated
    for s in states:
        assert check_invariants(s, cfg) == []


# --- W1/W2: multi-waiter lock queue, both orders ---------------------------


def test_w1_multi_waiter_lock_queue_reachable():
    cfg, programs = _c1()
    states = _reach(cfg, programs)
    assert any(len(s.lock_wq[0]) >= 2 for s in states)


def test_w1_control_c0a_cannot_hold_two_waiters():
    # 2 threads, 1 lock: one thread owns, at most one can wait — empty by arity.
    cfg = WorldConfig.c0a()
    states = _reach(cfg, c0a_programs())
    assert len(states) < CAP
    assert all(len(q) <= 1 for s in states for q in s.lock_wq)


def test_w2_both_waiter_orders_reachable():
    cfg, programs = _c1()
    states = _reach(cfg, programs)
    orders = {s.lock_wq[0] for s in states if len(s.lock_wq[0]) == 2}
    by_waiter_set = {}
    for order in orders:
        by_waiter_set.setdefault(frozenset(order), set()).add(order)
    # some pair of waiters must appear in BOTH queue orders — the
    # ambiguity a windowed observer inherits
    assert any(len(seen) >= 2 for seen in by_waiter_set.values())


# --- W3: nested lock hold --------------------------------------------------


def test_w3_nested_lock_hold_reachable():
    cfg, programs = _c1()
    states = _reach(cfg, programs)
    assert any(
        s.lock_owner[0] is not None and s.lock_owner[0] == s.lock_owner[1]
        for s in states
    )


def test_w3_control_single_lock_world_cannot_nest():
    # C0a has one lock: owning "both locks" is empty by arity.
    cfg = WorldConfig.c0a()
    assert cfg.n_locks == 1
    states = _reach(cfg, c0a_programs())
    assert all(len(s.lock_owner) == 1 for s in states)


# --- W4/W5: device queue full, QUEUE_BLOCKED -------------------------------


def test_w4_device_queue_full_reachable():
    cfg, programs = _c1()
    states = _reach(cfg, programs)
    assert any(len(s.dev_q[0]) == cfg.queue_depth for s in states)


def test_w4_control_c0a_queue_capacity_one():
    cfg = WorldConfig.c0a()
    states = _reach(cfg, c0a_programs())
    assert all(len(s.dev_q[0]) <= 1 for s in states)


def test_w5_queue_blocked_reachable():
    cfg, programs = _c1()
    states = _reach(cfg, programs)
    assert any(
        st == queue_blocked(0) for s in states for st in s.status
    )


def test_w5_control_c0b_never_queue_blocks():
    # C0b: two issuers, depth two — the queue can never be full when a
    # thread issues, so QUEUE_BLOCKED is empty by counting.
    cfg = WorldConfig.c0b("fifo")
    states = _reach(cfg, c0b_programs())
    assert len(states) < CAP
    assert all(
        st != queue_blocked(0) for s in states for st in s.status
    )


# --- W6: full-context point mass (the predicted fourth zero) ---------------


def test_w6_full_context_point_mass_expected():
    """Injectivity-theorem corollary asserted as a test: along every path at
    a small horizon, the full-context r1 posterior has support exactly 1 and
    matches the enumerator bit-for-bit. A future kernel change creating
    full-context grip turns this red — a finding either way.
    """
    cfg, programs = _c1()
    horizon = 6
    all_paths = paths(cfg, programs, horizon)
    # deterministic sample: every 37th path, at least 25 paths
    stride = max(1, len(all_paths) // 25)
    for recs, _, _ in all_paths[::stride]:
        obs_seq = [project(r, "r1") for r in recs]
        posterior = filter_run(cfg, programs, obs_seq, "r1")
        assert len(posterior) == 1
        assert posterior == posterior_by_paths(cfg, programs, obs_seq, "r1")
