"""Declared: docs/partial-support-declared-2026-10-27.md (stamped bfb76dd before running).

The two-step full-distribution score M2 = d_pure − d_withheld, computed against only a subset of the law groups (the
f most massive, or a uniform-random f), against the entropy profile S3, on the same learners and windows.

  python scripts/partial_support.py --dirs DIR [DIR ...] --rows ROWS_DIR [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from entropy_learner_precision import scores  # noqa: E402
from entropy_only_observer import auc  # noqa: E402
from learner_two_step_score import family  # noqa: E402

FS = (1.0, 0.5, 0.25, 0.1, 0.05, 0.01)
SEED = 20261027  # declared; --seed overrides for the post hoc robustness check


def dist(Q, P, chunk=64):
    D = np.empty((len(Q), len(P)), np.float32)
    for i in range(0, len(Q), chunk):
        D[i:i + chunk] = 0.5 * np.abs(Q[i:i + chunk, None, :] - P[None]).sum(-1)
    return D


def subset(W, G, f, mode, rng):
    k = max(1, int(round(f * len(W))))
    idx = np.argsort(-W, kind="stable")[:k] if mode == "mass" else rng.permutation(len(W))[:k]
    keep = np.zeros(len(W), bool); keep[idx] = True
    for lab in ("pure", "withheld"):  # at least one of each label
        if not (keep & (G == lab)).any():
            cand = np.where(G == lab)[0]
            keep[cand[np.argmax(W[cand])] if mode == "mass" else rng.choice(cand)] = True
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    fams, subsets, out = {}, {}, []
    for d in a.dirs:
        for ft in sorted(Path(d).glob("*-test.npz")):
            stem = ft.name[:-len("-test.npz")]
            z = np.load(ft)
            kinds = [str(k) for k in z["kinds"]]; n = len(kinds)
            rung = "r1" if "-r1-" in stem else "r3"; eps = "1_2" if "eps1_2" in stem else "1"
            if (rung, eps) not in fams:
                fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
                _, _, (_, P2, W2, G2) = fams[(rung, eps)]
                rng = np.random.default_rng(a.seed)
                subsets[(rung, eps)] = {(m, f): subset(W2, G2, f, m, rng) for m in ("mass", "random") for f in FS}
            tm, _, (_, P2, W2, G2) = fams[(rung, eps)]
            lab = np.array([tm[str(k)][0] for k in z["keys"]])
            sel = (lab == "pure") | (lab == "withheld"); pos = lab[sel] == "withheld"
            q1, q2 = z["q1"][sel], z["q2"][sel]
            D = dist(q2.astype(np.float32), P2.astype(np.float32))
            w = np.ones(len(pos))
            r = dict(run=stem, S3=auc(scores(q1, q2, n)[2], pos, w))
            for (m, f), keep in subsets[(rung, eps)].items():
                M = D[:, keep & (G2 == "pure")].min(1) - D[:, keep & (G2 == "withheld")].min(1)
                r[f"{m}|{f}"] = auc(M.astype(float), pos, w)
                r[f"{m}|{f}|mass_share"] = float(W2[keep].sum() / W2.sum())
            out.append(r)
            print("%-44s S3 %.3f | mass %s | random %s" % (stem[-44:], r["S3"],
                  " ".join("%.3f" % r[f"mass|{f}"] for f in FS), " ".join("%.3f" % r[f"random|{f}"] for f in FS)),
                  flush=True)
            del D
    med = {f"{m}|{f}": float(np.median([r[f"{m}|{f}"] for r in out])) for m in ("mass", "random") for f in FS}
    medS3 = float(np.median([r["S3"] for r in out]))
    cross = {m: min([f for f in FS if med[f"{m}|{f}"] > medS3], default=None) for m in ("mass", "random")}
    verdict = dict(n=len(out), P1=int(sum(r["mass|0.1"] >= r["S3"] for r in out)),
                   P2=int(sum(r["random|0.1"] < r["S3"] for r in out)), median=med, median_S3=medS3, crossover=cross,
                   mass_share={k: float(np.median([r[k + "|mass_share"] for r in out])) for k in med})
    print(json.dumps(verdict, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/partial-support-declared-2026-10-27.md", rows=out,
                                               verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
