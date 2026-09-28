"""Implicit information ι_m and the order-m exact ceiling
(docs/implicit-information-design-v0.1.md §4)."""
from fractions import Fraction as F

import pytest

from yupi.implicit_info import implicit_info, suffix_view
from yupi.records import Record


def R(kind, actor=None, obj=None, related=None, lineage=None):
    return Record(kind, actor, obj, related, lineage)


def test_markov_table_has_zero_implicit_information():
    # P* depends only on the last record: two histories, same last record, same law.
    nxt = {R("DISPATCH", 0): F(1, 3), R("STEP", 0): F(2, 3)}
    table = {
        (False, (R("DISPATCH", 0), R("STEP", 0))): (F(1, 4), dict(nxt)),
        (True, (R("DISPATCH", 0), R("DISPATCH", 1), R("STEP", 1))): (F(3, 4),
            {R("DISPATCH", 1): F(1, 3), R("STEP", 1): F(2, 3)}),
    }
    out = implicit_info(table, m=1)
    assert all(v == pytest.approx(0.0, abs=1e-15) for v in out["per_class"].values())
    assert out["H_m"] == pytest.approx(out["H_bar"], abs=1e-12)
    assert out["n_groups"] == 1


def test_two_classes_one_suffix_hand_computed():
    # Same last record, opposite deterministic continuations, equal mass:
    # P*_1 = (1/2, 1/2), so ι_1 = KL(δ ‖ uniform) = 1 bit for each class.
    table = {
        (False, (R("IO_ISSUE", 0), R("DISPATCH", 0))): (F(1, 2), {R("STEP", 0): F(1)}),
        (False, (R("BLOCK", 0), R("DISPATCH", 0))): (F(1, 2), {R("IDLE"): F(1)}),
    }
    out = implicit_info(table, m=1)
    assert sorted(out["per_class"].values()) == [pytest.approx(1.0), pytest.approx(1.0)]
    assert out["mean_iota_kl"] == pytest.approx(1.0)
    assert out["mean_iota_ent"] == pytest.approx(1.0)
    assert out["H_m"] == pytest.approx(1.0) and out["H_bar"] == pytest.approx(0.0)


def test_identity_mean_kl_equals_entropy_gap_on_uneven_table():
    table = {
        (False, (R("A", 0), R("B", 0))): (F(1, 5), {R("X", 0): F(1, 4), R("Y", 0): F(3, 4)}),
        (True, (R("C", 0), R("B", 0))): (F(3, 10), {R("X", 0): F(2, 3), R("Z"): F(1, 3)}),
        (False, (R("A", 0), R("D", 1))): (F(1, 2), {R("X", 1): F(1)}),
    }
    out = implicit_info(table, m=1)
    assert out["mean_iota_kl"] == pytest.approx(out["mean_iota_ent"], abs=1e-12)
    assert out["mean_iota_kl"] > 0


def test_entity_seen_only_before_the_suffix_becomes_fresh():
    pw = (R("ACQUIRE", 0, ("LOCK", 0)), R("DISPATCH", 1))
    s, beta = suffix_view(pw, 1)
    assert s == (R("DISPATCH", 0),)
    table = {(False, pw): (F(1), {R("DISPATCH", 0): F(1, 4), R("DISPATCH", 1): F(1, 4),
                                   R("RELEASE", 0, ("LOCK", 0)): F(1, 2)})}
    out = implicit_info(table, m=1, keep_laws=True)
    q = out["laws"][(False, pw)]
    # thread 1 is the suffix's thread 0; thread 0 (seen before the suffix) is fresh: index 1;
    # lock 0 was never in the suffix, so it is fresh too: index 0 of its type.
    assert q == {R("DISPATCH", 1): F(1, 4), R("DISPATCH", 0): F(1, 4),
                 R("RELEASE", 1, ("LOCK", 0)): F(1, 2)}
    assert out["H_star"] == pytest.approx(1.5)


def test_coarsening_merges_seen_earlier_and_fresh():
    # thread 0 seen before the suffix vs a genuinely fresh thread 2: an order-1 observer
    # cannot tell them apart, so both map to the suffix-fresh index and H_bar < H_star.
    pw = (R("DISPATCH", 0), R("DISPATCH", 1))
    table = {(False, pw): (F(1), {R("DISPATCH", 0): F(1, 2), R("DISPATCH", 2): F(1, 2)})}
    out = implicit_info(table, m=1)
    assert out["H_star"] == pytest.approx(1.0)
    assert out["H_bar"] == pytest.approx(0.0)
