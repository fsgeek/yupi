"""The pattern observer's exact filter (learner contract v0.1 §2.1–2.2, §4
items 2–3; 2026-09-18) — gated three ways at C1 (8, 4, 2), both statutory ε.

The observer the trained model instantiates sees the equality pattern Πw
(all four entity types renamed per episode, v0.2.9 Clause 4). Its exact
posterior over (U, S_T, β) — offset, structural state, and the partial
binding from pattern indices to structural entities — is computed here by
RECURSIVE MIXTURE FILTERING over the joint latent (`yupi.pattern_filter`),
and validated bit-for-bit against

  (i)  PREFIX-MARGINALIZED PATH SUMMATION (`yupi.pattern_enumerator`): every
       trajectory to every compatible endpoint, window suffix patterned by
       Π_all, matched, summed by (offset, final state, binding);
  (ii) the RE-KEYED CANONICAL AGGREGATE — the construction the corpus-track
       producer uses (scripts/c1_corpus_track.py), here from the enumerator's
       canonical windows re-keyed by Π_all: {(reset, Πw): {(S, β): mass}}.

Also gated: the law mass of the pattern window; the pattern-projected
NEXT-RECORD distribution P*(Πr | Πw) (the model's ceiling, contract §2.1)
against the path-summation tally of realized next records; and the PREFIX
mode (contract §2.2: compatibility relaxed to T − U ≥ k) against paths.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.naming import ENTITY_ORDER, extend_binding, pattern, pattern_all
from yupi.pattern_enumerator import (
    next_pattern_aggregate_by_paths,
    pattern_aggregate_by_paths,
)
from yupi.pattern_filter import (
    filter_pattern_window,
    next_pattern_dist,
    pattern_end_probability,
)
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

LAW = WindowLaw(T_ep=8, L=4, B=2)
RUNGS = ("r0", "r1", "r2", "r3", "r4")
EPS = [Fraction(1), Fraction(1, 2)]


def _rekeyed_aggregate(cfg, progs, rung, types=ENTITY_ORDER):
    """(ii): canonical windows from paths, re-keyed by Π_all -> {(reset, pw): {(S, β): mass}}."""
    w_T = endpoint_prior(LAW)
    out = {}
    for T in LAW.endpoints():
        u = LAW.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            pw, binding = pattern_all(tuple(project(r, rung) for r in recs[u:]), types)
            d = out.setdefault((u == 0, pw), {})
            d[(final, binding)] = d.get((final, binding), Fraction(0)) + w_T * prob
    return out


def test_extend_binding_folds_to_pattern_all():
    cfg, progs = WorldConfig.c1(), c1_programs()
    for recs, _, _ in paths(cfg, progs, 6)[:400]:
        for rung in RUNGS:
            win = tuple(project(r, rung) for r in recs)
            b, out = ((), (), (), ()), []
            for r in win:
                pr, b = extend_binding(b, r)
                out.append(pr)
            assert (tuple(out), b) == pattern_all(win)
            # thread-only: folds to the enacted Π
            b, out = ((), (), (), ()), []
            for r in win:
                pr, b = extend_binding(b, r, ("thread",))
                out.append(pr)
            assert (tuple(out), b[0]) == pattern(win) and b[1:] == ((), (), ())


def test_extend_binding_fresh_entities_get_the_next_indices():
    from yupi.records import Record
    b = ((3,), (1,), (), ())
    pr, b2 = extend_binding(b, Record("BLOCK", 0, ("LOCK", 0), 3, None))   # fresh actor, fresh lock, named related
    assert pr == Record("BLOCK", 1, ("LOCK", 1), 0, None) and b2 == ((3, 0), (1, 0), (), ())
    pr, b3 = extend_binding(b2, Record("IO_ISSUE", 2, ("DEV", 0), None, 1))
    assert pr == Record("IO_ISSUE", 2, ("DEV", 0), None, 0) and b3 == ((3, 0, 2), (1, 0), (0,), (1,))
    # a named entity keeps its index; the binding does not grow
    assert extend_binding(b3, Record("RELEASE", 3, ("LOCK", 1), 0, None)) == (Record("RELEASE", 0, ("LOCK", 0), 1, None), b3)   # structural lock 1 is pattern lock 0


@pytest.mark.parametrize("eps", EPS)
@pytest.mark.parametrize("rung", RUNGS)
def test_filter_equals_paths_and_rekeyed_aggregate(eps, rung):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    by_paths = pattern_aggregate_by_paths(cfg, progs, LAW, rung)          # (i)  {(reset, pw): {u: {(S, β): mass}}}
    rekeyed = _rekeyed_aggregate(cfg, progs, rung)                         # (ii) {(reset, pw): {(S, β): mass}}
    assert set(by_paths) == set(rekeyed)
    total_mass = Fraction(0)
    for (reset, pw), per_u in by_paths.items():
        post, mass = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset)
        # law mass of the pattern window
        class_mass = sum((m for d in per_u.values() for m in d.values()), Fraction(0))
        assert mass == class_mass == sum(rekeyed[(reset, pw)].values(), Fraction(0))
        total_mass += mass
        # joint over (u, S, β): filter == paths, component by component
        assert set(post.components) == set(per_u)
        for u, (w, belief) in post.components.items():
            d = per_u[u]
            mu = sum(d.values(), Fraction(0))
            assert w == mu / class_mass
            assert belief == {k: m / mu for k, m in d.items()}, (reset, pw, u)
        # marginal over (S, β): filter == re-keyed aggregate
        joint = post.joint_marginal()
        assert joint == {k: m / class_mass for k, m in rekeyed[(reset, pw)].items()}
        # a pattern window is a fixed point of the enacted thread-Π, and every
        # binding names exactly the window's distinct pattern indices per type
        assert pattern(pw)[0] == pw
        for (_, binding) in joint:
            assert len(binding[0]) == len(pattern(pw)[1])
            if rung == "r0":
                assert binding == ((), (), (), ())
    assert total_mass == 1


@pytest.mark.parametrize("eps", EPS)
@pytest.mark.parametrize("rung", ("r1", "r3"))
def test_thread_only_pattern_filter_matches_the_enacted_lemma_construction(eps, rung):
    """types=("thread",): the filter's state marginal is the pattern posterior of
    tests/test_naming_bridge.py (locks, devices, request ids structural)."""
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    rekeyed = _rekeyed_aggregate(cfg, progs, rung, ("thread",))
    for (reset, pw), joint in rekeyed.items():
        post, mass = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset, types=("thread",))
        tot = sum(joint.values(), Fraction(0))
        assert mass == tot
        assert post.joint_marginal() == {k: m / tot for k, m in joint.items()}


@pytest.mark.parametrize("eps", EPS)
@pytest.mark.parametrize("rung", RUNGS)
def test_next_record_ceiling_equals_realized_next_records(eps, rung):
    """P*(Πr_{T+1} | Πw) from the filter (one kernel step per support state,
    re-keyed through β, projected by Π) == the path tally of realized next
    records over trajectories to T + 1 whose window patterns to Πw."""
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    tally = next_pattern_aggregate_by_paths(cfg, progs, LAW, rung)         # {(reset, pw): {ρ: mass}}
    by_paths = pattern_aggregate_by_paths(cfg, progs, LAW, rung)
    assert set(tally) == set(by_paths)
    for (reset, pw), dist in tally.items():
        post, mass = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset)
        star = next_pattern_dist(post, cfg, progs, rung)
        assert sum(star.values(), Fraction(0)) == 1
        assert star == {k: m / mass for k, m in dist.items()}, (reset, pw)


@pytest.mark.parametrize("eps", EPS)
@pytest.mark.parametrize("rung", ("r1", "r4"))
def test_prefix_mode_against_paths(eps, rung):
    """Contract §2.2: a prefix of k records is compatible with every offset whose
    window runs at least k records (T − U ≥ k); RESET fixes U = 0 and leaves
    T ≥ k open. Gate: filter(prefix=True) == path summation over every
    compatible (T, U) with the window's first k records patterned."""
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    w_T = endpoint_prior(LAW)
    for k in (1, 2, 3, 4):
        by_paths = {}
        for T in LAW.endpoints():
            u = LAW.offset(T)
            if T - u < k:
                continue
            for recs, prob, final_T in paths(cfg, progs, u + k):     # state after the k-th window record
                pw, binding = pattern_all(tuple(project(r, rung) for r in recs[u:u + k]))
                d = by_paths.setdefault((u == 0, pw), {}).setdefault(u, {})
                d[(final_T, binding)] = d.get((final_T, binding), Fraction(0)) + w_T * prob
        for (reset, pw), per_u in by_paths.items():
            post, mass = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset, prefix=True)
            class_mass = sum((m for d in per_u.values() for m in d.values()), Fraction(0))
            assert mass == class_mass
            assert set(post.components) == set(per_u)
            for u, (w, belief) in post.components.items():
                mu = sum(per_u[u].values(), Fraction(0))
                assert w == mu / class_mass and belief == {kk: m / mu for kk, m in per_u[u].items()}
            # end-of-window probability at this position (contract §1 item 3)
            end = pattern_end_probability(LAW, k, reset)
            if reset:      # P(T = k | T >= k, U = 0): zero off the grid, else one over the endpoints still open
                open_T = [T for T in LAW.endpoints() if LAW.offset(T) == 0 and T >= k]
                assert end == (Fraction(1, len(open_T)) if k in open_T else Fraction(0))
            else:
                assert end == (Fraction(1) if k == LAW.L else Fraction(0))
        # full-window mode at k = L (non-RESET) or k = T (RESET, T = k on the grid) coincides with prefix mode
        # only when a single endpoint is compatible: non-RESET at k = L
        if k == LAW.L:
            for (reset, pw) in by_paths:
                if not reset:
                    a = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset)
                    b = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset, prefix=True)
                    assert a == b


def test_prefix_reset_differs_from_full_window_when_more_endpoints_remain():
    """A RESET prefix of 2 records: full-window mode says T = 2; prefix mode
    says T ∈ {T on the grid : U(T) = 0, T ≥ 2} = {2, 4} at L = 4 — same state
    posterior (T carries no state evidence), law mass doubled."""
    cfg, progs = WorldConfig.c1(), c1_programs()
    recs, prob, final = paths(cfg, progs, 2)[0]
    pw, _ = pattern_all(tuple(project(r, "r4") for r in recs))
    full, m_full = filter_pattern_window(cfg, progs, LAW, list(pw), "r4", True)
    pre, m_pre = filter_pattern_window(cfg, progs, LAW, list(pw), "r4", True, prefix=True)
    assert full.joint_marginal() == pre.joint_marginal()
    open_T = [T for T in LAW.endpoints() if LAW.offset(T) == 0 and T >= 2]
    assert open_T == [2, 4] and m_pre == len(open_T) * m_full
