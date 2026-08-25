"""Blind cost benchmark for the D8 attribution grid (prereg §4).

Records COST ONLY per candidate cell — path counts, census sizes, table
entries, per-step support/frontier, sampled filter wall-clock, projected
gate-2 wall, table-build peak memory — and a verdict against the frozen D4
budget plus one pre-stated grid rule (WALL_CAP_S). It computes no entropy,
no loss, no Δ; the tables it builds are discarded on return. The admitted
set is written to the grid-freeze note and stamped before the measurement
script runs; a refused cell is refused, not "explored".

Budget lines (d4-budget-freeze-v0.1.md + erratum E1/B4′, enacted 2026-08-24):
  B1  max support per filtering step 20,000 states / ≤ 70,000 expanded
      transitions (frontier);  B2 peak memory ≤ 8 GB;  B3 ≤ 1 s per step;
  B4′ aggregation ≤ 1.5 × 10⁶ paths per (ε, T) pass, ≤ 2 GB RSS;
      T_ep = 16 admitted, 18 refused.
Grid rule stated here before any cell is priced: projected filter-side
(gate 2) wall per cell ≤ WALL_CAP_S single-process, projected as
n_vis · median t_shuf + n_lat · median t_ord from a deterministic sample.
"""
import time
import tracemalloc
from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.attribution import latent_table, mass, visible_table
from yupi.config import WorldConfig
from yupi.programs import c0b_programs, c1_programs
from yupi.shuffled_window import shuffled_window_filter_with_evidence
from yupi.window import WindowLaw
from yupi.window_filter import filter_window_with_evidence

B1_SUPPORT = 20_000
B1_FRONTIER = 70_000
B3_STEP_S = 1.0
B4P_PATHS = 1_500_000
B4P_RSS_BYTES = 2 * 1024 ** 3
WALL_CAP_S = 20 * 60          # pre-stated grid rule (prereg §4): per-cell gate-2 wall
SAMPLE_K = 8
RUNGS = ("r1", "r2", "r3", "r4")
COST_KEYS_FORBIDDEN = ("bits", "entropy", "delta", "loss", "gain", "shapley")


def candidate_laws() -> List[WindowLaw]:
    """Prereg §4: B ∈ {1,2,3}; T_ep a multiple of B in [6, 16]; L a multiple
    of B in [B, T_ep]."""
    out = []
    for B in (1, 2, 3):
        for T in range(6, 17):
            if T % B:
                continue
            for L in range(B, T + 1, B):
                out.append(WindowLaw(T_ep=T, L=L, B=B))
    return out


def candidate_cells() -> List[dict]:
    """(world, discipline, ε, law, rung) over the prereg §4 axes, ordered so
    that cells sharing (world, ε, T_ep) are adjacent (path-cache reuse)."""
    cells = []
    for law in candidate_laws():
        for disc in ("stochastic", "fifo"):
            for rung in RUNGS:
                cells.append(dict(world="c0b", discipline=disc, eps="1", law=law, rung=rung))
        for eps in ("1", "1/2"):
            for rung in RUNGS:
                cells.append(dict(world="c1", discipline="fifo", eps=eps, law=law, rung=rung))
    key = lambda c: (c["world"], c["discipline"], c["eps"], c["law"].T_ep, c["law"].B, c["law"].L, c["rung"])
    return sorted(cells, key=key)


def world_of(cell: dict):
    if cell["world"] == "c0b":
        return WorldConfig.c0b(discipline=cell["discipline"]), c0b_programs()
    return WorldConfig.c1(epsilon=Fraction(cell["eps"])), c1_programs()


def _sample(keys, k):
    return sorted(keys, key=repr)[:k]


def benchmark_cell(cell: dict, path_cache: Dict[int, list], sample_k: int = SAMPLE_K) -> dict:
    """Price one cell. Returns cost fields only (see module docstring)."""
    cfg, progs = world_of(cell)
    law, rung = cell["law"], cell["rung"]
    tracemalloc.start()
    t0 = time.perf_counter()
    lat = latent_table(cfg, progs, law, rung, path_cache)
    vis, src = visible_table(lat, law.B)
    t_build = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert sum(mass(j) for j in vis.values()) == 1        # a cost-side sanity check, not a result
    n_paths = {T: len(path_cache[T]) for T in law.endpoints()}
    entries_lat = sum(len(j) for j in lat.values())
    entries_vis = sum(len(j) for j in vis.values())

    st_s, st_o = {}, {}
    ts, to = [], []
    for (reset, buckets) in _sample(vis.keys(), sample_k):
        t = time.perf_counter()
        shuffled_window_filter_with_evidence(cfg, progs, law, [list(b) for b in buckets], rung, reset, st_s)
        ts.append(time.perf_counter() - t)
    for (reset, win) in _sample(lat.keys(), sample_k):
        t = time.perf_counter()
        filter_window_with_evidence(cfg, progs, law, list(win), rung, reset, st_o)
        to.append(time.perf_counter() - t)
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else 0.0
    n_buckets = law.L // law.B
    out = dict(
        world=cell["world"], discipline=cell["discipline"], eps=cell["eps"],
        T_ep=law.T_ep, L=law.L, B=law.B, rung=rung,
        n_paths_max=max(n_paths.values()), n_paths=n_paths,
        n_lat=len(lat), n_vis=len(vis), entries_lat=entries_lat, entries_vis=entries_vis,
        t_build_s=t_build, peak_build_bytes=peak,
        max_support_shuf=st_s.get("max_support", 0), max_frontier_shuf=st_s.get("max_frontier", 0),
        max_support_ord=st_o.get("max_support", 0),
        t_shuf_med_s=med(ts), t_ord_med_s=med(to),
        t_step_shuf_s=(med(ts) / n_buckets if n_buckets else 0.0),
        t_step_ord_s=(med(to) / law.L if law.L else 0.0),
        sample_k=min(sample_k, len(vis)),
    )
    out["projected_gate2_wall_s"] = len(vis) * med(ts) + len(lat) * med(to)
    out.update(verdict(out))
    assert not any(bad in k for k in out for bad in COST_KEYS_FORBIDDEN)
    del lat, vis, src
    return out


def verdict(cost: dict) -> dict:
    reasons = []
    if cost["n_paths_max"] > B4P_PATHS:
        reasons.append("B4'_paths")
    if cost["peak_build_bytes"] > B4P_RSS_BYTES:
        reasons.append("B4'_rss")
    if max(cost["max_support_shuf"], cost["max_support_ord"]) > B1_SUPPORT:
        reasons.append("B1_support")
    if cost["max_frontier_shuf"] > B1_FRONTIER:
        reasons.append("B1_frontier")
    if max(cost["t_step_shuf_s"], cost["t_step_ord_s"]) > B3_STEP_S:
        reasons.append("B3_step")
    if cost["projected_gate2_wall_s"] > WALL_CAP_S:
        reasons.append("WALL_CAP")
    return dict(admitted=not reasons, refused_by=reasons)
