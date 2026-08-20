from fractions import Fraction
from dataclasses import replace as replace_cfg
from yupi.config import WorldConfig
from yupi.state import initial_state, RUNNABLE, RUNNING, TERMINATED, queue_blocked
from yupi.programs import c0a_programs
from yupi.kernel import enabled

CFG, PROGS = WorldConfig.c0a(), c0a_programs()

def total(pairs): return sum(p for _, p in pairs)

def test_probabilities_always_sum_to_one():
    s = initial_state(CFG)
    frontier, seen = [s], set()
    for _ in range(200):  # BFS a few hundred reachable states
        if not frontier: break
        s = frontier.pop()
        if s in seen: continue
        seen.add(s)
        pairs = enabled(s, CFG, PROGS)
        assert total(pairs) == Fraction(1), s
        frontier.extend(t.next_state for t, _ in pairs)

def test_initial_step_is_dispatch():
    pairs = enabled(initial_state(CFG), CFG, PROGS)
    kinds = {t.kind for t, _ in pairs}
    assert kinds == {"DISPATCH"}          # empty device queue: no completion branch
    assert total(pairs) == Fraction(1)
    assert {t.actor for t, _ in pairs} == {0, 1}  # ε=1: uniform over both runnable

def test_lock_block_records_owner():
    # drive: dispatch t0, t0 acquires, dispatch t1, t1 steps COMPUTE, dispatch t1
    # again, t1 tries acquire -> BLOCK related=0
    #
    # Deviation from the brief's verbatim listing, recorded here rather than
    # silently: CPU occupancy is one-tick (transient) -- see kernel.py's module
    # docstring for why (sticky occupancy makes lock contention unreachable in
    # C0a, which contradicts c0a_programs()'s documented purpose and Part II §9
    # witness 2). Under transient occupancy, thread 1 must be re-dispatched
    # after its COMPUTE step before it can attempt ACQUIRE, so the brief's
    # five-step sequence needs a second "DISPATCH actor=1" inserted between the
    # STEP and the BLOCK; the unqualified `kind == "DISPATCH"` predicates also
    # need `actor == 1` since both dispatch points here have two runnable
    # candidates under epsilon=1 (uniform), not one. The assertion at the end
    # (BLOCK records related=owner, obj=("LOCK", 0)) is unchanged from the brief.
    s = initial_state(CFG)
    def take(s, pred):
        (t,) = [t for t, _ in enabled(s, CFG, PROGS) if pred(t)]
        return t.next_state, t
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 0)
    s, _ = take(s, lambda t: t.kind == "ACQUIRE")
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 1)
    s, _ = take(s, lambda t: t.kind == "STEP" and t.actor == 1)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 1)
    s, blk = take(s, lambda t: t.kind == "BLOCK" and t.actor == 1)
    assert blk.related == 0 and blk.obj == ("LOCK", 0)


# --- Additional tests beyond the brief, covering semantics the brief's tests don't exercise ---

def take(s, pred, cfg=CFG, progs=PROGS):
    (t,) = [t for t, _ in enabled(s, cfg, progs) if pred(t)]
    return t.next_state, t


