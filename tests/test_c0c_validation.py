# tests/test_c0c_validation.py
"""C0c scheduling validation (Part I, Configurations): minimal 2-CPU world.

Part I line 145: "C0c (scheduling validation): minimal 2-CPU configuration.
Witnesses CPU-slot assignment, alternation, and scheduler invariants."

Design commitment (this file is its record): 3 threads, 2 CPUs, 0 locks,
1 device, queue depth 1, pool 2, epsilon = 1, fifo. Three threads and not
two because slot *assignment* only bites under contention — with
n_threads == n_cpus every runnable thread always finds a free slot and the
dispatch gate (len(running) >= n_cpus) never holds a thread back. Three is
the minimum that witnesses: both slots occupied, a runnable thread waiting
behind a full CPU complement, and the execution choice among two
simultaneously running threads. One device so Stage A completion is
witnessed concurrently with a full CPU complement. Depth 1 makes the two
completion disciplines extensionally identical (the C0b lesson), so this
file runs fifo only and does not pretend to discriminate disciplines.

Every witness is asserted as a proposition, not assumed from a green suite,
and the 2-CPU witnesses carry a paired control: the same predicates are
provably empty by arity on the 1-CPU C0a/C0b worlds. A witness without a
world where it must fail is uninterpretable (the C0-family losslessness
lesson, and the protocol lesson of the Riemann appendix C.6: give every
line control objects on which its claim is false).
"""
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.programs import c0a_programs, c0b_programs, c0c_programs
from yupi.kernel import enabled
from yupi.records import record_of
from yupi.state import initial_state, check_invariants, RUNNABLE
from yupi.enumerator import paths, posterior_by_paths
from yupi.interfaces import project
from yupi.filter import initial_belief, step

H = 8

CFG = WorldConfig.c0c()
PROGS = c0c_programs()

EXPECTED_KINDS = {"DISPATCH", "STEP", "IO_ISSUE", "IO_COMPLETE", "IDLE"}

RUNGS = ("r1", "r2", "r3", "r4")


# ---------------------------------------------------------------- helpers

def _walk_states(cfg, progs, horizon):
    """Yield every (state, transitions) pair reachable within `horizon`
    ticks, where transitions is enabled(state). Uses only the world
    definition (kernel.enabled), no filtering logic."""
    seen = set()
    frontier = [initial_state(cfg)]
    for _ in range(horizon + 1):
        next_frontier = []
        for s in frontier:
            if s in seen:
                continue
            seen.add(s)
            ts = enabled(s, cfg, progs)
            yield s, ts
            next_frontier.extend(t.next_state for t, _ in ts)
        frontier = next_frontier


def _replay_running(recs):
    """Yield (record, running_set_before_that_record) pairs, reconstructing
    the running set from the latent record sequence. Valid for lock-free
    worlds (no ACQUIRE/BLOCK/RELEASE handling on purpose: C0c has no locks,
    and silently mishandling a lock record would corrupt the replay, so
    unknown kinds raise)."""
    running = set()
    for r in recs:
        yield r, frozenset(running)
        if r.kind == "DISPATCH":
            running.add(r.actor)
        elif r.kind in ("STEP", "IO_ISSUE"):
            running.discard(r.actor)
        elif r.kind in ("IO_COMPLETE", "IDLE"):
            pass
        else:
            raise AssertionError(f"unexpected record kind in replay: {r.kind}")


def _max_running(cfg, progs, horizon):
    return max(len(s.running) for s, _ in _walk_states(cfg, progs, horizon))


# ------------------------------------------------------------ world shape

def test_config_shape_and_pool_constraint():
    assert CFG.n_threads == 3
    assert CFG.n_cpus == 2
    assert CFG.n_locks == 0
    assert CFG.n_devices == 1
    # Part II §1 (I4): req_pool >= 2 * queue_depth so id recycling is safe.
    assert CFG.req_pool >= 2 * CFG.queue_depth
    assert len(PROGS) == CFG.n_threads


def test_probabilities_sum_to_one():
    total = sum(p for _, p, _ in paths(CFG, PROGS, H))
    assert total == Fraction(1)


def test_horizon_covers_expected_record_kinds():
    # Coverage as an asserted proposition (Ruraq's fix, carried forward).
    kinds = {r.kind for recs, _, _ in paths(CFG, PROGS, H) for r in recs}
    assert kinds == EXPECTED_KINDS, kinds


# ------------------------------------------------- the three C0c witnesses

def test_both_cpus_occupied_witnessed():
    # Witness: some reachable state has both CPU slots occupied. The code
    # path (second DISPATCH stacking onto a nonempty running set) that no
    # 1-CPU world can execute.
    assert _max_running(CFG, PROGS, H) == 2


