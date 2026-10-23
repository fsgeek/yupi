"""Declared check: docs/kind-classifier-declared-2026-10-22.md (stamped at 7f4fc98 before any run).

An operational monitor for the kind of next-KIND uncertainty (pure randomness vs withheld state). It sees only the
cell's exact family (the split-v2 table: per-class exact law, mass and split) and one model output q. Nearest exact
law by TV, with abstention margin m; prior-only baseline; oracle-q reference (q = the true class's exact law).
Truth is per class (via the evaluator's on_window class key, matched to the split rows' key).

  python scripts/learner_kind_classifier.py RUN_DIR [RUN_DIR ...] --out docs/<name>.json [--n N]
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch

import yupi.learner.evaluate as ev
from yupi.corpus.manifest import Manifest
from yupi.learner.evaluate import evaluate, kind_belief, kind_output, torch_logprobs_fn
from yupi.learner.model import ModelConfig, build_model
from yupi.pattern_ceiling import load_table

SPLIT = Path.home() / ".cache/yupi-scratch/split-v2"
TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
K = 7
MARGINS = (0.0, 0.0025, 0.005, 0.01, 0.02)
HEADLINE_M = 0.005
LABELS = ("pure", "withheld", "deterministic", "none")


def label(h, g):
    if h <= 1e-12:
        return "deterministic"
    if abs(g) < 1e-12:
        return "pure"
    if g >= 0.1:
        return "withheld"
    return "none"


def family(rung, eps_tag):
    """Per-class truth by key; per-law groups with law vector, mass and mass-majority kind."""
    truth, groups = {}, {}
    for line in open(SPLIT / f"c1prime-loop-40-8-2-{rung}-eps{eps_tag}-k{K}.jsonl"):
        r = json.loads(line)
        lab = label(r["h_star"], r["g"])
        truth[r["key"]] = lab
        law = tuple(sorted(map(tuple, r["p_star"])))
        d = groups.setdefault(law, {})
        d[lab] = d.get(lab, 0.0) + r["mass"]
    laws = list(groups)
    kinds = list(ev.KINDS)
    P = np.array([[float(Fraction(dict(k).get(x, "0"))) for x in kinds] for k in laws])
    W = np.array([sum(groups[k].values()) for k in laws])
    G = np.array([max(groups[k], key=groups[k].get) for k in laws])
    return truth, P, W, G


def classify(Q, P, W, G, m):
    """Q: windows x KINDS. Returns predictions in {'pure', 'withheld', 'abstain'}."""
    is_p, is_w = G == "pure", G == "withheld"
    out = []
    for j0 in range(0, len(Q), 256):
        d = 0.5 * np.abs(Q[j0:j0 + 256, None, :] - P[None, :, :]).sum(-1)
        for row in d:
            dmin = row.min()
            cand = np.nonzero(row <= dmin + 1e-12)[0]
            g = cand[np.argmax(W[cand])]
            kd = G[g]
            if kd not in ("pure", "withheld"):
                out.append("abstain"); continue
            other = is_w if kd == "pure" else is_p
            out.append("abstain" if (other & (row <= dmin + m + 1e-12)).any() else kd)
    return np.array(out)


def score(pred, truth):
    head = np.isin(truth, ("pure", "withheld"))
    p, t = pred[head], truth[head]
    cov = p != "abstain"
    rec = {}
    for c in ("pure", "withheld"):
        sel = cov & (t == c)
        rec[c] = float(np.mean(p[sel] == c)) if sel.any() else None
        n_c = int(np.sum(t == c))
        rec[c + "_conservative"] = float(np.sum((p == c) & (t == c)) / n_c) if n_c else None
    bal = np.mean([rec["pure"], rec["withheld"]]) if None not in (rec["pure"], rec["withheld"]) else None
    bal_c = np.mean([rec["pure_conservative"], rec["withheld_conservative"]])
    confusion = {tl: {pl: int(np.sum((truth == tl) & (pred == pl))) for pl in ("pure", "withheld", "abstain")}
                 for tl in LABELS}
    return dict(n_headline=int(head.sum()), coverage=float(cov.mean()),
                balanced_accuracy_covered=None if bal is None else float(bal),
                balanced_accuracy_conservative=float(bal_c),
                accuracy_covered=float(np.mean(p[cov] == t[cov])) if cov.any() else None,
                recall_pure_covered=rec["pure"], recall_withheld_covered=rec["withheld"], confusion=confusion)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--split", default="test")
    ap.add_argument("--dump-dir", default=None, help="save per-window (Q, P_c, truth) arrays (certification margin)")
    a = ap.parse_args()
    out = []
    for run in map(Path, a.runs):
        rj = json.loads((run / "run.json").read_text())
        m = Manifest.from_json(json.loads((Path(rj["corpus_dir"]) / "manifest.json").read_text()))
        law, eps_tag = m.law(), m.epsilon.replace("/", "_")
        tfile = TABLES / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{eps_tag}-k{K}.jsonl"
        truth_of, P, W, G = family(m.rung, eps_tag)
        cap_q, cap_b, keys = [], [], []
        orig = ev.window_excess

        def wrapped(lp5, next_tokens, used, star, rho, rung=None):
            q, _ = kind_output(lp5[0])
            cap_q.append(q / q.sum()); cap_b.append(kind_belief(star))
            return orig(lp5, next_tokens, used, star, rho, rung)

        def on_window(idx, k, key, ex):
            keys.append(repr(key))

        ev.window_excess = wrapped
        try:
            ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
            model = build_model(ModelConfig(**rj["model"]))
            model.load_state_dict(ck["model"])
            model.eval()
            evaluate(torch_logprobs_fn(model, "cpu"), rj["corpus_dir"], law, {K: load_table(tfile)}, (K,),
                     rj["model"]["n_pos"], n=a.n, on_window=on_window, split=a.split)
        finally:
            ev.window_excess = orig
        assert len(keys) == len(cap_q), (len(keys), len(cap_q))
        unmatched = sum(1 for k in keys if k not in truth_of)
        truth = np.array([truth_of.get(k, "none") for k in keys])
        Q, B = np.array(cap_q), np.array(cap_b)
        if a.dump_dir:
            Path(a.dump_dir).mkdir(parents=True, exist_ok=True)
            np.savez_compressed(Path(a.dump_dir) / f"{m.rung}-eps{eps_tag}-s{rj['seed']}" + ("" if a.split == "test" else f"-{a.split}") + ".npz", Q=Q, B=B, truth=truth)
        majority = "pure" if W[G == "pure"].sum() >= W[G == "withheld"].sum() else "withheld"
        line: dict = dict(run=str(run), rung=m.rung, eps=m.epsilon, seed=rj["seed"], n=len(keys), unmatched=unmatched,
                    checkpoint_sha256=hashlib.sha256((run / "ckpt.pt").read_bytes()).hexdigest(),
                    truth_counts={c: int(np.sum(truth == c)) for c in LABELS},
                    prior_only=dict(predicts=majority, **score(np.array([majority] * len(truth)), truth)),
                    model={str(mm): score(classify(Q, P, W, G, mm), truth) for mm in MARGINS},
                    oracle_q={str(mm): score(classify(B, P, W, G, mm), truth) for mm in MARGINS})
        out.append(line)
        h = line["model"][str(HEADLINE_M)]; o = line["oracle_q"][str(HEADLINE_M)]
        print(json.dumps(dict(rung=m.rung, eps=m.epsilon, seed=rj["seed"], unmatched=unmatched,
                              model_cov=h["coverage"], model_bal=h["balanced_accuracy_covered"],
                              model_bal_cons=h["balanced_accuracy_conservative"],
                              oracle_cov=o["coverage"], oracle_bal=o["balanced_accuracy_covered"],
                              prior_acc=line["prior_only"]["accuracy_covered"])), flush=True)
    Path(a.out).write_text(json.dumps(dict(declared="docs/kind-classifier-declared-2026-10-22.md",
                                           headline_margin=HEADLINE_M, rows=out), indent=1))


if __name__ == "__main__":
    main()
