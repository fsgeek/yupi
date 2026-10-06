"""Severity v4's generative extensions and bookkeeping (scripts/three_arm_severity_v4.py). Synthetic only."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import three_arm_severity_v4 as V  # noqa: E402

BIG = 200000


def _draw(**kw):
    return V.draw(np.random.default_rng(0), V.SDS["point"], kw.pop("muR", 0.0), kw.pop("rho", 0.0), n=BIG, **kw)


def test_clean_null_means_zero_and_sds_match_v3_targets():
    K_R, K_D, KS_R, KS_D = _draw()
    sd = V.SDS["point"]
    for x, want in ((K_R, sd["K_R"]), (K_R - KS_R, sd["Kp_R"]), (K_D, sd["K_D"]), (K_D - KS_D, sd["Kp_D"])):
        assert abs(x.mean()) < 4 * want / np.sqrt(BIG)
        assert x.std() == pytest.approx(want, rel=0.01)


def test_shared_delta_cancels_in_Kp_arm_specific_does_not():
    K_R, K_D, KS_R, KS_D = _draw(sh=("R", 0.006))
    assert K_R.mean() == pytest.approx(0.006, abs=1e-4) and abs((K_R - KS_R).mean()) < 1e-4
    K_R, K_D, KS_R, KS_D = _draw(as_=("D", 0.0015))
    assert (K_D - KS_D).mean() == pytest.approx(0.0015, abs=1e-4) and abs(KS_D.mean()) < 1e-4


def test_offphase_replaces_Kp_on_hit_seeds_jointly():
    rng = np.random.default_rng(1)
    K_R, K_D, KS_R, KS_D = V.draw(rng, V.SDS["point"], 0.0, 0.0, off=dict(target="RD", p=0.2, v=2.5, mu_ref=0.006),
                                  n=BIG)
    hitR = np.isclose(K_R - KS_R, 2.5 * 0.006)
    hitD = np.isclose(K_D - KS_D, 2.5 * 0.006 * V.MD / V.MR)
    assert hitR.mean() == pytest.approx(0.2, abs=0.01)
    assert (hitR == hitD).all()                                         # the same seeds on both arms


def test_two_phase_mixture_preserves_the_mean():
    K_R, K_D, KS_R, KS_D = _draw(two=dict(target="RD", p=0.2, v=2.5, mu_ref=0.006))
    assert abs((K_R - KS_R).mean()) < 1e-4 and abs((K_D - KS_D).mean()) < 1e-4
    assert (K_R - KS_R).std() > V.SDS["point"]["Kp_R"] * 1.2


def test_claim_status():
    s = V._scen("null", "point", "B0", as_=("D", 0.0015))
    assert V.claim_status(s) == {"C1": "null", "C2": "null", "C3": "direct rival"}
    s = V._scen("null", "point", "B0", as_=("D", -0.0015))
    assert V.claim_status(s)["C3"] == "null"
    s = V._scen("null", "point", "B0", as_=("R", 0.004))
    assert V.claim_status(s) == {"C1": "alternative", "C2": "direct rival", "C3": "null"}
    assert V.claim_status(V._scen("null", "point", "B1")) == {"C1": "alternative", "C2": "alternative", "C3": "null"}
    assert V.claim_status(V._scen("null", "point", "B2")) == {"C1": "alternative", "C2": "null", "C3": "null"}
    assert V.claim_status(V._scen("power", "point", None, muR=0.006, rho=1.0))["C3"] == "alternative"


def test_wilson_upper():
    assert V.wilson_upper(0, 2000) == pytest.approx(0.00192, abs=1e-4)
    assert V.wilson_upper(100, 2000) > 0.05 > 100 / 2001


def test_grid_has_every_family_and_both_sd_sets():
    g = V.grid()
    fams = {s["family"] for s in g if s["kind"] == "null"}
    assert fams == {"clean", "arm-specific delta", "off-phase (one arm)", "off-phase (correlated across arms)",
                    "two-phase mixture (mean-preserving)", "heteroskedastic", "combined"}
    assert {s["sd"] for s in g} == {"point", "upper80"}
    assert [s["i"] for s in g] == list(range(len(g)))
