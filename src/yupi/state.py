from dataclasses import dataclass
from typing import Tuple, FrozenSet, Union
from yupi.config import WorldConfig


# Status tagged tuples
RUNNABLE = ("RUNNABLE",)
RUNNING = ("RUNNING",)
TERMINATED = ("TERMINATED",)


def lock_blocked(l: int) -> Tuple[str, int]:
    """Create a lock-blocked status for lock l."""
    return ("LOCK_BLOCKED", l)


def io_blocked(r: int) -> Tuple[str, int]:
    """Create an I/O-blocked status for request r."""
    return ("IO_BLOCKED", r)


def queue_blocked(d: int) -> Tuple[str, int]:
    """Create a queue-blocked status for device d."""
    return ("QUEUE_BLOCKED", d)


@dataclass(frozen=True)
class State:
    """Immutable state tuple for the Yupana simulator.

    Captures the complete state of all threads, their program counters,
    execution status, and the state of synchronization primitives
    (locks and device queues).

    Fields:
        pc: tuple of program counters, one per thread (indices 0..n_threads-1)
        status: tuple of status values, one per thread (each a tagged tuple)
        running: frozenset of thread IDs currently on CPU
        lock_owner: tuple of thread IDs (or None) owning each lock
        lock_wq: tuple of queues; lock_wq[l] = tuple of thread IDs waiting on lock l
        dev_q: tuple of queues; dev_q[d] = tuple of (thread_id, req_id) pairs in device d's queue
        rr_cursor: current round-robin cursor for CPU scheduling
    """
    pc: Tuple[int, ...]
    status: Tuple[Tuple, ...]
    running: FrozenSet[int]
    lock_owner: Tuple[Union[int, None], ...]
    lock_wq: Tuple[Tuple[int, ...], ...]
    dev_q: Tuple[Tuple[Tuple[int, int], ...], ...]
    rr_cursor: int


def initial_state(cfg: WorldConfig) -> State:
    """Construct the initial state for a configuration.

    All threads start RUNNABLE with pc=0, no thread is running,
    all locks are free (owner=None), all queues are empty, rr_cursor=0.
    """
    return State(
        pc=tuple(0 for _ in range(cfg.n_threads)),
        status=tuple(RUNNABLE for _ in range(cfg.n_threads)),
        running=frozenset(),
        lock_owner=tuple(None for _ in range(cfg.n_locks)),
        lock_wq=tuple(tuple() for _ in range(cfg.n_locks)),
        dev_q=tuple(tuple() for _ in range(cfg.n_devices)),
        rr_cursor=0
    )


def check_invariants(state: State, cfg: WorldConfig) -> list[str]:
    """Check all state invariants and return list of violated invariant names.

    I1: The running set must contain exactly those threads with RUNNING status.
    I2: A thread appears in at most one of: the running set, one lock wait
        queue, the in-flight relation (statute §1 — mutual exclusion across
        all three, strengthened 2026-08-20 round two: the earlier check only
        compared lock_wq against dev_q, so a RUNNING thread queued on a lock
        passed).
    I3: Lock owners must not have TERMINATED status.
    I4: All in-flight request IDs must be distinct.
    I5: At most one in-flight request per thread.
    I6: No blocked cycle in the lock wait-for graph (statute §1: lock-cycle
        deadlock unreachable). Detects any cycle thread→owner(lock it waits
        on)→…; the self-wait state of the 2026-08-20 direct-handoff audit is
        the 1-cycle. (Round two: the first version checked only the 1-cycle
        while carrying the general name.)

    Returns:
        List of invariant names that are violated (empty if all valid).
    """
    violations = []

    # I1: running set ↔ RUNNING status
    running_from_status = frozenset(
        i for i in range(cfg.n_threads)
        if state.status[i] == RUNNING
    )
    if state.running != running_from_status:
        violations.append("I1")

    # I2: mutual exclusion across running set, lock wait queues, in-flight
    for thread_id in range(cfg.n_threads):
        n_wq = sum(1 for lock_q in state.lock_wq if thread_id in lock_q)
        in_flight = sum(
            1 for dev_q in state.dev_q for tid, _ in dev_q if tid == thread_id
        )
        memberships = (thread_id in state.running) + (n_wq > 0) + (in_flight > 0)
        if memberships > 1 or n_wq > 1:
            violations.append("I2")
            break

    # I3: lock owners must not be TERMINATED
    for lock_id, owner in enumerate(state.lock_owner):
        if owner is not None and state.status[owner] == TERMINATED:
            violations.append("I3")
            break

    # I4: all in-flight request IDs must be distinct
    all_req_ids = []
    for dev_q in state.dev_q:
        for _, req_id in dev_q:
            all_req_ids.append(req_id)
    if len(all_req_ids) != len(set(all_req_ids)):
        violations.append("I4")

    # I5: at most one in-flight request per thread
    thread_req_count = {}
    for dev_q in state.dev_q:
        for thread_id, _ in dev_q:
            thread_req_count[thread_id] = thread_req_count.get(thread_id, 0) + 1
    for count in thread_req_count.values():
        if count > 1:
            violations.append("I5")
            break

    # I6: no blocked cycle in the lock wait-for graph (self-wait = 1-cycle)
    waits_on = {}  # thread -> owner of the lock it waits on
    for lock_id, wq in enumerate(state.lock_wq):
        owner = state.lock_owner[lock_id]
        for t in wq:
            if owner is not None:
                waits_on[t] = owner
    for start in waits_on:
        seen_t, cur = set(), start
        while cur in waits_on and cur not in seen_t:
            seen_t.add(cur)
            cur = waits_on[cur]
        if cur in seen_t:
            violations.append("I6")
            break

    return violations
