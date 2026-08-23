"""Witness 7 (Part II §9): the D8 shuffled order mode.

Statute (Part II §4, order modes): shuffled = uniform within-bucket
permutation, a stochastic kernel whose likelihood of a visible sequence is
m/B! where m is the number of permutations of the latent bucket producing
it (duplicates make m > 1). The filter multiplies world-path probability by
this channel likelihood; it never assumes uniformity over causally possible
latent orders.

Witness 7 requires: (a) a bucket with two noncommuting events where order
mode changes a posterior; (b) the filter validated against a hand-computed
channel likelihood, including a duplicate-record bucket (m > 1). We add
(c) the two-path gate: shuffled filter equals an independent enumerator-side
computation bit-for-bit, and (d) ordered mode at B ticks equals the existing
per-record filter exactly (identity serialization).
"""
from dataclasses import replace
from fractions import Fraction
from itertools import permutations

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import initial_belief, step
from yupi.interfaces import project
from yupi.programs import c0b_programs, c1_programs
from yupi.records import Record
from yupi.shuffled import (channel_likelihood, multiset_key, run_buckets,
                           step_bucket, step_ordered_bucket)


def _bucket_posterior_by_paths(cfg, progs, visible_buckets, rung, B):
    """Independent path-summation side of the two-path gate: enumerate every
    latent path of length B*len(buckets); weight = path prob × Π channel
    likelihoods; collapse to final state. No filter code used."""
    H = B * len(visible_buckets)
    out = {}
    for recs, p, s in paths(cfg, progs, H):
        w = p
        for b, vis in enumerate(visible_buckets):
            latent = [project(r, rung) for r in recs[b * B:(b + 1) * B]]
            w *= channel_likelihood(latent, vis)
            if w == 0:
                break
        if w:
            out[s] = out.get(s, Fraction(0)) + w
    Z = sum(out.values(), Fraction(0))
    return {s: m / Z for s, m in out.items()}


# ---- (b) hand-computed channel likelihood -------------------------------

R_A = Record(kind="DISPATCH", actor=0, obj=None, related=None, lineage=None)
R_B = Record(kind="IO_ISSUE", actor=0, obj=("DEV", 0), related=None, lineage=0)


def test_likelihood_distinct_records_is_one_over_B_factorial():
    # latent [A, B]; visible [A, B] is produced by exactly 1 of 2! permutations
    assert channel_likelihood([R_A, R_B], [R_A, R_B]) == Fraction(1, 2)
    assert channel_likelihood([R_A, R_B], [R_B, R_A]) == Fraction(1, 2)


def test_likelihood_duplicate_records_m_greater_than_one():
    # latent [A, A]: both permutations produce visible [A, A] → m = 2, m/B! = 1
    assert channel_likelihood([R_A, R_A], [R_A, R_A]) == Fraction(1)
    # B = 3 with one duplicate pair: m = 2!·1! = 2 of 3! = 6
    assert channel_likelihood([R_A, R_A, R_B], [R_B, R_A, R_A]) == Fraction(2, 6)


def test_likelihood_zero_when_multisets_differ():
    assert channel_likelihood([R_A, R_B], [R_A, R_A]) == 0


def test_likelihood_matches_literal_permutation_count():
    # the statute's definition, computed literally, for every visible order
    latent = [R_A, R_A, R_B]
    for vis in set(permutations(latent)):
        m = sum(1 for perm in permutations(latent) if list(perm) == list(vis))
        assert channel_likelihood(latent, list(vis)) == Fraction(m, 6)


# ---- (d) ordered mode is identity serialization ---------------------------

@pytest.mark.parametrize("rung", ["r1", "r4"])
def test_ordered_bucket_equals_per_record_filter(rung):
    cfg, progs = WorldConfig.c0b(discipline="stochastic"), c0b_programs()
    recs, _, _ = paths(cfg, progs, 4)[0]
    vis = [project(r, rung) for r in recs]
    b = initial_belief(cfg)
    for r in vis:
        b = step(b, r, rung, cfg, progs)
    assert step_ordered_bucket(step_ordered_bucket(initial_belief(cfg), vis[:2], rung, cfg, progs),
                               vis[2:], rung, cfg, progs) == b


# ---- (a) a noncommuting bucket where order mode changes the posterior ------

