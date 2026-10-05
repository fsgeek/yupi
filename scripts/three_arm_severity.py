"""Severity of the three-arm candidate predictions (docs/three-arm-design-v0.1.md §7), computed BEFORE the prereg.

  uv run python scripts/three_arm_severity.py --raw docs/three-arm-severity-2026-10-05.json [--sims 400]

Template data: the 2026-10-02 relay arm's own test windows (k = 7) and censuses, as assembled by
docs/review-2026-10-04/build.py into ~/.cache/yupi-scratch/review-2026-10-04/arrays.npz (sha256 recorded). Per window:
the paired relay gain G_R = mean_s y_r1 − mean_s y_r1R, the relay's |Δι_R| (column `dio`) and, joined by the r1 class
key, the decoy's |Δι_D| from the three-arm exact side's cache.

Noise model: fit G_R = a + b|Δι_R| (per budget) and keep the residuals e. A simulated arm's gain is its hypothesis's
mean plus e with a Rademacher sign drawn per CLASS (a wild cluster bootstrap: keeps heteroskedasticity and
within-class dependence). Each arm draws its signs independently. The real arms share the r1 seeds, which correlates
their noise and makes ratios more precise, so the severities here are conservative.

Hypotheses (b_R and a_R are the relay fit's, per budget):
  H_move   G_D = b_R |Δι_D|             G_S = 0
  H_bind   G_D = 0                      G_S = 0
  H_field  G_D = a_R                    G_S = a_R      (a field effect the size of the relay's intercept)
Relay arm in every simulation: G_R = a_R + b_R |Δι_R|.

Candidate predictions (scored on each simulated experiment; slopes by OLS with CR1 by class):
  P_move  decoy slope on |Δι_D| has t ≥ 3 and slope_D / slope_R ≥ 0.5
  P_bind  slope_D / slope_R ≤ 0.25
  P_null  self-copy mean gain within ±2 CR1 se of 0
Severity of a prediction against a rival = the share of the rival's simulated outcomes in which the prediction
FAILS. Power = the share of its own hypothesis's outcomes in which it holds. Design §7's bar: severity ≥ 0.8.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relay_v_diagnosis import ols_cr1  # noqa: E402

ARR = Path.home() / ".cache/yupi-scratch/review-2026-10-04/arrays.npz"
DECOY = Path.home() / ".cache/yupi-scratch/relay/c1prime-loop-40-8-2-r1D-eps1-k7-kind-diota4.jsonl"


def slope(y, x, g):
    X = np.column_stack([np.ones(len(y)), x])
    b, se, _ = ols_cr1(y, X, g)
    return b[1], b[1] / se[1], b[0], se[0]


def mean_se(y, g):
    b, se, _ = ols_cr1(y, np.ones((len(y), 1)), g)
    return b[0], se[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--sims", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20261005)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    A = np.load(ARR)
    dD = {}
    for line in open(DECOY):
        d = json.loads(line)
        dD[d["k"]] = d["d_iota4"]
    k1 = A["k1"]
    xR = np.abs(A["dio"])
    xD = np.abs(np.array([dD[k] for k in k1]))
    _, g = np.unique(k1, return_inverse=True)
    n_cls = g.max() + 1
    rng = np.random.default_rng(a.seed)
    out = dict(design="docs/three-arm-design-v0.1.md §7", arrays=str(ARR),
               arrays_sha256=hashlib.sha256(ARR.read_bytes()).hexdigest(), decoy_cache=str(DECOY),
               decoy_cache_sha256=hashlib.sha256(DECOY.read_bytes()).hexdigest(), sims=a.sims, seed=a.seed,
               n_windows=int(len(k1)), n_classes=int(n_cls),
               corr_absdiota_R_D=float(np.corrcoef(xR, xD)[0, 1]),
               discriminating=dict(share_D_gt_R_by_0_1=float(((xD - xR) > 0.1).mean()),
                                   share_R_gt_D_by_0_1=float(((xR - xD) > 0.1).mean())),
               budgets={})
    for budget in ("primary", "secondary"):
        y1 = np.mean([A[f"y_r1_{budget}_s{s}"] for s in range(3)], axis=0)
        yR = np.mean([A[f"y_r1R_{budget}_s{s}"] for s in range(3)], axis=0)
        G = y1 - yR
        bR, tR, aR, _ = slope(G, xR, g)
        e = G - (aR + bR * xR)
        hyp_means = {"H_move": (bR * xD, np.zeros_like(xD)), "H_bind": (np.zeros_like(xD), np.zeros_like(xD)),
                     "H_field": (np.full_like(xD, aR), np.full_like(xD, aR))}
        res = {}
        for h, (mD, mS) in hyp_means.items():
            hits = {"P_move": 0, "P_bind": 0, "P_null": 0}
            ratios = []
            for _ in range(a.sims):
                s1, s2, s3 = (rng.choice((-1.0, 1.0), n_cls)[g] for _ in range(3))
                GR = aR + bR * xR + s1 * e
                GD = mD + s2 * e
                GS = mS + s3 * e
                sr, _, _, _ = slope(GR, xR, g)
                sd, td, _, _ = slope(GD, xD, g)
                ms, ses = mean_se(GS, g)
                r = sd / sr if sr != 0 else np.nan
                ratios.append(r)
                hits["P_move"] += (td >= 3 and r >= 0.5)
                hits["P_bind"] += (r <= 0.25)
                hits["P_null"] += (abs(ms) <= 2 * ses)
            res[h] = dict(holds={p: v / a.sims for p, v in hits.items()},
                          ratio_quantiles=[float(q) for q in np.nanquantile(ratios, [0.05, 0.5, 0.95])])
        sev = {"P_move": dict(power=res["H_move"]["holds"]["P_move"],
                              severity_vs_H_bind=1 - res["H_bind"]["holds"]["P_move"],
                              severity_vs_H_field=1 - res["H_field"]["holds"]["P_move"]),
               "P_bind": dict(power=res["H_bind"]["holds"]["P_bind"],
                              severity_vs_H_move=1 - res["H_move"]["holds"]["P_bind"]),
               "P_null": dict(power=res["H_move"]["holds"]["P_null"],
                              severity_vs_H_field=1 - res["H_field"]["holds"]["P_null"])}
        out["budgets"][budget] = dict(relay_fit=dict(slope=float(bR), t=float(tR), intercept=float(aR)),
                                      by_hypothesis=res, severity=sev)
        print(budget, json.dumps(out["budgets"][budget]["relay_fit"]), json.dumps(sev), flush=True)
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
