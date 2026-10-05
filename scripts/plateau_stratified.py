"""EXPLORATORY (docs/plateau-stratified-design-v0.1.md): does the ι4 > 0 step survive fixed effects for observable
class type (last prefix kind × IO_ISSUE-in-window × reset)? Same windows, excess and covariates as
scripts/count_plateau.py; spec A must reproduce docs/count-baseline-comparison-2026-10-04.json.

  uv run --extra learner python scripts/plateau_stratified.py --raw docs/plateau-stratified-2026-10-05.json
"""
import argparse
import json
import sys
from math import log2
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_plateau import CACHE, EDGES, TABLES, census_rows  # noqa: E402
from relay_v_diagnosis import ols_cr1  # noqa: E402

from yupi.corpus.vocab import VOCAB  # noqa: E402
from yupi.corpus.writer import read_split  # noqa: E402
from yupi.learner.evaluate import surface_records  # noqa: E402
from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import load_table, serial_key  # noqa: E402

CELLS = ["r1-eps1", "r2-eps1", "r3-eps1", "r4-eps1", "r1-eps1_2", "r2-eps1_2", "r3-eps1_2", "r4-eps1_2"]
REF = "docs/count-baseline-comparison-2026-10-04.json"


def dummies(labels):
    levels = sorted(set(labels))
    return [(labels == v).astype(float) for v in levels[1:]], len(levels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    ref = json.load(open(REF))["cells"]
    out = {"status": "EXPLORATORY (docs/plateau-stratified-design-v0.1.md)", "cells": {}}
    for cell in CELLS:
        cnt = json.load(open(f"docs/count-baseline-{cell}-2026-10-04.json"))
        cnt_rows = {r["i"]: r for r in map(json.loads, open(cnt["per_window_file"]))}
        tf = [census_rows(f"docs/learner-window-census-{cell}-2M-e15-seed{s}-2026-10-02.json") for s in (1, 2, 3)]
        ids = sorted(cnt_rows)
        ys = {"count": np.array([cnt_rows[i]["by_field"]["kind"] for i in ids]),
              "transformer": np.array([np.mean([r[i]["by_field"]["kind"] for _, r in tf]) for i in ids])}
        iota = {d["k"]: (d["iota_1"], d["iota_4"]) for d in map(json.loads, open(CACHE / f"c1prime-loop-40-8-2-{cell}-k7-kind-m123456.jsonl"))}
        hk, lm = {}, {}
        for key, (mass, star) in load_table(TABLES / f"c1prime-loop-40-8-2-{cell}-k7.jsonl").items():
            kd = {}
            for r, p in star.items():
                kd[r.kind] = kd.get(r.kind, 0.0) + float(p)
            hk[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
            lm[serial_key(key)] = log2(float(mass))
        split = read_split(Path(tf[0][0]["corpus"]), "test")
        L4, S, H, M, G, LK, IO, R = [], [], [], [], [], [], [], []
        for i in ids:
            reset, recs = surface_records(tuple(VOCAB[t] for t in split[i][0]))
            key = serial_key((reset, pattern_all(recs[:7])[0]))
            i1, i4 = iota[key]
            L4.append(i4); S.append(i1 - i4); H.append(hk[key]); M.append(lm[key]); G.append(key)
            LK.append(recs[6].kind); IO.append(any(r.kind == "IO_ISSUE" for r in recs[:7])); R.append(bool(reset))
        L4, S, H, M, G, LK, IO, R = map(np.asarray, (L4, S, H, M, G, LK, IO, R))
        cellfe = np.array([f"{k}|{o}|{r}" for k, o, r in zip(LK, IO, R)])
        bins = [((L4 > lo) & (L4 <= hi)).astype(float) for lo, hi in zip(EDGES[:-1], EDGES[1:])]
        fe_lk, n_lk = dummies(LK)
        fe_c, n_c = dummies(cellfe)
        one = np.ones(len(ids))
        specs = {"A": np.column_stack([one] + bins + [S, H, M]),
                 "B": np.column_stack([one] + bins + [S, H, M] + fe_lk),
                 "C": np.column_stack([one] + bins + [S, H, M] + fe_c)}
        res = {"n": len(ids), "n_lastkind_levels": n_lk, "n_type_cells": n_c}
        for lab, y in ys.items():
            for sp, X in specs.items():
                b, se, _ = ols_cr1(y, X, G)
                res[f"{sp}_{lab}"] = [dict(lo=lo, hi=float(hi), beta=float(b[j + 1]), t=float(b[j + 1] / se[j + 1]))
                                      for j, (lo, hi) in enumerate(zip(EDGES[:-1], EDGES[1:]))]
            for d, r in zip(res[f"A_{lab}"], ref[cell][f"bins_{lab}"]):
                if abs(d["beta"] - r["beta"]) > 1e-9:
                    raise SystemExit(f"GATE FAIL {cell} {lab}: spec A does not reproduce {REF}")
            sub = L4 <= 0.01
            fe_d, _ = dummies(cellfe[sub])
            X = np.column_stack([np.ones(sub.sum()), (L4[sub] > 0).astype(float), S[sub], H[sub], M[sub]] + fe_d)
            b, se, _ = ols_cr1(y[sub], X, G[sub])
            res[f"D_{lab}"] = dict(beta=float(b[1]), t=float(b[1] / se[1]), n=int(sub.sum()),
                                   n_pos=int((L4[sub] > 0).sum()))
        out["cells"][cell] = res
        for lab in ys:
            print(f"{cell:10} {lab:11} " + "  ".join(
                f"{sp}: lo {res[f'{sp}_{lab}'][0]['beta']:+.4f}(t{res[f'{sp}_{lab}'][0]['t']:+.1f}) "
                f"top {res[f'{sp}_{lab}'][-1]['beta']:+.4f}(t{res[f'{sp}_{lab}'][-1]['t']:+.1f})" for sp in "ABC")
                + f"  D: {res[f'D_{lab}']['beta']:+.4f}(t{res[f'D_{lab}']['t']:+.1f}) n+{res[f'D_{lab}']['n_pos']}/{res[f'D_{lab}']['n']}",
                flush=True)
    for lab in ("count", "transformer"):
        ts = [out["cells"][c][f"D_{lab}"] for c in CELLS]
        surv = sum(d["beta"] > 0 and d["t"] >= 3 for d in ts); absb = sum(abs(d["t"]) < 2 for d in ts)
        verdict = "survives" if surv >= 6 else "absorbed" if absb >= 6 else "mixed"
        out[f"verdict_{lab}"] = dict(survives_cells=surv, absorbed_cells=absb, verdict=verdict)
        print(f"VERDICT {lab}: {verdict} (t>=3 & beta>0 in {surv}/8; |t|<2 in {absb}/8)")
    json.dump(out, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