def test_completion_wakes_issuer_and_all_queue_blocked():
    """§3.3/§3.4: a completion must wake BOTH the issuing thread (from IO_BLOCKED)
    AND every QUEUE_BLOCKED thread on that device (wake-all), in one transition.

    Build a 3-thread, depth-1 queue world so one thread issues IO (fills the
    only slot) and a second thread's IO attempt on the same device finds it
    full and goes QUEUE_BLOCKED. Then the completion transition must move
    both threads to RUNNABLE simultaneously.
    """
    cfg = WorldConfig(
        n_threads=3, n_cpus=3, n_locks=1, n_devices=1,
        queue_depth=1, req_pool=4, completion_p=Fraction(1, 2),
        epsilon=Fraction(1), discipline="fifo",
    )
    from yupi.programs import io as io_instr, COMPUTE
    progs = (
        # thread 0: issue IO (fills queue depth=1), then COMPUTE -- the trailing
        # instruction matters: it keeps thread 0 RUNNABLE (not TERMINATED) on
        # wake, isolating the wake-all assertion from the separate
        # completing-the-last-instruction-terminates semantics covered by
        # test_terminated_on_last_instruction_leaves_running below.
        (io_instr(0), COMPUTE),
        (io_instr(0),),  # thread 1: IO on full queue -> QUEUE_BLOCKED
        (COMPUTE,),       # thread 2: irrelevant filler, keeps n_cpus=3 satisfied
    )
    s = initial_state(cfg)
    # dispatch all three (n_cpus=3 so all can be RUNNING at once, one dispatch per tick)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 0, cfg, progs)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 1, cfg, progs)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 2, cfg, progs)
    # thread 0 issues IO -> IO_ISSUE, queue now full (depth 1)
    s, iss = take(s, lambda t: t.kind == "IO_ISSUE" and t.actor == 0, cfg, progs)
    assert s.status[0][0] == "IO_BLOCKED"
    assert len(s.dev_q[0]) == 1
    # thread 1 attempts IO -> queue full -> BLOCK with obj=("DEV",0), status queue_blocked(0)
    s, blk = take(s, lambda t: t.kind == "BLOCK" and t.actor == 1, cfg, progs)
    assert blk.obj == ("DEV", 0)
    assert s.status[1] == queue_blocked(0)
    assert 1 not in s.running

    # Call enabled() directly on s to inspect the completion branch: thread 0
    # (IO_BLOCKED, issuer) and thread 1 (QUEUE_BLOCKED) must both wake in the
    # single COMPLETION transition, regardless of what stage-B activity (e.g.
    # thread 2's COMPUTE) is also enabled alongside it.
    pairs = enabled(s, cfg, progs)
    completions = [t for t, _ in pairs if t.kind == "COMPLETION"]
    assert len(completions) == 1
    comp = completions[0]
    assert comp.actor == 0          # issuer of the departing (only) request
    assert comp.lineage is not None  # request id recorded as lineage
    ns = comp.next_state
    # issuer woken
    assert ns.status[0] == RUNNABLE
    # queue-blocked thread also woken (wake-all)
    assert ns.status[1] == RUNNABLE
    # device queue now empty
    assert ns.dev_q[0] == ()


def test_stochastic_discipline_completes_each_inflight_with_p_over_n():
    """§3.4: under 'stochastic' discipline with n in-flight requests, each
    request completes independently with probability p/n, rather than only
    the FIFO head completing with probability p.
    """
    cfg = WorldConfig(
        n_threads=2, n_cpus=2, n_locks=1, n_devices=1,
        queue_depth=2, req_pool=4, completion_p=Fraction(1, 2),
        epsilon=Fraction(1), discipline="stochastic",
    )
    from yupi.programs import io as io_instr
    progs = (
        (io_instr(0),),
        (io_instr(0),),
    )
    s = initial_state(cfg)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 0, cfg, progs)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 1, cfg, progs)
    s, _ = take(s, lambda t: t.kind == "IO_ISSUE" and t.actor == 0, cfg, progs)
    s, _ = take(s, lambda t: t.kind == "IO_ISSUE" and t.actor == 1, cfg, progs)
    assert len(s.dev_q[0]) == 2

    pairs = enabled(s, cfg, progs)
    completions = [(t, p) for t, p in pairs if t.kind == "COMPLETION"]
    # two in-flight requests -> two distinct completion transitions (one per
    # departing request), each with probability p/n = (1/2)/2 = 1/4
    assert len(completions) == 2
    actors = {t.actor for t, _ in completions}
    assert actors == {0, 1}
    for t, prob in completions:
        assert prob == Fraction(1, 4)
        # exactly one request departs; the other remains in flight
        assert len(t.next_state.dev_q[0]) == 1
    # total across the whole enabled() distribution still sums to 1
    assert total(pairs) == Fraction(1)


def test_terminated_on_last_instruction_leaves_running():
    """Completing the final instruction of a program transitions the thread
    to TERMINATED and removes it from the running set, in the same tick as
    the instruction that completed the program.
    """
    cfg = WorldConfig.c0a()
    from yupi.programs import COMPUTE
    progs = ((COMPUTE,), (COMPUTE,))  # single-instruction programs
    s = initial_state(cfg)
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 0, cfg, progs)
    assert 0 in s.running and s.status[0] == RUNNING
    s, step = take(s, lambda t: t.kind == "STEP" and t.actor == 0, cfg, progs)
    assert step.actor == 0
    assert s.status[0] == TERMINATED
    assert 0 not in s.running
    assert s.pc[0] == 1  # len(program) == 1


