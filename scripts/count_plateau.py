"""EXPLORATORY comparison for docs/count-baseline-design-v0.1.md §4-§5: per cell, the count learner's k = 7 KIND
excess against the converged transformer's (d128 e15, seeds 1-3 seed-mean), and the binned ι4 profile (bins vs
ι4 = 0, controls: short-range part, H_kind, log2 mass; CR1 by class), the same fit for both learners on the same
windows.

  uv run --extra learner python scripts/count_plateau.py --raw docs/count-baseline-comparison-2026-10-04.json
"""
import argparse
import json
import sys
from math import log2
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relay_v_diagnosis import ols_cr1  # noqa: E402

from yupi.corpus.vocab import VOCAB  # noqa: E402
from yupi.corpus.writer import read_split  # noqa: E402
from yupi.learner.evaluate import surface_records  # noqa: E402
from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import load_table, serial_key  # noqa: E402

CACHE = Path.home() / ".cache/yupi-scratch/implicit"
TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
CELLS = ["r0-eps1", "r1-eps1", "r2-eps1", "r3-eps1", "r4-eps1", "r0-eps1_2", "r1-eps1_2", "r2-eps1_2", "r3-eps1_2", "r4-eps1_2"]
EDGES = [0, 1e-3, 1e-2, 5e-2, 0.1, 0.2, 0.4, 0.6, np.inf]


def census_rows(raw):
    c = json.load(open(raw))
    return c, {r["i"]: r for r in map(json.loads, open(c["per_window_file"]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    out = {"status": "EXPLORATORY (docs/count-baseline-design-v0.1.md)", "cells": {}}
    for cell in CELLS:
        cnt = json.load(open(f"docs/count-baseline-{cell}-2026-10-04.json"))
        cnt_rows = {r["i"]: r for r in map(json.loads, open(cnt["per_window_file"]))}
        tf = [census_rows(f"docs/learner-window-census-{cell}-2M-e15-seed{s}-2026-10-02.json") for s in (1, 2, 3)]
        ids = sorted(cnt_rows)
        assert all(sorted(r) == ids for _, r in tf), f"{cell}: window sets differ between count and transformer"
        y_cnt = np.array([cnt_rows[i]["by_field"]["kind"] for i in ids])
        y_tf = np.array([np.mean([r[i]["by_field"]["kind"] for _, r in tf]) for i in ids])
        res = dict(n=len(ids), count_kind=float(y_cnt.mean()), count_se=float(y_cnt.std(ddof=1) / np.sqrt(len(ids))),
                   transformer_kind=float(y_tf.mean()), transformer_seed_means=[float(np.mean([r[i]["by_field"]["kind"] for i in ids])) for _, r in tf],
                   count_unseen_classes=cnt["test_k7"]["classes_unseen_in_train"], count_classes=cnt["test_k7"]["classes"],
                   count_mode=cnt["chosen"])
        if not cell.startswith("r0"):
            tag = cell
            iota = {d["k"]: (d["iota_1"], d["iota_4"]) for d in map(json.loads, open(CACHE / f"c1prime-loop-40-8-2-{tag}-k7-kind-m123456.jsonl"))}
            hk, lm = {}, {}
            for key, (mass, star) in load_table(TABLES / f"c1prime-loop-40-8-2-{tag}-k7.jsonl").items():
                kd = {}
                for r, p in star.items():
                    kd[r.kind] = kd.get(r.kind, 0.0) + float(p)
                hk[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
                lm[serial_key(key)] = log2(float(mass))
            split = read_split(Path(tf[0][0]["corpus"]), "test")
            L4, S, H, M, G = [], [], [], [], []
            for i in ids:
                reset, recs = surface_records(tuple(VOCAB[t] for t in split[i][0]))
                key = serial_key((reset, pattern_all(recs[:7])[0]))
                i1, i4 = iota[key]
                L4.append(i4); S.append(i1 - i4); H.append(hk[key]); M.append(lm[key]); G.append(key)
            L4, S, H, M, G = map(np.asarray, (L4, S, H, M, G))
            bins = [((L4 > lo) & (L4 <= hi)).astype(float) for lo, hi in zip(EDGES[:-1], EDGES[1:])]
            X = np.column_stack([np.ones(len(ids))] + bins + [S, H, M])
            for lab, y in (("count", y_cnt), ("transformer", y_tf)):
                b, se, _ = ols_cr1(y, X, G)
                res[f"bins_{lab}"] = [dict(lo=lo, hi=float(hi), beta=float(b[j + 1]), t=float(b[j + 1] / se[j + 1]))
                                      for j, (lo, hi) in enumerate(zip(EDGES[:-1], EDGES[1:]))]
            res["share_iota4_zero"] = float((L4 == 0).mean())
        out["cells"][cell] = res
        line = f"{cell:10} count {res['count_kind']:.5f}±{res['count_se']:.5f}  transformer {res['transformer_kind']:.5f}  " \
               f"unseen {res['count_unseen_classes']}/{res['count_classes']}  mode {res['count_mode']}"
        print(line, flush=True)
        for lab in ("count", "transformer"):
            if f"bins_{lab}" in res:
                print(f"   {lab:11} bins: " + " ".join(f"{d['beta']:+.3f}(t{d['t']:+.1f})" for d in res[f"bins_{lab}"]), flush=True)
    json.dump(out, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
