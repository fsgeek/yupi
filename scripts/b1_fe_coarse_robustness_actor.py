"""EXPLORATORY robustness of B1 (ACTOR target variant, 2026-10-13, whole-draft review W14; otherwise identical to
b1_fe_coarse_robustness.py, whose docstring follows)

 (skeleton v0.6 owed items 2 and 3, 2026-10-13), after the Claude reviewer's
findings 5 and 15 on the paper 1 drafts.

Per run (the D1 held-out and converged families, as in b1_clustered_refit.py):
  (a) raw bins: mean KIND excess by ι_kind,4 bin, with no controls;
  (b) the frozen model (full_plus_log2_class_mass) plus fixed effects for the last prefix record's KIND and the number
      of distinct actors in the prefix, with CR1 errors clustered on the coarse (last KIND × actor count) cells.
Gate: the frozen HC1 fit is reproduced to 1e-9 before anything is added (as in b1_clustered_refit.py).

  uv run python scripts/b1_fe_coarse_robustness_actor.py --raw docs/b1-fe-coarse-robustness-actor-2026-10-13.json
"""
import argparse
import glob
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import implicit_info_bintest_actor as frozen  # noqa: E402
from b1_clustered_refit_actor import FAMILIES  # noqa: E402
from relay_v_diagnosis import ols_cr1  # noqa: E402

from yupi.corpus.vocab import VOCAB  # noqa: E402
from yupi.corpus.writer import read_split  # noqa: E402
from yupi.learner.evaluate import surface_records  # noqa: E402

BINS = [(-1.0, 0.0), (0.0, 0.001), (0.001, 0.01), (0.01, 0.05), (0.05, 0.2), (0.2, 0.4), (0.4, 99.0)]   # (lo, hi]; first = {0}


def coarse(census_raw):
    c = json.load(open(census_raw))
    rows = [json.loads(l) for l in open(c["per_window_file"])]
    split = read_split(Path(c["corpus"]), c["split"])
    last, nact = [], []
    for r in rows:
        _, recs = surface_records(tuple(VOCAB[t] for t in split[r["i"]][0]))
        p = recs[:c["k"]]
        last.append(p[-1].kind if p else "NONE")
        nact.append(len({x.actor for x in p if x.actor not in (None, "MASKED")}))
    return np.array(last), np.array(nact)


def one(raw):
    c, (y, lo, sh, h, f) = frozen.windows(raw, 4)
    ref = frozen.analyse(y, lo, sh, h, f)["full_plus_log2_class_mass"]
    X0 = np.column_stack([np.ones(len(y)), lo, sh, h, f])
    b0, se0 = frozen.ols_hc1(y, X0)
    if np.max(np.abs(b0 - np.array(ref["beta"]))) > 1e-9 or np.max(np.abs(se0 - np.array(ref["se"]))) > 1e-9:
        raise SystemExit(f"GATE: {raw} does not reproduce the frozen HC1 fit")
    bins = []
    for a, b in BINS:
        sel = (lo == 0) if a < 0 else ((lo > a) & (lo <= b))
        bins.append(dict(bin=[a, b], n=int(sel.sum()), mean_excess=float(y[sel].mean()) if sel.any() else None))
    last, nact = coarse(raw)
    cell = np.array([f"{k}|{n}" for k, n in zip(last, nact)])
    cells, g = np.unique(cell, return_inverse=True)
    D = np.eye(len(cells))[g][:, 1:]                       # cell fixed effects (last KIND × actor count), one dropped
    X = np.column_stack([X0, D])
    keep = np.linalg.matrix_rank(X) == X.shape[1]
    if not keep:                                           # drop exactly collinear dummies
        Q, R = np.linalg.qr(X)
        X = X[:, np.abs(np.diag(R)) > 1e-10]
    b, se, _ = ols_cr1(y, X, g)
    return dict(raw=raw, rung=c["rung"], eps=c["eps"], seed=c["seed"], n=int(len(y)), n_cells=int(len(cells)),
                bins=bins, beta_long_fe=float(b[1]), t_fe_cr1_coarse=float(b[1] / se[1]),
                beta_long_frozen=float(b0[1]), t_frozen_hc1=float(b0[1] / se0[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    out = {"status": "EXPLORATORY robustness of confirmatory runs (not a re-score)", "families": {}}
    for fam, pat in FAMILIES.items():
        raws = sorted(glob.glob(pat))
        with ProcessPoolExecutor(max_workers=min(24, len(raws))) as ex:
            rows = list(ex.map(one, raws))
        ts = [r["t_fe_cr1_coarse"] for r in rows]
        mono = sum(all(x["mean_excess"] is None or y_["mean_excess"] is None or y_["mean_excess"] >= x["mean_excess"]
                       for x, y_ in zip(r["bins"][2:], r["bins"][3:])) for r in rows)
        summ = dict(n_runs=len(rows), pass_t3=sum(t >= 3 and r["beta_long_fe"] > 0 for t, r in zip(ts, rows)),
                    min_t=float(min(ts)), runs_monotone_from_bin2=int(mono))
        out["families"][fam] = dict(glob=pat, runs=rows, summary=summ)
        print(fam, json.dumps(summ), flush=True)
        for r in rows:
            print(f"  {r['rung']} eps={r['eps']} s{r['seed']} cells={r['n_cells']} t_fe={r['t_fe_cr1_coarse']:.2f} "
                  f"bins={[None if x['mean_excess'] is None else round(x['mean_excess'], 4) for x in r['bins']]}", flush=True)
    Path(a.raw).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
