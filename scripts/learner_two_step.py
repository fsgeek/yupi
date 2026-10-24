"""Learner-side two-step KIND law at position 6 (design v2: docs/learner-two-step-design-2026-10-23.md).

For each sampled eligible window (>= 8 records), enumerate the model's own record-7 completions token by token:
- each slot's conditional is renormalised over its legal set (KIND slot over KINDS excluding RESET; entity slots over
  non-PAD tokens); masked slots are forced to MASKED with weight one;
- at each node keep tokens in decreasing probability until their cumulative conditional mass reaches 1 - PRUNE, and
  drop any branch whose prefix probability falls below FLOOR; eta accumulates exactly the prefix-weighted pruned mass;
- after record 7, the record-8 KIND distribution is renormalised over KINDS.
q2 = normalised sum over leaves; asserted: sum q2 = 1 and its k1-marginal equals q1 (the one-step output at position
6) up to the pruning, checked as |marginal - q1|_TV <= eta + 1e-9.

  python scripts/learner_two_step.py RUN_DIR --split val|test --n-sample N --seed S --out FILE.npz
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import KINDS, MASKED, PAD, RESET, TOKEN_ID, VOCAB
from yupi.learner.data import frame, read_split
from yupi.learner.evaluate import surface_records
from yupi.learner.model import ModelConfig, build_model
from yupi.naming import pattern_all

K = 6
PRUNE = 1e-4
FLOOR = 1e-5    # absolute prefix-probability floor per branch (eta stays exact; design v2 note)
KIND_LIST = [k for k in KINDS if k != RESET]
KIND_IDS = np.array([TOKEN_ID[k] for k in KIND_LIST])
PAD_ID = TOKEN_ID[PAD]
MASKED_ID = TOKEN_ID[MASKED]
MASKED_SLOTS = {"r1": (2, 3, 4), "r2": (3, 4), "r3": (4,), "r4": ()}


def logprobs(model, seqs, n_pos):
    x, _, _ = frame(seqs, n_pos)
    out = []
    with torch.no_grad():
        for i in range(0, len(x), 1024):
            out.append(torch.log_softmax(model(torch.from_numpy(x[i:i + 1024])).double(), -1).numpy())
    return np.concatenate(out)


def slot_dist(lp_row, slot):
    if slot == 0:
        p = np.exp(lp_row[KIND_IDS]); return KIND_IDS, p / p.sum()
    p = np.exp(lp_row.copy()); p[PAD_ID] = 0.0
    ids = np.nonzero(p > 0)[0]; p = p[ids]
    return ids, p / p.sum()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--split", required=True)
    ap.add_argument("--n-sample", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run = Path(a.run)
    rj = json.loads((run / "run.json").read_text())
    m = Manifest.from_json(json.loads((Path(rj["corpus_dir"]) / "manifest.json").read_text()))
    n_pos = rj["model"]["n_pos"]
    model = build_model(ModelConfig(**rj["model"]))
    model.load_state_dict(torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")["model"])
    model.eval()
    masked = MASKED_SLOTS[m.rung]
    rows = read_split(rj["corpus_dir"], a.split)
    wins = [tuple(VOCAB[t] for t in w) for w, _ in rows]
    elig = [i for i, w in enumerate(wins) if len(surface_records(w, m.rung)[1]) >= 8]
    rng = np.random.default_rng(a.seed)
    pick = np.sort(rng.choice(len(elig), size=min(a.n_sample, len(elig)), replace=False))
    idx = [elig[j] for j in pick]
    keys, resets, prefixes = [], [], []
    for i in idx:
        reset, recs = surface_records(wins[i], m.rung)
        off = 1 if reset else 0
        keys.append(repr((reset, pattern_all(recs[:K])[0])))
        resets.append(reset)
        prefixes.append(tuple(TOKEN_ID[t] for t in wins[i][:off + 5 * K]))
    # nodes: (window j, token tuple of record 7 so far, prefix prob)
    nodes = [(j, (), 1.0) for j in range(len(idx))]
    eta = np.zeros(len(idx))
    q1 = np.zeros((len(idx), len(KIND_LIST)))
    for slot in range(5):
        if slot in masked:
            nodes = [(j, t + (MASKED_ID,), p) for j, t, p in nodes]
            continue
        lp = logprobs(model, [prefixes[j] + t for j, t, _ in nodes], n_pos)
        new = []
        for (j, t, p), row in zip(nodes, lp):
            L = len(prefixes[j]) + len(t)
            ids, pr = slot_dist(row[L], slot)
            if slot == 0:
                q1[j] = pr
            o = np.argsort(-pr); c = np.cumsum(pr[o])
            keep = o[:int(np.searchsorted(c, 1 - PRUNE)) + 1]
            eta[j] += p * (1.0 - pr[keep].sum())
            for x in keep:
                q = p * float(pr[x])
                if q >= FLOOR:
                    new.append((j, t + (int(ids[x]),), q))
                else:
                    eta[j] += q
        nodes = new
    n_leaves = np.bincount([j for j, _, _ in nodes], minlength=len(idx))
    lp = logprobs(model, [prefixes[j] + t for j, t, _ in nodes], n_pos)
    kpos = {k: i for i, k in enumerate(KIND_LIST)}
    q2 = np.zeros((len(idx), len(KIND_LIST), len(KIND_LIST)))
    for (j, t, p), row in zip(nodes, lp):
        L = len(prefixes[j]) + 5
        _, pr = slot_dist(row[L], 0)
        q2[j, kpos[VOCAB[t[0]]]] += p * pr
    tot = q2.sum((1, 2))
    q2 /= tot[:, None, None]
    marg = q2.sum(2)
    tv_marg = 0.5 * np.abs(marg - q1).sum(1)
    assert np.allclose(q2.sum((1, 2)), 1.0)
    assert (tv_marg <= eta + 1e-9).all(), float((tv_marg - eta).max())
    np.savez_compressed(a.out, q1=q1, q2=q2.reshape(len(idx), -1), eta=eta, keys=np.array(keys), resets=np.array(resets),
                        idx=np.array(idx), n_leaves=n_leaves, kinds=np.array(KIND_LIST))
    print(json.dumps(dict(run=str(run), split=a.split, n=len(idx), eligible=len(elig), eta_median=float(np.median(eta)),
                          eta_max=float(eta.max()), leaves_median=float(np.median(n_leaves)), leaves_max=int(n_leaves.max()),
                          tv_marg_max=float(tv_marg.max()))))


if __name__ == "__main__":
    main()
