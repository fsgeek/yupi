"""Post hoc (2026-10-27, not declared): split two-step joint entropy into H(K7) + H(K8|K7). See docs/entropy-only-observer-result-2026-10-27.md.

  python scripts/entropy_two_step_split_posthoc.py ROWS_DIR
"""
import json, math, sys
from fractions import Fraction
from pathlib import Path
import numpy as np
sys.path.insert(0, "scripts")
from entropy_only_observer import auc

def H(ps): return -sum(p*math.log2(p) for p in ps if p > 0)

for f in sorted(Path(sys.argv[1]).glob("*-k6.jsonl")):
    w, pos, h1, h2, hm, hc, dd, g = [], [], [], [], [], [], [], []
    for line in open(f):
        r = json.loads(line)
        if r["h_star"] <= 1e-12 or 1e-12 <= abs(r["g"]) < 0.1: continue
        w.append(r["mass"] * (0.5 if r["key"].startswith("(True,") else 1.0)); pos.append(r["g"] >= 0.1); g.append(r["g"])
        p1 = {k: float(Fraction(v)) for k, v in r["p_star"]}
        p2 = {k: float(Fraction(v)) for k, v in r["p2"]}
        marg = {}
        for k, v in p2.items(): a = k.split("|")[0]; marg[a] = marg.get(a, 0) + v
        h1.append(H(p1.values())); h2.append(H(p2.values())); hm.append(H(marg.values()))
        hcond = H(p2.values()) - H(marg.values()); hc.append(hcond)
        # share of second-step mass on DISPATCH continuations (scheduler-randomness proxy)
        dd.append(sum(v for k, v in p2.items() if k.split("|")[1] == "DISPATCH"))
    w, pos, h1, h2, hm, hc, dd, g = map(np.array, (w, pos, h1, h2, hm, hc, dd, g))
    def wm(x, s): return float((x[s]*w[s]).sum()/w[s].sum())
    print("   H1-Hc %.3f" % auc(h1 - hc, pos, w), end=" "); print("%-14s AUC H1 %.3f margK7 %.3f | H(K8|K7) %.3f | joint %.3f || mean H(K8|K7) pure %.2f wh %.2f | mean H1 pure %.2f wh %.2f | P(K8=DISPATCH) pure %.2f wh %.2f" % (
        f.stem[20:], auc(h1,pos,w), auc(hm,pos,w), auc(hc,pos,w), auc(h2,pos,w),
        wm(hc,~pos), wm(hc,pos), wm(h1,~pos), wm(h1,pos), wm(dd,~pos), wm(dd,pos)))
