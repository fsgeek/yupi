"""EXPLORATORY diagnosis of the relay's V-shaped gain (docs/relay-v-diagnosis-design-v0.1.md, committed
before this script was first run). Rebuilds the paired per-window arrays with the frozen relay_paired.py
functions (imported unchanged, all gates), attaches per-class ι4 at both rungs, n_relay and log2 class
mass, and fits the design's models M1-M3 with class-clustered (CR1) standard errors.

    uv run --extra learner python scripts/relay_v_diagnosis.py --raw docs/relay-v-diagnosis-2026-10-04.json
"""
import argparse
import hashlib
import json
import subprocess
import sys
from math import log2
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relay_paired as rp  # noqa: E402  (frozen; imported unchanged)

from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import load_table, serial_key  # noqa: E402

CACHE = Path.home() / ".cache/yupi-scratch/implicit"
TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
EXACT_SIDE = "docs/relay-exact-side-2026-09-30.json"
ARMS = {"primary": ([f"docs/learner-window-census-r1-eps1-2M-seed{s}-2026-09-21.json" for s in (1, 2, 3)],
                    [f"docs/learner-window-census-r1R-eps1-2M-e5-seed{s}-2026-10-02.json" for s in (1, 2, 3)]),
        "secondary": ([f"docs/learner-window-census-r1-eps1-2M-e15-seed{s}-2026-10-02.json" for s in (1, 2, 3)],
                      [f"docs/learner-window-census-r1R-eps1-2M-e15-seed{s}-2026-10-02.json" for s in (1, 2, 3)])}
K = rp.K


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ols_cr1(y, X, groups):
    """OLS with cluster-robust (CR1) standard errors."""
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    e = y - X @ beta
    n, p = X.shape
    _, g = np.unique(groups, return_inverse=True)
    G = g.max() + 1
    S = np.zeros((G, p))
    np.add.at(S, g, X * e[:, None])
    cov = XtX_inv @ (S.T @ S) @ XtX_inv * (G / (G - 1)) * ((n - 1) / (n - p))
    return beta, np.sqrt(np.diag(cov)), cov


def fit(name, terms, cols, y, groups, zero):
    X = np.column_stack([np.ones(len(y))] + cols)
    b, se, cov = ols_cr1(y, X, groups)
    pred_zero = float((X[zero] @ b).mean())
    obs_zero = float(y[zero].mean())
    se_zero = float(y[zero].std(ddof=1) / np.sqrt(zero.sum()))
    return dict(model=name, terms=["1"] + terms, beta=b.tolist(), se=se.tolist(), t=(b / se).tolist(),
                cov=cov.tolist(), zero_set=dict(observed=obs_zero, se=se_zero, predicted=pred_zero,
                                                gap_in_se=(obs_zero - pred_zero) / se_zero))


def vif(cols):
    X = np.column_stack(cols)
    out = []
    for j in range(X.shape[1]):
        others = np.column_stack([np.ones(len(X))] + [X[:, i] for i in range(X.shape[1]) if i != j])
        beta, *_ = np.linalg.lstsq(others, X[:, j], rcond=None)
        r = X[:, j] - others @ beta
        r2 = 1 - r.var() / X[:, j].var()
        out.append(float(1 / (1 - r2)))
    return out


