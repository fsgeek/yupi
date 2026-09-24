"""Shape of the model's actor distribution where the owner is uncertain (first-results
note §18.5 (a), 2026-09-24): on labelled windows whose realized record k + 1 has kind K
(default RELEASE), compare the model's distribution over the actor at the position after
the kind token with the ceiling's P*(actor | K, prefix). Splits are functions of the
PREFIX only (a split on the realized record's lock selects on an outcome correlated
with the actor and biases realized-record estimates; §18 correction): by H*(actor | K)
bins, and by whether every lock visible in the prefix has a prefix-determined owner
(§16 labels: "all-determined") or some lock's owner is uncertain ("some-uncertain").

  uv run --extra learner python scripts/learner_actor_shape.py --run <run dir> --k 7 \\
      --labels ~/.cache/yupi-scratch/probes/<name>-k7-test.jsonl [--kind RELEASE] [--device cpu] \\
      --raw docs/learner-actor-shape-<cell>-seed<s>-<date>.json

Per window: KL(P* || P~) in bits over the pattern actor classes {seen threads, fresh};
H(P*), H(P~); whether the argmaxes agree; the mass each puts on the actor of record k
(the most recent actor) and on the exact argmax; the model's off-thread mass; and the
realized-record estimate log2 P*(a) − log2 P~(a) beside the exact KL (they agree in
expectation only on prefix-defined subsets). Means per group, the entropy
calibration (mean H(P~) − H(P*)), and the KL binned by H(P*).
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np
import torch

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import TOKEN_ID, VOCAB, token_type
from yupi.corpus.writer import read_split
from yupi.learner.data import frame
from yupi.learner.evaluate import actor_pattern_dist, model_actor_dist, surface_records
from yupi.learner.model import Decoder, ModelConfig
from yupi.naming import pattern_all
from yupi.pattern_ceiling import load_table


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def owner_entropy(label_row, l):
    d = label_row["locks"].get(str(l))
    if not d:
        return None
    ps = [float(Fraction(q)) for q in d.values()]
    return float(-sum(p * math.log2(p) for p in ps if p > 0))


def prefix_owner_state(label_row):
    """'all-determined' if every lock visible in the prefix has H(owner | prefix) = 0,
    'some-uncertain' otherwise, 'no-lock' if none is visible. A function of the prefix."""
    hs = [owner_entropy(label_row, int(l)) for l in label_row["locks"]]
    if not hs:
        return "no-lock"
    return "all-determined" if all(h == 0.0 for h in hs) else "some-uncertain"


def seen_threads(recs, k):
    """Thread tokens of the first k records in first-appearance order (actor before related)."""
    seen = []
    for r in recs[:k]:
        for v in (r.actor, r.related):
            if isinstance(v, str) and token_type(v) == "thread" and v not in seen:
                seen.append(v)
    return seen


def ent(d):
    return float(-sum(float(q) * math.log2(float(q)) for q in d.values() if q > 0))


def kl_bits(p, q):
    tot = 0.0
    for k, pk in p.items():
        pk = float(pk)
        if pk > 0:
            qk = max(float(q.get(k, 0.0)), 1e-12)
            tot += pk * math.log2(pk / qk)
    return tot


def summarize(items):
    if not items:
        return None
    a = {k: np.array([it[k] for it in items], dtype=np.float64) for k in items[0]}
    n = len(items)
    out = dict(n=n, kl=float(a["kl"].mean()), kl_se=float(a["kl"].std(ddof=1) / math.sqrt(n)) if n > 1 else 0.0,
               h_exact=float(a["h_exact"].mean()), h_model=float(a["h_model"].mean()),
               argmax_agree=float(a["agree"].mean()), realized_estimate=float(np.nanmean(a["realized"])),
               realized_is_top=float(a["realized_is_top"].mean()), mass_recent_exact=float(a["recent_exact"].mean()),
               mass_recent_model=float(a["recent_model"].mean()), mass_on_exact_argmax_model=float(a["top_model"].mean()),
               mass_on_exact_argmax_exact=float(a["top_exact"].mean()), off_thread=float(a["off"].mean()))
    cuts = [0.0, 0.5, 1.0, 1.5, 2.1]
    bins = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        m = (a["h_exact"] >= lo) & (a["h_exact"] < hi)
        if m.sum() >= 20:
            bins.append(dict(h_exact_range=[lo, hi], n=int(m.sum()), kl=float(a["kl"][m].mean()), h_exact=float(a["h_exact"][m].mean()),
                             h_model=float(a["h_model"][m].mean()), argmax_agree=float(a["agree"][m].mean())))
    out["by_h_exact"] = bins
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--kind", default="RELEASE")
    ap.add_argument("--tables-dir", default=str(Path.home() / ".cache/yupi-scratch/ceilings"))
    ap.add_argument("--split", default="test")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    run = Path(a.run)
    run_json = json.loads((run / "run.json").read_text())
    m = Manifest.from_json(json.loads((Path(run_json["corpus_dir"]) / "manifest.json").read_text()))
    law = m.law()
    fn = Path(a.tables_dir) / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{m.epsilon.replace('/', '_')}-k{a.k}.jsonl"
    table = load_table(fn)
    labels = {}
    for line in Path(a.labels).read_text().splitlines():
        r = json.loads(line); labels[r["i"]] = r
    rows = read_split(run_json["corpus_dir"], a.split)
    seq_len = run_json["model"]["n_pos"]
    ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
    model = Decoder(ModelConfig(**run_json["model"])).to(a.device); model.load_state_dict(ck["model"]); model.eval()
    # select windows
    sel = []
    for i, (w, _) in enumerate(rows):
        if i not in labels:
            continue
        toks = tuple(VOCAB[t] for t in w)
        reset, recs = surface_records(toks)
        if len(recs) < a.k + 1:
            continue
        pw, _ = pattern_all(recs[:a.k])
        entry = table.get((reset, pw))
        if entry is None:
            continue
        rho = pattern_all(recs[:a.k + 1])[0][-1]
        if rho.kind != a.kind or rho.obj is None or rho.obj[0] != "LOCK":
            continue
        seen = seen_threads(recs, a.k)
        ex = actor_pattern_dist(entry[1], a.kind, len(seen))
        if not ex:
            continue
        state = prefix_owner_state(labels[i])
        off = 1 if reset else 0
        recent = recs[a.k - 1].actor
        recent_idx = seen.index(recent) if isinstance(recent, str) and recent in seen else None
        a_tok = recs[a.k].actor
        realized_cls = seen.index(a_tok) if isinstance(a_tok, str) and a_tok in seen else "fresh"
        sel.append((i, w, off + 5 * a.k + 1, seen, ex, state, recent_idx, realized_cls))
    groups = defaultdict(list)
    with torch.no_grad():
        for b0 in range(0, len(sel), 512):
            chunk = sel[b0:b0 + 512]
            x, _, _ = frame([tuple(c[1]) for c in chunk], seq_len)
            lp = torch.log_softmax(model(torch.from_numpy(x).to(a.device)), dim=-1).cpu().numpy()
            for j, (i, w, pos, seen, ex, state, recent_idx, realized_cls) in enumerate(chunk):
                md, off_mass = model_actor_dist(lp[j, pos], seen)
                top = max(ex, key=lambda k: ex[k])
                p_real = float(ex.get(realized_cls, 0.0))
                item = dict(kl=kl_bits(ex, md), h_exact=ent(ex), h_model=ent(md), agree=float(max(md, key=lambda k: md[k]) == top),
                            recent_exact=float(ex.get(recent_idx, 0.0)) if recent_idx is not None else 0.0,
                            recent_model=float(md.get(recent_idx, 0.0)) if recent_idx is not None else 0.0,
                            top_model=float(md.get(top, 0.0)), top_exact=float(ex[top]), off=off_mass,
                            realized=(math.log2(p_real) - math.log2(max(float(md.get(realized_cls, 0.0)), 1e-12))) if p_real > 0 else float("nan"),
                            realized_is_top=float(realized_cls == top))
                groups[state].append(item)
                groups["all"].append(item)
    out = dict(run=str(run), seed=run_json["seed"], rung=m.rung, eps=str(m.epsilon), k=a.k, kind=a.kind, labels=a.labels,
               labels_sha256=hashlib.sha256(Path(a.labels).read_bytes()).hexdigest(), table=str(fn),
               table_sha256=hashlib.sha256(fn.read_bytes()).hexdigest(), git=_git(), n_selected=len(sel),
               groups={g: summarize(v) for g, v in groups.items()})
    print(f"{run.name} {a.kind} k={a.k}: {len(sel)} windows")
    for g in ("all", "all-determined", "some-uncertain", "no-lock"):
        s = out["groups"].get(g)
        if not s:
            continue
        print(f"  {g:14s} n={s['n']:5d}  KL {s['kl']:.4f} ± {s['kl_se']:.4f} (realized est. {s['realized_estimate']:.4f}; realized==argmax {s['realized_is_top']:.3f} vs P* {s['mass_on_exact_argmax_exact']:.3f})  H* {s['h_exact']:.3f}  H~ {s['h_model']:.3f}  argmax agree {s['argmax_agree']:.3f}  "
              f"mass on recent actor: exact {s['mass_recent_exact']:.3f} model {s['mass_recent_model']:.3f}  on exact argmax: exact {s['mass_on_exact_argmax_exact']:.3f} model {s['mass_on_exact_argmax_model']:.3f}  off-thread {s['off_thread']:.4f}")
        for b in s["by_h_exact"]:
            print(f"      H* in [{b['h_exact_range'][0]:.1f}, {b['h_exact_range'][1]:.1f}): n={b['n']:5d}  KL {b['kl']:.4f}  H* {b['h_exact']:.3f}  H~ {b['h_model']:.3f}  agree {b['argmax_agree']:.3f}")
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
