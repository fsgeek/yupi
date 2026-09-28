"""EXPLORATORY per-window test of paper-1 decision D1 (docs/paper1-skeleton-v0.1.md,
readiness item 3): does a learner's per-window excess track the exact implicit
information ι_m of its prefix class (docs/implicit-information-design-v0.1.md)?

Inputs: the committed window-census raws (per-window structural and per-field
excess at k = 7) and the per-class ι caches (whole-record and KIND targets).
Each census row's class key is recomputed from the corpus test split (window
i, first k records, Π_all) and checked against the census's own class ids (one
id per key, one key per id), a gate. ι is a function of the prefix, so every
average over ι bins is free of outcome selection.

Per run: Spearman ρ of structural excess vs ι_record, of KIND excess vs ι_kind,
and of each vs the class's exact entropy H*(class) (the rival regressor); an OLS
of excess on [1, ι, H*] with coefficients; and mean excess by ι quintile.

    uv run python scripts/implicit_info_join.py --raw docs/implicit-info-join-k7-2026-09-28.json
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


def _rank(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="mergesort")] = np.arange(len(x))
    # average ties
    xs = np.asarray(x)
    _, inv, cnt = np.unique(xs, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=r)
    return (sums / cnt)[inv]


def spearman(a, b):
    ra, rb = _rank(a), _rank(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def _load_iota(tag, k, suffix):
    out = {}
    for line in open(CACHE / f"c1prime-loop-40-8-2-{tag}-k{k}{suffix}.jsonl"):
        d = json.loads(line)
        out[d["k"]] = (d["iota_1"], d["iota_2"])
    return out


def run_one(census_raw):
    c = json.load(open(census_raw))
    k, rung, eps = c["k"], c["rung"], c["eps"]
    tag = f"{rung}-eps{eps.replace('/', '_')}"
    rows = [json.loads(l) for l in open(c["per_window_file"])]
    split = read_split(Path(c["corpus"]), c["split"])
    table = load_table(TABLES / f"c1prime-loop-40-8-2-{tag}-k{k}.jsonl")
    h_class = {serial_key(key): -sum(float(p) * log2(float(p)) for p in star.values() if p > 0)
               for key, (_, star) in table.items()}
    kind_h = {}
    for key, (_, star) in table.items():
        kd = {}
        for r, p in star.items():
            kd[r.kind] = kd.get(r.kind, 0) + float(p)
        kind_h[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
    iota_rec = _load_iota(tag, k, "")
    iota_kind = _load_iota(tag, k, "-kind")
    id_of, key_of = {}, {}
    ex, exk, ir1, ir2, ik1, ik2, hc, hk = ([] for _ in range(8))
    for r in rows:
        toks = tuple(VOCAB[t] for t in split[r["i"]][0])
        reset, recs = surface_records(toks)
        key = serial_key((reset, pattern_all(recs[:k])[0]))
        if id_of.setdefault(key, r["key"]) != r["key"] or key_of.setdefault(r["key"], key) != key:
            raise SystemExit(f"GATE: class id mismatch at window {r['i']} in {census_raw}")
        ex.append(r["structural"]); exk.append(r["by_field"]["kind"])
        ir1.append(iota_rec[key][0]); ir2.append(iota_rec[key][1])
        ik1.append(iota_kind[key][0]); ik2.append(iota_kind[key][1])
        hc.append(h_class[key]); hk.append(kind_h[key])
    ex, exk, ir1, ir2, ik1, ik2, hc, hk = map(np.asarray, (ex, exk, ir1, ir2, ik1, ik2, hc, hk))

    def ols(y, *xs):
        X = np.column_stack([np.ones(len(y)), *xs])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * resid.var(ddof=X.shape[1]))
        return [float(b) for b in beta], [float(s) for s in se]

    def quint(y, x):
        edges = np.quantile(x, [0, .2, .4, .6, .8, 1])
        idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, 4)
        return [{"x_lo": float(edges[q]), "x_hi": float(edges[q + 1]), "n": int((idx == q).sum()),
                 "mean_x": float(x[idx == q].mean()) if (idx == q).any() else None,
                 "mean_y": float(y[idx == q].mean()) if (idx == q).any() else None} for q in range(5)]

    return {"census_raw": census_raw, "rung": rung, "eps": eps, "seed": c["seed"], "k": k, "n": int(len(ex)),
            "n_classes_seen": len(id_of),
            "mean_structural": float(ex.mean()), "mean_kind_excess": float(exk.mean()),
            "mean_iota_record_1": float(ir1.mean()), "mean_iota_kind_1": float(ik1.mean()),
            "mean_iota_kind_2": float(ik2.mean()), "mean_H_class": float(hc.mean()), "mean_H_kind": float(hk.mean()),
            "spearman": {"structural~iota_record_1": spearman(ex, ir1), "structural~iota_record_2": spearman(ex, ir2),
                         "structural~H_class": spearman(ex, hc),
                         "kind~iota_kind_1": spearman(exk, ik1), "kind~iota_kind_2": spearman(exk, ik2),
                         "kind~H_kind": spearman(exk, hk)},
            "ols_structural_on_iota_record_1_and_H_class": ols(ex, ir1, hc),
            "ols_kind_on_iota_kind_1_and_H_kind": ols(exk, ik1, hk),
            "quintiles_kind_by_iota_kind_1": quint(exk, ik1),
            "quintiles_structural_by_iota_record_1": quint(ex, ir1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--glob", default="docs/learner-window-census-r[1-4]-eps*-seed*-2026-09-2*.json")
    a = ap.parse_args()
    raws = sorted(glob.glob(a.glob))
    with ProcessPoolExecutor(max_workers=len(raws)) as ex:
        res = list(ex.map(run_one, raws))
    for r in res:
        s = r["spearman"]
        print(f"{r['rung']} eps={r['eps']} s{r['seed']}: n={r['n']} exc={r['mean_structural']:.4f} kindexc={r['mean_kind_excess']:.4f} "
              f"ι_kind1={r['mean_iota_kind_1']:.4f} | ρ(exc,ι_rec1)={s['structural~iota_record_1']:+.3f} ρ(exc,H)={s['structural~H_class']:+.3f} "
              f"ρ(kind,ι_kind1)={s['kind~iota_kind_1']:+.3f} ρ(kind,H_kind)={s['kind~H_kind']:+.3f}", flush=True)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    json.dump({"status": "EXPLORATORY (paper-1 readiness item 3)", "git": git + ("+dirty" if dirty else ""),
               "design": "docs/implicit-information-design-v0.1.md", "runs": res}, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
