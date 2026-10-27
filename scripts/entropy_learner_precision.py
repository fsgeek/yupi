"""Declared: docs/entropy-learner-precision-declared-2026-10-27.md (stamped b27de93 before running).

Entropy observers on learner outputs against the same observers on the true laws: one-step entropy (S1), joint
two-step entropy (S2), and the per-step profile difference (S3), AUC for withheld vs pure on test windows.

  python scripts/entropy_learner_precision.py --dirs DIR [DIR ...] --rows ROWS_DIR [--out FILE]
"""
import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from entropy_only_observer import auc  # noqa: E402
from learner_two_step_score import family  # noqa: E402


def H(P):
    P = np.clip(P, 0, None)
    return -(np.where(P > 0, P * np.log2(np.where(P > 0, P, 1)), 0)).sum(-1)


def scores(q1, q2, n):
    m = q2.reshape(-1, n, n).sum(2)
    hm, h2 = H(m), H(q2)
    return H(q1), h2, hm - (h2 - hm)


def vec(key, kix, n, two):
    v = np.zeros(n * n if two else n)
    for kk, p in key:
        if two:
            a, b = kk.split("|"); v[kix[a] * n + kix[b]] = float(Fraction(p))
        else:
            v[kix[kk]] = float(Fraction(p))
    return v


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
            kinds = [str(k) for k in z["kinds"]]; n = len(kinds); kix = {k: i for i, k in enumerate(kinds)}
            rung = "r1" if "-r1-" in stem else "r3"; eps = "1_2" if "eps1_2" in stem else "1"
            if (rung, eps) not in fams:
                fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)[0]
            tm = fams[(rung, eps)]
            keys = [str(k) for k in z["keys"]]
            lab = np.array([tm[k][0] for k in keys])
            sel = (lab == "pure") | (lab == "withheld")
            pos = lab[sel] == "withheld"
            T1 = np.array([vec(tm[k][1], kix, n, False) for k, s in zip(keys, sel) if s])
            T2 = np.array([vec(tm[k][2], kix, n, True) for k, s in zip(keys, sel) if s])
            learned = scores(z["q1"][sel], z["q2"][sel], n)
            exact = scores(T1, T2, n)
            w = np.ones(len(pos))
            res = dict(run=stem, src=Path(d).name, n_pure=int((~pos).sum()), n_withheld=int(pos.sum()))
            for name, s_l, s_e in zip(("S1", "S2", "S3"), learned, exact):
                res[name] = auc(s_l, pos, w); res[name + "*"] = auc(s_e, pos, w)
            out.append(res)
            print("%-52s S1 %.3f (%.3f) S2 %.3f (%.3f) S3 %.3f (%.3f)" % (
                stem[-52:], res["S1"], res["S1*"], res["S2"], res["S2*"], res["S3"], res["S3*"]), flush=True)
    N = len(out)
    verdict = dict(n=N,
                   L1=int(sum(abs(r["S1"] - r["S1*"]) <= 0.03 for r in out)),
                   L2=int(sum(r["S3"] > r["S1"] for r in out)),
                   L3=int(sum(r["S1"] - r["S2"] >= 0.15 for r in out)),
                   need=int(np.ceil(0.9 * N)))
    print(verdict)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/entropy-learner-precision-declared-2026-10-27.md",
                                               rows=out, verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
