"""Query layer (Part II §5 Q1–Q5, statutory and proxy): pure functions of
State, pushforward of a belief through a query, exact-probability entropy.

Design rule: queries are WORLD DEFINITION (functions of the state tuple),
so they may sit on the shared side of the two-path firewall like
`state`/`kernel`. No posterior computation lives here.
"""

from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.state import (
    RUNNABLE, RUNNING, TERMINATED, State, initial_state, io_blocked,
    lock_blocked, queue_blocked,
)
from yupi.queries import (
    all_queries, entropy_bits, pushforward, q1_owner, q2_status,
    q3_inflight, q3_inflight_ids, q4_next_release_wake, q5_pair,
    q5_relation, state_entropy_bits,
)


def _cfg():
    return WorldConfig.c1()


def _busy_state():
    """4T/2CPU/2L/1D. t0 RUNNING owns L0; t1 LOCK_BLOCKED on L0; t2 RUNNING
    IO in flight? no — t2 running; t3 IO_BLOCKED with req 1 while a
    hidden earlier request from t2... keep it simple and legal-looking:
    dev_q = ((3,1),) meaning t3 issued and got id 1 (id 0 recycled or
    in flight elsewhere — invariants are not asserted here; queries are
    pure functions and must not depend on reachability).
    """
    return State(
        pc=(1, 1, 2, 3),
        status=(RUNNING, lock_blocked(0), RUNNING, io_blocked(1)),
        running=frozenset({0, 2}),
        lock_owner=(0, None),
        lock_wq=((1,), ()),
        dev_q=(((3, 1),),),
        rr_cursor=1,
    )


def test_initial_state_answers():
    cfg = _cfg()
    s = initial_state(cfg)
    assert q1_owner(s, 0) is None and q1_owner(s, 1) is None
    assert all(q2_status(s, i) == "RUNNABLE" for i in range(4))
    assert q3_inflight(s, 0) == ()
    assert q3_inflight_ids(s, 0) == ()
    assert q4_next_release_wake(s, 0) is None
    assert q5_relation(s) == frozenset()


def test_busy_state_answers():
    s = _busy_state()
    assert q1_owner(s, 0) == 0
    assert q2_status(s, 1) == "LOCK_BLOCKED"
    assert q2_status(s, 3) == "IO_BLOCKED"
    assert q2_status(s, 0) == "RUNNING"
    # Q3 is thread-identified (I5): issuing threads in queue order.
    assert q3_inflight(s, 0) == (3,)
    assert q3_inflight_ids(s, 0) == ((3, 1),)
    # RELEASE hands off to the FIFO head.
    assert q4_next_release_wake(s, 0) == 1
    # t1 waits on L0, owned by running t0.
    assert q5_relation(s) == frozenset({(1, 0)})
    assert q5_pair(s, 1, 0) is True
    assert q5_pair(s, 0, 1) is False and q5_pair(s, 1, 2) is False


def test_all_queries_enumerates_per_entity():
    cfg = _cfg()
    qs = all_queries(cfg)
    names = [n for n, _ in qs]
    assert "Q1[L0]" in names and "Q1[L1]" in names
    assert "Q2[T3]" in names
    assert "Q3[D0]" in names and "Q3thr[D0]" in names
    assert "Q4proxy[L1]" in names
    assert "Q5[T1,T0]" in names and "Q5[T0,T1]" in names
    assert "Q5joint" in names
    assert len([n for n in names if n.startswith("Q5[")]) == 12
    s = initial_state(cfg)
    for _, fn in qs:
        fn(s)  # every query is total on states


def test_pushforward_and_entropy():
    s0 = _busy_state()
    s1 = State(
        pc=s0.pc, status=s0.status, running=s0.running,
        lock_owner=(2, None), lock_wq=s0.lock_wq, dev_q=s0.dev_q,
        rr_cursor=s0.rr_cursor,
    )
    belief = {s0: Fraction(1, 2), s1: Fraction(1, 2)}
    dist = pushforward(belief, lambda s: q1_owner(s, 0))
    assert dist == {0: Fraction(1, 2), 2: Fraction(1, 2)}
    assert sum(dist.values()) == 1
    assert entropy_bits(dist) == pytest.approx(1.0)
    # A query that does not see the difference: point mass, zero bits.
    dist_l1 = pushforward(belief, lambda s: q1_owner(s, 1))
    assert dist_l1 == {None: Fraction(1)}
    assert entropy_bits(dist_l1) == 0.0
    # Data processing: H(query) <= H(state).
    assert state_entropy_bits(belief) == pytest.approx(1.0)
    assert entropy_bits(dist) <= state_entropy_bits(belief) + 1e-12