def test_slot_contention_witnessed():
    # Witness: some reachable state has a full CPU complement AND a thread
    # still RUNNABLE — a thread held back by the dispatch gate, which is
    # what "CPU-slot assignment" means as a scheduling event.
    witnessed = any(
        len(s.running) == CFG.n_cpus and any(st == RUNNABLE for st in s.status)
        for s, _ in _walk_states(CFG, PROGS, H)
    )
    assert witnessed, "no reachable state with full slots and a waiting thread"


def test_execution_alternation_witnessed_both_orders():
    # Witness: from a both-running state, the ε-policy's execution pick is a
    # real choice — across histories, both running threads are seen stepping
    # first. Only threads 1 and 2 run COMPUTE, so the actor set is exactly
    # {1, 2} or the witness fails.
    actors_stepping_while_full = set()
    for recs, _, _ in paths(CFG, PROGS, H):
        for r, running_before in _replay_running(recs):
            if r.kind == "STEP" and len(running_before) == 2:
                actors_stepping_while_full.add(r.actor)
    assert actors_stepping_while_full == {1, 2}, actors_stepping_while_full


def test_completion_while_both_cpus_busy_witnessed():
    # Witness: Stage A (device completion) fires while the CPU complement is
    # full — the completion/dispatch interaction C1 will rely on.
    witnessed = False
    for recs, _, _ in paths(CFG, PROGS, H):
        for r, running_before in _replay_running(recs):
            if r.kind == "IO_COMPLETE" and len(running_before) == 2:
                witnessed = True
    assert witnessed, "no completion ever fired with both CPUs busy"


# ------------------------------------------------------- paired controls

def test_control_two_running_unreachable_at_one_cpu():
    # Control (Riemann C.6 discipline): the both-cpus-occupied witness class
    # must be empty by arity on every 1-CPU world. If this fails, the
    # witness above was never discriminating anything.
    assert _max_running(WorldConfig.c0a(), c0a_programs(), H) == 1
    for discipline in ("fifo", "stochastic"):
        cfg = WorldConfig.c0b(discipline=discipline)
        assert _max_running(cfg, c0b_programs(), H) == 1


# --------------------------------------------------- scheduler invariants

def test_running_never_exceeds_n_cpus():
    for s, _ in _walk_states(CFG, PROGS, H):
        assert len(s.running) <= CFG.n_cpus, s


def test_dispatch_priority_invariant():
    # §3.1: dispatch has priority. No execution-stage transition may be
    # offered from a state where a free slot and a runnable thread coexist.
    execution_kinds = {"STEP", "ACQUIRE", "BLOCK", "RELEASE", "IO_ISSUE"}
    for s, ts in _walk_states(CFG, PROGS, H):
        offers_execution = any(t.kind in execution_kinds for t, _ in ts)
        free_slot = len(s.running) < CFG.n_cpus
        runnable = any(st == RUNNABLE for st in s.status)
        if offers_execution:
            assert not (free_slot and runnable), s


def test_state_invariants_all_reachable_states():
    # I1-I5 (Part II §1) hold in every reachable state, not just sampled ones.
    for s, _ in _walk_states(CFG, PROGS, H):
        assert check_invariants(s, CFG) == [], (s, check_invariants(s, CFG))


# ----------------------------------------------------------- exact gates

def test_full_context_point_mass_expected():
    # Documented expectation, not a hope: the C0-family losslessness finding
    # (Aug 13) predicts every full-context posterior in C0c is a point mass
    # at every rung — every stochastic branch is immediately labeled by its
    # next record's kind+actor. If this ever fails, C0c has found grip the
    # family was measured not to have, and that is a finding either way.
    for rung in RUNGS:
        groups = {}
        def recurse(state, obs, depth):
            groups.setdefault((depth, obs), set()).add(state)
            if depth == H:
                return
            for t, _ in enabled(state, CFG, PROGS):
                recurse(
                    t.next_state,
                    obs + (project(record_of(t), rung),),
                    depth + 1,
                )
        recurse(initial_state(CFG), (), 0)
        for (depth, obs), states in groups.items():
            assert len(states) == 1, (rung, depth, obs, states)


def test_bit_for_bit_all_histories_all_rungs():
    # Part II §6: filter must match path-sum enumeration exactly (Fraction ==),
    # on every distinct observation sequence, at every prefix, at every rung.
    for rung in RUNGS:
        obs_seqs = {
            tuple(project(r, rung) for r in recs)
            for recs, _, _ in paths(CFG, PROGS, H)
        }
        for obs in sorted(obs_seqs, key=repr):
            belief = initial_belief(CFG)
            for i, o in enumerate(obs, 1):
                belief = step(belief, o, rung, CFG, PROGS)
                exact = posterior_by_paths(CFG, PROGS, list(obs[:i]), rung)
                assert belief == exact, (rung, obs[:i])
