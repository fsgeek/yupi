"""Frozen scorer for the three-arm pre-registration (docs/three-arm-prereg-v0.1.md), written and tested before any
three-arm model exists.

  uv run python scripts/three_arm_score.py --budget e5 --raw docs/three-arm-verdict-raw-e5-<date>.json \\
      --r1 <census raw> <census raw> <census raw> --r1R <3 raws> --r1D <3 raws> --r1S <3 raws>

Per test window w with ≥ 7 records (the same windows in every arm, gated), with y the realized KIND excess
(census by_field.kind):
  G_arm(w) = mean over r1 seeds of y − mean over the arm's seeds of y
and, from the window's r1 class c (computed from the fresh r1 corpus's test split): |Δι_arm(c)|, read from the
three-arm exact side's per-class caches (sha-gated). OLS with CR1 errors clustered by r1 class.

Predictions (prereg §3), scored only at e5; at e15 every number is reported and nothing is scored:
  P_V     relay slope of G_R on |Δι_R|: t ≥ 3                                         (replication of the V)
  P_move  decoy slope of G_D on |Δι_D|: t ≥ 3, and slope_D / slope_R ≥ 0.5
  P_bind  slope_D / slope_R ≤ 0.25
  P_null  self-copy mean gain within ±2 CR1 se of 0
Reading: H_move if P_move and P_null; H_bind if P_bind and P_null; H_field indicated if P_null fails with a
positive mean; otherwise unresolved. Reported, not scored: each arm's mean gain on ι4_r1 = 0 windows and off them.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relay_paired import Gate, load_census, load_diota, load_records  # noqa: E402
from relay_v_diagnosis import ols_cr1  # noqa: E402

from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import serial_key  # noqa: E402

EXACT = {"r1R": "docs/relay-exact-side-2026-09-30.json",
         "r1D": "docs/three-arm-exact-side-r1D-2026-10-05.json",
         "r1S": "docs/three-arm-exact-side-r1S-2026-10-05.json"}
FRESH_RUN = "0582ffbeb4693d27"


def slope(y, x, g):
    b, se, _ = ols_cr1(y, np.column_stack([np.ones(len(y)), x]), g)
    return float(b[1]), float(se[1]), float(b[1] / se[1])


def mean_se(y, g):
    b, se, _ = ols_cr1(y, np.ones((len(y), 1)), g)
    return float(b[0]), float(se[0])


def score(GR, GD, GS, xR, xD, groups, zero_mask):
    """The prereg's predictions on per-window paired gains (pure; unit-tested with planted gains)."""
    bR, seR, tR = slope(GR, xR, groups)
    bD, seD, tD = slope(GD, xD, groups)
    mS, seS = mean_se(GS, groups)
    ratio = bD / bR if bR != 0 else float("nan")
    P = dict(P_V=tR >= 3, P_move=(tD >= 3 and ratio >= 0.5), P_bind=ratio <= 0.25, P_null=abs(mS) <= 2 * seS)
    if P["P_move"] and P["P_null"]:
        reading = "H_move"
    elif P["P_bind"] and P["P_null"]:
        reading = "H_bind"
    elif not P["P_null"] and mS > 0:
        reading = "H_field indicated"
    else:
        reading = "unresolved"
    zero = {}
    for name, G in (("r1R", GR), ("r1D", GD), ("r1S", GS)):
        z = zero_mask
        zero[name] = dict(on_iota4_zero=float(G[z].mean()), off_iota4_zero=float(G[~z].mean()), all=float(G.mean()))
    return dict(relay=dict(slope=bR, se=seR, t=tR), decoy=dict(slope=bD, se=seD, t=tD), ratio_D_over_R=ratio,
                self_copy=dict(mean=mS, se=seS), predictions={k: bool(v) for k, v in P.items()}, reading=reading,
                mean_gains=zero)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budget", required=True, choices=("e5", "e15"))
    ap.add_argument("--raw", required=True)
    for r in ("r1", "r1R", "r1D", "r1S"):
        ap.add_argument(f"--{r}", nargs=3, required=True)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    cen = {r: [load_census(p) for p in getattr(a, r)] for r in ("r1", "r1R", "r1D", "r1S")}
    ids = sorted(cen["r1"][0][1])
    for r, lst in cen.items():
        for c, rows in lst:
            if sorted(rows) != ids:
                raise Gate(f"GATE: {r} census windows differ from r1's")
            if FRESH_RUN not in c["corpus"]:
                raise Gate(f"GATE: {r} census is not on the fresh corpus run {FRESH_RUN}")
    corpus_r1 = cen["r1"][0][0]["corpus"]
    recs = load_records(corpus_r1, ids, "r1")
    keys = [serial_key((recs[i][0], pattern_all(recs[i][1][:7])[0])) for i in ids]
    dio, prov = {}, {}
    for arm in ("r1R", "r1D", "r1S"):
        dio[arm], prov[arm] = load_diota(EXACT[arm], "1")
    x = {arm: np.abs(np.array([dio[arm][k][1] for k in keys])) for arm in dio}
    if not (x["r1S"] == 0).all():
        raise Gate("GATE: the self-copy arm's |Δι| is not identically 0")
    i4 = {}
    for line in open(Path.home() / ".cache/yupi-scratch/implicit/c1prime-loop-40-8-2-r1-eps1-k7-kind-m123456.jsonl"):
        d = json.loads(line)
        i4[d["k"]] = d["iota_4"]
    zero = np.array([i4[k] == 0 for k in keys])
    y = {r: np.mean([[rows[i]["by_field"]["kind"] for i in ids] for _, rows in cen[r]], axis=0) for r in cen}
    _, g = np.unique(np.array(keys), return_inverse=True)
    G = {arm: y["r1"] - y[arm] for arm in ("r1R", "r1D", "r1S")}
    res = score(G["r1R"], G["r1D"], G["r1S"], x["r1R"], x["r1D"], g, zero)
    out = dict(prereg="docs/three-arm-prereg-v0.1.md", budget=a.budget, scored=(a.budget == "e5"),
               n_windows=len(ids), n_classes=int(g.max() + 1), share_iota4_zero=float(zero.mean()),
               censuses={r: [dict(raw=p, sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
                             for p in getattr(a, r)] for r in cen},
               exact_side=prov, **res)
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("budget", "scored", "predictions", "reading", "ratio_D_over_R")}, indent=1))


if __name__ == "__main__":
    main()
