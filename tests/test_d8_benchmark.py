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
    assert out["stage"] == "B" and out["wall_stageA_estimate_s"] > 0


def test_stage_A_refuses_on_its_estimate_without_building_the_visible_table(monkeypatch):
    import yupi.d8_benchmark as b
    monkeypatch.setattr(b, "WALL_CAP_S", 1e-9)
    monkeypatch.setattr(b, "visible_table", lambda *a: (_ for _ in ()).throw(AssertionError("built")))
    cell = dict(world="c0b", discipline="stochastic", eps="1", law=WindowLaw(6, 3, 3), rung="r2")
    out = b.benchmark_cell(cell, {}, sample_k=2)
    assert out["stage"] == "A" and out["n_vis"] is None and not out["admitted"]
    assert out["refused_by"] == ["WALL_CAP"] and out["n_lat"] > 0 and out["wall_stageA_estimate_s"] > 0


def test_n_vis_upper_bound_never_understates_the_real_census():
    """The n_vis pre-check bounds the shuffled census from the latent table
    alone: sum over latent windows of the product of distinct within-bucket
    orderings. Collisions make the true n_vis smaller, so the bound is >=
    n_vis at every cell — safe for a REFUSAL guard (it can be conservative,
    never wrongly admit)."""
    from yupi.attribution import latent_table, visible_table
    from yupi.d8_benchmark import n_vis_upper_bound, world_of
    for law, rung in [(WindowLaw(6, 4, 2), "r2"), (WindowLaw(8, 4, 2), "r1"),
                      (WindowLaw(9, 3, 3), "r1"), (WindowLaw(6, 3, 3), "r4")]:
        cfg, progs = world_of(dict(world="c1", discipline="fifo", eps="1", law=law, rung=rung))
        lat = latent_table(cfg, progs, law, rung, {})
        vis, _ = visible_table(lat, law.B)
        assert n_vis_upper_bound(lat, law.B) >= len(vis)


def test_stage_A_refuses_a_huge_census_on_the_n_vis_bound_before_building(monkeypatch):
    """The failure the C1 benchmark hit: a B=3 cell whose n_vis is millions,
    cheap to enumerate latently but hours to build/gate. The n_vis bound must
    refuse it from the latent table, without visible_table ever running, even
    though the sampled filter timings are fast (small n_lat)."""
    import yupi.d8_benchmark as b
    monkeypatch.setattr(b, "N_VIS_CAP", 500)
    monkeypatch.setattr(b, "visible_table", lambda *a: (_ for _ in ()).throw(AssertionError("built")))
    cell = dict(world="c1", discipline="fifo", eps="1", law=WindowLaw(9, 3, 3), rung="r1")
    out = b.benchmark_cell(cell, {}, sample_k=2)
    assert out["stage"] == "A" and out["n_vis"] is None and not out["admitted"]
    assert "N_VIS_CAP" in out["refused_by"] and out["n_vis_upper_bound"] > 500


def test_verdict_names_every_breached_line():
    base = dict(n_paths_max=1, peak_build_bytes=1, max_support_shuf=1, max_support_ord=1,
                max_frontier_shuf=1, t_step_shuf_s=0.0, t_step_ord_s=0.0, projected_gate2_wall_s=0.0)
    assert verdict(base) == dict(admitted=True, refused_by=[])
    bad = dict(base, n_paths_max=2_000_000, max_support_ord=30_000, t_step_shuf_s=1.5,
               projected_gate2_wall_s=WALL_CAP_S + 1)
    v = verdict(bad)
    assert not v["admitted"] and v["refused_by"] == ["B4'_paths", "B1_support", "B3_step", "WALL_CAP"]


def test_grid_rule_versions_v01_default_and_v03_extension():
    """v0.1 is the prereg rule and stays the default; v0.3 (grid-freeze-c1-v0.2
    Decision + D4 erratum E2) raises only the wall cap, B4′ build RSS and the
    proportional N_VIS_CAP guard. A cost record just over the v0.1 lines is
    refused under v0.1 and admitted under v0.3; one over the v0.3 lines is
    refused by both."""
    from yupi import d8_benchmark as m
    assert m.RULE_VERSION == "v0.1" and m.WALL_CAP_S == 1200 and m.B4P_RSS_BYTES == 2 * 1024 ** 3
    base = dict(n_paths_max=1_315_454, max_support_shuf=10, max_support_ord=10, max_frontier_shuf=100,
                t_step_shuf_s=0.1, t_step_ord_s=0.1)
    just_over = dict(base, peak_build_bytes=int(2.28e9), projected_gate2_wall_s=1428.0)   # (12,12,2)-shaped
    far_over = dict(base, peak_build_bytes=int(4.5e9), projected_gate2_wall_s=21_791.0)   # (12,12,3)-shaped
    try:
        assert m.verdict(just_over)["refused_by"] == ["B4'_rss", "WALL_CAP"]
        r = m.set_rule("v0.3")
        assert (r["wall_cap_s"], r["b4p_rss_bytes"], r["n_vis_cap"]) == (3600, 4 * 1024 ** 3, 9_000_000)
        assert m.verdict(just_over)["admitted"]
        assert m.verdict(far_over)["refused_by"] == ["B4'_rss", "WALL_CAP"]
        assert m.B1_SUPPORT == 20_000 and m.B3_STEP_S == 1.0 and m.B4P_PATHS == 1_500_000
    finally:
        m.set_rule("v0.1")
    assert m.WALL_CAP_S == 1200
