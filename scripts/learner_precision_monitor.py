"""Declared check: docs/learner-precision-monitor-check-2026-10-15.md.

For each model, run the evaluator at k = 7 on the test split, capturing (exact P*, model Q) per window through a
wrapper around evaluate.window_excess (evaluate.py itself is untouched). Then, per window: t = TV(P*, Q); the
look-alike set = classes whose exact P*(KIND) is at least as close to Q as the truth; a = law-mass share of that set
whose transition randomness R differs from the true class's by >= 0.1 bits. R per class comes from the split-v2 rows
(grouped by exact P* vector; within an exact group R is constant to < 1e-9 except on < 0.05 % of mass, see
one-step-identifiability-check-2026-10-15.md), so no class-key matching is needed.

  python scripts/learner_precision_monitor.py RUN_DIR [RUN_DIR ...] --out docs/<name>.json
"""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch

import yupi.learner.evaluate as ev
from yupi.corpus.manifest import Manifest
from yupi.learner.evaluate import evaluate, kind_belief, kind_output, torch_logprobs_fn
from yupi.learner.exposure import kind_exposure
from yupi.learner.model import ModelConfig, build_model
from yupi.pattern_ceiling import load_table

SPLIT = Path.home() / ".cache/yupi-scratch/split-v2"
TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
K = 7


def groups_for(rung, eps_tag):
    """Distinct exact P*(KIND) vectors -> (vector over KINDS, [(mass, R)])."""
    g = {}
    for line in open(SPLIT / f"c1prime-loop-40-8-2-{rung}-eps{eps_tag}-k{K}.jsonl"):
        r = json.loads(line)
        key = tuple(sorted(map(tuple, r["p_star"])))
        g.setdefault(key, []).append((r["mass"], r["r"], r["g"]))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    out = []
    for run in map(Path, a.runs):
        rj = json.loads((run / "run.json").read_text())
        m = Manifest.from_json(json.loads((Path(rj["corpus_dir"]) / "manifest.json").read_text()))
        law, eps_tag = m.law(), m.epsilon.replace("/", "_")
        tfile = TABLES / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{eps_tag}-k{K}.jsonl"
        tables = {K: load_table(tfile)}
        groups = groups_for(m.rung, eps_tag)
        keys = list(groups)
        kinds = list(ev.KINDS)
        P = np.array([[float(Fraction(dict(k).get(x, "0"))) for x in kinds] for k in keys])
        gR = [np.array([x[1] for x in groups[k]]) for k in keys]
        gG = [np.array([x[2] for x in groups[k]]) for k in keys]
        gW = [np.array([x[0] for x in groups[k]]) for k in keys]
        index = {k: i for i, k in enumerate(keys)}
        captured = []
        orig = ev.window_excess

        def wrapped(lp5, next_tokens, used, star, rho, rung=None):
            b = kind_belief(star)
            q, _ = kind_output(lp5[0])
            q = q / q.sum()
            km = tuple(sorted((k, str(v)) for k, v in ev.kind_marginal(star).items() if v > 0))
            captured.append((b, q, km, kind_exposure(star, lp5[0])["kl_eval"]))
            return orig(lp5, next_tokens, used, star, rho, rung)

        ev.window_excess = wrapped
        try:
            ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
            model = build_model(ModelConfig(**rj["model"]))
            model.load_state_dict(ck["model"])
            model.eval()
            res = evaluate(torch_logprobs_fn(model, "cpu"), rj["corpus_dir"], law, tables, (K,), rj["model"]["n_pos"], n=a.n)
        finally:
            ev.window_excess = orig
        t_all, a_all, ag_all, kl_all, miss = [], [], [], [], 0
        Q = np.array([q for _, q, _, _ in captured])
        for j0 in range(0, len(captured), 256):
            tvq = 0.5 * np.abs(Q[j0:j0 + 256, None, :] - P[None, :, :]).sum(-1)   # windows x groups
            for jj in range(tvq.shape[0]):
                b, q, km, kl = captured[j0 + jj]
                gi = index.get(km)
                if gi is None:
                    miss += 1
                    continue
                t = 0.5 * float(np.abs(b - q).sum())
                rc = float(np.average(gR[gi], weights=gW[gi]))
                near = np.nonzero(tvq[jj] <= t + 1e-12)[0]
                tot = sum(float(gW[i].sum()) for i in near)
                dis = sum(float(gW[i][np.abs(gR[i] - rc) >= 0.1].sum()) for i in near)
                gc = float(np.average(gG[gi], weights=gW[gi]))
                if gc < 1e-12:
                    disg = sum(float(gW[i][gG[i] >= 0.1].sum()) for i in near)
                elif gc >= 0.1:
                    disg = sum(float(gW[i][gG[i] < 1e-12].sum()) for i in near)
                else:
                    disg = 0.0
                t_all.append(t); a_all.append(dis / tot); ag_all.append(disg / tot); kl_all.append(kl)
        t_arr, a_arr, ag_arr = np.array(t_all), np.array(a_all), np.array(ag_all)
        mean_kl = float(np.mean(kl_all))
        line = dict(run=str(run), rung=m.rung, eps=m.epsilon, seed=rj["seed"], n=len(t_all), unmatched=miss,
                    checkpoint_sha256=hashlib.sha256((run / "ckpt.pt").read_bytes()).hexdigest(),
                    tv_mean=float(t_arr.mean()), tv_median=float(np.median(t_arr)), tv_q90=float(np.quantile(t_arr, 0.9)),
                    a_mean=float(a_arr.mean()), share_a_ge_0_10=float(np.mean(a_arr >= 0.10)),
                    aG_mean=float(ag_arr.mean()), share_aG_ge_0_10=float(np.mean(ag_arr >= 0.10)),
                    share_tv_gt_0_05=float(np.mean(t_arr > 0.05)),
                    mean_kl_eval=mean_kl, evaluator_kind_kl=res["per_k"][K]["kind_kl_bits"]["mean"],
                    pinsker_bound_of_mean=math.sqrt(mean_kl * math.log(2) / 2))
        line["V1_kl_matches_evaluator"] = abs(line["mean_kl_eval"] - line["evaluator_kind_kl"]) < 1e-6
        line["V2_tv_le_pinsker"] = line["tv_mean"] <= line["pinsker_bound_of_mean"] + 1e-12
        out.append(line)
        print(json.dumps(line), flush=True)
    Path(a.out).write_text(json.dumps(dict(declared="docs/learner-precision-monitor-check-2026-10-15.md", rows=out), indent=1))


if __name__ == "__main__":
    main()
