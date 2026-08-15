"""Query layer — Part I §"Queries" Q1–Q5 as pure functions of State.

Firewall placement: queries are WORLD DEFINITION (functions of the state
tuple), so they sit on the shared side like `state`/`kernel`/`records`.
No posterior computation lives here; `pushforward` is a pure map of a
belief through a function, applied identically to whichever path
produced the belief.

Definitions (day seven, 2026-08-15; each is a decision, recorded):
- Q1[L]  ownership: owner of lock L, or None if free.
- Q2[T]  runnability: status TAG of thread T — RUNNABLE / RUNNING /
         LOCK_BLOCKED / IO_BLOCKED / QUEUE_BLOCKED / TERMINATED (class
         only; the tagged argument is dropped, per the statute wording).
- Q3[D]  in-flight: issuing threads at device D in queue order.
         THREAD-identified — under I5 (≤1 request per thread) the request
         IS the thread's request. Q3ids[D] carries (thread, req_id) pairs
         as a diagnostic of what lineage adds beyond thread identity.
- Q4[L]  next-wake: the thread a RELEASE of L would hand off to (FIFO
         head of L's wait queue), or None. Deterministic under the
         kernel's direct-handoff RELEASE; the completion-side wake is a
         predictive query (stochastic under D10) and is NOT modeled here.
- Q5     relational, name-free: the set of (blocked, running) pairs
         where `blocked` is LOCK_BLOCKED on a lock owned by `running`
         and `running` is on a CPU. Empty set when no such pair exists.
"""

from fractions import Fraction
from math import log2
from typing import Callable, Dict, FrozenSet, Hashable, List, Optional, Tuple

from yupi.config import WorldConfig
from yupi.state import State

Belief = Dict[State, Fraction]
Query = Callable[[State], Hashable]


def q1_owner(state: State, l: int) -> Optional[int]:
    return state.lock_owner[l]


def q2_status(state: State, i: int) -> str:
    return state.status[i][0]


def q3_inflight(state: State, d: int) -> Tuple[int, ...]:
    return tuple(t for t, _ in state.dev_q[d])


def q3_inflight_ids(state: State, d: int) -> Tuple[Tuple[int, int], ...]:
    return tuple(state.dev_q[d])


def q4_next_release_wake(state: State, l: int) -> Optional[int]:
    wq = state.lock_wq[l]
    return wq[0] if wq else None


def q5_relation(state: State) -> FrozenSet[Tuple[int, int]]:
    pairs = set()
    for b, st in enumerate(state.status):
        if st[0] == "LOCK_BLOCKED":
            owner = state.lock_owner[st[1]]
            if owner is not None and owner in state.running:
                pairs.add((b, owner))
    return frozenset(pairs)


def all_queries(cfg: WorldConfig) -> List[Tuple[str, Query]]:
    """Every query instance the configuration admits, named."""
    qs: List[Tuple[str, Query]] = []
    for l in range(cfg.n_locks):
        qs.append((f"Q1[L{l}]", lambda s, l=l: q1_owner(s, l)))
    for i in range(cfg.n_threads):
        qs.append((f"Q2[T{i}]", lambda s, i=i: q2_status(s, i)))
    for d in range(cfg.n_devices):
        qs.append((f"Q3[D{d}]", lambda s, d=d: q3_inflight(s, d)))
        qs.append((f"Q3ids[D{d}]", lambda s, d=d: q3_inflight_ids(s, d)))
    for l in range(cfg.n_locks):
        qs.append((f"Q4[L{l}]", lambda s, l=l: q4_next_release_wake(s, l)))
    qs.append(("Q5", q5_relation))
    return qs


def pushforward(belief: Belief, query: Query) -> Dict[Hashable, Fraction]:
    """Exact distribution over query answers induced by a state belief."""
    out: Dict[Hashable, Fraction] = {}
    for s, m in belief.items():
        if m == 0:
            continue
        a = query(s)
        out[a] = out.get(a, Fraction(0)) + m
    return out


def entropy_bits(dist: Dict[Hashable, Fraction]) -> float:
    """Shannon entropy in bits of an exact-probability distribution."""
    return -sum(float(p) * log2(float(p)) for p in dist.values() if p > 0)


def state_entropy_bits(belief: Belief) -> float:
    return entropy_bits(belief)
