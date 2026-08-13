# tests/test_c0b_validation.py
"""C0b device validation (Part I, Configurations): 2 threads, 1 CPU, 0 locks,
1 device, queue depth 2, minimal workload placing two requests in flight.

Witnesses required by Part I: stochastic-order completion of a non-head
request, the FIFO/stochastic transition-rule difference (extensionally
invisible at depth 1), and bit-for-bit filter-vs-enumeration validation on
both disciplines. Coverage is asserted as propositions, not assumed from a
green suite (Part II §6, and the C0a precedent).
"""
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import c0b_programs
from yupi.enumerator import paths, posterior_by_paths
from yupi.interfaces import project
from yupi.filter import initial_belief, step

H = 10

CFG_FIFO = WorldConfig.c0b(discipline="fifo")
CFG_STOCH = WorldConfig.c0b(discipline="stochastic")
PROGS = c0b_programs()

EXPECTED_KINDS = {"DISPATCH", "IO_ISSUE", "IO_COMPLETE", "IDLE"}


def _completions_with_queue_head(recs):
    """Yield (completed_req_id, head_req_id_at_that_tick) pairs, reconstructing
    the device queue from the latent record sequence (single device)."""
    queue = []
    for r in recs:
        if r.kind == "IO_ISSUE":
            queue.append(r.lineage)
        elif r.kind == "IO_COMPLETE":
            head = queue[0]
            yield r.lineage, head
            queue.remove(r.lineage)


def test_config_respects_pool_constraint():
    # Part II §1 (I4): req_pool >= 2 * queue_depth so id recycling is safe.
    for cfg in (CFG_FIFO, CFG_STOCH):
        assert cfg.queue_depth == 2
        assert cfg.req_pool >= 2 * cfg.queue_depth


def test_two_requests_in_flight_witnessed():
    # The defining feature of C0b: some history has both requests in flight
    # simultaneously (two IO_ISSUEs before any IO_COMPLETE).
    for cfg in (CFG_FIFO, CFG_STOCH):
        witnessed = False
        for recs, _, _ in paths(cfg, PROGS, H):
            kinds = [r.kind for r in recs]
            issues = [i for i, k in enumerate(kinds) if k == "IO_ISSUE"]
            completes = [i for i, k in enumerate(kinds) if k == "IO_COMPLETE"]
            if len(issues) == 2 and (not completes or completes[0] > issues[1]):
                witnessed = True
                break
        assert witnessed, f"no two-in-flight history under {cfg.discipline}"


def test_non_head_completion_witnessed_under_stochastic():
    # The transition depth 1 cannot express: a request departs that is not
    # the queue head. This is the code path C0a's green suite never ran.
    witnessed = False
    for recs, _, _ in paths(CFG_STOCH, PROGS, H):
        for completed, head in _completions_with_queue_head(recs):
            if completed != head:
                witnessed = True
    assert witnessed, "stochastic discipline never completed a non-head request"


def test_fifo_never_completes_non_head():
    # Control: under fifo the departing request is always the head, in every
    # history. If this fails, the disciplines are not what D10 says they are.
    for recs, _, _ in paths(CFG_FIFO, PROGS, H):
        for completed, head in _completions_with_queue_head(recs):
            assert completed == head, "fifo completed a non-head request"


def test_horizon_covers_expected_record_kinds():
    # Coverage as an asserted proposition (Ruraq's fix, carried forward).
    for cfg in (CFG_FIFO, CFG_STOCH):
        kinds = {r.kind for recs, _, _ in paths(cfg, PROGS, H) for r in recs}
        assert kinds == EXPECTED_KINDS, (cfg.discipline, kinds)


def test_probabilities_sum_to_one():
    for cfg in (CFG_FIFO, CFG_STOCH):
        total = sum(p for _, p, _ in paths(cfg, PROGS, H))
        assert total == Fraction(1), (cfg.discipline, total)


def test_bit_for_bit_all_histories_all_rungs_both_disciplines():
    # Part II §6: filter must match path-sum enumeration exactly (Fraction ==),
    # on every distinct observation sequence, at every prefix, for every rung —
    # now including the stochastic-completion likelihood path.
    for cfg in (CFG_FIFO, CFG_STOCH):
        for rung in ("r1", "r2", "r3", "r4"):
            obs_seqs = {
                tuple(project(r, rung) for r in recs)
                for recs, _, _ in paths(cfg, PROGS, H)
            }
            for obs in sorted(obs_seqs, key=repr):
                belief = initial_belief(cfg)
                for i, o in enumerate(obs, 1):
                    belief = step(belief, o, rung, cfg, PROGS)
                    exact = posterior_by_paths(cfg, PROGS, list(obs[:i]), rung)
                    assert belief == exact, (cfg.discipline, rung, obs[:i])
