"""Pins for `docs/c1-residual-ambiguity-census-v0.1.md` (2026-09-03): the
committed census artifacts say what they are cited as saying, and the
exhaustion check reproduces from the enumerator.
"""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.programs import c1_programs

DOCS = pathlib.Path(__file__).parent.parent / "docs"


def _row(L, eps):
    d = json.load(open(DOCS / f"c1-residual-ambiguity-census-14-{L}-2-2026-09-03.json"))
    return next(r for r in d["rows"] if r["eps"] == eps)


@pytest.mark.parametrize("L,eps,amb", [(4, "1", 0.670), (4, "1/2", 0.668), (8, "1", 0.165),
                                       (8, "1/2", 0.145), (10, "1", 0.040), (10, "1/2", 0.020)])
def test_ambiguous_mass_falls_along_L(L, eps, amb):
    assert round(_row(L, eps)["ambiguous_mass"], 3) == amb


@pytest.mark.parametrize("L", [4, 8, 10])
@pytest.mark.parametrize("eps", ["1", "1/2"])
def test_pc_only_and_queue_order_are_unreachable_by_any_rung(L, eps):
    sig = {tuple(s["fields"]): s for s in _row(L, eps)["signatures"]}
    assert sig[("pc",)]["split_by"] == {"r2": 0, "r3": 0, "r4": 0}
    if ("status", "lock_wq") in sig:
        assert sig[("status", "lock_wq")]["split_by"] == {"r2": 0, "r3": 0, "r4": 0}


@pytest.mark.parametrize("L,n_r2,n_win", [(4, 108, 539), (8, 1871, 3353), (10, 1788, 1888)])
def test_lock_ownership_is_the_rung_reachable_residual(L, n_r2, n_win):
    for eps in ("1", "1/2"):
        s = {tuple(x["fields"]): x for x in _row(L, eps)["signatures"]}[("pc", "lock_owner")]
        assert (s["split_by"]["r2"], s["n_windows"]) == (n_r2, n_win)
        assert s["split_by"]["r3"] == s["split_by"]["r4"] > s["split_by"]["r2"]


def test_pc_only_dominates_at_L10_and_unreachable_share_rises():
    for eps in ("1", "1/2"):
        r = _row(10, eps)
        sig = {tuple(s["fields"]): s for s in r["signatures"]}
        assert sig[("pc",)]["mass"] > 0.5 * r["ambiguous_mass"]
    shares = []
    for L in (4, 8, 10):
        r = _row(L, "1")
        unreach = sum(s["mass"] for s in r["signatures"] if s["split_by"]["r4"] == 0)
        shares.append(unreach / r["ambiguous_mass"])
    assert shares[0] < shares[1] < shares[2]
    assert round(shares[0], 2) == 0.24 and round(shares[2], 2) == 0.64


def test_no_exhaustion_within_14_records():
    for eps, expect in ((Fraction(1), 0.04), (Fraction(1, 2), 0.0)):
        cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
        term = sum(p * sum(1 for st in s.status if st[0] == "TERMINATED")
                   for _, p, s in paths(cfg, progs, 14))
        assert round(float(term), 2) == expect
