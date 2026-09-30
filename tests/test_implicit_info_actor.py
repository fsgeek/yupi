"""docs/actor-long-lag-design-prereg-v0.1.md: the (KIND, ACTOR) ι computation
(scripts/implicit_info_actor.py) on a hand table, and the frozen actor analysis
(scripts/implicit_info_bintest_actor.py) on SYNTHETIC census rows with a planted slope.
No docs/learner-window-census-* file is read here."""
import json
import sys
from fractions import Fraction as F
from math import log2
from pathlib import Path

import numpy as np
import pytest

from yupi.implicit_info import implicit_info
from yupi.naming import pattern_all
from yupi.pattern_ceiling import serial_key
from yupi.records import Record

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import implicit_info_actor as A  # noqa: E402
import implicit_info_bintest_actor as B  # noqa: E402


def R(kind, actor=None, obj=None, related=None, lineage=None):
    return Record(kind, actor, obj, related, lineage)


def _table():
    a = (False, (R("IO_ISSUE", 0), R("DISPATCH", 0)))
    b = (False, (R("BLOCK", 0), R("DISPATCH", 1)))
    c = (True, (R("STEP", 0), R("STEP", 0)))
    return a, b, c, {
        a: (F(1, 4), {R("STEP", 0): F(1, 4), R("DISPATCH", 0): F(3, 4)}),
        b: (F(1, 4), {R("STEP", 1): F(3, 4), R("DISPATCH", 0): F(1, 4)}),
        c: (F(1, 2), {R("STEP", 0): F(1, 2), R("STEP", 1): F(1, 2)}),
    }


def test_actor_cell_gates_and_pinned_values():
    a, b, c, table = _table()
    ms = (1, 2)
    kind = {m: implicit_info(table, m, target=lambda r: r.kind)["per_class"] for m in ms}
    rows, per, h_row = A.actor_cell(table, {k: {m: kind[m][k] for m in ms} for k in table}, ms)
    assert all(rows[m]["gate"] for m in ms) and h_row["gate"]
    # m = 1: a and b share the suffix (DISPATCH 0); ι_{A|K} as hand-computed in
    # tests/test_implicit_info.py; c is alone in its suffix group, so every ι is 0.
    assert per[a]["iota_agk_1"] == pytest.approx(0.75 * log2(4 / 3), abs=1e-12)
    assert per[b]["iota_agk_1"] == pytest.approx(0.5, abs=1e-12)
    assert per[c]["iota_agk_1"] == pytest.approx(0.0, abs=1e-15)
    # m = 2: every class is its own group → nothing is implicit
    assert all(abs(per[k]["iota_agk_2"]) < 1e-15 and abs(per[k]["iota_ka_2"]) < 1e-15 for k in table)
    assert rows[1]["mean_iota_agk"] == pytest.approx(0.25 * (0.75 * log2(4 / 3) + 0.5), abs=1e-12)
    assert rows[1]["min_iota_agk"] >= -1e-12
    # H(A | K): a 0, b 0, c 1 bit (STEP split between two threads)
    assert [per[k]["H_agk"] for k in (a, b, c)] == [0.0, 0.0, 1.0]
    assert h_row["mean_H_actor_given_kind"] == pytest.approx(0.5)


def test_actor_cell_gate_fails_on_a_wrong_kind_cache():
    a, b, c, table = _table()
    kind = implicit_info(table, 1, target=lambda r: r.kind)["per_class"]
    bad = {k: {1: kind[k]} for k in table}
    bad[a][1] += 0.5   # ι_{A|K}(a) would go negative and the recomputed ι_K would disagree
    rows, _, _ = A.actor_cell(table, bad, (1,))
    assert not rows[1]["gate"] and rows[1]["min_iota_agk"] < -0.1


# ---- the frozen actor analysis on synthetic census rows ----

THREADS = ("T3", "T17", "T40")
KINDS = ("DISPATCH", "STEP", "ACQUIRE", "RELEASE")
SLOPE, ICPT, H_COEF = 0.05, 0.02, 0.1


