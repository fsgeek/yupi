"""UNSCORED descriptive supplement (addendum v0.1.1 §4 says the deciles of Δι are reported; the
frozen relay_paired.py does not compute them). Rebuilds the exact per-window arrays with the frozen
relay_paired.py functions (imported, unchanged) and reports Δexcess by decile of Δι_kind,4 plus the
exact-zero and Δι<-0.05 sets."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/tony/projects/yupi/scripts")
import relay_paired as rp
ARMS = {"primary": ([f"docs/learner-window-census-r1-eps1-2M-seed{s}-2026-09-21.json" for s in (1, 2, 3)],
                    [f"docs/learner-window-census-r1R-eps1-2M-e5-seed{s}-2026-10-02.json" for s in (1, 2, 3)]),
        "secondary": ([f"docs/learner-window-census-r1-eps1-2M-e15-seed{s}-2026-10-02.json" for s in (1, 2, 3)],
                      [f"docs/learner-window-census-r1R-eps1-2M-e15-seed{s}-2026-10-02.json" for s in (1, 2, 3)])}
out = {}
for arm, (r1, r1R) in ARMS.items():
    c1 = [rp.load_census(r) for r in r1]; cR = [rp.load_census(r) for r in r1R]
    ids = sorted(c1[0][1])
    recs1 = rp.load_records(c1[0][0]["corpus"], ids, "r1"); recsR = rp.load_records(cR[0][0]["corpus"], ids, "r1R")
    diota, _ = rp.load_diota("docs/relay-exact-side-2026-09-30.json", "1")
    ids, y, x, z, relay = rp.join([r for _, r in c1], [r for _, r in cR], recs1, recsR, diota)
    res = rp.analyse(y, x, z, relay, arm)
    edges = np.quantile(x, np.linspace(0, 1, 11))
    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, 9)
    dec = []
    for q in range(10):
        s = idx == q
        if s.any():
            dec.append(dict(q=q, x_lo=float(edges[q]), x_hi=float(edges[q + 1]), n=int(s.sum()), mean_d_iota=float(x[s].mean()),
                            mean_d_excess=float(y[s].mean()), se=float(y[s].std(ddof=1) / np.sqrt(s.sum()))))
    sets = {}
    for name, m in [("d_iota_lt_-0.05", x < -0.05), ("d_iota_in_[-0.05,0)", (x >= -0.05) & (x < 0)), ("exact_zero", z),
                    ("d_iota_eq_0_float_not_exact", (x == 0) & ~z), ("d_iota_gt_0", x > 0)]:
        sets[name] = dict(n=int(m.sum()), mean_d_excess=float(y[m].mean()) if m.any() else None,
                          se=float(y[m].std(ddof=1) / np.sqrt(m.sum())) if m.sum() > 1 else None,
                          mean_d_iota=float(x[m].mean()) if m.any() else None)
    out[arm] = dict(slope=res["slope"], intercept=res["intercept"], deciles_by_d_iota=dec, sets=sets)
    print(f"== {arm}: slope {res['slope']:+.5f} intercept {res['intercept']:+.5f}")
    for d in dec:
        print(f"  dec{d['q']} Δι [{d['x_lo']:+.4f},{d['x_hi']:+.4f}] n={d['n']:5d} meanΔι {d['mean_d_iota']:+.4f}  meanΔexcess {d['mean_d_excess']:+.5f} ± {d['se']:.5f}")
    for k, v in sets.items():
        print(f"  set {k:28} n={v['n']:5d} meanΔexcess {v['mean_d_excess'] if v['mean_d_excess'] is None else round(v['mean_d_excess'],5)} se {v['se'] if v['se'] is None else round(v['se'],5)} meanΔι {v['mean_d_iota']}")
Path("/home/tony/.cache/yupi-scratch/census/relay-deciles/relay-deciles-2026-10-02.json").write_text(json.dumps(out, indent=1))
