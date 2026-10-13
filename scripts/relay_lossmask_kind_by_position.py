"""EXPLORATORY (2026-10-13), relay-lossmask verdict §4: raw next-KIND cross-entropy (bits) by record position, on the
same first 20,000 r1R test windows, for r1R and r1Rm models. A finest-grain check of the census difference.
  uv run --extra learner python scripts/relay_lossmask_kind_by_position.py RUN_DIR... > docs/relay-lossmask-kind-by-position-2026-10-13.jsonl"""
import sys, json, numpy as np, torch, torch.nn.functional as F
from yupi.learner.model import Decoder, ModelConfig
from yupi.learner.data import load_split, RESET_ID
from yupi.learner.checkpoint import load
C = "corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d"
X, Y, M, _ = load_split(C, "test")
N = 20000; X, Y, M = X[:N], Y[:N], M[:N]
L = M.sum(1) - 1
off = (Y[:, 0] == RESET_ID).astype(int)
def run(d):
    ck = load(d); cfg = ck["config"]["model"]
    m = Decoder(ModelConfig(**cfg)); m.load_state_dict(ck["model"]); m.eval()
    out = np.zeros((N, X.shape[1]))
    with torch.no_grad():
        for i in range(0, N, 2000):
            lg = m(torch.from_numpy(X[i:i+2000]))
            ce = F.cross_entropy(lg.transpose(1, 2), torch.from_numpy(Y[i:i+2000]), reduction="none")
            out[i:i+2000] = ce.numpy() / np.log(2)
    res = {}
    for r in range(8):
        j = off + 5 * r
        ok = j < L
        res[r] = float(out[np.arange(N)[ok], j[ok]].mean())
    return res
for d in sys.argv[1:]:
    print(json.dumps({"run": d.split("/")[-1], "kind_ce_bits_by_record": run(d), "n_windows": N}), flush=True)
