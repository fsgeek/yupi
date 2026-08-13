from fractions import Fraction
from yupi.config import WorldConfig
from yupi.state import State, initial_state, check_invariants, RUNNABLE

def test_c0a_config():
    cfg = WorldConfig.c0a()
    assert (cfg.n_threads, cfg.n_cpus, cfg.n_locks, cfg.n_devices) == (2, 1, 1, 1)
    assert cfg.queue_depth == 1 and cfg.req_pool == 2
    assert cfg.epsilon == Fraction(1) and cfg.discipline == "fifo"
    assert isinstance(cfg.completion_p, Fraction)

def test_initial_state_valid_and_hashable():
    cfg = WorldConfig.c0a()
    s = initial_state(cfg)
    assert s.pc == (0, 0) and s.status == (RUNNABLE, RUNNABLE)
    assert s.running == frozenset() and s.lock_owner == (None,)
    assert check_invariants(s, cfg) == []
    assert hash(s) == hash(initial_state(cfg))

def test_invariant_violation_detected():
    cfg = WorldConfig.c0a()
    s = initial_state(cfg)
    bad = State(pc=s.pc, status=s.status, running=frozenset({0}),  # 0 RUNNABLE but in running
                lock_owner=s.lock_owner, lock_wq=s.lock_wq, dev_q=s.dev_q, rr_cursor=0)
    assert "I1" in check_invariants(bad, cfg)
