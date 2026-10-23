"""Declared: docs/two-step-margin-declared-2026-10-23.md (stamped before computing).

Per (interface, eps): for pure classes (G < 1e-12, H* > 1e-12), mu1 = TV from the class's one-step law to the nearest
withheld (G >= 0.1) one-step law group of law mass >= floor, and mu2 the same with two-step laws (groups by p2).
Reported pure-mass-weighted (median, q10) over all pure classes and over the coin's classes (one-step law
2/3 DISPATCH, 1/3 IO_COMPLETE), for floors 0, 1e-5, 1e-4, 1e-3. Also T0: the share of pure mass with mu2 < mu1.

  python scripts/two_step_margin.py --rows-dir DIR [--out FILE]
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

FLOORS = (0.0, 1e-5, 1e-4, 1e-3)
COIN = (("DISPATCH", "2/3"), ("IO_COMPLETE", "1/3"))


def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]) / w.sum()
    return float(x[o][min(np.searchsorted(c, q), len(x) - 1)])


def vecs(laws):
    keys = sorted({k for law in laws for k, _ in law})
    ix = {k: i for i, k in enumerate(keys)}
    V = np.zeros((len(laws), len(keys)))
    for i, law in enumerate(laws):
        for k, v in law:
            V[i, ix[k]] = float(Fraction(v))
    return V


def nearest(A, B, chunk=512):
    out = np.empty(len(A))
    for i in range(0, len(A), chunk):
        out[i:i + chunk] = (0.5 * np.abs(A[i:i + chunk, None, :] - B[None, :, :]).sum(-1)).min(1)
    return out


def cell(path):
    rows = [json.loads(l) for l in open(path)]
    M = sum(r["mass"] for r in rows)
    pure = [r for r in rows if r["h_star"] > 1e-12 and abs(r["g"]) < 1e-12]
    wh = [r for r in rows if r["g"] >= 0.1]
    g1, g2 = {}, {}
    for r in wh:
        k1 = tuple(map(tuple, r["p_star"])); k2 = tuple(map(tuple, r["p2"]))
        g1[k1] = g1.get(k1, 0.0) + r["mass"]; g2[k2] = g2.get(k2, 0.0) + r["mass"]
    pg = {}
    for r in pure:
        key = (tuple(map(tuple, r["p_star"])), tuple(map(tuple, r["p2"])))
        pg[key] = pg.get(key, 0.0) + r["mass"]
    pkeys = list(pg); pw = np.array([pg[k] for k in pkeys])
    coin = np.array([k[0] == COIN for k in pkeys])
    l1 = list(g1); l2 = list(g2)
    m1 = np.array([g1[k] for k in l1]) / M; m2 = np.array([g2[k] for k in l2]) / M
    A1 = vecs([k[0] for k in pkeys] + l1); P1, W1 = A1[:len(pkeys)], A1[len(pkeys):]
    A2 = vecs([k[1] for k in pkeys] + l2); P2, W2 = A2[:len(pkeys)], A2[len(pkeys):]
    out: dict = dict(n_pure_groups=len(pkeys), n_withheld_laws_1=len(l1), n_withheld_laws_2=len(l2))
    for f in FLOORS:
        mu1 = nearest(P1, W1[m1 >= f]) if (m1 >= f).any() else np.full(len(pkeys), np.nan)
        mu2 = nearest(P2, W2[m2 >= f]) if (m2 >= f).any() else np.full(len(pkeys), np.nan)
        e = dict(mu1_median=wq(mu1, pw, 0.5), mu1_q10=wq(mu1, pw, 0.1),
                 mu2_median=wq(mu2, pw, 0.5), mu2_q10=wq(mu2, pw, 0.1),
                 coin_mu1_median=wq(mu1[coin], pw[coin], 0.5), coin_mu2_median=wq(mu2[coin], pw[coin], 0.5),
                 coin_mu2_q10=wq(mu2[coin], pw[coin], 0.1),
                 T0_share_mu2_lt_mu1=float(pw[mu2 < mu1 - 1e-12].sum() / pw.sum()))
        out[str(f)] = e
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows-dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = []
    for eps in ("1", "1_2"):
        for rung in ("r0", "r1", "r2", "r3", "r4"):
            c = cell(Path(a.rows_dir) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl")
            c.update(rung=rung, eps=eps.replace("_", "/"))
            res.append(c)
            print(rung, c["eps"], " | ".join(
                f"f{f}: coin mu1 {c[str(f)]['coin_mu1_median']:.4f} mu2 {c[str(f)]['coin_mu2_median']:.4f} (q10 {c[str(f)]['coin_mu2_q10']:.4f}); all mu2 med {c[str(f)]['mu2_median']:.4f}; T0 {c[str(f)]['T0_share_mu2_lt_mu1']:.3f}"
                for f in FLOORS), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/two-step-margin-declared-2026-10-23.md", rows=res), indent=1))


if __name__ == "__main__":
    main()
