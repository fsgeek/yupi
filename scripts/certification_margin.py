"""Declared check: docs/certification-margin-declared-2026-10-22.md (stamped before per-window data was read).

mu_c: TV from a pure class's exact law to the nearest exact law (same table) whose kind is withheld or none (G > 0,
not deterministic). M1: on pure windows, the monitor's m = 0 decision is "pure" on >= 90 % of windows with
t < 0.4 mu and <= 10 % of windows with t > 0.6 mu, in every model.

  python scripts/certification_margin.py --dump-dir DIR [--out FILE]
"""
import argparse
import json
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent))
from learner_kind_classifier import classify, family  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = []
    for f in sorted(Path(a.dump_dir).glob("*.npz")):
        rung, eps_tag, seed = f.stem.split("-")
        eps_tag = eps_tag[3:]
        z = np.load(f)
        Q, B, truth = z["Q"], z["B"], z["truth"]
        _, P, W, G = family(rung, eps_tag)
        nonpure = np.isin(G, ("withheld", "none"))
        sel = truth == "pure"
        Bp, Qp = B[sel], Q[sel]
        d_np = 0.5 * np.abs(Bp[:, None, :] - P[None, nonpure, :]).sum(-1)
        mu = d_np.min(1)
        t = 0.5 * np.abs(Bp - Qp).sum(1)
        pred = classify(Qp, P, W, G, 0.0)
        is_pure = pred == "pure"
        lo, hi = t < 0.4 * mu, t > 0.6 * mu
        line = dict(rung=rung, eps=eps_tag.replace("_", "/"), seed=int(seed[1:]), n_pure=int(sel.sum()),
                    mu_q10=float(np.quantile(mu, 0.1)), mu_median=float(np.median(mu)), mu_q90=float(np.quantile(mu, 0.9)),
                    t_median=float(np.median(t)),
                    n_lo=int(lo.sum()), pure_rate_lo=float(is_pure[lo].mean()) if lo.any() else None,
                    n_hi=int(hi.sum()), pure_rate_hi=float(is_pure[hi].mean()) if hi.any() else None,
                    n_mid=int((~lo & ~hi).sum()), pure_rate_mid=float(is_pure[~lo & ~hi].mean()) if (~lo & ~hi).any() else None)
        line["M1"] = (line["pure_rate_lo"] is not None and line["pure_rate_lo"] >= 0.9 and
                      line["pure_rate_hi"] is not None and line["pure_rate_hi"] <= 0.1)
        out.append(line)
        print(json.dumps(line), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/certification-margin-declared-2026-10-22.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
