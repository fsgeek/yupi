"""Part II proposal v0.2.7.1 Clause 2 — the synchronization horizon's
truncation-conditional mean, corrected for a non-injective rung:

    E[H | U > 0] = (H_law − H_{U=0}) / Pr(U > 0)

which equals the v0.2.5 closed form T_ep/(T_ep − L) · H_law exactly when
H_{U=0} = 0 (every rung r1–r4, by full-context injectivity of the reset-
anchored windows) and differs for r0. Owed by the proposal as "the
corrected-formula producer with a regression pinning every committed
r1–r4 horizon unchanged". Written before `yupi.sync` existed.
"""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.programs import c1_programs
from yupi.queries import state_entropy_bits
from yupi.sync import conditional_from_aggregate, conditional_from_by_endpoint
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregates

DOCS = pathlib.Path(__file__).parent.parent / "docs"


@pytest.fixture(scope="module")
def aggs_14_4_2():
    return window_law_aggregates(WorldConfig.c1(epsilon=Fraction(1)), c1_programs(),
                                 WindowLaw(T_ep=14, L=4, B=2))


@pytest.mark.parametrize("rung", ["r1", "r2", "r3", "r4"])
def test_r1_to_r4_reduce_to_the_closed_form(aggs_14_4_2, rung):
    law = WindowLaw(T_ep=14, L=4, B=2)
    c = conditional_from_aggregate(aggs_14_4_2[rung], law, state_entropy_bits)
    assert c["H_U0"] == 0.0                              # injective from reset
    assert c["P_U_pos"] == Fraction(10, 14)              # (T_ep − L)/T_ep
    assert c["E_H_given_U_pos"] == pytest.approx(c["H_law"] * 14 / 10, rel=1e-12)


def test_r0_needs_the_correction(aggs_14_4_2):
    law = WindowLaw(T_ep=14, L=4, B=2)
    c = conditional_from_aggregate(aggs_14_4_2["r0"], law, state_entropy_bits)
    assert c["H_U0"] > 0.1                                # r0 is not injective from reset
    closed_form = c["H_law"] * 14 / 10
    assert c["E_H_given_U_pos"] < closed_form - 0.1       # the closed form overstates r0
    assert c["E_H_given_U_pos"] == pytest.approx((c["H_law"] - c["H_U0"]) / float(c["P_U_pos"]), rel=1e-12)


def test_committed_artifact_by_endpoint_reproduces_the_closed_form():
    """Every committed r1–r4 truncation-conditional value (v0.2.5 semantics,
    the T_ep/(T_ep − L) factor used in c1-sync-sweep-v0.1.md) is reproduced
    from the artifact's per-endpoint means by the corrected formula — i.e.
    the committed horizons are unchanged."""
    for L in (4, 8, 12):
        d = json.load(open(DOCS / f"c1-query-ceilings-14-{L}-2-corrected-2026-08-20.json"))
        law = WindowLaw(T_ep=14, L=L, B=2)
        for row in d["rows"]:
            for q in ("mean_state_entropy_bits", "Q1[L0]", "Q2[T0]"):
                c = conditional_from_by_endpoint(row["by_endpoint"], law, q)
                law_mass = row["mean_state_entropy_bits"] if q == "mean_state_entropy_bits" else row["queries"][q]["mean_bits"]
                assert c["H_law"] == pytest.approx(law_mass, abs=1e-9), (L, row["eps"], row["rung"], q)
                assert c["H_U0"] == pytest.approx(0.0, abs=1e-12)
                assert c["E_H_given_U_pos"] == pytest.approx(law_mass * 14 / (14 - L), rel=1e-9)


def test_by_endpoint_and_aggregate_agree(aggs_14_4_2):
    """The two entry points compute the same conditional on the same law."""
    law = WindowLaw(T_ep=14, L=4, B=2)
    c_agg = conditional_from_aggregate(aggs_14_4_2["r0"], law, state_entropy_bits)
    reset_mass = sum(sum(j.values(), Fraction(0)) for (reset, _), j in aggs_14_4_2["r0"].items() if reset)
    assert reset_mass == 1 - c_agg["P_U_pos"]
