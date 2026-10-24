"""Declared: docs/observer-space-declared-2026-10-24.md (stamped before computing).

32 observers per model (prior temper beta x query x noise scale c) on the k = 6 test dumps; conservative balanced
accuracy; observer range vs learner range per cell; O1-O4.

  python scripts/observer_space.py --dir DIR --rows ROWS_DIR --scores SCORE_JSON [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import family, log_mass, score  # noqa: E402

BETAS = (0.0, 0.5, 1.0, 2.0)
CS = (0.25, 0.5, 1.0, 2.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    taus = {r["run"]: (r["tau1"], r["tau2"]) for r in json.loads(Path(a.scores).read_text())["rows"]}
    fams, res = {}, []
    for f in sorted(Path(a.dir).glob("*-test.npz")):
        stem = f.name[:-len("-test.npz")]
        rung = "r1" if "-r1-" in stem else "r3"; eps = "1_2" if "eps1_2" in stem else "1"
        z = np.load(f); kinds = [str(k) for k in z["kinds"]]
        if (rung, eps) not in fams:
            fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
        tm, (_, P1, W1, G1), (_, P2, W2, G2) = fams[(rung, eps)]
        lab = np.array([tm[str(k)][0] for k in z["keys"]])
        grid = {}
        for q, Q, P, W, G, tau in (("one", z["q1"], P1, W1, G1, taus[stem][0]), ("two", z["q2"], P2, W2, G2, taus[stem][1])):
            Pp, Pw, Wp, Ww = P[G == "pure"], P[G == "withheld"], W[G == "pure"], W[G == "withheld"]
            for c in CS:
                for b in BETAS:
                    lp = log_mass(Q, Pp, b * np.log(Wp), tau * c)
                    lw = log_mass(Q, Pw, b * np.log(Ww), tau * c)
                    pi = 1 / (1 + np.exp(np.clip(lw - lp, -700, 700)))
                    pred = np.where(pi >= 0.9, "pure", np.where(pi <= 0.1, "withheld", "abstain"))
                    grid[f"{q}|c{c}|b{b}"] = score(pred, lab)["balanced_conservative"]
        res.append(dict(run=stem, rung=rung, eps=eps.replace("_", "/"), grid=grid))
        print(stem[-30:], "best", max(grid, key=grid.get), "%.3f" % max(grid.values()), "worst", min(grid, key=grid.get),
              "%.3f" % min(grid.values()), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/observer-space-declared-2026-10-24.md", rows=res), indent=1))


if __name__ == "__main__":
    main()
