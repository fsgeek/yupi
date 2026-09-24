"""Belief geometry, coordinate-free (design docs/superpowers/specs/2026-09-24-belief-geometry-design.md v0.1):
does the residual stream at the record boundary p0 linearly carry the exact next-kind belief
P*(kind_{k+1} | prefix), and how does what is there compare with what the model emits there?

  uv run --extra learner python scripts/learner_belief_kind.py --run <run dir> --k 7 [--tables-dir ...] \\
      [--fit-from 30000] [--eval-n 30000] [--device cpu] [--l2 1e-4,1e-3,1e-2,1e-1] \\
      --raw docs/learner-belief-kind-<cell>-seed<s>-<date>.json

Per layer 0..4: an affine probe from the residual at p0 to logits over the 9 kinds, fit
against the exact soft target on test windows [fit-from, end) and evaluated on the first
eval-n test windows: CE, H(Z), H(Z | h), OIR; KL_repr = mean per-window KL(P* || probe); beside
it KL_out = mean KL(P* || P_M(kind | non-PAD) at p0) (the evaluator's kind_kl_bits, recomputed
from the same forward pass; its eval-set mean is the gate against the run's learner-eval raw);
their per-window Spearman; both by H*(kind) bins; a class-disjoint evaluation (eval windows
whose class is absent from the fit set); and the geometry item: Spearman between pairwise
Euclidean distances of exact beliefs and of probe outputs on a sample of eval windows.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import KINDS, VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.data import frame
from yupi.learner.evaluate import kind_belief, kind_output, kl_bits_vec, surface_records
from yupi.learner.model import Decoder, ModelConfig
from yupi.learner.probe import fit_probe, oir, probe_ce, probe_logq
from yupi.naming import pattern_all
from yupi.pattern_ceiling import load_table

N_LAYERS = 5


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def _rank(x):
    order = np.argsort(x, kind="stable"); r = np.empty(len(x)); r[order] = np.arange(len(x))
    return r


def spearman(x, y):
    x, y = _rank(np.asarray(x)), _rank(np.asarray(y))
    x = x - x.mean(); y = y - y.mean()
    d = float(np.sqrt((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / d) if d > 0 else None


def entropy_bits(p):
    p = np.asarray(p); p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def pairwise_distance_alignment(P, Q, n=1000, seed=0):
    """Spearman between pairwise Euclidean distances of rows of P and of Q on a sample of n rows."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(P), size=min(n, len(P)), replace=False)
    A, B = P[idx], Q[idx]
    iu = np.triu_indices(len(idx), 1)
    da = np.sqrt(((A[:, None, :] - A[None, :, :]) ** 2).sum(-1))[iu]
    db = np.sqrt(((B[:, None, :] - B[None, :, :]) ** 2).sum(-1))[iu]
    return spearman(da, db)


