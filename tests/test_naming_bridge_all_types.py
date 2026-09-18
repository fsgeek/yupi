"""The naming bridge over ALL FOUR entity types (learner contract v0.1 §2.1,
§4 item 1, 2026-09-18).

The corpus renames threads, locks, devices and request ids per episode
(design v0.1 §3); the enacted lemma (tests/test_naming_bridge.py,
yupi.naming.pattern) relabels thread fields only, so every corpus-track
artifact to date holds locks, devices and request ids canonical and is a
thread-naming LOWER BOUND on the pattern observer's uncertainty. This file
extends the lemma: with σ drawn independently and uniformly per entity type,
the posterior over the structural state given the surface window is a
function of the joint equality pattern Π_all (first-appearance relabeling
per type), and the surface class mass is the pattern class mass split
uniformly over the token assignments of the k_type distinct entities of
each type.

Checked Fraction for Fraction at C1 (8, 4, 2), both statutory ε:
  (a) r4, threads held at the identity (so the observer's pattern leaves
      threads structural — Π relabels exactly the renamed types), locks ×
      device × request ids exhaustive over permutation pools;
  (b) r2, threads × locks exhaustive (lineage is MASKED at r2, so request
      renaming is vacuous there and is omitted);
  (c) r4, all four types jointly (slow: 1,152 injections per window);
  (d) Π_all is coarser than Π_thread with canonical non-thread entities
      (the existing corpus-track numbers are lower bounds), and equals it
      at r1 and r0 where no non-thread field is visible.
"""
import itertools
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.naming import pattern, pattern_all, rename_all
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

LAW = WindowLaw(T_ep=8, L=4, B=2)
TYPES = ("thread", "lock", "device", "request")


def _windows(cfg, progs, rung):
    w_T = endpoint_prior(LAW)
    for T in LAW.endpoints():
        u = LAW.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            yield (u == 0, tuple(project(r, rung) for r in recs[u:]), w_T * prob, final)


def _counts(cfg):
    return {"thread": cfg.n_threads, "lock": cfg.n_locks, "device": cfg.n_devices, "request": cfg.req_pool}


def _sigmas(cfg, renamed):
    """Every joint injection: permutation pools (|pool| = count) for the types
    in `renamed`, the identity for the rest. Uniform over the product."""
    n = _counts(cfg)
    per_type = []
    for et in TYPES:
        if et in renamed:
            pool = tuple(f"{et[0]}{j}" for j in range(n[et]))
            per_type.append([dict(zip(range(n[et]), toks)) for toks in itertools.permutations(pool, n[et])])
        else:
            per_type.append([{i: i for i in range(n[et])}])
    for combo in itertools.product(*per_type):
        yield dict(zip(TYPES, combo))


def _aggregates(cfg, progs, rung, renamed):
    sigmas = list(_sigmas(cfg, renamed))
    w_sigma = Fraction(1, len(sigmas))
    surface, patt = {}, {}
    for reset, win, mass, final in _windows(cfg, progs, rung):
        pw, binding = pattern_all(win, tuple(renamed))   # the observer's pattern relabels exactly the renamed types
        d = patt.setdefault((reset, pw), {})
        d[(final, binding)] = d.get((final, binding), Fraction(0)) + mass
        for sig in sigmas:
            sw = tuple(rename_all(r, sig) for r in win)
            e = surface.setdefault((reset, sw), {})
            key = (final, tuple(tuple(sig[et][i] for i in range(_counts(cfg)[et])) for et in TYPES))
            e[key] = e.get(key, Fraction(0)) + mass * w_sigma
    return surface, patt, sigmas


def _state_marginal(joint):
    tot = sum(joint.values(), Fraction(0)); out = {}
    for (s, _), m in joint.items():
        out[s] = out.get(s, Fraction(0)) + m / tot
    return out


