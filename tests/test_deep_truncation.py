"""Pins for `docs/deep-truncation-census-v0.1.md`: at horizon 32 every
adjacent C1 rung pair is above δ = 0.01 on a statutory query at L = 8
(ε = 1); the world is dying by tick 24; the recursion agrees with the
filter on a small sample outside its path gate.
"""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.programs import c1_programs
from yupi.state import initial_state
from yupi.window import WindowLaw
from yupi.window_filter import filter_window
from yupi.window_process import window_law_aggregate

DOCS = pathlib.Path(__file__).parent.parent / "docs"
DELTA = 0.01


def _ladder(T, L):
    d = json.load(open(DOCS / f"r0-ladder-census-{T}-{L}-2-2026-09-03.json"))
    if T == 32:
        assert d["aggregation"] == "window" and d["programs"] == "c1"
    return {(r["eps"], r["rung"]): r for r in d["rows"]}


def test_every_pair_above_delta_at_32_8_2_eps_one():
    rows = _ladder(32, 8)
    q = lambda r, n: rows[("1", r)]["facts"][n]
    assert q("r1", "Q1[L0]") - q("r2", "Q1[L0]") >= DELTA          # r1→r2: 0.012
    assert q("r2", "Q1[L0]") - q("r3", "Q1[L0]") > 0.09            # r2→r3: 0.097
    assert q("r3", "Q3[D0]") - q("r4", "Q3[D0]") >= DELTA          # r3→r4: 0.014 — lineage above δ
    g = lambda r: rows[("1", r)]["predictive"]["kinds2"]["gap"]
    assert round(g("r1") - g("r4"), 3) == 0.064


def test_from_reset_comparison_at_14_8_2():
    rows = _ladder(14, 8)
    q = lambda r, n: rows[("1", r)]["facts"][n]
    assert q("r3", "Q3[D0]") - q("r4", "Q3[D0]") < 0.002            # lineage collapsed from reset
    g = lambda r: rows[("1", r)]["predictive"]["kinds2"]["gap"]
    assert round(g("r1") - g("r4"), 3) == 0.023


@pytest.mark.parametrize("L,r1_minus_r4", [(4, 0.139), (8, 0.064)])
def test_exposure_range_roughly_doubles_mid_episode(L, r1_minus_r4):
    rows = _ladder(32, L)
    g = lambda r: rows[("1", r)]["predictive"]["kinds2"]["gap"]
    assert round(g("r1") - g("r4"), 3) == r1_minus_r4
    rows14 = _ladder(14, L)
    g14 = lambda r: rows14[("1", r)]["predictive"]["kinds2"]["gap"]
    assert (g("r1") - g("r4")) > 1.8 * (g14("r1") - g14("r4"))


def test_c1_is_dying_by_tick_24():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    dist = {initial_state(cfg): Fraction(1)}
    marks = {}
    for t in range(1, 41):
        nxt = {}
        for s, m in dist.items():
            for tr, p in enabled(s, cfg, progs):
                nxt[tr.next_state] = nxt.get(tr.next_state, Fraction(0)) + m * p
        dist = nxt
        if t in (24, 32, 40):
            marks[t] = (float(sum(m * sum(1 for st in s.status if st[0] == "TERMINATED") for s, m in dist.items())),
                        float(sum(m for s, m in dist.items() if all(st[0] == "TERMINATED" for st in s.status))))
    assert round(marks[24][0], 2) == 0.99 and round(marks[32][0], 2) == 2.28
    assert round(marks[40][1], 2) == 0.79


def test_recursion_matches_filter_outside_path_gate():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    law = WindowLaw(T_ep=32, L=4, B=2)
    for rung in ("r1", "r4"):
        agg = window_law_aggregate(cfg, progs, law, rung)
        keys = sorted(agg, key=lambda k: -len(agg[k]))[:4] + sorted(agg, key=str)[:4]
        for reset, win in keys:
            post = filter_window(cfg, progs, law, list(win), rung, reset)
            joint = agg[(reset, win)]
            mass = sum(joint.values(), Fraction(0))
            filt = {}
            for u, (w, b) in post.components.items():
                for s, m in b.items():
                    if w * m > 0:
                        filt[s] = filt.get(s, Fraction(0)) + w * m
            assert filt == {s: m / mass for s, m in joint.items()}
