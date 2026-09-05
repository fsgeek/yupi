"""`scripts/window_gate.py` — the two-path gate on the recursion (filter vs
window-process aggregate, mass and state marginal, exact). Written before
the script ran on any law (2026-09-04). Passes on committed straight-line
worlds where both paths are already known to agree, and on a looping world;
and it must FAIL loudly on a deliberately corrupted aggregate."""
import importlib.util
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.programs import COMPUTE, Loop, acquire, c1_programs, io, release
from yupi.window import WindowLaw

_spec = importlib.util.spec_from_file_location(
    "window_gate", pathlib.Path(__file__).parent.parent / "scripts" / "window_gate.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
gate = _mod.gate


@pytest.mark.parametrize("rung", ["r0", "r1", "r4"])
def test_c1_8_2_2_every_window_passes(rung):
    r = gate(WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=8, L=2, B=2), rung)
    assert r["n"] == r["n_windows_total"] > 0 and r["mismatches"] == []


def test_top_n_takes_the_largest_supports():
    r_all = gate(WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2), "r1")
    r_top = gate(WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2), "r1", top=5)
    assert r_top["n"] == 5 and r_top["n_windows_total"] == r_all["n_windows_total"]
    assert r_top["max_support"] == r_all["max_support"] and r_top["mismatches"] == []


def test_looping_world_passes_every_rung():
    cfg = WorldConfig(n_threads=2, n_cpus=1, n_locks=1, n_devices=1, queue_depth=1, req_pool=2,
                      completion_p=Fraction(1, 3), epsilon=Fraction(1), discipline="stochastic")
    progs = (Loop((acquire(0), release(0), io(0))), Loop((COMPUTE, acquire(0), release(0))))
    for rung in ("r0", "r1", "r2", "r3", "r4"):
        r = gate(cfg, progs, WindowLaw(T_ep=12, L=4, B=1), rung)
        assert r["mismatches"] == [] and r["n"] > 0, rung


def test_gate_detects_a_corrupted_aggregate(monkeypatch):
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=6, L=2, B=2)
    real = _mod.window_law_aggregate
    def corrupted(*a, **k):
        agg = real(*a, **k)
        key = next(iter(agg))
        s = next(iter(agg[key]))
        agg[key][s] += Fraction(1, 10**9)     # shift one mass by a hair
        return agg
    monkeypatch.setattr(_mod, "window_law_aggregate", corrupted)
    r = gate(cfg, progs, law, "r1")
    assert len(r["mismatches"]) == 1


def test_stride_takes_every_kth_window_in_support_order():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    r_all = gate(cfg, progs, law, "r1")
    r_s = gate(cfg, progs, law, "r1", stride=7)
    assert r_s["n"] == -(-r_all["n_windows_total"] // 7) and r_s["mismatches"] == []
    assert r_s["max_support"] == r_all["max_support"]        # the largest support is index 0


def test_shards_partition_every_window_exactly_once():
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    total = gate(cfg, progs, law, "r1")["n_windows_total"]
    ns = [gate(cfg, progs, law, "r1", shard=(i, 3))["n"] for i in range(3)]
    assert sum(ns) == total and max(ns) - min(ns) <= 1
    assert all(gate(cfg, progs, law, "r1", shard=(i, 3))["mismatches"] == [] for i in range(3))
