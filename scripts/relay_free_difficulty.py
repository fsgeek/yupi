"""EXPLORATORY: which exact long-lag quantity indexes each rung's learner, ι4 of the relay-free history (r1)
or of the relayed one (r1ʀ)? docs/relay-free-difficulty-design-v0.1.md, committed before this script first ran.
Reuses the frozen relay_paired.py loaders and join (gates included) and relay_v_diagnosis.py's CR1 estimator.

    uv run --extra learner python scripts/relay_free_difficulty.py --raw docs/relay-free-difficulty-2026-10-04.json
"""
import argparse
import json
import subprocess
import sys
from math import log2
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relay_paired as rp  # noqa: E402  (frozen; imported unchanged)
import relay_v_diagnosis as dg  # noqa: E402  (ARMS, CR1 estimator, paths)

from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import load_table, serial_key  # noqa: E402

K = rp.K


def iota(path):
    out = {}
    for line in open(path):
        d = json.loads(line)
        out[d["k"]] = (d["iota_1"], d["iota_4"])
    return out


def fit(terms, cols, y, groups):
    X = np.column_stack([np.ones(len(y))] + cols)
    b, se, _ = dg.ols_cr1(y, X, groups)
    return dict(terms=["1"] + terms, beta=b.tolist(), se=se.tolist(), t=(b / se).tolist())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    f1 = dg.CACHE / "c1prime-loop-40-8-2-r1-eps1-k7-kind-m123456.jsonl"
    fR = dg.CACHE / "c1prime-loop-40-8-2-r1R-eps1-k7-kind-m123456.jsonl"
    ft = dg.TABLES / "c1prime-loop-40-8-2-r1-eps1-k7.jsonl"
    i1, iR = iota(f1), iota(fR)
    hk, lm = {}, {}
    for key, (mass, star) in load_table(ft).items():
        kd = {}
        for r, p in star.items():
            kd[r.kind] = kd.get(r.kind, 0.0) + float(p)
        hk[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
        lm[serial_key(key)] = log2(float(mass))
    diota, diota_meta = rp.load_diota(dg.EXACT_SIDE, "1")
    out = dict(status="EXPLORATORY (docs/relay-free-difficulty-design-v0.1.md)",
               git=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
               inputs=dict(iota_r1=dict(file=str(f1), sha256=dg.sha(f1)), iota_r1R=dict(file=str(fR), sha256=dg.sha(fR)),
                           table_r1=dict(file=str(ft), sha256=dg.sha(ft)), diota=diota_meta), fits={})
    for arm, (r1, r1R) in dg.ARMS.items():
        c1 = [rp.load_census(r) for r in r1]
        cR = [rp.load_census(r) for r in r1R]
        ids = sorted(c1[0][1])
        recs1 = rp.load_records(c1[0][0]["corpus"], ids, "r1")
        recsR = rp.load_records(cR[0][0]["corpus"], ids, "r1R")
        rp.join([r for _, r in c1], [r for _, r in cR], recs1, recsR, diota)  # gates only
        cols = {k: [] for k in ("l1", "lR", "s1", "sR", "h", "m", "g")}
        for i in ids:
            (s1, q1), (sR, qR) = recs1[i], recsR[i]
            k1 = serial_key((s1, pattern_all(q1[:K])[0]))
            kR = serial_key((sR, pattern_all(qR[:K])[0]))
            (a1, b1), (aR, bR) = i1[k1], iR[kR]
            cols["l1"].append(b1); cols["lR"].append(bR); cols["s1"].append(a1 - b1); cols["sR"].append(aR - bR)
            cols["h"].append(hk[k1]); cols["m"].append(lm[k1]); cols["g"].append(k1)
        l1, lR, s1, sR, h, m = (np.asarray(cols[k]) for k in ("l1", "lR", "s1", "sR", "h", "m"))
        g = np.asarray(cols["g"])
        ind = (l1 > 0).astype(float)
        for rung, rows in (("r1", c1), ("r1R", cR)):
            y = np.array([np.mean([r[i]["by_field"]["kind"] for _, r in rows]) for i in ids])
            names = ["iota4_r1", "iota4_r1R", "any_long_r1", "short_r1", "short_r1R", "H_kind", "log2mass"]
            full = fit(names, [l1, lR, ind, s1, sR, h, m], y, g)
            noind = fit([n for n in names if n != "any_long_r1"], [l1, lR, s1, sR, h, m], y, g)
            out["fits"][f"{rung}-{arm}"] = dict(n=int(len(y)), mean_excess=float(y.mean()), F=full, F_no_indicator=noind)
            for lab, r in (("F", full), ("F-ind", noind)):
                terms = " ".join(f"{tn}={bb:+.5f}(t {tt:+.1f})" for tn, bb, tt in zip(r["terms"], r["beta"], r["t"]))
                print(f"{rung:4} {arm:9} {lab:5} {terms}", flush=True)
    json.dump(out, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
