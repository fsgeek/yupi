"""Probe: lock ownership in the residual stream (design
docs/superpowers/specs/2026-09-23-probe-lock-owner-design.md, v0.1 + amendment v0.2).

  uv run --extra learner python scripts/learner_probe_owner.py --run <run dir> --k 7 \\
      --labels-fit ~/.cache/yupi-scratch/probes/<name>-k7-val.jsonl \\
      --labels-eval ~/.cache/yupi-scratch/probes/<name>-k7-test.jsonl \\
      [--readout linear|bilinear] [--device cpu] [--l2 1e-4,1e-3,1e-2,1e-1] \\
      --raw docs/learner-probe-owner-<cell>-seed<s>[-bilinear]-<date>.json

Per (layer 0..4, lock index l): a probe from the residual stream at position
p0 (the state after k records) to the owner, fit on the fit split's windows
against the exact posterior (soft labels; λ chosen on a held-out fifth of the
fit split), evaluated on the eval split: CE(Z|A), H(Z), H(Z|h), OIR, argmax
accuracy vs the posterior argmax, and CE on the determined (H(Z|h) = 0) and
uncertain subsets.
  linear    (v0.1) affine map to the pattern classes {none, t0..t3, unseen};
            H(Z) = entropy of the eval-set marginal (the constant probe).
  bilinear  (v0.2) the owner as a thread TOKEN read through the model's token
            embedding: logit(τ) = hᵀ W E_τ + b_tok over the prefix's thread tokens,
            plus learned directions for none / unseen; H(Z) = CE of the same
            family fit with no activation (biases only).
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch

from yupi.corpus.vocab import VOCAB, token_type
from yupi.corpus.writer import read_split
from yupi.learner.data import frame
from yupi.learner.model import Decoder, ModelConfig
from yupi.learner.probe import CLASSES, CLASS_ID, bilinear_ce, bilinear_logq, fit_bilinear, fit_probe, oir, probe_ce, probe_logq

N_LAYERS = 5


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def load_labels(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines()]


def hidden_states(model, split_rows, rows, seq_len, device, batch=1024):
    """[N_layers][n_rows, d] residual stream at each row's p0."""
    windows = [tuple(split_rows[r["i"]][0]) for r in rows]
    p0 = np.array([r["p0"] for r in rows])
    out = [[] for _ in range(N_LAYERS)]
    model.eval()
    with torch.no_grad():
        for b0 in range(0, len(windows), batch):
            x, _, _ = frame(windows[b0:b0 + batch], seq_len)
            _, hidden = model(torch.from_numpy(x).to(device), return_hidden=True)
            pp = torch.from_numpy(p0[b0:b0 + batch]).to(device)
            ar = torch.arange(len(pp), device=device)
            for L in range(N_LAYERS):
                out[L].append(hidden[L][ar, pp].double().cpu().numpy())
    return [np.concatenate(o, 0) for o in out]


def examples(rows, l):
    """(row indices, posterior matrix over CLASSES) for lock index l where visible."""
    idx, P = [], []
    for j, r in enumerate(rows):
        d = r["locks"].get(str(l))
        if not d:
            continue
        p = np.zeros(len(CLASSES))
        for z, q in d.items():
            p[CLASS_ID[z]] = float(Fraction(q))
        idx.append(j); P.append(p)
    return np.array(idx), np.array(P)


def thread_order(window_ids, k, reset):
    """Thread token ids of the first k records in first-appearance order (actor before related)."""
    off = 1 if reset else 0
    seen = []
    for j in range(k):
        rec = window_ids[off + 5 * j: off + 5 * j + 5]
        for pos in (1, 3):
            t = rec[pos]
            if token_type(VOCAB[t]) == "thread" and t not in seen:
                seen.append(t)
    return seen


def to_candidates(rows, split_rows, idx, P):
    """Per example: candidates [None, 'unseen', tok_t0, tok_t1, ...] and the posterior re-indexed onto them."""
    cands, Pc = [], []
    for j, p in zip(idx, P):
        r = rows[j]
        toks = thread_order(split_rows[r["i"]][0], r["k"], r["reset"])
        c = [None, "unseen"] + toks
        q = np.zeros(len(c))
        q[0] = p[CLASS_ID["none"]]; q[1] = p[CLASS_ID["unseen"]]
        for i, t in enumerate(toks):
            q[2 + i] = p[CLASS_ID[f"t{i}"]]
        for i in range(len(toks), 4):
            assert p[CLASS_ID[f"t{i}"]] == 0.0, "posterior mass on a thread index beyond the seen threads"
        cands.append(c); Pc.append(q)
    return cands, Pc


