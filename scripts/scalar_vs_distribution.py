"""Declared: docs/scalar-vs-distribution-declared-2026-10-27.md (stamped 68d6a38 before running).

AUC of the full-distribution score M = d_pure − d_withheld (nearest-law TV) against the entropy scores S1 and S3, on
the same learners and test windows as scripts/entropy_learner_precision.py.

  python scripts/scalar_vs_distribution.py --dirs DIR [DIR ...] --rows ROWS_DIR [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from entropy_learner_precision import scores  # noqa: E402
from entropy_only_observer import auc  # noqa: E402
from learner_two_step_score import family, min_tv  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    fams, out = {}, []
    for d in a.dirs:
        for ft in sorted(Path(d).glob("*-test.npz")):
            stem = ft.name[:-len("-test.npz")]
            z = np.load(ft)
            kinds = [str(k) for k in z["kinds"]]; n = len(kinds)
            rung = "r1" if "-r1-" in stem else "r3"; eps = "1_2" if "eps1_2" in stem else "1"
            if (rung, eps) not in fams:
                fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
            tm, (_, P1, _, G1), (_, P2, _, G2) = fams[(rung, eps)]
            lab = np.array([tm[str(k)][0] for k in z["keys"]])
            sel = (lab == "pure") | (lab == "withheld"); pos = lab[sel] == "withheld"
            q1, q2 = z["q1"][sel], z["q2"][sel]
            M1 = min_tv(q1, P1[G1 == "pure"], 64) - min_tv(q1, P1[G1 == "withheld"], 64)
            M2 = min_tv(q2, P2[G2 == "pure"], 64) - min_tv(q2, P2[G2 == "withheld"], 64)
            S1, _, S3 = scores(q1, q2, n)
            w = np.ones(len(pos))
            r = dict(run=stem, M1=auc(M1, pos, w), M2=auc(M2, pos, w), S1=auc(S1, pos, w), S3=auc(S3, pos, w))
            out.append(r)
            print("%-52s M1 %.3f S1 %.3f | M2 %.3f S3 %.3f" % (stem[-52:], r["M1"], r["S1"], r["M2"], r["S3"]), flush=True)
    verdict = dict(n=len(out), C1=int(sum(r["M1"] >= r["S1"] for r in out)), C2=int(sum(r["M2"] >= r["S3"] for r in out)),
                   median_M2_minus_S3=float(np.median([r["M2"] - r["S3"] for r in out])),
                   median_M1_minus_S1=float(np.median([r["M1"] - r["S1"] for r in out])))
    print(verdict)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/scalar-vs-distribution-declared-2026-10-27.md", rows=out,
                                               verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
