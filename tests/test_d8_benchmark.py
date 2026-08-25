"""Blind cost benchmark for the D8 attribution grid (prereg §4)."""
from yupi.d8_benchmark import (COST_KEYS_FORBIDDEN, WALL_CAP_S, benchmark_cell,
                               candidate_cells, candidate_laws, verdict)
from yupi.window import WindowLaw


def test_candidate_grid_is_the_prereg_grid():
    laws = candidate_laws()
    assert len(laws) == 121 + 33 + 14
    assert all(l.T_ep % l.B == 0 and l.L % l.B == 0 and 6 <= l.T_ep <= 16 and l.B <= l.L <= l.T_ep
               for l in laws)
    assert WindowLaw(6, 3, 3) in laws and WindowLaw(16, 16, 1) in laws and WindowLaw(15, 3, 3) in laws
    cells = candidate_cells()
    assert len(cells) == len(laws) * 4 * 4           # rungs × (2 disciplines + 2 ε)
    assert {(c["world"], c["discipline"], c["eps"]) for c in cells} == {
        ("c0b", "stochastic", "1"), ("c0b", "fifo", "1"), ("c1", "fifo", "1"), ("c1", "fifo", "1/2")}


def test_benchmark_cell_records_cost_only_and_prices_the_known_census():
    cell = dict(world="c0b", discipline="stochastic", eps="1", law=WindowLaw(6, 3, 3), rung="r2")
    cache = {}
    out = benchmark_cell(cell, cache, sample_k=4)
    assert out["n_vis"] == 90 and out["n_lat"] < 90 and out["n_paths_max"] == len(cache[6])
    assert set(cache) == {3, 6}
    assert not any(bad in k for k in out for bad in COST_KEYS_FORBIDDEN)
    assert out["admitted"] and out["refused_by"] == []
    assert out["projected_gate2_wall_s"] > 0 and out["max_frontier_shuf"] >= out["max_support_shuf"] > 0
    assert out["sample_k"] == 4 and out["t_step_shuf_s"] > 0


def test_verdict_names_every_breached_line():
    base = dict(n_paths_max=1, peak_build_bytes=1, max_support_shuf=1, max_support_ord=1,
                max_frontier_shuf=1, t_step_shuf_s=0.0, t_step_ord_s=0.0, projected_gate2_wall_s=0.0)
    assert verdict(base) == dict(admitted=True, refused_by=[])
    bad = dict(base, n_paths_max=2_000_000, max_support_ord=30_000, t_step_shuf_s=1.5,
               projected_gate2_wall_s=WALL_CAP_S + 1)
    v = verdict(bad)
    assert not v["admitted"] and v["refused_by"] == ["B4'_paths", "B1_support", "B3_step", "WALL_CAP"]
