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
from math import factorial

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import initial_belief, step
from yupi.interfaces import project
from yupi.programs import c0b_programs, c1_programs
from yupi.records import Record
from yupi.shuffled import (channel_likelihood, multiset_key, run_buckets,
                           step_bucket, step_ordered_bucket)


def _literal_likelihood(latent, visible):
    """Test-side channel likelihood by literal permutation count (the
    statute's definition), independent of yupi.shuffled.channel_likelihood."""
    n = len(latent)
    m = sum(1 for perm in permutations(range(n)) if [latent[i] for i in perm] == list(visible))
    return Fraction(m, factorial(n))


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
            w *= _literal_likelihood(latent, vis)
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


def test_c0b_shuffled_channel_is_null_at_r4_only():
    """Scoped negative witness (corrected 2026-08-23 after truthsayer review):
    at r4 — lineage visible — no C0b bucket's order changes a posterior for
    B ≤ 4, H ≤ 8, either discipline. The v0.1 note over-generalized this to
    "C0b has no noncommuting bucket"; it has them at r1–r3 (next test)."""
    for disc in ("stochastic", "fifo"):
        cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
        for B in (2, 3, 4):
            assert _find_noncommuting_bucket(cfg, progs, "r4", B=B, H=8) is None, (disc, B)


@pytest.mark.parametrize("disc", ["fifo", "stochastic"])
@pytest.mark.parametrize("rung", ["r1", "r2", "r3"])
def test_w7_c0b_supplies_noncommuting_bucket_at_masked_lineage(disc, rung):
    """Witness 7 in C0b, as Part I says: at r1–r3 the bucket
    [IO_COMPLETE T0, IO_ISSUE T1, IDLE] at B = 3 is order-sensitive —
    completion-before-issue vs issue-before-completion changes request-id
    allocation (lowest-free) and hence status/dev_q, while the masked
    lineage hides which happened. At r4 the lineage values disambiguate."""
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    found = _find_noncommuting_bucket(cfg, progs, rung, B=3, H=6)
    assert found is not None
    prefix, latent = found
    assert {r.kind for r in latent} >= {"IO_COMPLETE", "IO_ISSUE"}
    belief = run_buckets(cfg, progs, prefix, rung, 3, mode="ordered") if prefix else initial_belief(cfg)
    o = step_ordered_bucket(belief, latent, rung, cfg, progs)
    sh = step_bucket(belief, latent, rung, cfg, progs)
    assert set(o) <= set(sh) and o != sh


def test_w7_c1_r4_wait_queue_bucket_at_B3():
    """Witness 7 in C1 at r4: at ε = 1 the first r4 noncommuting bucket is
    BLOCK·DISPATCH·BLOCK on one lock — order fixes
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
    """At ε = ½, r4, B = 2 the channel differs from ordered already at bucket 0
    ([DISPATCH T0, DISPATCH T1]): the two dispatches commute except through
    rr_cursor. The state marginal *without* the cursor must agree. Scoped to
    this bucket at r4; not a claim about the ladder."""
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




@pytest.mark.parametrize("rung", ["r1", "r2", "r3"])
def test_c1_B2_allocator_bucket_appears_at_H12_at_masked_lineage(rung):
    """Reproduced 2026-08-23 (truthsayer residual): at C1 ε = 1, B = 2 the
    coarse rungs acquire an order-sensitive bucket [IO_COMPLETE T0,
    IO_ISSUE T3] by H = 12 — the allocator mechanism — while none exists at
    H ≤ 8. The earlier null was a horizon boundary, not a property of B = 2.
    r4 remains null at H = 12 (lineage disambiguates; ~50 s, not asserted
    here)."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    assert _find_noncommuting_bucket(cfg, progs, rung, B=2, H=8) is None
    found = _find_noncommuting_bucket(cfg, progs, rung, B=2, H=12)
    assert found is not None
    assert {r.kind for r in found[1]} == {"IO_COMPLETE", "IO_ISSUE"}
