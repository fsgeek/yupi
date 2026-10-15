"""Declared check: docs/identifiability-tolerance-check-2026-10-15.md. U(δ) = law mass of classes whose TV δ-ball
(over exact P*(KIND) vectors) contains a class with |ΔG| ≥ 0.1 bits.
  python scripts/identifiability_tolerance.py [--out docs/<name>.json]
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROWS = Path.home() / ".cache/yupi-scratch/split-v2"
DELTAS = (0.005, 0.01, 0.02, 0.05)
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
res = []
for eps in ("1", "1_2"):
    for rung in ("r1", "r2", "r3", "r4"):
        rows = [json.loads(l) for l in open(ROWS / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl")]
        kinds = sorted({k for r in rows for k, _ in r["p_star"]})
        groups = {}
        for r in rows:
            key = tuple(sorted(map(tuple, r["p_star"])))
            g = groups.setdefault(key, [0.0, [], ])
            g[0] += r["mass"]
            g[1].append((r["mass"], r["g"]))
        keys = list(groups)
        P = np.array([[float(Fraction(dict(k).get(x, "0"))) for x in kinds] for k in keys])
        gmin = np.array([min(y for _, y in groups[k][1]) for k in keys])
        gmax = np.array([max(y for _, y in groups[k][1]) for k in keys])
        M = sum(r["mass"] for r in rows)
        line = dict(eps=eps.replace("_", "/"), rung=rung, n_classes=len(rows), n_groups=len(keys))
        # per class: is there a class within δ whose G differs by >= 0.1? Using group extremes is exact for that.
        lo_ball = {d: np.empty(len(keys)) for d in DELTAS}
        hi_ball = {d: np.empty(len(keys)) for d in DELTAS}
        for i0 in range(0, len(keys), 512):
            tv = 0.5 * np.abs(P[i0:i0 + 512, None, :] - P[None, :, :]).sum(-1)
            for d in DELTAS:
                inb = tv <= d + 1e-15
                lo_ball[d][i0:i0 + 512] = np.where(inb, gmin[None, :], np.inf).min(1)
                hi_ball[d][i0:i0 + 512] = np.where(inb, gmax[None, :], -np.inf).max(1)
        for d in DELTAS:
            u = 0.0
            for j, k in enumerate(keys):
                for m, g in groups[k][1]:
                    if hi_ball[d][j] - g >= 0.1 or g - lo_ball[d][j] >= 0.1:
                        u += m
            line[f"U_{d}"] = u / M
        res.append(line)
        print(line, flush=True)
for eps in ("1", "1/2"):
    c = [r for r in res if r["eps"] == eps]
    hi = sum(r["U_0.05"] >= 0.25 for r in c)
    lo = all(r["U_0.05"] < 0.05 for r in c)
    print(f"eps {eps}: rungs with U(0.05) >= 25%: {hi}/4 -> " + ("NOT DETERMINED AT LEARNER PRECISION" if hi >= 3 else "READABLE" if lo else "CURVE ONLY"))
if out:
    Path(out).write_text(json.dumps(dict(declared="docs/identifiability-tolerance-check-2026-10-15.md", rows=res), indent=1))
