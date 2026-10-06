"""Power and severity of prereg v0.2's readings (docs/three-arm-prereg-v0.2.md §5), simulated at the SEED level with
the frozen scorer's own score_seeds(). Computed before stamping. No pilot means are used; only the pilot's sds
(docs/three-arm-pilot-sd-2026-10-05.json) and the 10-02 templates' sd.

  uv run python scripts/three_arm_severity_v2.py --raw docs/three-arm-severity-v2-2026-10-05.json [--sims 400]

Per scenario: n = 12 seeds; K_R ~ N(mu_R, sd_R); K_D ~ N(rho·mu_R·mD/mR, sd_D) with corr(K_R, K_D) = c;
KS_R, KS_D ~ N(0, sd_S) independent; F ~ N(0, sd_F). sd sets: "point" and "upper80" (the 80 % upper bound for each sd's
df: ×1.94 at df 4, ×3.08 at df 2). sd_S is not measured by the pilot directly; it is bracketed at 0.002 and 0.004.
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from three_arm_score_v2 import MARGINS, score_seeds  # noqa: E402

MR, MD = 0.340, 0.383


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--sims", type=int, default=400)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    rng = np.random.default_rng(20261005)
    sds = {"point": dict(R=0.0025, D=0.0017, F=0.0011), "upper80": dict(R=0.0025 * 1.94, D=0.0017 * 3.08, F=0.0011 * 3.08)}
    rows = []
    for (sdname, sd), muR, rho, c, sdS in itertools.product(sds.items(), (0.004, 0.006), (1.0, 0.4, 0.0), (0.0, 0.5), (0.002, 0.004)):
        counts = {}
        for _ in range(a.sims):
            z1, z2 = rng.normal(size=(2, 12))
            KR = muR + sd["R"] * z1
            KD = rho * muR * MD / MR + sd["D"] * (c * z1 + np.sqrt(1 - c * c) * z2)
            KSR, KSD = rng.normal(0, sdS, (2, 12))
            F = rng.normal(0, sd["F"], 12)
            r = score_seeds(KR, KD, KSR, KSD, MR, MD, F, MARGINS, n_boot=1000, rng_seed=int(rng.integers(1 << 31)))
            counts[r["reading"]] = counts.get(r["reading"], 0) + 1
        row = dict(sd=sdname, mu_R=muR, rho=rho, corr=c, sd_S=sdS, readings={k: v / a.sims for k, v in counts.items()})
        rows.append(row)
        print(json.dumps(row), flush=True)
    Path(a.raw).write_text(json.dumps(dict(prereg="docs/three-arm-prereg-v0.2.md §5", sims=a.sims, margins=MARGINS,
                                           sds=sds, mR=MR, mD=MD, rows=rows), indent=1) + "\n")


if __name__ == "__main__":
    main()
