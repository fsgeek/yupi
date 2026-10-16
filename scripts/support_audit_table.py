"""The §4.2 support table and the §4.3 exact kind sweep of the methods paper (owner, 2026-10-15).

Rows: ~/.cache/yupi-scratch/split-v2 (hashes in docs/split-v2-rows-sha256-2026-10-15.txt). Pattern observer, k = 7,
KIND. All shares are of the position-7 population (law mass 0.85). Definitions:
- pure: G < 1e-12 and H* > 1e-12; withheld (high-gap): H* > 1e-12 and G/H* >= 0.5; bins floor(H*/0.05).
- device coin: a pure class with |H* - h(1/3)| < 1e-4 (h(1/3) = 0.9182958 bits, the Bernoulli(1/3) entropy).
- graded: mass in bins where the mass-weighted (lower, first-crossing) q90 - q10 of G/H* is >= 0.30; "restricted"
  also requires bin mass >= 0.5 % and >= 5 classes.
- exact kind sweep: kinds are pure (G < 1e-12, H* > 0) and withheld (G >= 0.1); a class with a kind counts at δ if
  some class of the other kind has an exact next-KIND law within TV δ. Reported as a share of all position-7 mass
  and of the mass that carries a kind.
  python scripts/support_audit_table.py [--out docs/<name>.json]
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROWS = Path.home() / ".cache/yupi-scratch/split-v2"
H13 = 0.9182958340544896


def wq(xs, ws, q):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); t = sum(ws); a = 0.0
    for i in o:
        a += ws[i]
        if a >= q * t:
            return xs[i]
    return xs[o[-1]]


out = []
for eps in ("1", "1_2"):
    for rung in ("r1", "r2", "r3", "r4"):
        rows = [json.loads(l) for l in open(ROWS / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl")]
        M = sum(x["mass"] for x in rows)
        pos = [x for x in rows if x["h_star"] > 1e-12]
        pure = [x for x in pos if abs(x["g"]) < 1e-12]
        high = [x for x in pos if x["g"] / x["h_star"] >= 0.5]
        pb = {int(x["h_star"] / 0.05) for x in pure}
        hb = {int(x["h_star"] / 0.05) for x in high}
        line = dict(eps=eps.replace("_", "/"), rung=rung,
                    pure_eligible=sum(x["mass"] for x in pure) / M,
                    pure_matched=sum(x["mass"] for x in pure if int(x["h_star"] / 0.05) in hb) / M,
                    coin_share_of_pure=sum(x["mass"] for x in pure if abs(x["h_star"] - H13) < 1e-4) / sum(x["mass"] for x in pure),
                    high_eligible=sum(x["mass"] for x in high) / M,
                    high_matched=sum(x["mass"] for x in high if int(x["h_star"] / 0.05) in pb) / M,
                    n_shared_bins=len(pb & hb))
        bins = {}
        for x in pos:
            bins.setdefault(int(x["h_star"] / 0.05), []).append(x)
        g_all = g_res = 0.0
        for xs in bins.values():
            m = sum(x["mass"] for x in xs)
            f = [x["g"] / x["h_star"] for x in xs]; w = [x["mass"] for x in xs]
            if wq(f, w, 0.9) - wq(f, w, 0.1) >= 0.30:
                g_all += m
                if m / M >= 0.005 and len(xs) >= 5:
                    g_res += m
        line.update(graded=g_all / M, graded_restricted=g_res / M)
        # exact kind sweep over distinct (law, kind) pairs
        kinds = sorted({k for x in rows for k, _ in x["p_star"]})
        kind_of = lambda x: ("pure" if x["h_star"] > 1e-12 and abs(x["g"]) < 1e-12 else "withheld" if x["g"] >= 0.1 else None)
        agg = {}
        for x in rows:
            kd = kind_of(x)
            if kd is None:
                continue
            key = (tuple(sorted(map(tuple, x["p_star"]))), kd)
            agg[key] = agg.get(key, 0.0) + x["mass"]
        keys = list(agg)
        P = np.array([[float(Fraction(dict(k[0]).get(c, "0"))) for c in kinds] for k in keys])
        K = np.array([k[1] == "pure" for k in keys]); W = np.array([agg[k] for k in keys])
        carried = W.sum()
        for d in (0.01, 0.02, 0.05):
            hit = np.zeros(len(keys), bool)
            for i0 in range(0, len(keys), 512):
                tv = 0.5 * np.abs(P[i0:i0 + 512, None, :] - P[None, :, :]).sum(-1)
                other = K[i0:i0 + 512, None] != K[None, :]
                hit[i0:i0 + 512] = ((tv <= d + 1e-15) & other).any(1)
            line[f"kind_exist_{d}"] = float(W[hit].sum() / M)
            line[f"kind_exist_{d}_of_carried"] = float(W[hit].sum() / carried)
        line["kind_carried"] = float(carried / M)
        out.append(line)
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in line.items()}), flush=True)
if "--out" in sys.argv:
    Path(sys.argv[sys.argv.index("--out") + 1]).write_text(json.dumps(dict(rows_hashes="docs/split-v2-rows-sha256-2026-10-15.txt", rows=out), indent=1))
