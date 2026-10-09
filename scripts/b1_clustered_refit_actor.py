"""EXPLORATORY re-analysis (inventory v0.2 §F owed item 1, ACTOR target, 2026-10-09): the confirmatory actor A1 (36 runs) and
converged-ladder A4 (24 runs) per-model tests used HC1 errors over windows, but ι is a property of the CLASS, so
the effective sample is the number of classes. This refits the frozen model per run with CR1 errors clustered by
class. Gate: the HC1 betas and ses must reproduce the frozen script's (scripts/implicit_info_bintest_actor.py, model
"full" and "full_plus_log2_class_mass") to 1e-9. The stamped verdicts are not re-scored; this reports how many runs
keep β_long > 0 with t ≥ 3 under clustering.

  uv run python scripts/b1_clustered_refit.py --raw docs/b1-clustered-refit-actor-2026-10-09.json
"""
import argparse
import glob
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from math import log2
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import implicit_info_bintest_actor as frozen  # noqa: E402
from relay_v_diagnosis import ols_cr1  # noqa: E402

from yupi.corpus.vocab import VOCAB  # noqa: E402
from yupi.corpus.writer import read_split  # noqa: E402
from yupi.learner.evaluate import surface_records  # noqa: E402
from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import serial_key  # noqa: E402

FAMILIES = {"A1_actor": "docs/learner-window-census-r[1-4]-eps*-seed*-2026-09-2*.json",
            "A4_converged_e15": "docs/learner-window-census-r[1-4]-eps*-2M-e15-seed*-2026-10-02.json"}


def keys_for(census_raw):
    c = json.load(open(census_raw))
    rows = [json.loads(l) for l in open(c["per_window_file"])]
    split = read_split(Path(c["corpus"]), c["split"])
    out = []
    for r in rows:
        reset, recs = surface_records(tuple(VOCAB[t] for t in split[r["i"]][0]))
        out.append(serial_key((reset, pattern_all(recs[:c["k"]])[0])))
    return np.array(out)


def one(raw):
    c, (y, lo, sh, h, f) = frozen.windows(raw, 4)
    ref = frozen.analyse(y, lo, sh, h, f)
    g = np.unique(keys_for(raw), return_inverse=True)[1]
    out = dict(raw=raw, rung=c["rung"], eps=c["eps"], seed=c["seed"], n=int(len(y)), n_classes=int(g.max() + 1))
    for name, X in (("full", np.column_stack([np.ones(len(y)), lo, sh, h])),
                    ("full_plus_log2_class_mass", np.column_stack([np.ones(len(y)), lo, sh, h, f]))):
        b_hc, se_hc = frozen.ols_hc1(y, X)
        if np.max(np.abs(b_hc - np.array(ref[name]["beta"]))) > 1e-9 or np.max(np.abs(se_hc - np.array(ref[name]["se"]))) > 1e-9:
            raise SystemExit(f"GATE: {raw} {name} does not reproduce the frozen HC1 fit")
        b, se, _ = ols_cr1(y, X, g)
        out[name] = dict(beta_long=float(b[1]), t_hc1=float(b_hc[1] / se_hc[1]), t_cr1_class=float(b[1] / se[1]),
                         se_ratio_cr1_over_hc1=float(se[1] / se_hc[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    out = {"status": "EXPLORATORY re-analysis of confirmatory runs (not a re-score)", "families": {}}
    for fam, pat in FAMILIES.items():
        raws = sorted(glob.glob(pat))
        with ProcessPoolExecutor(max_workers=min(24, len(raws))) as ex:
            rows = list(ex.map(one, raws))
        summ = {}
        for m in ("full", "full_plus_log2_class_mass"):
            ts = [r[m]["t_cr1_class"] for r in rows]
            summ[m] = dict(n_runs=len(rows), pass_t3=sum(t >= 3 and r[m]["beta_long"] > 0 for t, r in zip(ts, rows)),
                           min_t=float(min(ts)), median_se_ratio=float(np.median([r[m]["se_ratio_cr1_over_hc1"] for r in rows])))
        out["families"][fam] = dict(glob=pat, runs=rows, summary=summ)
        print(fam, json.dumps(summ), flush=True)
        for r in rows:
            print(f"  {r['rung']} eps={r['eps']} s{r['seed']} classes={r['n_classes']} full t_hc1={r['full']['t_hc1']:.2f} "
                  f"t_cr1={r['full']['t_cr1_class']:.2f} | +mass t_hc1={r['full_plus_log2_class_mass']['t_hc1']:.2f} "
                  f"t_cr1={r['full_plus_log2_class_mass']['t_cr1_class']:.2f}", flush=True)
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