def test_epsilon_policy_cursor_canonical_and_merges_across_mixture_components():
    """Regression for the cursor-canonicalization bug found in review: both
    the uniform and round-robin components of the epsilon-mixture must
    advance the cursor identically (mod n_threads), so that when they pick
    the same thread the two contributions collapse into ONE Transition via
    _merge, rather than surviving as two entries that differ only in
    rr_cursor. Before the fix, a uniform pick left the cursor unchanged
    while a round-robin pick advanced it -- so at the initial state
    (cursor=0), dispatching thread 0 via the mixture at eps=1/2 produced two
    distinct next_states (cursor 0 vs cursor 1) instead of one, and the
    reachable-state space grew without the cursor ever being bounded back
    into range.
    """
    cfg = replace_cfg(CFG, epsilon=Fraction(1, 2))
    pairs = enabled(initial_state(cfg), cfg, PROGS)
    # Exactly one entry per distinct chosen thread: two runnable threads (0
    # and 1), no completion branch (device queue empty) -- so exactly 2
    # entries, not 4 (which is what the pre-fix bug produced: one per
    # thread from the uniform component plus a separate one for whichever
    # thread round-robin picked).
    assert len(pairs) == 2
    assert {t.actor for t, _ in pairs} == {0, 1}
    assert total(pairs) == Fraction(1)
    # Every resulting cursor is canonical: in range [0, n_threads).
    for t, _ in pairs:
        assert 0 <= t.next_state.rr_cursor < cfg.n_threads


def test_epsilon_mixture_reachable_space_has_no_duplicate_transitions():
    """BFS the eps=1/2 C0a reachable space and assert every state's
    enabled() list has unique (kind, actor, next_state) triples -- i.e. no
    two entries differ only by an uncanonicalized or mixture-path-dependent
    cursor value that should have merged.
    """
    cfg = replace_cfg(CFG, epsilon=Fraction(1, 2))
    s = initial_state(cfg)
    frontier, seen = [s], set()
    while frontier:
        s = frontier.pop()
        if s in seen:
            continue
        seen.add(s)
        pairs = enabled(s, cfg, PROGS)
        assert total(pairs) == Fraction(1), s
        keys = [(t.kind, t.actor, t.next_state) for t, _ in pairs]
        assert len(keys) == len(set(keys)), (s, pairs)
        # canonical cursor invariant on every reachable next_state
        for t, _ in pairs:
            assert 0 <= t.next_state.rr_cursor < cfg.n_threads
        frontier.extend(t.next_state for t, _ in pairs)
    assert len(seen) > 1  # sanity: BFS actually explored something


def test_epsilon_one_cursor_absent_from_effective_state():
    """Regression: at eps=1 the round-robin cursor must be truly absent from
    the dynamics (per §3.1), not merely omitted from the round-robin-only
    advancement. Before the fix, `_epsilon_policy`'s uniform branch advanced
    the cursor unconditionally `(c+1) % n_threads` even at eps=1, and both
    call sites wrote that into next_state -- so the cursor silently kept
    moving even though eps=1 documents it as absent. That inflated the
    reachable C0a space to 85 states over a 72-state physical quotient (13
    states split only by rr_cursor).

    BFS the full reachable space of WorldConfig.c0a() (eps=1 by default) and
    assert (a) no two reachable states are identical except for rr_cursor --
    i.e. the cursor never actually varies once eps=1 is in effect -- and (b)
    the reachable count is exactly 58. (History: 72 was measured under the
    pre-2026-08-20 kernel, whose direct-handoff defect made self-deadlock
    states reachable and left handoff recipients' pc behind; §3.2a's
    "transient gives 72 states" figure carries the same defect and is flagged
    for statute erratum. Corrected kernel: 58.)
    """
    cfg = WorldConfig.c0a()
    assert cfg.epsilon == Fraction(1)
    progs = c0a_programs()
    s = initial_state(cfg)
    frontier, seen = [s], set()
    while frontier:
        s = frontier.pop()
        if s in seen:
            continue
        seen.add(s)
        pairs = enabled(s, cfg, progs)
        assert total(pairs) == Fraction(1), s
        frontier.extend(t.next_state for t, _ in pairs)

    # (a) no two reachable states differ only by rr_cursor
    quotient = {replace_cfg(st, rr_cursor=0) for st in seen}
    assert len(quotient) == len(seen), (
        "reachable states differ only by rr_cursor -- cursor is not truly "
        "absent from the dynamics at eps=1"
    )

    # (b) exact reachable count under the corrected (2026-08-20) kernel;
    # §3.2a's 72 was a buggy-kernel measurement, flagged for statute erratum
    assert len(seen) == 58
