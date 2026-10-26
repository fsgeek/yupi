"""Declared: docs/three-step-margin-declared-2026-10-26.md (stamped before computing).

Per (interface, eps) at k = 5: mu_d (d = 1, 2, 3) from each pure class to the nearest withheld class (floor 0);
medians over the coin's classes and over all pure classes (pure-mass-weighted); D0 check.

  python scripts/three_step_margin.py --rows-dir DIR [--out FILE]
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

COIN = (("DISPATCH", "2/3"), ("IO_COMPLETE", "1/3"))


def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]) / w.sum()
    return float(x[o][min(np.searchsorted(c, q), len(x) - 1)])


def vecs(laws):
    keys = sorted({k for law in laws for k, _ in law}); ix = {k: i for i, k in enumerate(keys)}
    V = np.zeros((len(laws), len(keys)))
    for i, law in enumerate(laws):
        for k, v in law:
            V[i, ix[k]] = float(Fraction(v))
    return V


def nearest(A, B, chunk=256):
    out = np.empty(len(A))
    for i in range(0, len(A), chunk):
        out[i:i + chunk] = (0.5 * np.abs(A[i:i + chunk, None, :] - B[None, :, :]).sum(-1)).min(1)
    return out


def cell(path):
    rows = [json.loads(l) for l in open(path)]
    pure = [r for r in rows if r["h_star"] > 1e-12 and abs(r["g"]) < 1e-12]
    wh = [r for r in rows if r["g"] >= 0.1]
    pg = {}
    for r in pure:
        key = tuple(tuple(map(tuple, r[f])) for f in ("p_star", "p2", "p3"))
        pg[key] = pg.get(key, 0.0) + r["mass"]
    keys = list(pg); w = np.array([pg[k] for k in keys]); coin = np.array([k[0] == COIN for k in keys])
    out: dict = dict(n_pure_groups=len(keys))
    mus = []
    for d, f in enumerate(("p_star", "p2", "p3")):
        wl = list({tuple(map(tuple, r[f])) for r in wh})
        A = vecs([k[d] for k in keys] + wl)
        mu = nearest(A[:len(keys)], A[len(keys):])
        mus.append(mu)
        out[f"mu{d + 1}"] = dict(coin_median=wq(mu[coin], w[coin], 0.5) if coin.any() else None, all_median=wq(mu, w, 0.5))
    out["D0_violations_mass"] = float(w[(mus[0] > mus[1] + 1e-12) | (mus[1] > mus[2] + 1e-12)].sum() / w.sum())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows-dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = []
    for eps in ("1", "1_2"):
        for rung in ("r0", "r1", "r2", "r3", "r4"):
            c = cell(Path(a.rows_dir) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k5.jsonl")
            c.update(rung=rung, eps=eps.replace("_", "/")); res.append(c)
            print(rung, c["eps"], "coin mu1 %.4f mu2 %.4f mu3 %.4f | all mu1 %.4f mu2 %.4f mu3 %.4f | D0 viol %.4f" % (
                c["mu1"]["coin_median"], c["mu2"]["coin_median"], c["mu3"]["coin_median"],
                c["mu1"]["all_median"], c["mu2"]["all_median"], c["mu3"]["all_median"], c["D0_violations_mass"]), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/three-step-margin-declared-2026-10-26.md", rows=res), indent=1))


if __name__ == "__main__":
    main()
