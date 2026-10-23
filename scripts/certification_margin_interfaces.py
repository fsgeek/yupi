"""Declared: docs/certification-margin-interfaces-declared-2026-10-22.md (stamped before computing).

mu_c(gamma): TV from a pure class's exact next-KIND law to the nearest exact law (same table) whose class-mass-weighted
G is >= gamma. Per (interface, eps): pure-mass-weighted median and q10 of mu(gamma), and the pure mass share with
mu(gamma) >= 0.02.

  python scripts/certification_margin_interfaces.py [--out FILE]
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

SPLIT = Path.home() / ".cache/yupi-scratch/split-v2"
GAMMAS = (0.01, 0.03, 0.1, 0.3)


def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]) / w.sum()
    return float(x[o][np.searchsorted(c, q)])


def cell(rung, eps):
    groups = {}
    for line in open(SPLIT / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl"):
        r = json.loads(line)
        law = tuple(sorted(map(tuple, r["p_star"])))
        g = groups.setdefault(law, [0.0, 0.0, 0.0, 0.0])  # mass, mass*g, mass*h, pure mass
        g[0] += r["mass"]; g[1] += r["mass"] * r["g"]; g[2] += r["mass"] * r["h_star"]
        if r["h_star"] > 1e-12 and abs(r["g"]) < 1e-12:
            g[3] += r["mass"]
    laws = list(groups)
    kinds = sorted({k for law in laws for k, _ in law})
    P = np.array([[float(Fraction(dict(law).get(k, "0"))) for k in kinds] for law in laws])
    G = np.array([groups[l][1] / groups[l][0] for l in laws])
    PM = np.array([groups[l][3] for l in laws])
    pi = np.nonzero(PM > 0)[0]
    out: dict = dict(rung=rung, eps=eps.replace("_", "/"), n_pure_laws=int(len(pi)), pure_mass=float(PM.sum()))
    for gam in GAMMAS:
        ni = np.nonzero(G >= gam)[0]
        if len(ni) == 0:
            out[str(gam)] = None
            continue
        mu = (0.5 * np.abs(P[pi, None, :] - P[None, ni, :]).sum(-1)).min(1)
        w = PM[pi]
        out[str(gam)] = dict(median=wq(mu, w, 0.5), q10=wq(mu, w, 0.1),
                             share_ge_0_02=float(w[mu >= 0.02].sum() / w.sum()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = []
    for eps in ("1", "1_2"):
        for rung in ("r0", "r1", "r2", "r3", "r4"):
            r = cell(rung, eps)
            rows.append(r)
            print(r["rung"], r["eps"], r["n_pure_laws"], " | ".join(
                f"g{g}: med {r[str(g)]['median']:.4f} q10 {r[str(g)]['q10']:.4f} >=.02 {r[str(g)]['share_ge_0_02']:.3f}"
                if r[str(g)] else f"g{g}: none" for g in GAMMAS), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/certification-margin-interfaces-declared-2026-10-22.md",
                                               rows=rows), indent=1))


if __name__ == "__main__":
    main()
