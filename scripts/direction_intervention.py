"""Declared: docs/direction-intervention-declared-2026-10-26.md; --null family per docs/direction-null-declared-2026-10-26.md.

For pure-truth test windows: certify the real output, an adversarial output (toward the nearest withheld law) and a
random-direction output (toward a Dirichlet(1) law), all at the model's real per-window TV error, with the same
val-fitted bound B (q = 0.95) and prior-free certifier as certified_bound.py.

  python scripts/direction_intervention.py --rows ROWS --dir DIR [--dir DIR] [--fresh-for-ladder FRESH] [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import family, min_tv  # noqa: E402
from error_direction import nearest_idx  # noqa: E402

Q = 0.95


def towards(T, D, e):
    dist = 0.5 * np.abs(D - T).sum(1)
    alpha = np.minimum(1.0, np.where(dist > 0, e / np.maximum(dist, 1e-300), 0.0))
    return T + alpha[:, None] * (D - T)


def certified_pure(Qo, P, G, B):
    dp, dw = min_tv(Qo, P[G == "pure"]), min_tv(Qo, P[G == "withheld"])
    return (dp <= B) & (dw > B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--dir", action="append", required=True)
    ap.add_argument("--fresh-for-ladder", default=None)
    ap.add_argument("--null", default="dirichlet", choices=("dirichlet", "family"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rng = np.random.default_rng(20261026 if a.null == "dirichlet" else 20261027)
    fams, out = {}, []
    for d in a.dir:
        for fv in sorted(Path(d).glob("*-val.npz")):
            stem = fv.name[:-len("-val.npz")]
            rung = "r1" if "-r1-" in stem else "r3"; eps = "1_2" if "eps1_2" in stem else "1"
            v = np.load(fv)
            if a.fresh_for_ladder and (Path(a.fresh_for_ladder) / f"{stem}-test.npz").exists() and "learner-quality" in d:
                z = np.load(Path(a.fresh_for_ladder) / f"{stem}-test.npz"); old = np.load(Path(d) / f"{stem}-test.npz")
                keep = ~np.isin(z["idx"], old["idx"])
            else:
                z = np.load(Path(d) / f"{stem}-test.npz"); keep = np.ones(len(z["idx"]), bool)
            kinds = [str(k) for k in v["kinds"]]
            if (rung, eps) not in fams:
                fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
            tm, (k1, P1, W1, G1), (k2, P2, W2, G2) = fams[(rung, eps)]
            res: dict = dict(run=stem, rung=rung, eps=eps.replace("_", "/"))
            for s, ks, P, W, G, slot, qk in (("one", k1, P1, W1, G1, 1, "q1"), ("two", k2, P2, W2, G2, 2, "q2")):
                ix = {k: i for i, k in enumerate(ks)}
                Tv = np.array([P[ix[tm[str(k)][slot]]] for k in v["keys"]])
                B = float(np.quantile(0.5 * np.abs(Tv - v[qk]).sum(1), Q))
                keys = [str(k) for k in z["keys"]]
                lab = np.array([tm[k][0] for k in keys])
                sel = keep & (lab == "pure")
                T = np.array([P[ix[tm[k][slot]]] for k, f in zip(keys, sel) if f])
                Qr = z[qk][sel]
                e = 0.5 * np.abs(T - Qr).sum(1)
                Pw = P[G == "withheld"]
                Qa = towards(T, Pw[nearest_idx(T, Pw)], e)
                if a.null == "dirichlet":
                    R = rng.dirichlet(np.ones(P.shape[1]), size=len(T))
                else:
                    R = P[rng.choice(len(P), size=len(T), p=W / W.sum())]
                Qn = towards(T, R, e)
                res[s] = dict(B=B, n=int(sel.sum()), real=float(certified_pure(Qr, P, G, B).mean()),
                              adversarial=float(certified_pure(Qa, P, G, B).mean()), random=float(certified_pure(Qn, P, G, B).mean()))
            out.append(res)
            t = res["two"]
            print("%-34s two: real %.3f adv %.3f rand %.3f | one: real %.3f adv %.3f rand %.3f" % (
                stem[-34:], t["real"], t["adversarial"], t["random"], res["one"]["real"], res["one"]["adversarial"], res["one"]["random"]), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/direction-intervention-declared-2026-10-26.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