def _check_lemma(cfg, progs, rung, renamed):
    surface, patt, sigmas = _aggregates(cfg, progs, rung, renamed)
    assert sum((sum(v.values(), Fraction(0)) for v in surface.values()), Fraction(0)) == 1
    assert sum((sum(v.values(), Fraction(0)) for v in patt.values()), Fraction(0)) == 1
    n = _counts(cfg)
    for (reset, sw), joint in surface.items():
        pw, binding = pattern_all(sw, tuple(renamed))
        pj = patt[(reset, pw)]
        # 1. the same posterior over structural states
        assert _state_marginal(joint) == _state_marginal(pj), (reset, sw)
        # 1'. the pattern class's mass splits uniformly over the joint token assignments
        #     of the k_type distinct entities of each renamed type (falling factorials)
        split = Fraction(1)
        for et, order in zip(TYPES, binding):
            if et in renamed:
                for j in range(len(order)):
                    split *= n[et] - j
        assert sum(joint.values(), Fraction(0)) * split == sum(pj.values(), Fraction(0)), (reset, sw)
    # the surface partition is strictly finer than the pattern partition iff some renamed type is visible
    visible = {"thread": rung != "r0", "lock": rung in ("r2", "r3", "r4"),
               "device": rung in ("r2", "r3", "r4"), "request": rung == "r4"}
    assert (len(surface) > len(patt)) == any(visible[et] for et in renamed)


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_non_thread_types_alone_r4(eps):
    _check_lemma(WorldConfig.c1(epsilon=eps), c1_programs(), "r4", {"lock", "device", "request"})


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_threads_and_locks_r2(eps):
    _check_lemma(WorldConfig.c1(epsilon=eps), c1_programs(), "r2", {"thread", "lock"})


@pytest.mark.slow
@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_all_four_types_jointly_r4(eps):
    _check_lemma(WorldConfig.c1(epsilon=eps), c1_programs(), "r4", set(TYPES))


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("rung", ["r0", "r1", "r2", "r3", "r4"])
def test_pattern_all_is_coarser_than_thread_pattern(eps, rung):
    """Π_all classes are unions of Π_thread classes (the deterministic map
    Π_thread(w) -> Π_all(w) is well defined), with equality at r0/r1 where
    no non-thread field is visible; and the thread component of Π_all's
    binding is Π_thread's order."""
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    thread_to_all, n_thread, n_all = {}, set(), set()
    for reset, win, mass, final in _windows(cfg, progs, rung):
        pt, order = pattern(win)
        pa, binding = pattern_all(win)
        assert binding[0] == order
        assert pattern_all(win, ("thread",)) == (pt, (order, (), (), ()))   # thread-only Π_all is Π
        assert thread_to_all.setdefault((reset, pt), (reset, pa)) == (reset, pa)
        n_thread.add((reset, pt)); n_all.add((reset, pa))
    assert len(n_all) <= len(n_thread)
    assert (len(n_all) == len(n_thread)) == (rung in ("r0", "r1"))


def test_pattern_all_record_shape():
    """Pattern indices sit where structural indices sat; MASKED and None
    survive; obj keeps its kind tag; a record's two thread fields are
    labelled actor before related."""
    from yupi.interfaces import MASKED
    from yupi.records import Record
    win = (Record("ACQUIRE", 3, ("LOCK", 1), None, None),
           Record("BLOCK", 1, ("LOCK", 1), 3, None),
           Record("IO_ISSUE", 3, ("DEV", 0), None, 2),
           Record("IO_COMPLETE", 3, ("DEV", 0), None, 2),
           Record("STEP", 0, MASKED, MASKED, MASKED))
    pw, binding = pattern_all(win)
    assert pw == (Record("ACQUIRE", 0, ("LOCK", 0), None, None),
                  Record("BLOCK", 1, ("LOCK", 0), 0, None),
                  Record("IO_ISSUE", 0, ("DEV", 0), None, 0),
                  Record("IO_COMPLETE", 0, ("DEV", 0), None, 0),
                  Record("STEP", 2, MASKED, MASKED, MASKED))
    assert binding == ((3, 1, 0), (1,), (0,), (2,))
