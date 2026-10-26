"""v3 of prospective_certification_v2.py: e drawn from pure-window val errors (L3). Field L2 in output holds L3.
Declared: docs/prospective-certification-v3-declared-2026-10-26.md (stamped before computing).

L2 = sum_c m_c P_val(e < min(B, mu_c - B)) / sum_c m_c over pure classes, with each learner's val error distribution
(TV to the true law, per step) and the q = 0.95 bound B from the certified-bound runs.

  python scripts/prospective_certification_v2.py --rows ROWS --prior PRIOR_JSON --val-dir DIR [--val-dir DIR] [--out F]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import family  # noqa: E402
from prospective_certification import tables  # noqa: E402
from learner_two_step_score import min_tv  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--prior", required=True, help="prospective-certification-2026-10-25.json (B and observed)")
    ap.add_argument("--val-dir", action="append", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    prior = json.loads(Path(a.prior).read_text())["rows"]
    vals = {}
    for d in a.val_dir:
        for f in Path(d).glob("*-val.npz"):
            vals[f.name[:-len("-val.npz")]] = f
    cache, fams, out = {}, {}, []
    for o in prior:
        stem = o["run"]; rung, eps = o["rung"], o["eps"]
        z = np.load(vals[stem]); kinds = [str(k) for k in z["kinds"]]
        if (rung, eps) not in cache:
            p1, p2, pm, w1, w2 = tables(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
            cache[(rung, eps)] = (pm, min_tv(p1, w1), min_tv(p2, w2))
            fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
        pm, mu1, mu2 = cache[(rung, eps)]
        tm, (k1, P1, _, _), (k2, P2, _, _) = fams[(rung, eps)]
        if o["step"] == "one":
            ix = {k: i for i, k in enumerate(k1)}; T = np.array([P1[ix[tm[str(k)][1]]] for k in z["keys"]]); Q = z["q1"]; mu = mu1
        else:
            ix = {k: i for i, k in enumerate(k2)}; T = np.array([P2[ix[tm[str(k)][2]]] for k in z["keys"]]); Q = z["q2"]; mu = mu2
        labs = np.array([tm[str(k)][0] for k in z["keys"]])
        e = np.sort((0.5 * np.abs(T - Q).sum(1))[labs == "pure"])   # v3: pure-window val errors only
        thr = np.minimum(o["B"], mu - o["B"])
        frac = np.searchsorted(e, thr, side="left") / len(e)
        frac[thr <= 0] = 0.0
        L2 = float((pm * frac).sum() / pm.sum())
        out.append(dict(o, L2=L2))  # field named L2 for reuse; it is L3 here
    res = {}
    for s in ("one", "two"):
        L = np.array([x["L"] for x in out if x["step"] == s]); L2 = np.array([x["L2"] for x in out if x["step"] == s])
        O = np.array([x["observed"] for x in out if x["step"] == s])
        sp = lambda a_, b_: float(np.corrcoef(np.argsort(np.argsort(a_)), np.argsort(np.argsort(b_)))[0, 1])
        res[s] = dict(floor_ok=int(np.sum(O >= L2 - 0.03)), median_gap_L2=float(np.median(O - L2)), median_gap_L=float(np.median(O - L)),
                      spearman_L2=sp(L2, O), spearman_L=sp(L, O), L2_range=[float(L2.min()), float(L2.max())])
    print(json.dumps(res, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/prospective-certification-v3-declared-2026-10-26.md", summary=res, rows=out), indent=1))


if __name__ == "__main__":
    main()
