"""Declared: docs/challenge-declared-2026-10-25.md (stamped before running).

NL1/NL2 (nearest-law, score s = d_withheld - d_pure) and PA* (prior-aware, best (beta, c) on val, one step), each with
a symmetric threshold set on val to 0.95 coverage of the headline population; frozen; scored on fresh test windows
(seed 20261025) after dropping windows used in the 10-25 run.

  python scripts/challenge_score.py --dir DIR --fresh FRESH_DIR --rows ROWS_DIR --scores SCORE_JSON [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from learner_two_step_score import family, log_mass, min_tv  # noqa: E402

COVER = 0.95


def bal(pred, lab):
    head = np.isin(lab, ("pure", "withheld"))
    p, t = pred[head], lab[head]
    cov = p != "abstain"
    rc = [np.mean(p[cov & (t == c)] == c) for c in ("pure", "withheld")]
    cons = [np.mean(p[t == c] == c) for c in ("pure", "withheld")]
    return dict(coverage=float(cov.mean()), balanced_covered=float(np.mean(rc)), balanced_conservative=float(np.mean(cons)))


def decide(score, t):
    return np.where(score >= t, "pure", np.where(score <= -t, "withheld", "abstain"))


def thr_for_coverage(score, lab):
    head = np.isin(lab, ("pure", "withheld"))
    a = np.sort(np.abs(score[head]))
    return float(a[int((1 - COVER) * len(a))])     # abstain on the smallest |score| 5 %


def scores_nl(Q, P, G):
    return min_tv(Q, P[G == "withheld"]) - min_tv(Q, P[G == "pure"])


def scores_pa(Q, P, W, G, tau, beta):
    lp = log_mass(Q, P[G == "pure"], beta * np.log(W[G == "pure"]), tau)
    lw = log_mass(Q, P[G == "withheld"], beta * np.log(W[G == "withheld"]), tau)
    return 2.0 / (1.0 + np.exp(np.clip(lw - lp, -700, 700))) - 1.0   # pi mapped to [-1, 1]; threshold symmetric


def main():
    ap = argparse.ArgumentParser()
    for k in ("--dir", "--fresh", "--rows", "--scores"):
        ap.add_argument(k, required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    taus = {r["run"]: r["tau1"] for r in json.loads(Path(a.scores).read_text())["rows"]}
    fam, out = None, []
    for fv in sorted(Path(a.dir).glob("*-val.npz")):
        stem = fv.name[:-len("-val.npz")]
        v, old, z = np.load(fv), np.load(Path(a.dir) / f"{stem}-test.npz"), np.load(Path(a.fresh) / f"{stem}-test.npz")
        kinds = [str(k) for k in v["kinds"]]
        if fam is None:
            fam = family(Path(a.rows) / "c1prime-loop-40-8-2-r1-eps1-k6.jsonl", kinds)
        tm, (_, P1, W1, G1), (_, P2, W2, G2) = fam
        keep = ~np.isin(z["idx"], old["idx"])
        labv = np.array([tm[str(k)][0] for k in v["keys"]])
        labt = np.array([tm[str(k)][0] for k in z["keys"]])[keep]
        res: dict = dict(run=stem, n_fresh=int(keep.sum()), eta_median=float(np.median(z["eta"][keep])))
        for name, Qv, Qt, P, G in (("NL1", v["q1"], z["q1"][keep], P1, G1), ("NL2", v["q2"], z["q2"][keep], P2, G2)):
            t = thr_for_coverage(scores_nl(Qv, P, G), labv)
            res[name] = dict(threshold=t, val=bal(decide(scores_nl(Qv, P, G), t), labv),
                             test=bal(decide(scores_nl(Qt, P, G), t), labt))
        best = None
        for beta in (1.0, 2.0):
            for c in (1 / 16, 1 / 8, 1 / 4):
                sv = scores_pa(v["q1"], P1, W1, G1, taus[stem] * c, beta)
                t = thr_for_coverage(sv, labv)
                b = bal(decide(sv, t), labv)
                if best is None or b["balanced_conservative"] > best[0]:
                    best = (b["balanced_conservative"], beta, c, t, b)
        _, beta, c, t, bv = best
        res["PA*"] = dict(beta=beta, c=c, threshold=t, val=bv,
                          test=bal(decide(scores_pa(z["q1"][keep], P1, W1, G1, taus[stem] * c, beta), t), labt))
        out.append(res)
        print("%-30s n %d | NL1 %.3f NL2 %.3f PA* %.3f (b%.0f c%.4g) | cov %.3f %.3f %.3f" % (
            stem.split("eps1-2M-")[1][:30], res["n_fresh"], res["NL1"]["test"]["balanced_covered"],
            res["NL2"]["test"]["balanced_covered"], res["PA*"]["test"]["balanced_covered"], beta, c,
            res["NL1"]["test"]["coverage"], res["NL2"]["test"]["coverage"], res["PA*"]["test"]["coverage"]), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/challenge-declared-2026-10-25.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
