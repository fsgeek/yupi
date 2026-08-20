"""Transition kernel: exact probability distribution over next transitions.

Implements Part II §3 of docs/yupana-m1-part2-semantics-draft.md. Every
`enabled()` call returns a list of (Transition, Fraction) pairs whose
probabilities sum to exactly Fraction(1). No floats anywhere in this module.

CPU-slot occupancy is one-tick (transient), not sticky across instructions:
DISPATCH puts exactly one thread into `running` for the tick that follows;
after that thread executes one instruction, it leaves `running` again --
back to RUNNABLE (needing a fresh DISPATCH for its next instruction) unless
that instruction blocked it (already leaves running per §3.3) or it was the
program's last instruction (TERMINATED). §3.3's text only states "leave
run" for the blocking cases, which read alone would suggest a thread stays
RUNNING across multiple non-blocking instructions ("sticky"). That reading
is rejected here: under sticky with C0a's config (n_cpus=1), thread 0's
program releases lock 0 (index 2) before its only blocking instruction,
IO(0) (index 3), so thread 1 can never observe the lock held while it has
the CPU -- lock contention, the documented purpose of c0a_programs() (Part
II §9 witness 2; plan Task 2 "exercises lock contention, blocking, I/O"),
becomes unreachable. §3.2's own rationale ("interleaving entropy source --
continuous through the episode, not only at scheduling boundaries") only
holds if dispatch recurs every tick, which requires transient occupancy.
This is a gap in Part II §3.3's wording, not a free implementation choice;
flagged for a doc revision.
"""

from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Optional, Tuple, List

from yupi.config import WorldConfig
from yupi.state import (
    State,
    RUNNABLE,
    RUNNING,
    TERMINATED,
    lock_blocked,
    io_blocked,
    queue_blocked,
)


class KernelInvariantViolation(RuntimeError):
    """A statute precondition failed at a transition site (2026-08-20).

    Raised, not assert-ed, so `python -O` cannot strip it. Because the
    enumerator exhaustively walks every path, any reachable violation fires
    deterministically during validation: an embedded invariant here is a
    horizon-bounded proof, not a spot check. A firing is a falsifier per
    Part II §9 — investigate the kernel or the statute; never catch and
    continue. The direct-handoff defect would have raised here (a thread
    blocking on a lock it already owns) on day one of its reachability.
    """


@dataclass(frozen=True)
class Transition:
    """One recorded transition: the record fields plus the resulting state.

    kind: one of COMPLETION, DISPATCH, STEP, ACQUIRE, BLOCK, RELEASE,
          IO_ISSUE, IDLE.
    actor: the transitioning thread id, or None (IDLE has no actor).
    obj: ("LOCK", l) or ("DEV", d), or None when the transition kind has
         no natural object (e.g. STEP, DISPATCH, IDLE).
    related: current owner (on BLOCK for a lock), woken thread (on RELEASE),
             or None.
    lineage: request id (completion / IO_ISSUE), or None.
    next_state: the State reached by taking this transition.
    """

    kind: str
    actor: Optional[int]
    obj: Optional[Tuple[str, int]]
    related: Optional[int]
    lineage: Optional[int]
    next_state: State


def _program_len(programs, i: int) -> int:
    return len(programs[i])


def _epsilon_policy(
    candidates: List[int], cursor: int, eps: Fraction, n_threads: int
) -> List[Tuple[int, Fraction, int]]:
    """ε-policy over a candidate list: uniform-among-candidates with total
    probability eps, plus a single round-robin pick with probability 1-eps.

    Returns a list of (choice, probability, new_cursor) triples.

    CRITICAL invariant (fixed after review — was previously violated): the
    cursor advances past the picked thread on BOTH mixture components, not
    just the round-robin one, and every returned cursor is canonicalized mod
    n_threads. Previously the uniform entries kept the cursor unchanged while
    only the round-robin entry advanced it, so a uniform pick and a
    round-robin pick landing on the *same* thread produced two Transitions
    differing only in rr_cursor -- they never merged, and the reachable
    cursor space was unbounded (any thread index the RR pick had ever
    stopped at), blowing up the exact posterior support (measured: 198 vs 72
    reachable C0a states at eps=1/2, a 2.75x blowup against the committed
    support bound). With every choice advancing the cursor identically
    (new_cursor = (chosen + 1) % n_threads), the uniform and round-robin
    components picking the same thread now produce IDENTICAL next_states and
    merge via `_merge`, and the cursor's reachable range collapses to
    {0, ..., n_threads-1} regardless of mixture path.

    candidates must be non-empty and sorted (callers pass sorted lists). The
    round-robin pick is the candidate at-or-after `cursor` (wrapping).
    At eps == 1, the round-robin contribution is zero-weight and omitted, and
    every uniform entry returns the INCOMING cursor unchanged (per §3.1: "at
    the ε=1 base the cursor is absent from the effective state") -- the
    cursor is then never written at ε=1, stays at its initial value forever,
    and is truly absent from the dynamics rather than merely absent from the
    round-robin-only advancement.
    """
    assert candidates, "_epsilon_policy requires a non-empty candidate list"
    assert n_threads > 0
    n = len(candidates)
    results: List[Tuple[int, Fraction, int]] = []

    if eps == Fraction(1):
        share = eps / n
        for c in candidates:
            results.append((c, share, cursor))
        return results

    if eps > 0:
        share = eps / n
        for c in candidates:
            results.append((c, share, (c + 1) % n_threads))

    if eps < 1:
        # Round-robin: the first candidate at-or-after cursor, wrapping.
        rr_choice = None
        for c in candidates:
            if c >= cursor:
                rr_choice = c
                break
        if rr_choice is None:
            rr_choice = candidates[0]
        results.append((rr_choice, Fraction(1) - eps, (rr_choice + 1) % n_threads))

    return results