def _find_noncommuting_bucket(cfg, progs, rung, B, H):
    """Search latent paths for a bucket whose reversed order is also
    realizable but leads to a different posterior. Returns (prefix_buckets,
    bucket_visible) or None. Asserted non-empty by the test, per the C0b
    design note that C0b 'supplies a candidate bucket containing two
    noncommuting events'."""
    seen = set()
    for recs, _, _ in paths(cfg, progs, H):
        for b in range(H // B):
            vis_prefix = [[project(r, rung) for r in recs[k * B:(k + 1) * B]] for k in range(b)]
            latent = [project(r, rung) for r in recs[b * B:(b + 1) * B]]
            key = (tuple(map(tuple, vis_prefix)), multiset_key(latent))
            if len(set(latent)) < 2 or key in seen:
                continue
            seen.add(key)
            belief = run_buckets(cfg, progs, vis_prefix, rung, B, mode="ordered") if vis_prefix else initial_belief(cfg)
            ordered = step_ordered_bucket(belief, latent, rung, cfg, progs)
            shuffled = step_bucket(belief, latent, rung, cfg, progs)
            if ordered != shuffled:
                return vis_prefix, latent
    return None


def test_c0b_shuffled_channel_is_information_free_at_eps_1():
    """NEGATIVE witness (measured 2026-08-23): Part I's C0b paragraph says
    C0b 'supplies a candidate bucket containing two noncommuting events'.
    At ε = 1 it does not, for any B ≤ 4 and H ≤ 8, either discipline: C0b has
    no locks (no wait-queue order) and no cursor (ε = 1), so every same-
    multiset reordering of a realizable bucket reaches the same state.
    This test pins the refutation; if it ever fails, the statute line was
    right and this note is wrong."""
    for disc in ("stochastic", "fifo"):
        cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
        for B in (2, 3, 4):
            assert _find_noncommuting_bucket(cfg, progs, "r4", B=B, H=8) is None, (disc, B)


def test_w7_noncommuting_bucket_in_c1_at_B3_and_order_mode_changes_posterior():
    """Witness 7, relocated to C1 (as witnesses 1–2 were): at ε = 1 the first
    noncommuting bucket is BLOCK·DISPATCH·BLOCK on one lock — order fixes
    the wait-queue (I2). Same-lock BLOCKs are never adjacent (dispatch fills
    the freed CPU first), so B = 2 can never expose it; B = 3 aligned at
    ticks 7–9 does."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    assert _find_noncommuting_bucket(cfg, progs, "r4", B=2, H=8) is None
    found = _find_noncommuting_bucket(cfg, progs, "r4", B=3, H=9)
    assert found is not None
    prefix, latent = found
    kinds = sorted(r.kind for r in latent)
    assert kinds.count("BLOCK") == 2
    belief = run_buckets(cfg, progs, prefix, "r4", 3, mode="ordered") if prefix else initial_belief(cfg)
    ordered = step_ordered_bucket(belief, latent, "r4", cfg, progs)
    shuffled = step_bucket(belief, latent, "r4", cfg, progs)
    assert set(ordered) <= set(shuffled) and ordered != shuffled


def test_at_eps_half_B2_channel_carries_only_cursor_information():
    """At ε = ½ the B = 2 channel differs from ordered already at bucket 0
    ([DISPATCH T0, DISPATCH T1]): the two dispatches commute except through
    rr_cursor. The state marginal *without* the cursor must agree."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs()
    found = _find_noncommuting_bucket(cfg, progs, "r4", B=2, H=4)
    assert found is not None
    prefix, latent = found
    belief = run_buckets(cfg, progs, prefix, "r4", 2, mode="ordered") if prefix else initial_belief(cfg)
    o = step_ordered_bucket(belief, latent, "r4", cfg, progs)
    s = step_bucket(belief, latent, "r4", cfg, progs)
    def drop_cursor(b):
        out = {}
        for st, m in b.items():
            k = replace(st, rr_cursor=0)
            out[k] = out.get(k, Fraction(0)) + m
        return out
    assert o != s
    assert drop_cursor(o) == drop_cursor(s)


# ---- (c) two-path gate ---------------------------------------------------

@pytest.mark.parametrize("cfg,progs,rung,B,H", [
    (WorldConfig.c0b(discipline="stochastic"), c0b_programs(), "r4", 2, 6),
    (WorldConfig.c0b(discipline="fifo"), c0b_programs(), "r1", 2, 6),
    (WorldConfig.c0b(discipline="stochastic"), c0b_programs(), "r2", 3, 6),
])
def test_shuffled_filter_matches_enumerator_bit_for_bit(cfg, progs, rung, B, H):
    checked = 0
    for recs, _, _ in paths(cfg, progs, H)[:40]:
        buckets = [[project(r, rung) for r in recs[k * B:(k + 1) * B]] for k in range(H // B)]
        # deliver each bucket in a deterministic non-identity order to exercise the channel
        vis = [list(reversed(b)) for b in buckets]
        f = run_buckets(cfg, progs, vis, rung, B, mode="shuffled")
        e = _bucket_posterior_by_paths(cfg, progs, vis, rung, B)
        assert f == e
        checked += 1
    assert checked == min(40, len(paths(cfg, progs, H)))


