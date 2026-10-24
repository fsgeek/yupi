"""Score one-step vs two-step kind monitors at position 6 on the same windows (design v2:
docs/learner-two-step-design-2026-10-23.md; predictions in docs/learner-two-step-declared-2026-10-23.md).

Family: the k = 6 two-step rows; RESET-class masses halved (8-record population); groups by p_star (one step) and by
p2 (two steps); group kind = mass-majority class label. Monitors, same rule at both resolutions:
- mass-blind: nearest pure vs nearest withheld (G >= 0.1) law; abstain if |d_pure - d_withheld| <= 0.005 + 2 eta;
- prior-aware: pi_pure from W_g exp(-TV/tau) over pure and withheld groups; tau fitted on val (mean TV to truth);
  pure if pi >= 0.9, withheld if <= 0.1, else abstain.
Also, per pure window, the sufficient condition 2 TV(P_c, q) + 0.005 + 2 eta < mu_c (mu_c: the class's own distance to
the nearest withheld law, floor 0).

  python scripts/learner_two_step_score.py --dir DIR --rows ROWS_DIR [--out FILE]
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

KIND_LIST = None


def label(h, g):
    if h <= 1e-12:
        return "deterministic"
    if abs(g) < 1e-12:
        return "pure"
    return "withheld" if g >= 0.1 else "none"


def family(rows_path, kinds):
    kix = {k: i for i, k in enumerate(kinds)}
    n = len(kinds)
    truth, law1, law2, g1, g2 = {}, {}, {}, {}, {}
    for line in open(rows_path):
        r = json.loads(line)
        m = r["mass"] * (0.5 if r["key"].startswith("(True,") else 1.0)
        lab = label(r["h_star"], r["g"])
        k1 = tuple(map(tuple, r["p_star"])); k2 = tuple(map(tuple, r["p2"]))
        truth[r["key"]] = (lab, k1, k2)
        for key, store in ((k1, g1), (k2, g2)):
            d = store.setdefault(key, {})
            d[lab] = d.get(lab, 0.0) + m

    def mats(store, two):
        keys = list(store)
        V = np.zeros((len(keys), n * n if two else n))
        for i, key in enumerate(keys):
            for kk, v in key:
                if two:
                    a, b = kk.split("|"); V[i, kix[a] * n + kix[b]] = float(Fraction(v))
                else:
                    V[i, kix[kk]] = float(Fraction(v))
        W = np.array([sum(store[k].values()) for k in keys])
        G = np.array([max(store[k], key=store[k].get) for k in keys])
        return keys, V, W, G
    return truth, mats(g1, False), mats(g2, True)


def min_tv(Q, P, chunk=512):
    out = np.empty(len(Q))
    for i in range(0, len(Q), chunk):
        out[i:i + chunk] = (0.5 * np.abs(Q[i:i + chunk, None, :] - P[None]).sum(-1)).min(1)
    return out


def log_mass(Q, P, logW, tau, chunk=512):
    out = np.empty(len(Q))
    for i in range(0, len(Q), chunk):
        a = logW[None] - (0.5 * np.abs(Q[i:i + chunk, None, :] - P[None]).sum(-1)) / tau
        mx = a.max(1); out[i:i + chunk] = mx + np.log(np.exp(a - mx[:, None]).sum(1))
    return out


def score(pred, truth):
    out = {}
    for c in ("pure", "withheld"):
        sel = truth == c
        out[f"n_{c}"] = int(sel.sum())
        cov = sel & (pred != "abstain")
        out[f"recall_{c}_covered"] = float(np.mean(pred[cov] == c)) if cov.any() else None
        out[f"recall_{c}_conservative"] = float(np.mean(pred[sel] == c)) if sel.any() else None
    head = np.isin(truth, ("pure", "withheld"))
    out["coverage"] = float(np.mean(pred[head] != "abstain"))
    rc = [out["recall_pure_covered"], out["recall_withheld_covered"]]
    out["balanced_covered"] = None if None in rc else float(np.mean(rc))
    out["balanced_conservative"] = float(np.mean([out["recall_pure_conservative"], out["recall_withheld_conservative"]]))
    return out


def run_one(npz_test, npz_val, fam, kinds):
    truth_map, (k1s, P1, W1, G1), (k2s, P2, W2, G2) = fam
    ix1 = {k: i for i, k in enumerate(k1s)}; ix2 = {k: i for i, k in enumerate(k2s)}
    res: dict = {}
    taus = {}
    for name, z in (("val", np.load(npz_val)), ("test", np.load(npz_test))):
        keys = [str(k) for k in z["keys"]]
        ok = np.array([k in truth_map for k in keys])
        lab = np.array([truth_map[k][0] if k in truth_map else "unmatched" for k in keys])
        T1 = np.array([P1[ix1[truth_map[k][1]]] if k in truth_map else np.zeros(P1.shape[1]) for k in keys])
        T2 = np.array([P2[ix2[truth_map[k][2]]] if k in truth_map else np.zeros(P2.shape[1]) for k in keys])
        q1, q2, eta = z["q1"], z["q2"], z["eta"]
        t1 = 0.5 * np.abs(T1 - q1).sum(1); t2 = 0.5 * np.abs(T2 - q2).sum(1)
        if name == "val":
            taus = dict(tau1=float(t1[ok].mean()), tau2=float(t2[ok].mean()))
            continue
        out: dict = dict(n=len(keys), unmatched=int((~ok).sum()), tau1=taus["tau1"], tau2=taus["tau2"],
                   eta_median=float(np.median(eta)), eta_q90=float(np.quantile(eta, 0.9)), eta_max=float(eta.max()),
                   tv1_median=float(np.median(t1[ok])), tv2_median=float(np.median(t2[ok])))
        for res_name, Q, P, W, G, e, tau, Tt in (("one", q1, P1, W1, G1, np.zeros(len(eta)), taus["tau1"], T1),
                                                  ("two", q2, P2, W2, G2, eta, taus["tau2"], T2)):
            Pp, Pw = P[G == "pure"], P[G == "withheld"]
            dp, dw = min_tv(Q, Pp), min_tv(Q, Pw)
            mb = np.where(np.abs(dp - dw) <= 0.005 + 2 * e, "abstain", np.where(dp < dw, "pure", "withheld"))
            lp_ = log_mass(Q, Pp, np.log(W[G == "pure"]), tau); lw = log_mass(Q, Pw, np.log(W[G == "withheld"]), tau)
            pi = 1 / (1 + np.exp(lw - lp_))
            pa = np.where(pi >= 0.9, "pure", np.where(pi <= 0.1, "withheld", "abstain"))
            sel = lab == "pure"
            mu = min_tv(Tt[sel], Pw)
            tv = 0.5 * np.abs(Tt[sel] - Q[sel]).sum(1)
            suff = float(np.mean(2 * tv + 0.005 + 2 * e[sel] < mu)) if sel.any() else None
            out[res_name] = dict(mass_blind=score(mb, lab), prior_aware=score(pa, lab), sufficient_share_pure=suff,
                                 mu_pure_median=float(np.median(mu)) if sel.any() else None)
        res = out
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    D = Path(a.dir)
    out = []
    fams = {}
    for f in sorted(D.glob("*-test.npz")):
        stem = f.name[:-len("-test.npz")]
        rung = "r1" if "-r1-" in stem else "r3"
        eps = "1_2" if "eps1_2" in stem else "1"
        kinds = [str(k) for k in np.load(f)["kinds"]]
        if (rung, eps) not in fams:
            fams[(rung, eps)] = family(Path(a.rows) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k6.jsonl", kinds)
        r = run_one(f, D / f"{stem}-val.npz", fams[(rung, eps)], kinds)
        r.update(run=stem, rung=rung, eps=eps.replace("_", "/"))
        out.append(r)
        o, t = r["one"], r["two"]
        print(json.dumps(dict(run=stem, unmatched=r["unmatched"], tv1=round(r["tv1_median"], 4), tv2=round(r["tv2_median"], 4),
                              eta_med=round(r["eta_median"], 5),
                              mb1=[round(o["mass_blind"]["coverage"], 3), o["mass_blind"]["balanced_covered"] and round(o["mass_blind"]["balanced_covered"], 3), round(o["mass_blind"]["balanced_conservative"], 3)],
                              mb2=[round(t["mass_blind"]["coverage"], 3), t["mass_blind"]["balanced_covered"] and round(t["mass_blind"]["balanced_covered"], 3), round(t["mass_blind"]["balanced_conservative"], 3)],
                              pa1=round(o["prior_aware"]["balanced_conservative"], 3), pa2=round(t["prior_aware"]["balanced_conservative"], 3),
                              suff1=o["sufficient_share_pure"], suff2=t["sufficient_share_pure"])), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(design="docs/learner-two-step-design-2026-10-23.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