def _merge(pairs: List[Tuple[Transition, Fraction]]) -> List[Tuple[Transition, Fraction]]:
    """Merge duplicate (transition, prob) pairs by summing probabilities.

    Two transitions are the "same" for merging purposes iff every field
    (including next_state) is equal — Transition is a frozen dataclass so
    it is hashable/eq-comparable as long as next_state is hashable, which
    State is (frozen dataclass of tuples/frozensets).
    """
    merged: dict = {}
    order: List[Transition] = []
    for t, p in pairs:
        if t in merged:
            merged[t] += p
        else:
            merged[t] = p
            order.append(t)
    return [(t, merged[t]) for t in order]


def _completion_candidates(state: State, cfg: WorldConfig) -> List[Tuple[int, int, int]]:
    """Return (device, thread, req_id) triples eligible to depart this tick,
    per discipline (§3.4):

    - fifo: the head of each nonempty device queue (one candidate per
      nonempty device).
    - stochastic: every in-flight request on every nonempty device queue.
    """
    candidates: List[Tuple[int, int, int]] = []
    for d, q in enumerate(state.dev_q):
        if not q:
            continue
        if cfg.discipline == "fifo":
            thread, req_id = q[0]
            candidates.append((d, thread, req_id))
        elif cfg.discipline == "stochastic":
            for thread, req_id in q:
                candidates.append((d, thread, req_id))
        else:
            raise ValueError(f"unknown discipline: {cfg.discipline}")
    return candidates


def _completion_transitions(
    state: State, cfg: WorldConfig, programs
) -> List[Tuple[Transition, Fraction]]:
    """Stage A completion branch (§3.4): total probability mass `p` split
    across all completion candidates. fifo: one candidate per nonempty
    device (the head), each carrying an equal share of p. stochastic: every
    in-flight request is a candidate, each carrying p/n_total (n_total =
    total in-flight requests across all nonempty device queues) — this
    reduces to the single-device p/n rule of §3.4 whenever n_devices == 1,
    which is every M1 configuration.

    The issuer normally wakes to RUNNABLE. But IO_ISSUE always advances pc
    past the instruction before blocking (§3.3), so an issuer whose IO was
    its program's last instruction has pc == len(program) already: on
    completion there is no further instruction to dispatch, so it
    terminates instead of becoming RUNNABLE/dispatchable (which would leave
    a TERMINATED-looking pc but a schedulable status — and would crash
    dispatch on an out-of-range pc).
    """
    candidates = _completion_candidates(state, cfg)
    if not candidates:
        return []

    p = cfg.completion_p
    share = p / len(candidates)

    out: List[Tuple[Transition, Fraction]] = []
    for d, thread, req_id in candidates:
        new_dev_q = list(state.dev_q)
        new_dev_q[d] = tuple(
            (t, r) for (t, r) in state.dev_q[d] if not (t == thread and r == req_id)
        )

        new_status = list(state.status)
        # issuer wakes: IO_BLOCKED -> RUNNABLE, unless its program is
        # already exhausted (IO was its last instruction) -> TERMINATED.
        if state.pc[thread] == _program_len(programs, thread):
            new_status[thread] = TERMINATED
        else:
            new_status[thread] = RUNNABLE

        # wake-all: every QUEUE_BLOCKED thread on device d also -> RUNNABLE
        for i, st in enumerate(new_status):
            if st == queue_blocked(d):
                new_status[i] = RUNNABLE

        next_state = replace(
            state,
            status=tuple(new_status),
            dev_q=tuple(new_dev_q),
        )

        out.append(
            (
                Transition(
                    kind="COMPLETION",
                    actor=thread,
                    obj=("DEV", d),
                    related=None,
                    lineage=req_id,
                    next_state=next_state,
                ),
                share,
            )
        )
    return out


