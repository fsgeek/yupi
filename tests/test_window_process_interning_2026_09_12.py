"""The window-process pass under the line (2026-09-12,
`docs/window-process-interning-note-v0.1.md`): the shared-object recursion
with the compact per-endpoint mass equals the 2026-09-04 recursion on every
rung at the frozen law (40,8,2), both ε, with the same key order; the
fresh-process re-price is under E3's 8 GB line at the identical frontier;
and MassT round-trips the dict-of-Fractions form on a small law."""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.programs import c1_programs
from yupi.window import WindowLaw
from yupi.window_process import MassT, window_law_aggregates

DOCS = pathlib.Path(__file__).parent.parent / "docs"
RUNGS = ("r0", "r1", "r2", "r3", "r4")
COUNTS = {  # (windows, aggregate entries, mass_T entries) per rung at (40,8,2), identical at both ε except r0's entries
    "r4": (1524612, 2248814, 9995214), "r3": (991585, 1631167, 7433505),
    "r2": (923461, 1631167, 7094476), "r1": (819073, 1631167, 6490210),
}


@pytest.mark.parametrize("tag,eps", [("", "1"), ("-eps1_2", "1/2")])
@pytest.mark.parametrize("kind", ["interning-only", "interned"])
def test_gate_against_the_2026_09_04_recursion_every_rung_equal(kind, tag, eps):
    d = json.load(open(DOCS / f"window-gate-{kind}-40-8-2-2026-09-12{tag}.json"))
    assert d["law"] == dict(T_ep=40, L=8, B=2) and d["programs"] == "c1prime-loop" and d["eps"] == eps
    assert d["verdict"] == "ALL RUNGS EQUAL" and d["max_pairs"] == 1964919
    assert set(d["rungs"]) == set(RUNGS)
    for r, row in d["rungs"].items():
        assert row["equal"] and row["same_key_order"], r
        if r in COUNTS:
            assert (row["n_windows"], row["agg_entries"], row["mass_T_entries"]) == COUNTS[r], r
    assert d["rungs"]["r0"]["n_windows"] == 12739 and d["rungs"]["r0"]["mass_T_entries"] == 122630
    assert d["wall_new_s"] < d["wall_old_s"] / 2       # the memoized kernel


def test_reprice_under_the_line_at_the_identical_frontier():
    new = json.load(open(DOCS / "window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-12-interned.json"))
    sep4 = json.load(open(DOCS / "window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-04.json"))
    sep6 = json.load(open(DOCS / "window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-06-reprice.json"))
    assert new["rungs"] == list(RUNGS) and new["programs"] == "c1prime-loop"
    expected = {"1": 4.97, "1/2": 5.12}
    for n, o, r in zip(new["rows"], sep4["rows"], sep6["rows"]):
        assert n["eps"] == o["eps"] == r["eps"] and n["rss_isolated_per_eps"]
        assert n["max_pairs"] == 1964919 and n["pairs_per_tick"] == o["pairs_per_tick"] and n["states_per_tick"] == o["states_per_tick"]
        assert n["per_rung"] == o["per_rung"] == r["per_rung"]          # same values from the same aggregate
        assert round(n["peak_rss_kb"] / 1e6, 2) == expected[n["eps"]] < 8.0 < r["peak_rss_kb"] / 1e6


def test_mass_t_round_trips_the_dict_form_and_projects_exactly():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    stats = {}
    aggs = window_law_aggregates(cfg, progs, law, RUNGS, stats)
    fine = stats["mass_T"]
    assert isinstance(fine, MassT) and len(fine) == len(aggs["r4"])
    for key, joint in aggs["r4"].items():
        assert sum(fine[key].values(), Fraction(0)) == sum(joint.values(), Fraction(0))
    for r in RUNGS:
        mT = stats["mass_T_by_rung"][r]
        assert list(mT.keys()) == list(aggs[r].keys())
        plain = {k: dict(v) for k, v in mT.items()}
        assert mT == plain and plain == mT
        for T in law.endpoints():
            assert sum((v.get(T, Fraction(0)) for v in plain.values()), Fraction(0)) == Fraction(1, len(law.endpoints()))
