"""Declared: docs/error-direction-declared-2026-10-26.md (stamped before computing).

For pure-truth windows: cosine of the model's error (q - P_c) with the direction to the nearest withheld law (u_W) and
to the nearest other pure law (u_P), at one and two steps; per-model mean and median.

  python scripts/error_direction.py --rows ROWS --dir DIR [--dir DIR] [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import family  # noqa: E402


def nearest_idx(A, B, budget=2e8):
    chunk = max(1, int(budget / max(1, B.shape[0] * B.shape[1])))
    out = np.empty(len(A), dtype=int)
    for i in range(0, len(A), chunk):
        out[i:i + chunk] = (0.5 * np.abs(A[i:i + chunk, None, :] - B[None, :, :]).sum(-1)).argmin(1)
    return out


def cos(a, b):
    na, nb = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1)
    ok = (na > 0) & (nb > 0)
    c = np.full(len(a), np.nan)
    c[ok] = (a[ok] * b[ok]).sum(1) / (na[ok] * nb[ok])
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--dir", action="append", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    fams, out = {}, []
    for d in a.dir:
        for f in sorted(Path(d).glob("*-test.npz")):
            stem = f.name[:-len("-test.npz")]
            rung = "r1" if "-r1-" in stem else "r3"; eps = "1_2" if "eps1_2" in stem else "1"
            z = np.load(f); kinds = [str(k) for k in z["kinds"]]
            if (rung, eps) not in fams:
                fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
            tm, (k1, P1, _, G1), (k2, P2, _, G2) = fams[(rung, eps)]
            keys = [str(k) for k in z["keys"]]
            pure = np.array([tm[k][0] == "pure" for k in keys])
            res: dict = dict(run=stem, rung=rung, eps=eps.replace("_", "/"), n_pure=int(pure.sum()))
            for s, ks, P, G, slot, qk in (("one", k1, P1, G1, 1, "q1"), ("two", k2, P2, G2, 2, "q2")):
                ix = {k: i for i, k in enumerate(ks)}
                T = np.array([P[ix[tm[k][slot]]] for k, p in zip(keys, pure) if p])
                Q = z[qk][pure]
                Pw, Pp = P[G == "withheld"], P[G == "pure"]
                uW = Pw[nearest_idx(T, Pw)] - T
                # nearest OTHER pure law: mask exact self-match by adding a large distance
                d = np.stack([(0.5 * np.abs(T[i] - Pp).sum(1)) for i in range(len(T))])
                d[d < 1e-12] = np.inf
                uP = Pp[d.argmin(1)] - T
                err = Q - T
                cW, cP = cos(err, uW), cos(err, uP)
                res[s] = dict(cosW_mean=float(np.nanmean(cW)), cosW_median=float(np.nanmedian(cW)),
                              cosP_mean=float(np.nanmean(cP)), cosP_median=float(np.nanmedian(cP)))
            out.append(res)
            print("%-36s two: cosW %.3f cosP %.3f | one: cosW %.3f cosP %.3f" % (stem[-36:], res["two"]["cosW_mean"], res["two"]["cosP_mean"],
                                                                              res["one"]["cosW_mean"], res["one"]["cosP_mean"]), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/error-direction-declared-2026-10-26.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