def collect(model, rows, table, k, seq_len, device, batch=1024):
    """For every window with >= k+1 records and a table class: (index, class key, P*(kind),
    hidden[L] at p0, KL_out, off-kind mass)."""
    sel = []
    for i, (w, _) in enumerate(rows):
        reset, recs = surface_records(tuple(VOCAB[t] for t in w))
        if len(recs) < k + 1:
            continue
        pw, _ = pattern_all(recs[:k]); key = (reset, pw)
        e = table.get(key)
        if e is None:
            continue
        sel.append((i, key, kind_belief(e[1]), (1 if reset else 0) + 5 * k, w))
    H = [[] for _ in range(N_LAYERS)]; kl_out = []; off = []
    model.eval()
    with torch.no_grad():
        for b0 in range(0, len(sel), batch):
            chunk = sel[b0:b0 + batch]
            x, _, _ = frame([tuple(c[4]) for c in chunk], seq_len)
            logits, hidden = model(torch.from_numpy(x).to(device), return_hidden=True)
            lp = torch.log_softmax(logits, dim=-1).cpu().numpy()
            pp = torch.tensor([c[3] for c in chunk], device=device); ar = torch.arange(len(chunk), device=device)
            for L in range(N_LAYERS):
                H[L].append(hidden[L][ar, pp].double().cpu().numpy())
            for j, c in enumerate(chunk):
                q, o = kind_output(lp[j, c[3]])
                kl_out.append(kl_bits_vec(c[2], q)); off.append(o)
    return (np.array([c[0] for c in sel]), [c[1] for c in sel], np.array([c[2] for c in sel]),
            [np.concatenate(h, 0) for h in H], np.array(kl_out), np.array(off))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--tables-dir", default=str(Path.home() / ".cache/yupi-scratch/ceilings"))
    ap.add_argument("--split", default="test")
    ap.add_argument("--fit-from", type=int, default=30000)
    ap.add_argument("--eval-n", type=int, default=30000)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--l2", default="1e-4,1e-3,1e-2,1e-1")
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    t0 = time.time()
    run = Path(a.run); run_json = json.loads((run / "run.json").read_text())
    m = Manifest.from_json(json.loads((Path(run_json["corpus_dir"]) / "manifest.json").read_text())); law = m.law()
    fn = Path(a.tables_dir) / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{m.epsilon.replace('/', '_')}-k{a.k}.jsonl"
    table = load_table(fn)
    rows = read_split(run_json["corpus_dir"], a.split)
    ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
    model = Decoder(ModelConfig(**run_json["model"])).to(a.device); model.load_state_dict(ck["model"])
    seq_len = run_json["model"]["n_pos"]
    idx, keys, P, H, kl_out, off = collect(model, rows, table, a.k, seq_len, a.device)
    fit = idx >= a.fit_from; ev = idx < a.eval_n
    fit_keys = {keys[j] for j in np.where(fit)[0]}
    disjoint = np.array([ev[j] and keys[j] not in fit_keys for j in range(len(idx))])
    Pe = P[ev]; h_z = entropy_bits(Pe.mean(0)); h_z_h = float(np.mean([entropy_bits(p) for p in Pe]))
    h_star = np.array([entropy_bits(p) for p in Pe])
    cuts = [0.0, 0.5, 1.0, 1.5, 2.0, 3.2]
    l2s = [float(x) for x in a.l2.split(",")]
    rng = np.random.default_rng(0)
    nf = int(fit.sum()); perm = rng.permutation(nf); hold, tr = perm[:nf // 5], perm[nf // 5:]
    results = {}
    out_bins = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        mm = (h_star >= lo) & (h_star < hi)
        if mm.sum() >= 50:
            out_bins.append(dict(h_range=[lo, hi], n=int(mm.sum()), kl_out=float(kl_out[ev][mm].mean())))
    for L in range(N_LAYERS):
        A_f, A_e = H[L][fit], H[L][ev]
        best = None
        for l2 in l2s:
            pr = fit_probe(A_f[tr], P[fit][tr], l2=l2)
            ce_h = probe_ce(pr, A_f[hold], P[fit][hold])
            if best is None or ce_h < best[0]:
                best = (ce_h, l2)
        pr = fit_probe(A_f, P[fit], l2=best[1])
        ce = probe_ce(pr, A_e, Pe)
        Q = np.exp(probe_logq(pr, A_e))
        kl_repr = np.array([kl_bits_vec(p, q) for p, q in zip(Pe, Q)])
        bins = []
        for lo, hi in zip(cuts[:-1], cuts[1:]):
            mm = (h_star >= lo) & (h_star < hi)
            if mm.sum() >= 50:
                bins.append(dict(h_range=[lo, hi], n=int(mm.sum()), kl_repr=float(kl_repr[mm].mean()), kl_out=float(kl_out[ev][mm].mean()),
                                 h_star=float(h_star[mm].mean()), h_probe=float(np.mean([entropy_bits(q) for q in Q[mm]]))))
        dj = disjoint[ev]
        res = dict(layer=L, n_fit=nf, n_eval=int(ev.sum()), l2=best[1], holdout_ce=best[0], ce=ce, h_z=h_z, h_z_given_h=h_z_h,
                   oir=oir(ce, h_z, h_z_h), kl_repr=float(kl_repr.mean()), kl_repr_se=float(kl_repr.std(ddof=1) / math.sqrt(len(kl_repr))),
                   kl_out=float(kl_out[ev].mean()), spearman_repr_out=spearman(kl_repr, kl_out[ev]),
                   h_probe=float(np.mean([entropy_bits(q) for q in Q])), h_model_out=None,
                   class_disjoint=dict(n=int(dj.sum()), ce=probe_ce(pr, A_e[dj], Pe[dj]), kl_repr=float(kl_repr[dj].mean()), kl_out=float(kl_out[ev][dj].mean()),
                                       oir=oir(probe_ce(pr, A_e[dj], Pe[dj]), entropy_bits(Pe[dj].mean(0)), float(np.mean([entropy_bits(p) for p in Pe[dj]])))) if dj.sum() >= 50 else None,
                   geometry_alignment=pairwise_distance_alignment(Pe, Q), by_h_star=bins)
        results[f"L{L}"] = res
        f = lambda v: "—" if v is None else f"{v:.3f}"
        print(f"layer {L}: n_fit={nf} n_eval={int(ev.sum())}  H(Z)={h_z:.3f} H(Z|h)={h_z_h:.3f}  CE={ce:.3f}  OIR={f(res['oir'])}  "
              f"KL_repr={res['kl_repr']:.4f}  KL_out={res['kl_out']:.4f}  ρ(repr,out)={f(res['spearman_repr_out'])}  geom={f(res['geometry_alignment'])}  "
              f"disjoint: n={res['class_disjoint']['n'] if res['class_disjoint'] else 0} OIR={f(res['class_disjoint']['oir']) if res['class_disjoint'] else '—'} KL_repr={f(res['class_disjoint']['kl_repr']) if res['class_disjoint'] else '—'}  λ={best[1]:g}", flush=True)
    out = dict(run=str(run), step=ck["step"], seed=run_json["seed"], rung=m.rung, eps=str(m.epsilon), k=a.k, split=a.split,
               fit_from=a.fit_from, eval_n=a.eval_n, table=str(fn), table_sha256=hashlib.sha256(fn.read_bytes()).hexdigest(),
               checkpoint_sha256=hashlib.sha256((run / "ckpt.pt").read_bytes()).hexdigest(), git=_git(), l2_grid=l2s,
               kinds=list(KINDS), off_kind_mass_mean=float(off[ev].mean()), kl_out_eval_mean=float(kl_out[ev].mean()),
               kl_out_by_h_star=out_bins, results=results, wall_s=time.time() - t0)
    print(f"KL_out eval mean {out['kl_out_eval_mean']:.4f} (gate: the run's learner-eval kind_kl_bits at k={a.k} over the same windows)  off-kind mass {out['off_kind_mass_mean']:.5f}")
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
