"""Statutory shuffled-window machinery (D8 × Part II §2 WindowLaw).

Required before the order-mode attribution prereg (Codex round 2026-08-24,
point 1): the shuffled channel composed with the offset-unanchored window
law — compatible-endpoint mixture, RESET-as-flag semantics (unchanged from
the ordered machinery), bucket-boundary delivery — plus an independent
path-summation gate over statutory windows and the B = 1 analytic null.
TIME_CLASS: the base condition masks it (absence ≡ masked); the anchored
condition is modeled by conditioning the posterior on U (known offset),
which is what unmasked absolute bucket indices reveal under a fixed law.
"""
from fractions import Fraction
from itertools import permutations
from math import factorial

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c0b_programs, c1_programs
from yupi.shuffled_window import (shuffled_window_by_paths,
                                  shuffled_window_filter)
from yupi.window import WindowLaw
from yupi.window_filter import filter_window


def _visible_windows(cfg, progs, law, rung):
    """Every genuinely possible shuffled observation of the law: for each
    realizable latent window, the Cartesian product of all DISTINCT
    within-bucket permutations of every bucket (a shuffled bucket can emit
    any permutation, including visible orders that are not themselves causal
    latent orders — reversal-only sampling missed those; Codex round,
    2026-08-24)."""
    from itertools import product
    seen = set()
    B = law.B
    for T in law.endpoints():
        u = law.offset(T)
        for recs, _, _ in paths(cfg, progs, T):
            win = [project(r, rung) for r in recs[u:T]]
            buckets = [win[k * B:(k + 1) * B] for k in range(len(win) // B)]
            per_bucket = [sorted({tuple(pm) for pm in permutations(b)}, key=repr) for b in buckets]
            for vis in product(*per_bucket):
                key = (vis, u == 0)
                if key not in seen:
                    seen.add(key)
                    yield [list(b) for b in vis], u == 0


@pytest.mark.parametrize("disc,rung,expected", [("stochastic", "r2", 64), ("fifo", "r4", 56)])
def test_two_path_gate_on_every_statutory_window_c0b(disc, rung, expected):
    """Complete census: every genuinely possible shuffled observation at the
    cell, both paths bit-for-bit. Counts pinned (64 stochastic/r2, 56
    fifo/r4 — independently obtained by the reviewer before this test
    asserted them)."""
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    law = WindowLaw(T_ep=6, L=4, B=2)
    n = 0
    for buckets, reset in _visible_windows(cfg, progs, law, rung):
        f = shuffled_window_filter(cfg, progs, law, buckets, rung, reset)
        e = shuffled_window_by_paths(cfg, progs, law, buckets, rung, reset)
        assert f == e
        n += 1
    assert n == expected


def test_B1_shuffled_equals_ordered_exactly():
    """The analytic null control: at B = 1 the permutation channel is the
    identity, so the shuffled window posterior must equal the ordered
    window filter bit-for-bit on every window."""
    cfg, progs = WorldConfig.c0b(discipline="stochastic"), c0b_programs()
    law = WindowLaw(T_ep=6, L=3, B=1)
    for buckets, reset in _visible_windows(cfg, progs, law, "r4"):
        flat = [b[0] for b in buckets]
        assert shuffled_window_filter(cfg, progs, law, buckets, "r4", reset) == \
            filter_window(cfg, progs, law, flat, "r4", reset)


def test_compatible_endpoint_mixture_is_a_real_mixture():
    """Rebuilt (Codex round): the old version used a law with one truncated
    endpoint and broke on the first (RESET) window, testing no mixture.
    Now: C1 (8,4,2), reset False required, >= 2 surviving offsets required,
    and every component weight AND belief verified against path summation."""
    from yupi.shuffled_window import shuffled_window_by_paths as by_paths
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=8, L=4, B=2)
    checked = 0
    for buckets, reset in _visible_windows(cfg, progs, law, "r1"):
        if reset:
            continue
        post = shuffled_window_filter(cfg, progs, law, buckets, "r1", reset)
        if len(post.components) < 2:
            continue
        e = by_paths(cfg, progs, law, buckets, "r1", reset)
        assert set(post.components) == set(e.components)
        for u in post.components:
            assert post.components[u][0] == e.components[u][0]   # weight
            assert post.components[u][1] == e.components[u][1]   # belief
        checked += 1
        if checked >= 5:
            break
    assert checked == 5


def test_anchored_conditioning_is_component_selection():
    """Anchored (TIME_CLASS-unmasked) = conditioning on U: the anchored
    posterior at offset u is the u-component's belief, renormalized."""
    # C1 full census at this law: 628 multi-component of 2112 distinct
    # observations (211 was the earlier reversal-only helper's count). C0b
    # has ZERO under the complete channel too — its window content pins the
    # offset even shuffled; offset mixing needs C1's record repertoire.
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=8, L=4, B=2)   # endpoints 6 and 8 both give U > 0
    for buckets, reset in _visible_windows(cfg, progs, law, "r1"):
        post = shuffled_window_filter(cfg, progs, law, buckets, "r1", reset)
        if len(post.components) > 1:
            from yupi.shuffled_window import shuffled_window_by_paths
            e = shuffled_window_by_paths(cfg, progs, law, buckets, "r1", reset)
            for u, (w, belief) in post.components.items():
                assert sum(belief.values()) == 1            # component = anchored posterior
                assert e.components[u][1] == belief         # both paths agree per component
            return
    pytest.fail("no multi-component C1 window found at (8,4,2)")


def test_kappa_range_invariant():
    """v0.2.6 Clause 1 addendum: check_invariants flags an out-of-range cursor."""
    from dataclasses import replace
    from yupi.state import check_invariants, initial_state
    cfg = WorldConfig.c1(epsilon=Fraction(1, 2))
    s0 = initial_state(cfg)
    assert check_invariants(s0, cfg) == []
    bad = replace(s0, rr_cursor=cfg.n_threads)
    assert "KAPPA_RANGE" in check_invariants(bad, cfg)
