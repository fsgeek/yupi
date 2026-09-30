"""scripts/relay_paired.py (relay pre-registration v0.1, frozen analysis R1, R2, R4) on
synthetic census rows with a planted slope: the join's gates, the recovered slope and
intercept (pinned), and the verdict thresholds."""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from yupi.interfaces import MASKED, relay_window
from yupi.naming import pattern_all
from yupi.pattern_ceiling import serial_key
from yupi.records import Record

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import relay_paired as P  # noqa: E402

KINDS = ("DISPATCH", "STEP", "ACQUIRE", "RELEASE", "BLOCK")
THREADS = ("T7", "T19", "T33")
SLOPE, ICPT = 0.04, 0.01


def _synthetic(n_win=4000, seeds=3, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    recs1, recsR = {}, {}
    for i in range(n_win):
        n_rec = 8
        r1 = tuple(Record(KINDS[rng.integers(3)], THREADS[rng.integers(2)], MASKED, MASKED, MASKED)
                   for _ in range(n_rec))
        reset = bool(rng.integers(2))
        recs1[i] = (reset, r1)
        recsR[i] = (reset, relay_window(r1))
    diota, cls = {}, {}
    for i in recs1:
        reset, r1 = recs1[i]
        k1 = serial_key((reset, pattern_all(r1[:7])[0]))
        kR = serial_key((reset, pattern_all(recsR[i][1][:7])[0]))
        if k1 not in diota:
            u = rng.random()
            if u < 0.15:
                diota[k1] = (kR, 0.0, True)
            else:
                diota[k1] = (kR, float(rng.uniform(-0.25, 0.55)), False)
            cls[k1] = len(cls)
    r1_rows, rR_rows = [], []
    for s in range(seeds):
        a, b = {}, {}
        for i in recs1:
            reset, r1 = recs1[i]
            k1 = serial_key((reset, pattern_all(r1[:7])[0]))
            _, di, _ = diota[k1]
            base = 0.2 + rng.normal() * 0.3
            a[i] = dict(i=i, key=cls[k1], by_field=dict(kind=base, actor=0.0, obj=0.0, related=0.0, lineage=0.0))
            b[i] = dict(i=i, key=cls[k1], by_field=dict(kind=base - ICPT - SLOPE * di + rng.normal() * 0.05,
                                                         actor=0.0, relay=0.5, related=0.0, lineage=0.0))
        r1_rows.append(a)
        rR_rows.append(b)
    return r1_rows, rR_rows, recs1, recsR, diota


def test_planted_slope_is_recovered_and_scored():
    r1_rows, rR_rows, recs1, recsR, diota = _synthetic()
    ids, y, x, z, relay = P.join(r1_rows, rR_rows, recs1, recsR, diota)
    assert len(ids) == 4000 and z.sum() > 0 and (x < -0.05).sum() > 0
    res = P.analyse(y, x, z, relay)
    # pinned 2026-09-30 (rng seed 0): the planted 0.04 / 0.01 recovered
    assert res["slope"] == pytest.approx(PIN_SLOPE, abs=1e-12)
    assert res["intercept"] == pytest.approx(PIN_ICPT, abs=1e-12)
    assert res["slope_se"] == pytest.approx(PIN_SLOPE_SE, abs=1e-12)
    assert abs(res["slope"] - SLOPE) < 3 * res["slope_se"] and abs(res["intercept"] - ICPT) < 3 * res["intercept_se"]
    assert res["verdict"]["R1"] == "PASS" and res["verdict"]["R2"] == "PASS"
    # the planted law has no extra harm below the line: R4's set sits on the intercept line
    # (mean − intercept = slope · mean Δι over the set, negative), and is scored by t
    r4 = res["R4_set"]
    assert r4["minus_intercept"] < 0
    assert r4["n"] == 813 and r4["t"] == pytest.approx(-6.181399447115319, abs=1e-9)
    assert res["verdict"]["R4"] == "PASS"
    assert res["R2_zero_set"]["n"] == 599
    assert res["relay_field_excess_r1R"]["mean"] == pytest.approx(0.5)


def test_verdict_thresholds():
    rng = np.random.default_rng(1)
    x = rng.uniform(-0.3, 0.6, 20000)
    z = np.zeros(len(x), bool)
    z[:2000] = True
    x[:2000] = 0.0
    # a slope of 0.1 is outside the band: R1 fails although t is large
    res = P.analyse(0.1 * x + rng.normal(size=len(x)) * 0.01, x, z)
    assert res["slope_t"] > 3 and res["verdict"]["R1"] == "FAIL"
    # a zero set shifted off the line fails R2
    y = 0.03 * x + rng.normal(size=len(x)) * 0.01
    y[:2000] += 0.05
    assert P.analyse(y, x, z)["verdict"]["R2"] == "FAIL"
    # an R4 set pushed below the intercept passes R4
    y = 0.03 * x + rng.normal(size=len(x)) * 0.01
    y[x < -0.05] -= 0.02
    assert P.analyse(y, x, z)["verdict"]["R4"] == "PASS"
    # the secondary arm reports without thresholds
    assert isinstance(P.analyse(y, x, z, arm="secondary")["verdict"], str)


def test_join_gates():
    r1_rows, rR_rows, recs1, recsR, diota = _synthetic(n_win=300)
    # a relay record that is not the relay of the r1 window
    bad = dict(recsR)
    reset, rr = bad[5]
    bad[5] = (reset, (replace(rr[0], kind="IDLE"),) + rr[1:])
    with pytest.raises(P.Gate):
        P.join(r1_rows, rR_rows, recs1, bad, diota)
    # a Δι table whose r1R class differs
    k = next(iter(diota))
    d2 = dict(diota)
    d2[k] = ("N|nonsense",) + d2[k][1:]
    with pytest.raises(P.Gate):
        P.join(r1_rows, rR_rows, recs1, recsR, d2)
    # a class id that is not a bijection
    r2 = [dict(r) for r in r1_rows]
    r2[1] = {i: dict(row, key=0) for i, row in r2[1].items()}
    with pytest.raises(P.Gate):
        P.join(r2, rR_rows, recs1, recsR, diota)
    # different window sets
    r3 = [dict(r) for r in rR_rows]
    r3[0].pop(7)
    with pytest.raises(P.Gate):
        P.join(r1_rows, r3, recs1, recsR, diota)


PIN_SLOPE = 0.04008320091506955
PIN_ICPT = 0.010621345524863768
PIN_SLOPE_SE = 0.002077634888886963
