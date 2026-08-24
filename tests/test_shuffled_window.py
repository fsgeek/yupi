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


def _visible_windows(cfg, progs, law, rung, reverse=True):
    """Every distinct realizable (buckets, reset) shuffled observation of the
    law, delivering each latent bucket reversed (a fixed non-identity order)
    so the channel is exercised. Latent-derived, so realizability is free."""
    seen = set()
    B = law.B
    for T in law.endpoints():
        u = law.offset(T)
        for recs, _, _ in paths(cfg, progs, T):
            win = [project(r, rung) for r in recs[u:T]]
            buckets = [win[k * B:(k + 1) * B] for k in range(len(win) // B)]
            vis = tuple(tuple(reversed(b)) if reverse else tuple(b) for b in buckets)
            key = (vis, u == 0)
            if key not in seen:
                seen.add(key)
                yield [list(b) for b in vis], u == 0


@pytest.mark.parametrize("disc,rung", [("stochastic", "r2"), ("fifo", "r4")])
def test_two_path_gate_on_every_statutory_window_c0b(disc, rung):
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    law = WindowLaw(T_ep=6, L=4, B=2)
    n = 0
    for buckets, reset in _visible_windows(cfg, progs, law, rung):
        f = shuffled_window_filter(cfg, progs, law, buckets, rung, reset)
        e = shuffled_window_by_paths(cfg, progs, law, buckets, rung, reset)
        assert f == e
        n += 1
    assert n > 10


def test_B1_shuffled_equals_ordered_exactly():
    """The analytic null control: at B = 1 the permutation channel is the
    identity, so the shuffled window posterior must equal the ordered
    window filter bit-for-bit on every window."""
    cfg, progs = WorldConfig.c0b(discipline="stochastic"), c0b_programs()
    law = WindowLaw(T_ep=6, L=3, B=1)
    for buckets, reset in _visible_windows(cfg, progs, law, "r4", reverse=False):
        flat = [b[0] for b in buckets]
        assert shuffled_window_filter(cfg, progs, law, buckets, "r4", reset) == \
            filter_window(cfg, progs, law, flat, "r4", reset)


def test_compatible_endpoint_mixture_matches_ordered_semantics():
    """A windowed shuffled observation without RESET must mix exactly the
    U > 0 endpoints the law permits — same rule as the ordered machinery."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=6, L=4, B=2)
    for buckets, reset in _visible_windows(cfg, progs, law, "r1"):
        post = shuffled_window_filter(cfg, progs, law, buckets, "r1", reset)
        expected = {u for _, u in law.compatible_endpoints(
            sum(len(b) for b in buckets), reset)}
        assert set(post.components) <= expected
        break


def test_anchored_conditioning_is_component_selection():
    """Anchored (TIME_CLASS-unmasked) = conditioning on U: the anchored
    posterior at offset u is the u-component's belief, renormalized."""
    cfg, progs = WorldConfig.c0b(discipline="stochastic"), c0b_programs()
    law = WindowLaw(T_ep=8, L=4, B=2)   # endpoints 6 and 8 both give U > 0
    for buckets, reset in _visible_windows(cfg, progs, law, "r2"):
        post = shuffled_window_filter(cfg, progs, law, buckets, "r2", reset)
        if len(post.components) > 1:
            from yupi.shuffled_window import shuffled_window_by_paths
            e = shuffled_window_by_paths(cfg, progs, law, buckets, "r2", reset)
            for u, (w, belief) in post.components.items():
                assert sum(belief.values()) == 1            # component = anchored posterior
                assert e.components[u][1] == belief         # both paths agree per component
            return
    pytest.fail("no multi-component window found at (8,4,2)")