def _runnable_threads(state: State) -> List[int]:
    return sorted(i for i, st in enumerate(state.status) if st == RUNNABLE)


def _dispatch_transitions(
    state: State, cfg: WorldConfig
) -> List[Tuple[Transition, Fraction]]:
    """§3.1: dispatch a runnable thread onto a free CPU slot, chosen by the
    ε-policy over the runnable set. Priority over execution steps.
    """
    if len(state.running) >= cfg.n_cpus:
        return []
    runnable = _runnable_threads(state)
    if not runnable:
        return []

    picks = _epsilon_policy(runnable, state.rr_cursor, cfg.epsilon, cfg.n_threads)
    out: List[Tuple[Transition, Fraction]] = []
    for thread, prob, new_cursor in picks:
        new_status = list(state.status)
        new_status[thread] = RUNNING
        next_state = replace(
            state,
            status=tuple(new_status),
            running=state.running | {thread},
            rr_cursor=new_cursor,
        )
        out.append(
            (
                Transition(
                    kind="DISPATCH",
                    actor=thread,
                    obj=None,
                    related=None,
                    lineage=None,
                    next_state=next_state,
                ),
                prob,
            )
        )
    return out


def _lowest_free_request_id(state: State, cfg: WorldConfig) -> int:
    in_flight = {r for q in state.dev_q for (_, r) in q}
    for r in range(cfg.req_pool):
        if r not in in_flight:
            return r
    raise RuntimeError("no free request id available (req_pool exhausted)")


def _execute_one(
    thread: int, state: State, cfg: WorldConfig, programs
) -> Transition:
    """§3.2-3.3: execute thread's current instruction, building the single
    resulting Transition. Caller supplies the probability.
    """
    pc = state.pc[thread]
    instr = programs[thread][pc]
    kind = instr[0]

    if kind == "COMPUTE":
        new_pc = list(state.pc)
        new_pc[thread] = pc + 1
        terminated = new_pc[thread] == _program_len(programs, thread)

        new_status = list(state.status)
        # One-tick CPU occupancy (see module docstring / _execute_one docstring):
        # a thread that executes a non-blocking instruction always leaves
        # `running` afterward -- TERMINATED if that was its last instruction,
        # otherwise back to RUNNABLE, requiring a fresh DISPATCH before its
        # next instruction. Only a still-blocked/still-running thread stays
        # off this path.
        if terminated:
            new_status[thread] = TERMINATED
        else:
            new_status[thread] = RUNNABLE
        new_running = state.running - {thread}
        next_state = replace(
            state,
            pc=tuple(new_pc),
            status=tuple(new_status),
            running=new_running,
        )
        return Transition("STEP", thread, None, None, None, next_state)

    if kind == "ACQUIRE":
        l = instr[1]
        owner = state.lock_owner[l]
        if owner is None:
            new_pc = list(state.pc)
            new_pc[thread] = pc + 1
            new_lock_owner = list(state.lock_owner)
            new_lock_owner[l] = thread

            terminated = new_pc[thread] == _program_len(programs, thread)
            new_status = list(state.status)
            if terminated:
                new_status[thread] = TERMINATED
            else:
                new_status[thread] = RUNNABLE
            new_running = state.running - {thread}

            next_state = replace(
                state,
                pc=tuple(new_pc),
                lock_owner=tuple(new_lock_owner),
                status=tuple(new_status),
                running=new_running,
            )
            return Transition("ACQUIRE", thread, ("LOCK", l), None, None, next_state)
        else:
            if owner == thread:
                raise KernelInvariantViolation(
                    f"thread {thread} blocking on lock {l} it already owns "
                    "(handoff pc defect signature, §3.3/§3.5)"
                )
            new_status = list(state.status)
            new_status[thread] = lock_blocked(l)
            new_lock_wq = list(state.lock_wq)
            new_lock_wq[l] = new_lock_wq[l] + (thread,)
            next_state = replace(
                state,
                status=tuple(new_status),
                running=state.running - {thread},
                lock_wq=tuple(new_lock_wq),
            )
            return Transition("BLOCK", thread, ("LOCK", l), owner, None, next_state)

    if kind == "RELEASE":
        l = instr[1]
        if state.lock_owner[l] != thread:
            raise KernelInvariantViolation(
                f"thread {thread} releasing lock {l} owned by "
                f"{state.lock_owner[l]} (§3.3: only the owner releases)"
            )
        new_pc = list(state.pc)
        new_pc[thread] = pc + 1
        new_lock_owner = list(state.lock_owner)
        new_lock_wq = list(state.lock_wq)

        waiters = new_lock_wq[l]
        woken = None
        if waiters:
            woken = waiters[0]
            w_pc = state.pc[woken]
            if not (w_pc < _program_len(programs, woken)
                    and programs[woken][w_pc] == ("ACQUIRE", l)):
                raise KernelInvariantViolation(
                    f"handoff head {woken} of lock {l} is not parked on "
                    f"ACQUIRE({l}) (pc={w_pc}) — wait queue corrupt"
                )
            new_lock_wq[l] = waiters[1:]
            new_lock_owner[l] = woken  # direct handoff: head owns immediately
            # §3.3/§3.5: the woken head "acquires ownership immediately" — its
            # ACQUIRE is complete, so its pc advances at handoff. (2026-08-20
            # audit: leaving pc on the ACQUIRE made the woken thread re-execute
            # it against itself and self-block behind its own lock.)
            new_pc[woken] = new_pc[woken] + 1
        else:
            new_lock_owner[l] = None

        terminated = new_pc[thread] == _program_len(programs, thread)
        new_status = list(state.status)
        if terminated:
            new_status[thread] = TERMINATED
        else:
            new_status[thread] = RUNNABLE
        new_running = state.running - {thread}
        if woken is not None:
            new_status[woken] = (
                TERMINATED if new_pc[woken] == _program_len(programs, woken)
                else RUNNABLE
            )

        next_state = replace(
            state,
            pc=tuple(new_pc),
            status=tuple(new_status),
            running=new_running,
            lock_owner=tuple(new_lock_owner),
            lock_wq=tuple(new_lock_wq),
        )
        return Transition("RELEASE", thread, ("LOCK", l), woken, None, next_state)

    if kind == "IO":
        d = instr[1]
        q = state.dev_q[d]
        if len(q) < cfg.queue_depth:
            req_id = _lowest_free_request_id(state, cfg)
            new_pc = list(state.pc)
            new_pc[thread] = pc + 1
            new_status = list(state.status)
            new_status[thread] = io_blocked(req_id)
            new_dev_q = list(state.dev_q)
            new_dev_q[d] = q + ((thread, req_id),)
            next_state = replace(
                state,
                pc=tuple(new_pc),
                status=tuple(new_status),
                running=state.running - {thread},
                dev_q=tuple(new_dev_q),
            )
            return Transition("IO_ISSUE", thread, ("DEV", d), None, req_id, next_state)
        else:
            new_status = list(state.status)
            new_status[thread] = queue_blocked(d)
            next_state = replace(
                state,
                status=tuple(new_status),
                running=state.running - {thread},
            )
            return Transition("BLOCK", thread, ("DEV", d), None, None, next_state)

    raise ValueError(f"unknown instruction kind: {kind}")


