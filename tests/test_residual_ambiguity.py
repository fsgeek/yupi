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
        # v0.1.1: per WINDOW — ambiguous mass minus mass actually split by r4
        # (the v0.1 per-signature figure understated: 0.24 / 0.53 / 0.64)
        reach = sum(s["split_mass"]["r4"] for s in r["signatures"])
        shares.append((r["ambiguous_mass"] - reach) / r["ambiguous_mass"])
    assert shares[0] < shares[1] < shares[2]
    assert [round(x, 2) for x in shares] == [0.48, 0.65, 0.72]


def test_no_exhaustion_within_14_records():
    for eps, expect in ((Fraction(1), 0.04), (Fraction(1, 2), 0.0)):
        cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
        term = sum(p * sum(1 for st in s.status if st[0] == "TERMINATED")
                   for _, p, s in paths(cfg, progs, 14))
        assert round(float(term), 2) == expect


@pytest.mark.parametrize("L,tag,r1_minus_r4,pnext_r1", [
    (2, "2026-08-20", 0.079, 0.764), (4, "2026-08-20", 0.076, 0.263), (6, "2026-09-03", 0.048, 0.081),
    (8, "2026-09-03", 0.023, 0.021), (10, "2026-09-03", 0.007, 0.003), (12, "2026-09-03", 0.000, 0.000)])
def test_exposure_side_ladder_collapses_on_the_same_horizon(L, tag, r1_minus_r4, pnext_r1):
    """Census note §7: the interface's share of the next-2-kinds observation
    gap at ε = 1 is under δ = 0.01 by L = 10 and zero by L = 12, and the whole
    predictive gap is gone with it."""
    d = json.load(open(DOCS / f"c1-predictive-targets-14-{L}-2-corrected-{tag}.json"))
    rows = {r["rung"]: r for r in d["rows"] if r["eps"] == "1"}
    g = lambda t, r: rows[r]["means"][t]["gap"]
    assert round(g("kinds2", "r1") - g("kinds2", "r4"), 3) == r1_minus_r4
    assert round(g("pnext", "r1"), 3) == pnext_r1
    assert g("kinds2", "r1") >= g("kinds2", "r2") >= g("kinds2", "r3") >= g("kinds2", "r4") - 1e-12