def entropy_bits(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def sub(seq, sel):
    """Subset of a list by a boolean mask or an index array."""
    sel = np.asarray(sel)
    idx = np.where(sel)[0] if sel.dtype == bool else sel
    return [seq[i] for i in idx]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--labels-fit", required=True)
    ap.add_argument("--labels-eval", required=True)
    ap.add_argument("--fit-split", default="val")
    ap.add_argument("--eval-split", default="test")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--l2", default="1e-4,1e-3,1e-2,1e-1")
    ap.add_argument("--readout", default="linear", choices=("linear", "bilinear"))
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    run = Path(a.run)
    run_json = json.loads((run / "run.json").read_text())
    ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
    model = Decoder(ModelConfig(**run_json["model"])).to(a.device)
    model.load_state_dict(ck["model"])
    seq_len = run_json["model"]["n_pos"]
    fit_rows, eval_rows = load_labels(a.labels_fit), load_labels(a.labels_eval)
    assert all(r["k"] == a.k for r in fit_rows + eval_rows)
    fit_split_rows = read_split(run_json["corpus_dir"], a.fit_split)
    eval_split_rows = read_split(run_json["corpus_dir"], a.eval_split)
    t0 = time.time()
    H_fit = hidden_states(model, fit_split_rows, fit_rows, seq_len, a.device)
    H_eval = hidden_states(model, eval_split_rows, eval_rows, seq_len, a.device)
    E = model.tok.weight.detach().double().cpu().numpy()
    l2s = [float(x) for x in a.l2.split(",")]
    results = {}
    n_locks = max(int(l) for r in fit_rows + eval_rows for l in r["locks"]) + 1
    for l in range(n_locks):
        fi, Pf = examples(fit_rows, l)
        ei, Pe = examples(eval_rows, l)
        if len(fi) < 50 or len(ei) < 50:
            continue
        h_z_h = float(np.mean([entropy_bits(p) for p in Pe]))
        det = np.array([entropy_bits(p) == 0.0 for p in Pe])
        rng = np.random.default_rng(0)
        perm = rng.permutation(len(fi)); n_hold = len(fi) // 5
        hold, tr = perm[:n_hold], perm[n_hold:]
        if a.readout == "bilinear":
            Cf, Pfc = to_candidates(fit_rows, fit_split_rows, fi, Pf)
            Ce, Pec = to_candidates(eval_rows, eval_split_rows, ei, Pe)
            base = fit_bilinear(np.zeros((len(fi), 1)), Cf, Pfc, E, l2=0.0)      # same family, no activation
            h_z = bilinear_ce(base, np.zeros((len(ei), 1)), Ce, Pec, E)
        else:
            h_z = entropy_bits(Pe.mean(0))
        for L in range(N_LAYERS):
            A_f, A_e = H_fit[L][fi], H_eval[L][ei]
            best = None
            if a.readout == "bilinear":
                for l2 in l2s:
                    pr = fit_bilinear(A_f[tr], sub(Cf, tr), sub(Pfc, tr), E, l2=l2)
                    ce_h = bilinear_ce(pr, A_f[hold], sub(Cf, hold), sub(Pfc, hold), E)
                    if best is None or ce_h < best[0]:
                        best = (ce_h, l2)
                pr = fit_bilinear(A_f, Cf, Pfc, E, l2=best[1])
                ce = bilinear_ce(pr, A_e, Ce, Pec, E)
                lq = bilinear_logq(pr, A_e, Ce, E)
                acc = float(np.mean([lq[i, :len(Pec[i])].argmax() == np.argmax(Pec[i]) for i in range(len(ei))]))
                ce_det = bilinear_ce(pr, A_e[det], sub(Ce, det), sub(Pec, det), E) if det.any() else None
                ce_unc = bilinear_ce(pr, A_e[~det], sub(Ce, ~det), sub(Pec, ~det), E) if (~det).any() else None
            else:
                for l2 in l2s:
                    pr = fit_probe(A_f[tr], Pf[tr], l2=l2)
                    ce_h = probe_ce(pr, A_f[hold], Pf[hold])
                    if best is None or ce_h < best[0]:
                        best = (ce_h, l2)
                pr = fit_probe(A_f, Pf, l2=best[1])
                ce = probe_ce(pr, A_e, Pe)
                logq = probe_logq(pr, A_e)
                acc = float(np.mean(logq.argmax(1) == Pe.argmax(1)))
                ce_det = probe_ce(pr, A_e[det], Pe[det]) if det.any() else None
                ce_unc = probe_ce(pr, A_e[~det], Pe[~det]) if (~det).any() else None
            results[f"l{l}/L{L}"] = dict(lock=l, layer=L, n_fit=int(len(fi)), n_eval=int(len(ei)), l2=best[1], holdout_ce=best[0],
                                         ce=ce, h_z=h_z, h_z_given_h=h_z_h, oir=oir(ce, h_z, h_z_h), acc=acc,
                                         frac_determined=float(det.mean()), ce_determined=ce_det, ce_uncertain=ce_unc,
                                         h_z_given_h_uncertain=float(np.mean([entropy_bits(p) for p in Pe[~det]])) if (~det).any() else None)
    out = dict(run=str(run), step=ck["step"], seed=run_json["seed"], corpus=run_json["corpus_dir"], k=a.k,
               labels_fit=a.labels_fit, labels_fit_sha256=hashlib.sha256(Path(a.labels_fit).read_bytes()).hexdigest(),
               labels_eval=a.labels_eval, labels_eval_sha256=hashlib.sha256(Path(a.labels_eval).read_bytes()).hexdigest(),
               checkpoint_sha256=hashlib.sha256((run / "ckpt.pt").read_bytes()).hexdigest(), git=_git(),
               classes=list(CLASSES), l2_grid=l2s, readout=a.readout, results=results, wall_s=time.time() - t0)
    fmt = lambda v: "—" if v is None else f"{v:.3f}"
    print(f"run {run.name} k={a.k} readout={a.readout}: {len(fit_rows)} fit / {len(eval_rows)} eval windows")
    for r in results.values():
        print(f"  lock {r['lock']} layer {r['layer']}: n={r['n_eval']}  H(Z)={r['h_z']:.3f}  H(Z|h)={r['h_z_given_h']:.3f}  "
              f"CE={r['ce']:.3f}  OIR={fmt(r['oir'])}  acc={r['acc']:.3f}  det {r['frac_determined']:.2f}: CE {fmt(r['ce_determined'])}  "
              f"unc: CE {fmt(r['ce_uncertain'])} vs H {fmt(r['h_z_given_h_uncertain'])}  λ={r['l2']:g}")
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
