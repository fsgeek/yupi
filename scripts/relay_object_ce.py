"""Relay-2x2 prereg §5 (2026-10-13): did a model learn the lookup? Mean cross-entropy (bits) at OBJECT target
positions against the r1R corpus's relay values, with inputs from INPUTS (r1 for r1Rs, r1R for r1R), over the
first N test windows. The ideal observer pays 0 bits: the relay value is a function of the preceding tokens.

  uv run --extra learner python scripts/relay_object_ce.py --inputs CORPUS --runs RUN... [--n 20000]
"""
import argparse
import json

import numpy as np
import torch
import torch.nn.functional as F

from yupi.learner.checkpoint import load
from yupi.learner.data import load_split, paired_targets, unscore_fields
from yupi.learner.model import Decoder, ModelConfig

R1R = "corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--n", type=int, default=20000)
    a = ap.parse_args()
    X, Y, M, _ = load_split(a.inputs, "test")
    _, Y2, M2, _ = load_split(R1R, "test")
    X, Y, M, Y2, M2 = X[:a.n], Y[:a.n], M[:a.n], Y2[:a.n], M2[:a.n]
    T = Y2 if a.inputs.rstrip("/") == R1R else paired_targets(Y, M, Y2, M2, ("OBJECT",))
    obj = ~unscore_fields([T[i, :M[i].sum() - 1] for i in range(len(T))], M, ("OBJECT",)) & M
    for d in a.runs:
        ck = load(d)
        m = Decoder(ModelConfig(**ck["config"]["model"])); m.load_state_dict(ck["model"]); m.eval()
        tot, cnt = 0.0, 0
        with torch.no_grad():
            for i in range(0, len(X), 2000):
                ce = F.cross_entropy(m(torch.from_numpy(X[i:i + 2000])).transpose(1, 2), torch.from_numpy(T[i:i + 2000]),
                                     reduction="none").numpy() / np.log(2)
                sel = obj[i:i + 2000]
                tot += float(ce[sel].sum()); cnt += int(sel.sum())
        print(json.dumps({"run": d.rstrip("/").split("/")[-1], "inputs": a.inputs, "n_windows": len(X), "n_object": cnt,
                          "object_ce_bits_vs_relay": tot / cnt, "step": ck["step"]}), flush=True)


if __name__ == "__main__":
    main()
