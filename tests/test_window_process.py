"""Gate for `yupi.window_process`: the (state, last-L window) forward
recursion reproduces the path aggregation exactly — same keys, same final-
state masses, Fraction for Fraction — wherever both can be computed, and
matches the committed (14, L, 2) ceilings artifacts' window counts and
mean state entropies. The recursion imports no path or filter code.
"""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c0b_programs, c1_programs
from yupi.queries import state_entropy_bits
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_process import window_law_aggregate

DOCS = pathlib.Path(__file__).parent.parent / "docs"
RUNGS = ("r0", "r1", "r2", "r3", "r4")


def _by_paths(cfg, progs, law, rung):
    w_T = endpoint_prior(law)
    agg = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
            d = agg.setdefault(key, {})
            d[final] = d.get(final, Fraction(0)) + w_T * prob
    return agg


def test_firewall_no_path_or_filter_imports():
    src = (pathlib.Path(__file__).parent.parent / "src" / "yupi" / "window_process.py").read_text()
    for banned in ("window_filter", "window_enumerator", "from yupi.enumerator", "import enumerator"):
        assert banned not in src.replace("`window_filter`", "").replace("`window_enumerator`", "").replace("`enumerator`", "")


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("L", [2, 4, 8])
@pytest.mark.parametrize("rung", RUNGS)
def test_c1_8_L_2_equals_path_aggregation(eps, L, rung):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    law = WindowLaw(T_ep=8, L=L, B=2)
    assert window_law_aggregate(cfg, progs, law, rung) == _by_paths(cfg, progs, law, rung)


@pytest.mark.parametrize("disc", ["fifo", "stochastic"])
@pytest.mark.parametrize("L", [1, 3, 6])
def test_c0b_6_L_1_equals_path_aggregation(disc, L):
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    law = WindowLaw(T_ep=6, L=L, B=1)
    for rung in RUNGS:
        assert window_law_aggregate(cfg, progs, law, rung) == _by_paths(cfg, progs, law, rung)


def test_c1_12_4_2_equals_path_aggregation_r1():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=12, L=4, B=2)
    stats = {}
    agg = window_law_aggregate(cfg, progs, law, "r1", stats)
    assert agg == _by_paths(cfg, progs, law, "r1")
    assert stats["max_pairs"] < 69210          # fewer pairs than paths at T = 12


@pytest.mark.parametrize("L", [2, 10, 14])
def test_matches_committed_14_L_2_ceilings(L):
    d = json.load(open(DOCS / f"c1-query-ceilings-14-{L}-2-corrected-2026-08-20.json"))
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=14, L=L, B=2)
    for rung in ("r1", "r4"):
        ref = next(r for r in d["rows"] if r["eps"] == "1" and r["rung"] == rung)
        stats = {}
        agg = window_law_aggregate(cfg, progs, law, rung, stats)
        assert len(agg) == ref["n_windows"]
        total = sum((sum(j.values(), Fraction(0)) for j in agg.values()), Fraction(0))
        assert total == 1
        H = sum(float(sum(j.values())) * state_entropy_bits({s: m / sum(j.values()) for s, m in j.items()})
                for j in agg.values())
        assert abs(H - ref["mean_state_entropy_bits"]) < 1e-9


from yupi.window_process import window_law_aggregates


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("T_ep,L", [(8, 2), (8, 4), (12, 4)])
def test_one_recursion_at_r4_yields_every_rung(eps, T_ep, L):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    law = WindowLaw(T_ep=T_ep, L=L, B=2)
    derived = window_law_aggregates(cfg, progs, law)
    for rung in RUNGS:
        assert derived[rung] == window_law_aggregate(cfg, progs, law, rung), rung


def test_stats_record_reachable_states_per_tick():
    # Codex review of v0.2.8 (2026-09-04, finding 10): the reachable-state
    # counts the proposals cite were never retained in a raw. The recursion
    # now records them alongside the pair counts, and they must equal the
    # enumerator's distinct final states at every tick.
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=6, L=2, B=2)
    stats = {}
    window_law_aggregate(cfg, progs, law, "r4", stats)
    assert len(stats["states_per_tick"]) == 6
    for t in range(1, 7):
        assert stats["states_per_tick"][t - 1] == len({final for _, _, final in paths(cfg, progs, t)})
        assert stats["states_per_tick"][t - 1] <= stats["pairs_per_tick"][t - 1]
    assert stats["max_states"] == max(stats["states_per_tick"])


def test_stats_record_per_endpoint_mass_per_window():
    # For the ceilings producer on the recursion (2026-09-04): by_endpoint
    # (per-endpoint means, needed by the §6 truncation-conditional formula)
    # requires each window's law mass split by the endpoint T that generated
    # it. The recursion records it in stats["mass_T"] and it must equal the
    # path side's split exactly.
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=8, L=4, B=2)
    stats = {}
    agg = window_law_aggregate(cfg, progs, law, "r2", stats)
    w_T = endpoint_prior(law)
    by_paths = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            key = (u == 0, tuple(project(r, "r2") for r in recs[u:]))
            d = by_paths.setdefault(key, {})
            d[T] = d.get(T, Fraction(0)) + w_T * prob
    assert stats["mass_T"] == by_paths
    for key, joint in agg.items():
        assert sum(stats["mass_T"][key].values(), Fraction(0)) == sum(joint.values(), Fraction(0))


def test_aggregates_project_per_endpoint_mass_to_every_rung():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs()
    law = WindowLaw(T_ep=8, L=4, B=2)
    stats = {}
    aggs = window_law_aggregates(cfg, progs, law, RUNGS, stats)
    for rung in RUNGS:
        single = {}
        window_law_aggregate(cfg, progs, law, rung, single)
        assert stats["mass_T_by_rung"][rung] == single["mass_T"], rung
        assert set(stats["mass_T_by_rung"][rung]) == set(aggs[rung])