def iota4(path):
    return {json.loads(l)["k"]: json.loads(l)["iota_4"] for l in open(path)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    f_r1 = CACHE / "c1prime-loop-40-8-2-r1-eps1-k7-kind-m123456.jsonl"
    f_r1R = CACHE / "c1prime-loop-40-8-2-r1R-eps1-k7-kind-m123456.jsonl"
    f_tab = TABLES / "c1prime-loop-40-8-2-r1-eps1-k7.jsonl"
    i_r1, i_r1R = iota4(f_r1), iota4(f_r1R)
    lmass = {serial_key(key): log2(float(mass)) for key, (mass, _) in load_table(f_tab).items()}
    diota, diota_meta = rp.load_diota(EXACT_SIDE, "1")
    out = dict(status="EXPLORATORY (docs/relay-v-diagnosis-design-v0.1.md)",
               git=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
               inputs=dict(iota_r1=dict(file=str(f_r1), sha256=sha(f_r1)), iota_r1R=dict(file=str(f_r1R), sha256=sha(f_r1R)),
                           table_r1=dict(file=str(f_tab), sha256=sha(f_tab)), diota=diota_meta,
                           relay_paired_sha256=sha(Path(__file__).resolve().parent / "relay_paired.py")),
               arms={})
    for arm, (r1, r1R) in ARMS.items():
        c1 = [rp.load_census(r) for r in r1]
        cR = [rp.load_census(r) for r in r1R]
        ids = sorted(c1[0][1])
        recs1 = rp.load_records(c1[0][0]["corpus"], ids, "r1")
        recsR = rp.load_records(cR[0][0]["corpus"], ids, "r1R")
        ids_j, y, x, z, _ = rp.join([r for _, r in c1], [r for _, r in cR], recs1, recsR, diota)
        assert list(ids_j) == ids
        a1, aR, nrel, lm, grp = [], [], [], [], []
        for i in ids:
            (reset1, rec1), (resetR, recR) = recs1[i], recsR[i]
            k1 = serial_key((reset1, pattern_all(rec1[:K])[0]))
            kR = serial_key((resetR, pattern_all(recR[:K])[0]))
            a1.append(i_r1[k1]); aR.append(i_r1R[kR]); lm.append(lmass[k1]); grp.append(k1)
            nrel.append(kR.split("|", 1)[1].count("K:"))
        a1, aR, nrel, lm = map(np.asarray, (a1, aR, nrel, lm))
        recon = np.abs((a1 - aR) - x).max()
        if recon > 1e-9:
            raise SystemExit(f"REFUSED: ι4_r1 − ι4_r1R differs from the Δι table by {recon} in arm {arm}")
        grp = np.asarray(grp)
        res = dict(n=int(len(y)), n_classes=int(len(np.unique(grp))), d_iota_reconstruction_max_abs=float(recon),
                   corr_iota4_r1_r1R=float(np.corrcoef(a1, aR)[0, 1]),
                   n_relay=dict(mean=float(nrel.mean()), min=int(nrel.min()), max=int(nrel.max())),
                   vif_M3=dict(zip(["iota4_r1", "iota4_r1R", "n_relay", "log2mass"], vif([a1, aR, nrel, lm]))))
        res["A_ref"] = fit("A: Δι", ["d_iota"], [x], y, grp, z)
        res["M1"] = fit("M1", ["iota4_r1", "iota4_r1R", "log2mass"], [a1, aR, lm], y, grp, z)
        b, cov = np.array(res["M1"]["beta"]), np.array(res["M1"]["cov"])
        s = b[1] + b[2]
        res["M1"]["sum_b_r1_b_r1R"] = dict(value=float(s), se=float(np.sqrt(cov[1, 1] + cov[2, 2] + 2 * cov[1, 2])))
        res["M1"]["sum_b_r1_b_r1R"]["t"] = res["M1"]["sum_b_r1_b_r1R"]["value"] / res["M1"]["sum_b_r1_b_r1R"]["se"]
        res["M2"] = fit("M2", ["n_relay", "log2mass"], [nrel, lm], y, grp, z)
        res["M3"] = fit("M3", ["iota4_r1", "iota4_r1R", "n_relay", "log2mass"], [a1, aR, nrel, lm], y, grp, z)
        res["split"] = fit("split", ["d_iota_pos", "d_iota_neg"], [np.maximum(x, 0), np.maximum(-x, 0)], y, grp, z)
        for m in ("A_ref", "M1", "M2", "M3", "split"):
            res[m].pop("cov")
        out["arms"][arm] = res
        print(f"== {arm}: n={res['n']} classes={res['n_classes']} corr(ι4_r1, ι4_r1R)={res['corr_iota4_r1_r1R']:+.3f} "
              f"VIF={ {k: round(v, 2) for k, v in res['vif_M3'].items()} }")
        for m in ("A_ref", "M1", "M2", "M3", "split"):
            r = res[m]
            terms = " ".join(f"{tn}={bb:+.5f}(t {tt:+.1f})" for tn, bb, tt in zip(r["terms"], r["beta"], r["t"]))
            print(f"  {m:6} {terms} | zero set obs {r['zero_set']['observed']:+.5f} pred {r['zero_set']['predicted']:+.5f} "
                  f"gap {r['zero_set']['gap_in_se']:+.1f} se")
        sm = res["M1"]["sum_b_r1_b_r1R"]
        print(f"  M1 b_r1 + b_r1R = {sm['value']:+.5f} (t {sm['t']:+.1f})")
    json.dump(out, open(a.raw, "w"), indent=1)


if __name__ == "__main__":
    main()
