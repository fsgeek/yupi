"""Declared: docs/entropy-only-observer-declared-2026-10-27.md (stamped 815e138 before running).

Exact ceilings for an observer that sees only the entropy of the next-KIND law, against one that sees the law:
mass-weighted AUC of entropy (withheld vs pure), and Bayes-optimal balanced accuracy from entropy or from the law,
at one and two steps.

  python scripts/entropy_only_observer.py --rows ROWS_DIR [--out FILE]
"""
import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np


def entropy(law):
    return -sum(p * math.log2(p) for p in law if p > 0)


def auc(score, pos, w):
    """Mass-weighted AUC of score for pos against ~pos; ties count one half."""
    o = np.argsort(score, kind="stable")
    s, y, w = score[o], pos[o], w[o]
    wn_below, num, i = 0.0, 0.0, 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        wp, wn = w[i:j][y[i:j]].sum(), w[i:j][~y[i:j]].sum()
        num += wp * (wn_below + 0.5 * wn)
        wn_below += wn; i = j
    return num / (w[pos].sum() * w[~pos].sum())


def bayes_ba(groups, pos, w):
    """Balanced accuracy of assigning each group to the label with larger label-normalised mass."""
    wp, wn = w[pos].sum(), w[~pos].sum()
    acc = {}
    for g, y, m in zip(groups, pos, w):
        a = acc.setdefault(g, [0.0, 0.0]); a[0 if y else 1] += m
    return 0.5 * sum(max(a[0] / wp, a[1] / wn) for a in acc.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = []
    for f in sorted(Path(a.rows).glob("c1prime-loop-40-8-2-*-k6.jsonl")):
        w, pos, h1, h2, l1, l2 = [], [], [], [], [], []
        for line in open(f):
            r = json.loads(line)
            if r["h_star"] <= 1e-12 or 1e-12 <= abs(r["g"]) < 0.1:
                continue
            w.append(r["mass"] * (0.5 if r["key"].startswith("(True,") else 1.0))
            pos.append(r["g"] >= 0.1)
            p1 = tuple(sorted(map(tuple, r["p_star"]))); p2 = tuple(sorted(map(tuple, r["p2"])))
            l1.append(p1); l2.append(p2)
            h1.append(entropy([float(Fraction(v)) for _, v in p1]))
            h2.append(entropy([float(Fraction(v)) for _, v in p2]))
        w, pos, h1, h2 = map(np.array, (w, pos, h1, h2))
        res = dict(cell=f.stem.replace("c1prime-loop-40-8-2-", ""), n_pure=int((~pos).sum()), n_withheld=int(pos.sum()),
                   withheld_mass_share=float(w[pos].sum() / w.sum()))
        for d, h, laws in (("one", h1, l1), ("two", h2, l2)):
            res[d] = dict(AUC_H=auc(h, pos, w), BA_H=bayes_ba([round(x, 9) for x in h], pos, w),
                          BA_P=bayes_ba(laws, pos, w))
        out.append(res)
        o, t = res["one"], res["two"]
        print("%-12s pure %5d wh %5d | one: AUC_H %.3f BA_H %.3f BA_P %.3f | two: AUC_H %.3f BA_H %.3f BA_P %.3f" % (
            res["cell"], res["n_pure"], res["n_withheld"], o["AUC_H"], o["BA_H"], o["BA_P"], t["AUC_H"], t["BA_H"],
            t["BA_P"]), flush=True)
    one = [r["one"] for r in out]; two = [r["two"] for r in out]
    verdict = dict(
        E1=int(sum(o["AUC_H"] > 0.5 for o in one)), E2_median_AUC_H=float(np.median([o["AUC_H"] for o in one])),
        E3=int(sum(o["BA_P"] - o["BA_H"] >= 0.10 for o in one)),
        E4=int(sum((t["BA_P"] - o["BA_P"]) > (t["BA_H"] - o["BA_H"]) for o, t in zip(one, two))))
    print(verdict)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/entropy-only-observer-declared-2026-10-27.md",
                                               rows=out, verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
