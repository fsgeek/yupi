"""Declared: docs/prospective-certification-declared-2026-10-25.md (stamped before computing).

L = q * (pure mass with mu_c > 2B) / (pure mass), from the exact k = 6 tables (RESET masses halved) and the val bound
B, compared with the observed certified pure share from the certified-bound runs.

  python scripts/prospective_certification.py --rows ROWS_DIR --obs OBS_JSON [--obs OBS_JSON ...] [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import min_tv  # noqa: E402
from fractions import Fraction

KIND_LIST = ["DISPATCH", "STEP", "ACQUIRE", "BLOCK", "RELEASE", "IO_ISSUE", "IO_COMPLETE", "IDLE"]


def tables(path, kinds):
    kix = {k: i for i, k in enumerate(kinds)}; n = len(kinds)
    pure1, pure2, pm, wh1, wh2 = [], [], [], {}, {}
    for line in open(path):
        r = json.loads(line)
        m = r["mass"] * (0.5 if r["key"].startswith("(True,") else 1.0)
        v1 = np.zeros(n); v2 = np.zeros(n * n)
        for k, p in r["p_star"]:
            v1[kix[k]] = float(Fraction(p))
        for kk, p in r["p2"]:
            a, b = kk.split("|"); v2[kix[a] * n + kix[b]] = float(Fraction(p))
        if r["h_star"] > 1e-12 and abs(r["g"]) < 1e-12:
            pure1.append(v1); pure2.append(v2); pm.append(m)
        elif r["g"] >= 0.1:
            wh1[tuple(v1)] = v1; wh2[tuple(v2)] = v2
    return np.array(pure1), np.array(pure2), np.array(pm), np.array(list(wh1.values())), np.array(list(wh2.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--obs", action="append", required=True)
    ap.add_argument("--kinds-from", required=True, help="any dump npz, for the KIND order")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    kinds = [str(k) for k in np.load(a.kinds_from)["kinds"]]
    cache, out = {}, []
    for f in a.obs:
        for r in json.loads(Path(f).read_text())["rows"]:
            rung = r.get("rung") or ("r1" if "-r1-" in r["run"] else "r3")
            eps = (r.get("eps") or ("1/2" if "eps1_2" in r["run"] else "1")).replace("/", "_")
            if (rung, eps) not in cache:
                p1, p2, pm, w1, w2 = tables(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
                cache[(rung, eps)] = (pm, min_tv(p1, w1), min_tv(p2, w2))
            pm, mu1, mu2 = cache[(rung, eps)]
            for s, mu in (("one", mu1), ("two", mu2)):
                B = r[f"{s}|q0.95"]["B"]
                L = 0.95 * pm[mu > 2 * B].sum() / pm.sum()
                obs = r[f"{s}|q0.95"]["certified_pure_share"]
                out.append(dict(run=r["run"], rung=rung, eps=eps, step=s, B=B, L=float(L), observed=obs))
    L = np.array([o["L"] for o in out]); O = np.array([o["observed"] for o in out])
    ra, rb = np.argsort(np.argsort(L)), np.argsort(np.argsort(O))
    summ = dict(n=len(out), P1_pairs_ok=int(np.sum(O >= L - 0.03)), spearman=float(np.corrcoef(ra, rb)[0, 1]),
                median_gap=float(np.median(O - L)), min_gap=float(np.min(O - L)))
    print(json.dumps(summ))
    for o in sorted(out, key=lambda o: o["L"] - o["observed"])[-5:]:
        print("worst:", o["run"][-30:], o["step"], "L %.3f obs %.3f" % (o["L"], o["observed"]))
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/prospective-certification-declared-2026-10-25.md", summary=summ, rows=out), indent=1))


if __name__ == "__main__":
    main()
