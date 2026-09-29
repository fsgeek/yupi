"""EXPLORATORY per-window test of paper-1 decision D1 over ALL windows (the long-lag
tail included): does a learner's realized KIND excess rise with the exact
information about the next KIND lying more than m records back (ι_kind,m),
controlling the short-range part and the class's exact KIND entropy?

implicit_info_lagjoin.py regressed class means over classes with ≥ 30 windows,
which covered 5-9 % of windows and missed the rare long-memory classes
(docs/implicit-information-first-results-v0.1.md §2). Here every scored window
enters once, so classes count at their law frequency. The realized KIND excess
is an unbiased estimate of its class's KIND KL, and every regressor is a
function of the prefix only, so OLS is unbiased; standard errors are HC1
(heteroskedasticity-robust). Also: mean excess by decile of ι_kind,m, with the
decile's mean H_kind beside it (to see the confound), and the same pooled over
the seeds of each rung.

    uv run python scripts/implicit_info_bintest.py --raw docs/implicit-info-bintest-k7-<date>.json
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


def ols_hc1(y, X):
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    n, p = X.shape
    meat = (X * e[:, None] ** 2).T @ X
    cov = XtX_inv @ meat @ XtX_inv * n / (n - p)
    return beta, np.sqrt(np.diag(cov))


def deciles(y, x, h):
    edges = np.quantile(x, np.linspace(0, 1, 11))
    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, 9)
    out = []
    for q in range(10):
        s = idx == q
        if s.any():
            out.append({"x_lo": float(edges[q]), "x_hi": float(edges[q + 1]), "n": int(s.sum()),
                        "mean_iota": float(x[s].mean()), "mean_excess": float(y[s].mean()),
                        "se_excess": float(y[s].std(ddof=1) / np.sqrt(s.sum())) if s.sum() > 1 else None,
                        "mean_H_kind": float(h[s].mean())})
    return out


def windows(census_raw, m_long):
    c = json.load(open(census_raw))
    k, rung, eps = c["k"], c["rung"], c["eps"]
    tag = f"{rung}-eps{eps.replace('/', '_')}"
    rows = [json.loads(l) for l in open(c["per_window_file"])]
    split = read_split(Path(c["corpus"]), c["split"])
    iota = {}
    for line in open(CACHE / f"c1prime-loop-40-8-2-{tag}-k{k}-kind-m123456.jsonl"):
        d = json.loads(line)
        iota[d["k"]] = (d["iota_1"], d[f"iota_{m_long}"])
    hk = {}
    for key, (_, star) in load_table(TABLES / f"c1prime-loop-40-8-2-{tag}-k{k}.jsonl").items():
        kd = {}
        for r, p in star.items():
            kd[r.kind] = kd.get(r.kind, 0.0) + float(p)
        hk[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
    id_of, key_of = {}, {}
    y, lo, sh, h = [], [], [], []
    for r in rows:
        toks = tuple(VOCAB[t] for t in split[r["i"]][0])
        reset, recs = surface_records(toks)
        key = serial_key((reset, pattern_all(recs[:k])[0]))
        if id_of.setdefault(key, r["key"]) != r["key"] or key_of.setdefault(r["key"], key) != key:
            raise SystemExit(f"GATE: class id mismatch at window {r['i']} in {census_raw}")
        i1, im = iota[key]
        y.append(r["by_field"]["kind"]); lo.append(im); sh.append(i1 - im); h.append(hk[key])
    return c, tuple(np.asarray(v) for v in (y, lo, sh, h))


def analyse(y, lo, sh, h):
    X = np.column_stack([np.ones(len(y)), lo, sh, h])
    b, se = ols_hc1(y, X)
    Xl = np.column_stack([np.ones(len(y)), lo])
    bl, sel = ols_hc1(y, Xl)
    return {"n": int(len(y)), "mean_excess": float(y.mean()),
            "full": {"terms": ["1", "iota_long", "iota_short", "H_kind"], "beta": b.tolist(), "se": se.tolist()},
            "long_only": {"beta": bl.tolist(), "se": sel.tolist()},
            "deciles_by_iota_long": deciles(y, lo, h)}


def run_one(args):
    census_raw, m_long = args
    c, (y, lo, sh, h) = windows(census_raw, m_long)
    return {"census_raw": census_raw, "rung": c["rung"], "eps": c["eps"], "seed": c["seed"],
            **analyse(y, lo, sh, h)}, (c["rung"], c["eps"], y, lo, sh, h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--m-long", type=int, default=4)
    ap.add_argument("--glob", default="docs/learner-window-census-r[1-4]-eps*-seed*-2026-09-2*.json")
    a = ap.parse_args()
    raws = sorted(glob.glob(a.glob))
    with ProcessPoolExecutor(max_workers=len(raws)) as ex:
        res = list(ex.map(run_one, [(r, a.m_long) for r in raws]))
    runs, pooled_in = [r for r, _ in res], {}
    for _, (rung, eps, y, lo, sh, h) in res:
        pooled_in.setdefault((rung, eps), []).append((y, lo, sh, h))
    pooled = []
    for (rung, eps), parts in sorted(pooled_in.items()):
        cat = [np.concatenate([p[i] for p in parts]) for i in range(4)]
        pooled.append({"rung": rung, "eps": eps, "seeds": len(parts), **analyse(*cat)})
    for r in runs + pooled:
        f = r["full"]
        t = [bb / ss for bb, ss in zip(f["beta"], f["se"])]
        lab = f"{r['rung']} eps={r['eps']} " + (f"s{r['seed']}" if "seed" in r else f"POOLED×{r['seeds']}")
        d = r["deciles_by_iota_long"]
        print(f"{lab:22} n={r['n']:6} β_long={f['beta'][1]:+.4f} (t {t[1]:+.1f}) β_short={f['beta'][2]:+.4f} "
              f"(t {t[2]:+.1f}) β_H={f['beta'][3]:+.4f} (t {t[3]:+.1f}) | decile excess "
              + " ".join(f"{q['mean_excess']:.3f}" for q in d), flush=True)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    json.dump({"status": "EXPLORATORY (paper-1 readiness item 3, all windows)", "git": git + ("+dirty" if dirty else ""),
               "m_long": a.m_long, "runs": runs, "pooled_by_rung": pooled}, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