def _synthetic(tmp_path, monkeypatch, n_win=3000, rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    recs, keys = [], []
    for _ in range(n_win):
        r = tuple(R(KINDS[rng.integers(2)], THREADS[rng.integers(3)]) for _ in range(8))
        reset = bool(rng.integers(2))
        recs.append((reset, r))
        keys.append((reset, pattern_all(r[:7])[0]))
    classes = list(dict.fromkeys(keys))
    table, cache = {}, []
    iota4, hagk = {}, {}
    for j, key in enumerate(classes):
        # the class's law over the next record: actor split p / 1 − p between two pattern threads
        p = F(int(rng.integers(1, 8)), 8)
        star = {R("STEP", 0): p, R("STEP", 1): 1 - p}
        table[key] = (F(int(rng.integers(1, 20)), 1000), star)
        i4 = float(rng.uniform(0.0, 1.0))
        i1 = i4 + float(rng.uniform(0.0, 0.5))
        iota4[key] = i4
        hagk[key] = -(float(p) * log2(float(p)) + float(1 - p) * log2(float(1 - p)))
        cache.append({"k": serial_key(key), "iota_agk_1": i1, "iota_agk_4": i4, "iota_1": 99.0, "iota_4": 99.0})
    tag = "r2-eps1"
    (tmp_path / f"c1prime-loop-40-8-2-{tag}-k7-actorgk-m123456.jsonl").write_text(
        "".join(json.dumps(d) + "\n" for d in cache))
    rows = []
    for i, key in enumerate(keys):
        y = ICPT + SLOPE * iota4[key] + H_COEF * hagk[key] + rng.normal() * 0.05
        rows.append({"i": i, "key": classes.index(key),
                     "by_field": {"kind": 7.0 + rng.normal(), "actor": y, "obj": 0.0, "related": 0.0, "lineage": 0.0}})
    pw = tmp_path / "per_window.jsonl"
    pw.write_text("".join(json.dumps(r) + "\n" for r in rows))
    census = tmp_path / "census.json"
    census.write_text(json.dumps({"k": 7, "rung": "r2", "eps": "1", "seed": 1, "per_window_file": str(pw),
                                  "corpus": str(tmp_path), "split": "test"}))
    monkeypatch.setattr(B, "CACHE", tmp_path)
    monkeypatch.setattr(B, "read_split", lambda d, s: [((i,), None) for i in range(n_win)])
    monkeypatch.setattr(B, "VOCAB", {i: i for i in range(n_win)})
    monkeypatch.setattr(B, "surface_records", lambda toks: recs[toks[0]])
    monkeypatch.setattr(B, "load_table", lambda path: table)
    return str(census), iota4, hagk, keys


def test_bintest_actor_reads_actor_field_and_agk_cache(tmp_path, monkeypatch):
    census, iota4, hagk, keys = _synthetic(tmp_path, monkeypatch)
    c, (y, lo, sh, h, f) = B.windows(census, 4)
    assert len(y) == 3000
    assert np.allclose(lo, [iota4[k] for k in keys]) and (sh >= 0).all()
    assert np.allclose(h, [hagk[k] for k in keys])
    assert abs(y.mean() - 7.0) > 5   # the response is by_field.actor, not by_field.kind


def test_bintest_actor_recovers_planted_slope(tmp_path, monkeypatch):
    census, *_ = _synthetic(tmp_path, monkeypatch)
    res, _ = B.run_one((census, 4))
    fb, fse = res["full"]["beta"], res["full"]["se"]
    assert res["full"]["terms"] == ["1", "iota_long", "iota_short", "H_actor_given_kind"]
    # pinned 2026-09-30 (rng seed 0): the planted 0.05 on ι_{A|K},4 recovered, within 3 se
    assert fb[1] == pytest.approx(PIN_BETA_LONG, abs=1e-12)
    assert fse[1] == pytest.approx(PIN_SE_LONG, abs=1e-12)
    assert abs(fb[1] - SLOPE) < 3 * fse[1] and abs(fb[2]) < 3 * fse[2] and abs(fb[3] - H_COEF) < 3 * fse[3]
    g = res["full_plus_log2_class_mass"]
    assert abs(g["beta"][1] - SLOPE) < 3 * g["se"][1]
    assert len(res["deciles_by_iota_long"]) == 10 and "mean_H_actor_given_kind" in res["deciles_by_iota_long"][0]


PIN_BETA_LONG = 0.05423074362064019
PIN_SE_LONG = 0.003180902873979875
