"""Query layer — Part II §5 queries as pure functions of State.

Firewall placement: queries are WORLD DEFINITION (functions of the state
tuple), so they sit on the shared side like `state`/`kernel`/`records`.
No posterior computation lives here; `pushforward` is a pure map of a
belief through a function, applied identically to whichever path
produced the belief.

Statutory (Part II §5) vs proxy — labels as emitted by `all_queries`:
- Q1[L]      STATUTORY. own[L] ∈ threads ∪ {FREE}; None encodes FREE.
- Q2[T]      STATUTORY. st[T]'s six-value tag (RUNNABLE / RUNNING /
             LOCK_BLOCKED / IO_BLOCKED / QUEUE_BLOCKED / TERMINATED).
- Q3[D]      STATUTORY. Ordered in-flight list of (thread, request_id).
- Q3thr[D]   PROXY (day seven). Issuing threads only, in queue order —
             what Q3 becomes after quotienting request-id identity out;
             under I5 the request IS the thread's request, but the
             statute's answer carries the id, so this is not Q3.
- Q4proxy[L] PROXY (day seven). The FIFO head of L's wait queue — the
             thread a RELEASE of L would hand off to now. Statutory Q4
             (the thread directly woken by the first wake-causing
             transition in (t, t+W], completions included; a forward
             sum with an irreducible predictive term) is UNIMPLEMENTED.
- Q5[Tb,Tr]  STATUTORY. Predicate over an ordered pair: ∃l: Tb ∈ wq[l]
             ∧ own[l] = Tr ∧ Tr ∈ run.
- Q5joint    PROXY (day seven). The set of all currently-true Q5 pairs;
             its entropy is a joint quantity, not any single predicate's.

v0.1 of this module (commit 0742d1d) labeled Q3thr as "Q3", Q3 as
"Q3ids", Q4proxy as "Q4", Q5joint as "Q5", and had no per-pair Q5; the
raw JSONs of that commit carry those labels. Relabeled after the day-seven
truthsayer round (Part II §5 read; the note's v0.2 block).
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


def q5_pair(state: State, b: int, r: int) -> bool:
    st = state.status[b]
    return (st[0] == "LOCK_BLOCKED" and state.lock_owner[st[1]] == r
            and r in state.running)


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
        qs.append((f"Q3[D{d}]", lambda s, d=d: q3_inflight_ids(s, d)))
        qs.append((f"Q3thr[D{d}]", lambda s, d=d: q3_inflight(s, d)))
    for l in range(cfg.n_locks):
        qs.append((f"Q4proxy[L{l}]", lambda s, l=l: q4_next_release_wake(s, l)))
    for b in range(cfg.n_threads):
        for r in range(cfg.n_threads):
            if b != r:
                qs.append((f"Q5[T{b},T{r}]", lambda s, b=b, r=r: q5_pair(s, b, r)))
    qs.append(("Q5joint", q5_relation))
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
