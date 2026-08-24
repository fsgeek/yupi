"""Executable D10 witness regressions (Codex round, 2026-08-24, point 6).

Pins the verdict's load-bearing facts so the interface-witness suite (Part
II §9) carries them, not just a standalone producer:
witness 3 positive (stochastic), FIFO null at T*=6, FIFO crossover positive
at (8,2), full-context zero both disciplines, and the exact Q3/Q3thr
mechanism split (FIFO thrΔ = Δ; stochastic pure-allocator cells thrΔ = 0).
"""
import importlib.util, pathlib, sys

import pytest
from yupi.config import WorldConfig
from yupi.programs import c0b_programs
from yupi.window import WindowLaw

spec = importlib.util.spec_from_file_location(
    "d10_search", pathlib.Path(__file__).parent.parent / "scripts" / "d10_lineage_search.py")
d10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d10)

PROGS = c0b_programs()
CFG = {d: WorldConfig.c0b(discipline=d) for d in ("fifo", "stochastic")}


def _cell(disc, T_ep, L):
    cls = d10.classes_for(CFG[disc], PROGS, WindowLaw(T_ep=T_ep, L=L, B=2))
    total = sum(c["mass"] for ch in cls.values() for c in ch.values())
    return d10.analyze(cls, total)


def test_tep_star_rule_gives_6():
    assert d10.tep_star(CFG["stochastic"], PROGS) == 6


def test_witness3_stochastic_positive_at_tstar():
    r = _cell("stochastic", 6, 2)
    assert r["Q3"]["n_informative_histories"] >= 4
    assert r["Q3"]["delta"] > 0.05
    assert r["Q3thr"]["delta"] == 0.0        # pure allocator-label cell


def test_witness6_fifo_null_at_tstar_positive_at_8():
    assert _cell("fifo", 6, 2)["Q3"]["n_informative_histories"] == 0
    r = _cell("fifo", 8, 2)["Q3"]
    assert r["n_informative_histories"] >= 4 and r["delta"] > 0.02


def test_fifo_mechanism_is_pure_thread_order():
    r = _cell("fifo", 8, 2)
    assert r["Q3"]["delta"] == pytest.approx(r["Q3thr"]["delta"], abs=1e-12)


@pytest.mark.parametrize("disc", ["fifo", "stochastic"])
def test_full_context_exact_zero(disc):
    r = _cell(disc, 6, 6)
    assert r["Q3"]["n_informative_histories"] == 0
    assert r["Q3"]["delta"] == 0.0
