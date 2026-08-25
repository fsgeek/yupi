"""Measurement per cell (prereg §5 gates, §7 reporting). Cells used here are
either the B = 1 null (every quantity 0 by theorem) or a law BELOW the grid
(T_ep = 4 — never a measured cell), so no in-grid Δ is computed before the
blind grid freeze."""
import pytest

from yupi.d8_measure import GateFailure, measure_cell
from yupi.window import WindowLaw


def test_B1_null_cell_all_gates_and_all_zero():
    cell = dict(world="c0b", discipline="stochastic", eps="1", law=WindowLaw(6, 3, 1), rung="r2")
    r = measure_cell(cell, {})
    assert r["gates"]["all_passed"] and r["gates"]["Z3"] and r["gates"]["Z1"] and r["gates"]["Z2"]
    assert r["delta_un"] == r["delta_an"] == r["offset_term"] == 0.0
    assert r["prevalence"] == 0.0 and r["n_vis_informative"] == 0 and r["n_vis"] == r["n_lat"]
    assert r["collapsed_un"] and r["collapsed_an"]
    assert all(v == 0.0 for v in r["chain_semantic_un"].values())
    assert set(r["chain_semantic_un"]) == {"U", "kappa", "WQ", "DQ", "REQ", "rho"}
    assert set(r["chain_semantic_an"]) == {"kappa", "WQ", "DQ", "REQ", "rho"}
    assert set(r["per_endpoint_an"]) == {str(T) for T in range(1, 7)}   # B = 1: every tick is an endpoint


def test_below_grid_cell_runs_every_gate_and_reports_every_field():
    cell = dict(world="c1", discipline="fifo", eps="1/2", law=WindowLaw(4, 4, 2), rung="r1")
    r = measure_cell(cell, {})
    assert r["gates"]["all_passed"] and not r["gates"]["Z1"] and not r["gates"]["Z2"]
    assert r["gates"]["two_path_n_vis"] == r["n_vis"] and r["gates"]["bijection_n"] > 0
    for k in ("delta_un", "delta_an", "offset_term", "shapley_un", "shapley_an", "envelope_un",
              "envelope_an", "g_quantiles", "per_endpoint_un", "max_g", "cost"):
        assert k in r
    assert r["delta_un"] >= r["delta_an"] >= 0 and r["offset_term"] >= 0
    assert 0 <= r["prevalence"] <= 1 and r["n_vis_informative"] <= r["n_vis"]
    assert set(r["g_quantiles"]) == {"50", "90", "99"}
    assert r["cost"]["t_gate2_s"] > 0


def test_gate_failure_names_the_gate(monkeypatch):
    import yupi.d8_measure as m
    monkeypatch.setattr(m, "check_bijection", lambda *t: (_ for _ in ()).throw(AssertionError("coordinate bijection fails at X")))
    cell = dict(world="c0b", discipline="fifo", eps="1", law=WindowLaw(6, 3, 1), rung="r4")
    with pytest.raises(AssertionError, match="bijection"):
        measure_cell(cell, {})
