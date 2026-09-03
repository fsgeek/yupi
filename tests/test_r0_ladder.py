"""Pins for `docs/r0-ladder-census-v0.1.md` (2026-09-03, exploratory): the
kind-only rung r0 keeps the interface axis's range at every context, is not
injective at full context, and is cheap. Artifact pins plus one enumerator
check that r0 breaks full-context injectivity where r1 does not.
"""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.queries import state_entropy_bits

DOCS = pathlib.Path(__file__).parent.parent / "docs"


def _rows(L):
    d = json.load(open(DOCS / f"r0-ladder-census-14-{L}-2-2026-09-03.json"))
    return {(r["eps"], r["rung"]): r for r in d["rows"]}, {b["eps"]: b for b in d["r0"]}


@pytest.mark.parametrize("L", [2, 4, 6, 8, 10, 12, 14])
def test_r0_to_r1_step_keeps_range_at_every_context(L):
    rows, _ = _rows(L)
    for eps in ("1", "1/2"):
        g = lambda r: rows[(eps, r)]["predictive"]["kinds2"]["gap"]
        assert g("r0") - g("r1") >= (0.30 if L == 2 else 0.48), (L, eps, g("r0"), g("r1"))
        assert g("r0") >= g("r1") >= g("r2") >= g("r3") >= g("r4") - 1e-12
        if L >= 12:
            assert g("r1") < 0.001 and g("r0") > 0.48


@pytest.mark.parametrize("L,eps,plateau", [(12, "1", 2.577), (14, "1", 2.577), (12, "1/2", 2.375), (14, "1/2", 2.375)])
def test_r0_is_not_injective_at_full_context(L, eps, plateau):
    rows, _ = _rows(L)
    assert round(rows[(eps, "r0")]["mean_state_entropy_bits"], 3) == plateau
    assert rows[(eps, "r1")]["mean_state_entropy_bits"] < 0.002


@pytest.mark.parametrize("L", [2, 4, 6, 8, 10, 12, 14])
def test_r0_is_cheap_and_filter_sample_agrees(L):
    rows, r0 = _rows(L)
    for eps in ("1", "1/2"):
        assert rows[(eps, "r0")]["max_support"] <= 282
        fs = r0[eps]["filter_sample"]
        assert fs["mismatches"] == 0 and fs["n"] == 20 and fs["seconds"] < 30
        assert r0[eps]["ambiguous_mass"] > 0.97


def test_r1_splits_every_r0_window_at_long_context():
    rows, r0 = _rows(12)
    for eps in ("1", "1/2"):
        for e in r0[eps]["residual"]:
            assert e["split_by_r1"] == e["n_windows"], (eps, e["fields"])


def test_r0_breaks_full_context_injectivity_from_enumerator():
    """At (6, 6, 2), full context from reset: r1 windows are point masses
    (the injectivity theorem); r0 windows are not."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    agg = {"r0": {}, "r1": {}}
    for recs, prob, final in paths(cfg, progs, 6):
        for r in agg:
            k = tuple(project(x, r) for x in recs)
            d = agg[r].setdefault(k, {})
            d[final] = d.get(final, Fraction(0)) + prob
    assert all(len(j) == 1 for j in agg["r1"].values())
    H = sum(float(sum(j.values())) * state_entropy_bits({s: m / sum(j.values()) for s, m in j.items()})
            for j in agg["r0"].values())
    assert H > 1.0 and len(agg["r0"]) < len(agg["r1"])
