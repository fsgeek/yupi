"""Declared: docs/prior-aware-monitor-declared-2026-10-23.md (stamped before any run).

Prior-aware kind monitor. L(q | g) ∝ exp(-TV(q, P_g) / tau), with tau = the model's mean TV(true law, output) on its
val split. pi_pure = sum over pure groups of W_g L / sum over pure and withheld (G >= 0.1) groups. Predict pure if
pi_pure >= 0.9, withheld if <= 0.1, else abstain. Scored on test. Also reports tau x {0.5, 2}.

  python scripts/prior_aware_monitor.py --dump-dir DIR [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_kind_classifier import family, score  # noqa: E402


def log_mass(Q, P, logW, tau):
    out = np.empty(len(Q))
    for i in range(0, len(Q), 1024):
        d = 0.5 * np.abs(Q[i:i + 1024, None, :] - P[None, :, :]).sum(-1)
        a = logW[None, :] - d / tau
        mx = a.max(1)
        out[i:i + 1024] = mx + np.log(np.exp(a - mx[:, None]).sum(1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    D = Path(a.dump_dir)
    rows = []
    for f in sorted(p for p in D.glob("*.npz") if not p.stem.endswith("-val")):
        rung, et, seed = f.stem.split("-")
        et = et[3:]
        v = np.load(D / f"{f.stem}-val.npz")
        tau = float((0.5 * np.abs(v["B"] - v["Q"]).sum(1)).mean())
        z = np.load(f)
        Q, truth = z["Q"], z["truth"]
        _, P, W, G = family(rung, et)
        Pp, Wp, Pw, Ww = P[G == "pure"], W[G == "pure"], P[G == "withheld"], W[G == "withheld"]
        line: dict = dict(rung=rung, eps=et.replace("_", "/"), seed=int(seed[1:]), tau_val=tau)
        for k in (0.5, 1.0, 2.0):
            lp = log_mass(Q, Pp, np.log(Wp), tau * k)
            lw = log_mass(Q, Pw, np.log(Ww), tau * k)
            pi = 1.0 / (1.0 + np.exp(lw - lp))
            pred = np.where(pi >= 0.9, "pure", np.where(pi <= 0.1, "withheld", "abstain"))
            line[f"tau_x{k}"] = score(pred, truth)
        h = line["tau_x1.0"]
        print(json.dumps(dict(rung=rung, eps=line["eps"], seed=line["seed"], tau=round(tau, 4),
                              cov=round(h["coverage"], 3), bal=round(h["balanced_accuracy_covered"], 3),
                              cons=round(h["balanced_accuracy_conservative"], 3),
                              rp=round(h["recall_pure_covered"], 3), rw=round(h["recall_withheld_covered"], 3))), flush=True)
        rows.append(line)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/prior-aware-monitor-declared-2026-10-23.md", rows=rows), indent=1))


if __name__ == "__main__":
    main()
