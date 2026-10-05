"""BLIND variance reader for the three-arm pilot (docs/three-arm-pilot-v0.1.md). Prints and stores ONLY between-seed
standard deviations, never means, signs or ratios.

  uv run python scripts/three_arm_pilot_sd.py --census-dir ~/.cache/yupi-scratch/runs/threearm-pilot/census \\
      --raw docs/three-arm-pilot-sd-<date>.json

Expects census raws named <rung>-s<seed>.json for rung in r1, r1R, r1D, r1S and seed in 101, 102, 103.
Per seed s and arm A in {R, D}: D_A,s(w) = y_S,s(w) − y_A,s(w), K_A,s = mean D over |Δι_A| > τ minus mean D over
Δι_A = 0 exactly (design v0.2 §2), and F_s = mean over windows of y_r1,s − y_S,s. Output: sd across seeds of
K_R, K_D and F (ddof = 1), and of the r1-control K (y_r1 − y_A) for continuity.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relay_paired import Gate, load_census, load_diota, load_records  # noqa: E402

from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import serial_key  # noqa: E402

EXACT = {"r1R": "docs/relay-exact-side-2026-09-30.json", "r1D": "docs/three-arm-exact-side-r1D-2026-10-05.json"}
SEEDS = (101, 102, 103)
TAUS = (0.05, 0.1, 0.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-dir", required=True)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    cd = Path(a.census_dir).expanduser()
    cen = {(r, s): load_census(cd / f"{r}-s{s}.json") for r in ("r1", "r1R", "r1D", "r1S") for s in SEEDS}
    ids = sorted(cen[("r1", SEEDS[0])][1])
    for (r, s), (c, rows) in cen.items():
        if sorted(rows) != ids or "0582ffbeb4693d27" not in c["corpus"] or f"-{r}-" not in c["corpus"] + "-":
            raise Gate(f"GATE: census {r} s{s} window set or corpus mismatch")
    recs = load_records(cen[("r1", SEEDS[0])][0]["corpus"], ids, "r1")
    keys = [serial_key((recs[i][0], pattern_all(recs[i][1][:7])[0])) for i in ids]
    dio = {arm: load_diota(EXACT[arm], "1")[0] for arm in EXACT}
    y = {k: np.array([rows[i]["by_field"]["kind"] for i in ids]) for k, (_, rows) in cen.items()}
    out = {"status": "BLIND PILOT: standard deviations across seeds only", "seeds": SEEDS, "n_windows": len(ids), "sd": {}}
    for arm in ("r1R", "r1D"):
        x = np.abs(np.array([dio[arm][k][1] for k in keys]))
        z = np.array([dio[arm][k][2] for k in keys])
        for tau in TAUS:
            M = x > tau
            for ctrl in ("r1S", "r1"):
                K = [(lambda D: D[M].mean() - D[z].mean())(y[(ctrl, s)] - y[(arm, s)]) for s in SEEDS]
                out["sd"][f"K_{arm}_tau{tau}_ctrl{ctrl}"] = float(np.std(K, ddof=1))
    out["sd"]["F_r1_minus_r1S"] = float(np.std([(y[("r1", s)] - y[("r1S", s)]).mean() for s in SEEDS], ddof=1))
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["sd"], indent=1))


if __name__ == "__main__":
    main()
