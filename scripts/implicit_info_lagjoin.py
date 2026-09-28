"""EXPLORATORY per-class test of paper-1 decision D1 at long lag (readiness item 3):
does a learner's KIND excess on a prefix class track the exact information about
the next KIND that lies MORE than m records back (ι_kind,m, m = 4), controlling
the short-range part (ι_kind,1 − ι_kind,4) and the class's exact KIND entropy?

Per census run: windows are grouped by prefix class (the class key recomputed from
the corpus and checked against the census ids, as in implicit_info_join.py); class
means of the realized KIND excess (an unbiased estimate of the class's KIND KL) are
regressed by weighted least squares (weight = windows in the class) on
[1, long, short, H_kind] over classes with at least --min-n windows. Every
regressor is a function of the prefix only.

    uv run python scripts/implicit_info_lagjoin.py --raw docs/implicit-info-lagjoin-k7-2026-09-28.json
"""
import argparse
import glob
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from math import log2
from pathlib import Path

import numpy as np

from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.evaluate import surface_records
from yupi.naming import pattern_all
from yupi.pattern_ceiling import load_table, serial_key

CACHE = Path.home() / ".cache/yupi-scratch/implicit"
TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
MIN_N = 30
LONG = 4


def _rank(x):
    xs = np.asarray(x)
    order = np.argsort(xs, kind="mergesort")
    r = np.empty(len(xs)); r[order] = np.arange(len(xs))
    _, inv, cnt = np.unique(xs, return_inverse=True, return_counts=True)
    return (np.bincount(inv, weights=r) / cnt)[inv]


def spearman(a, b):
    return float(np.corrcoef(_rank(a), _rank(b))[0, 1])


def wls(y, w, *xs):
    X = np.column_stack([np.ones(len(y)), *xs])
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    resid = (y - X @ beta) * sw
    cov = np.linalg.inv((X * sw[:, None]).T @ (X * sw[:, None])) * (resid @ resid) / (len(y) - X.shape[1])
    return [float(b) for b in beta], [float(s) for s in np.sqrt(np.diag(cov))]


def run_one(args):
    census_raw, min_n = args
    c = json.load(open(census_raw))
    k, rung, eps = c["k"], c["rung"], c["eps"]
    tag = f"{rung}-eps{eps.replace('/', '_')}"
    rows = [json.loads(l) for l in open(c["per_window_file"])]
    split = read_split(Path(c["corpus"]), c["split"])
    iota = {}
    for line in open(CACHE / f"c1prime-loop-40-8-2-{tag}-k{k}-kind-m123456.jsonl"):
        d = json.loads(line)
        iota[d["k"]] = d
    hk = {}
    for key, (_, star) in load_table(TABLES / f"c1prime-loop-40-8-2-{tag}-k{k}.jsonl").items():
        kd = {}
        for r, p in star.items():
            kd[r.kind] = kd.get(r.kind, 0.0) + float(p)
        hk[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
    id_of, key_of, by = {}, {}, {}
    for r in rows:
        toks = tuple(VOCAB[t] for t in split[r["i"]][0])
        reset, recs = surface_records(toks)
        key = serial_key((reset, pattern_all(recs[:k])[0]))
        if id_of.setdefault(key, r["key"]) != r["key"] or key_of.setdefault(r["key"], key) != key:
            raise SystemExit(f"GATE: class id mismatch at window {r['i']} in {census_raw}")
        by.setdefault(key, []).append(r["by_field"]["kind"])
    keys = [kk for kk, v in by.items() if len(v) >= min_n]
    n = np.array([len(by[kk]) for kk in keys], float)
    y = np.array([np.mean(by[kk]) for kk in keys])
    long_ = np.array([iota[kk][f"iota_{LONG}"] for kk in keys])
    short = np.array([iota[kk]["iota_1"] - iota[kk][f"iota_{LONG}"] for kk in keys])
    h = np.array([hk[kk] for kk in keys])
    cover = float(n.sum() / len(rows))
    b, se = wls(y, n, long_, short, h)
    return {"census_raw": census_raw, "rung": rung, "eps": eps, "seed": c["seed"], "k": k,
            "n_windows": len(rows), "n_classes": len(keys), "window_coverage": cover,
            "mean_kind_excess_covered": float((y * n).sum() / n.sum()),
            "spearman_class_means": {"long": spearman(y, long_), "short": spearman(y, short), "H_kind": spearman(y, h)},
            "wls": {"terms": ["1", f"iota_kind_{LONG}", f"iota_kind_1-iota_kind_{LONG}", "H_kind"], "beta": b, "se": se}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--min-n", type=int, default=MIN_N)
    ap.add_argument("--glob", default="docs/learner-window-census-r[1-4]-eps*-seed*-2026-09-2*.json")
    a = ap.parse_args()
    raws = sorted(glob.glob(a.glob))
    with ProcessPoolExecutor(max_workers=len(raws)) as ex:
        res = list(ex.map(run_one, [(r, a.min_n) for r in raws]))
    for r in res:
        s, w = r["spearman_class_means"], r["wls"]
        t = [bb / ss for bb, ss in zip(w["beta"], w["se"])]
        print(f"{r['rung']} eps={r['eps']} s{r['seed']}: classes={r['n_classes']} cover={r['window_coverage']:.2f} "
              f"ρ(long)={s['long']:+.3f} ρ(short)={s['short']:+.3f} ρ(H)={s['H_kind']:+.3f} | "
              f"β_long={w['beta'][1]:+.4f} (t {t[1]:+.1f}) β_short={w['beta'][2]:+.4f} (t {t[2]:+.1f}) "
              f"β_H={w['beta'][3]:+.4f} (t {t[3]:+.1f})", flush=True)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    json.dump({"status": "EXPLORATORY (paper-1 readiness item 3, long lag)", "git": git + ("+dirty" if dirty else ""),
               "long_lag_m": LONG, "min_n": a.min_n, "runs": res}, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
