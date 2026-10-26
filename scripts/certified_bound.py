"""Declared: docs/certified-bound-declared-2026-10-25.md (stamped before running).

Prior-free worst-case certifier with an error bound B fitted on val (q-quantile of TV(true law, output)), one and two
steps; scored on the fresh paired test windows of the challenge run.

  python scripts/certified_bound.py --dir DIR --fresh FRESH_DIR --rows ROWS_DIR [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import family, min_tv  # noqa: E402

QS = (0.90, 0.95, 0.99)


def main():
    ap = argparse.ArgumentParser()
    for k in ("--dir", "--fresh", "--rows"):
        ap.add_argument(k, required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    fam, out = None, []
    for fv in sorted(Path(a.dir).glob("*-val.npz")):
        stem = fv.name[:-len("-val.npz")]
        v, old, z = np.load(fv), np.load(Path(a.dir) / f"{stem}-test.npz"), np.load(Path(a.fresh) / f"{stem}-test.npz")
        kinds = [str(k) for k in v["kinds"]]
        if fam is None:
            fam = family(Path(a.rows) / "c1prime-loop-40-8-2-r1-eps1-k6.jsonl", kinds)
        tm, (k1, P1, _, G1), (k2, P2, _, G2) = fam
        i1 = {k: i for i, k in enumerate(k1)}; i2 = {k: i for i, k in enumerate(k2)}
        keep = ~np.isin(z["idx"], old["idx"])
        res: dict = dict(run=stem, n=int(keep.sum()))
        for s, Pk, G, ix, qk, slot in (("one", P1, G1, i1, "q1", 1), ("two", P2, G2, i2, "q2", 2)):
            Tv = np.array([Pk[ix[tm[str(k)][slot]]] for k in v["keys"]])
            ev = 0.5 * np.abs(Tv - v[qk]).sum(1)
            keys = [str(k) for k in z["keys"]]
            Tt = np.array([Pk[ix[tm[k][slot]]] for k in keys])[keep]
            lab = np.array([tm[k][0] for k in keys])[keep]
            Q = z[qk][keep]
            et = 0.5 * np.abs(Tt - Q).sum(1)
            dp, dw = min_tv(Q, Pk[G == "pure"]), min_tv(Q, Pk[G == "withheld"])
            for q in QS:
                B = float(np.quantile(ev, q))
                cp = (dp <= B) & (dw > B); cw = (dw <= B) & (dp > B)
                pure, wh = lab == "pure", lab == "withheld"
                n_cert = int(((cp | cw) & (pure | wh)).sum())
                wrong = int((cp & wh).sum() + (cw & pure).sum())
                res[f"{s}|q{q}"] = dict(B=B, certified_pure_share=float(cp[pure].mean()), certified_withheld_share=float(cw[wh].mean()),
                                        false_certificate_rate=wrong / n_cert if n_cert else None,
                                        test_share_error_gt_B=float(np.mean(et[pure | wh] > B)))
        out.append(res)
        r1, r2 = res["one|q0.95"], res["two|q0.95"]
        print("%-28s q.95 | one: B %.3f pure %.3f wh %.3f false %.4f >B %.3f | two: B %.3f pure %.3f wh %.3f false %.4f >B %.3f" % (
            stem.split("eps1-2M-")[1][:28], r1["B"], r1["certified_pure_share"], r1["certified_withheld_share"], r1["false_certificate_rate"] or 0,
            r1["test_share_error_gt_B"], r2["B"], r2["certified_pure_share"], r2["certified_withheld_share"], r2["false_certificate_rate"] or 0,
            r2["test_share_error_gt_B"]), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/certified-bound-declared-2026-10-25.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
