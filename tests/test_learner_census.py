"""The window census summarizer (yupi.learner.census): per-window excesses ->
tail shares, per-class aggregates, worst windows. Pure arithmetic on rows;
no model, no exact side."""
import math

import numpy as np
import pytest

from yupi.learner.census import summarize


def _rows():
    # 100 windows in three classes; class "B" carries a fat tail: two windows at 5.0 bits
    rows = []
    for i in range(100):
        cls = ("A", "B", "C")[i % 3]
        x = 0.1 if cls != "B" else 0.2
        if i in (7, 43):                        # both in class B (7 % 3 == 1, 43 % 3 == 1)
            x = 5.0
        if i == 12:                             # a negative window (model beat the ceiling on the realized record)
            x = -0.3
        rows.append(dict(i=i, key=cls, structural=x, naming=0.01,
                         by_field=dict(kind=x / 2, actor=x / 2, obj=0.0, related=0.0, lineage=0.0)))
    return rows


def test_mean_and_tail_shares():
    s = summarize(_rows(), top=3)
    xs = np.array([r["structural"] for r in _rows()])
    assert s["n"] == 100
    assert abs(s["mean"] - xs.mean()) < 1e-12
    assert s["negative_share"] == 0.01
    # the top 1% (1 window) carries 5.0 of the total; top 5% (5 windows) carries 5+5+0.2*3
    total = xs.sum()
    assert abs(s["tail_share"]["0.01"] - 5.0 / total) < 1e-12
    assert abs(s["tail_share"]["0.05"] - (10.0 + 0.6) / total) < 1e-12
    assert s["quantiles"]["0.5"] == pytest.approx(np.quantile(xs, 0.5))
    assert s["max"] == 5.0


def test_per_class_aggregates_and_worst_windows():
    s = summarize(_rows(), top=3)
    assert s["n_classes"] == 3
    top = s["classes"]                           # ordered by summed excess, descending
    assert [c["key"] for c in top] == ["B", "A", "C"] or [c["key"] for c in top] == ["B", "C", "A"]
    b = top[0]
    assert b["n"] == 33 and abs(b["mean"] - (31 * 0.2 + 10.0) / 33) < 1e-12
    assert abs(b["share"] - (31 * 0.2 + 10.0) / sum(r["structural"] for r in _rows())) < 1e-12
    assert abs(b["by_field"]["kind"] - b["mean"] / 2) < 1e-12
    assert [w["i"] for w in s["worst"]][:2] == [7, 43] or [w["i"] for w in s["worst"]][:2] == [43, 7]
    assert len(s["worst"]) == 3 and s["worst"][2]["structural"] == 0.2


def test_variance_split_within_between():
    """Total per-window variance splits into a pooled within-class part (classes
    with n >= 2) and the remainder attributed to class; a table where every
    class is constant has within = 0; one where classes have equal means has
    between share ≈ 0."""
    from yupi.learner.census import variance_split
    rows = [dict(i=i, key=i % 4, structural=float(i % 4), naming=0.0, by_field={}) for i in range(40)]
    v = variance_split(rows)
    assert v["within"] == 0.0 and v["between_share"] == pytest.approx(1.0)
    rows = [dict(i=i, key=i % 2, structural=float((-1) ** i), naming=0.0, by_field={}) for i in range(40)]
    v = variance_split(rows)      # class 0 all +1, class 1 all -1 -> within 0 again
    assert v["within"] == 0.0
    rows = [dict(i=i, key=i % 2, structural=float((-1) ** (i // 2)), naming=0.0, by_field={}) for i in range(40)]
    v = variance_split(rows)      # each class alternates ±1 -> all variance within
    assert v["between_share"] == pytest.approx(0.0, abs=1e-12)


def test_attribute_by_outcome_is_a_signed_decomposition_of_the_total():
    """attribute(rows, features): per feature and value, n, mean, se, share and
    by_field means; shares over a feature's values sum to 1 (signed: a value's
    mean may be negative — conditioning on an outcome is not a KL)."""
    from yupi.learner.census import attribute
    rows = [dict(i=i, key=0, structural=x, naming=0.0, by_field=dict(kind=x, actor=0.0, obj=0.0, related=0.0, lineage=0.0))
            for i, x in enumerate([1.0, 1.0, -0.5, 2.0, 0.5, 0.0])]
    feats = [dict(kind="A", fresh=True), dict(kind="A", fresh=False), dict(kind="B", fresh=False),
             dict(kind="B", fresh=True), dict(kind="C", fresh=False), dict(kind="C", fresh=False)]
    a = attribute(rows, feats)
    assert set(a) == {"kind", "fresh"}
    assert sum(v["share"] for v in a["kind"].values()) == pytest.approx(1.0)
    assert a["kind"]["A"]["n"] == 2 and a["kind"]["A"]["mean"] == 1.0 and a["kind"]["A"]["share"] == 2.0 / 4.0
    assert a["kind"]["B"]["mean"] == 0.75 and a["kind"]["B"]["by_field"]["kind"] == 0.75
    assert a["fresh"]["True"]["n"] == 2 and a["fresh"]["True"]["share"] == 3.0 / 4.0
    assert a["kind"]["C"]["se"] == pytest.approx(np.std([0.5, 0.0], ddof=1) / math.sqrt(2))


def test_record_features_of_the_predicted_record():
    """record_features(prefix, nxt): the realized kind, whether its actor is
    fresh (not an actor in the prefix) or bound, the number of distinct
    actors in the prefix, and the joint kind/actor label."""
    from yupi.learner.census import record_features
    from yupi.records import Record
    R = lambda kind, actor: Record(kind, actor, None, "MASKED", "MASKED")
    prefix = (R("DISPATCH", "T01"), R("RELEASE", "T02"), R("DISPATCH", "T01"))
    f = record_features(prefix, R("BLOCK", "T07"))
    assert f == dict(kind="BLOCK", actor="fresh", nthreads=2, kind_actor="BLOCK/fresh")
    f = record_features(prefix, R("STEP", "T02"))
    assert f == dict(kind="STEP", actor="bound", nthreads=2, kind_actor="STEP/bound")
    f = record_features((R("IDLE", None),), R("DISPATCH", "T03"))       # IDLE has no actor
    assert f["nthreads"] == 0 and f["actor"] == "fresh"