def _execution_transitions(
    state: State, cfg: WorldConfig, programs
) -> List[Tuple[Transition, Fraction]]:
    """§3.2: pick a running thread by the ε-policy and execute its
    instruction. Only reached when dispatch is not enabled (dispatch has
    priority, §3.1).
    """
    running = sorted(state.running)
    if not running:
        return []

    picks = _epsilon_policy(running, state.rr_cursor, cfg.epsilon, cfg.n_threads)
    out: List[Tuple[Transition, Fraction]] = []
    for thread, prob, new_cursor in picks:
        t = _execute_one(thread, state, cfg, programs)
        # the cursor update belongs on top of whatever _execute_one computed
        t = replace(t, next_state=replace(t.next_state, rr_cursor=new_cursor))
        out.append((t, prob))
    return out


def enabled(
    state: State, cfg: WorldConfig, programs
) -> List[Tuple[Transition, Fraction]]:
    """Exact distribution over next transitions from `state` (Part II §3).

    Every returned list's probabilities sum to exactly Fraction(1).
    """
    any_device_nonempty = any(len(q) > 0 for q in state.dev_q)
    p = cfg.completion_p if any_device_nonempty else Fraction(0)

    pairs: List[Tuple[Transition, Fraction]] = []

    if any_device_nonempty:
        completions = _completion_transitions(state, cfg, programs)
        # completions' shares already sum to p by construction
        pairs.extend(completions)

    remaining = Fraction(1) - p

    # Stage B: dispatch has priority over execution steps (§3.1).
    stage_b = _dispatch_transitions(state, cfg)
    if not stage_b:
        stage_b = _execution_transitions(state, cfg, programs)

    if stage_b:
        pairs.extend((t, prob * remaining) for t, prob in stage_b)
    elif remaining > 0:
        # §3.6: IDLE self-loop with the residual probability.
        pairs.append(
            (
                Transition("IDLE", None, None, None, None, state),
                remaining,
            )
        )

    return _merge(pairs)
