"""The window census: the per-window distribution behind one cell's mean
excess at prefix length k (contract v0.1.2 evaluator; yupi.learner.census).

  uv run --extra learner python scripts/learner_window_census.py --run <run dir> [--k 7] \\
      [--tables-dir ~/.cache/yupi-scratch/ceilings] [--device cpu] [--n N] [--top 20] \\
      [--per-window ~/.cache/yupi-scratch/census/<run>-k<k>-<split>.jsonl] \\
      --raw docs/learner-window-census-<cell>-seed<s>-<date>.json

One evaluator pass at the one k. The rung is the corpus manifest's: at the relay
rung r1ʀ ("r1R") the OBJECT slot's term is by_field "relay" (relay pre-registration
v0.1), separate from "kind"; at r0–r4 the per-window file is unchanged. Every scored window's excess (structural,
by field, naming) and its ceiling-table class go to the per-window file
(cache, sha256 recorded in the raw); the raw carries the summary: mean
(must equal the cell's learner-eval raw), quantiles, negative share, the
share of the total carried by the top 1/5/10 % of windows, the classes
ordered by summed excess, and the worst windows rendered as records.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import torch

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.interfaces import Lit
from yupi.learner.census import summarize
from yupi.learner.evaluate import evaluate, surface_records, torch_logprobs_fn
from yupi.learner.model import Decoder, ModelConfig
from yupi.pattern_ceiling import load_table


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def _ent(v):
    if v is None:
        return "-"
    if v == "MASKED":
        return "#"
    if isinstance(v, Lit):                       # the relay rung's literal (a KIND name)
        return f"<{v.kind}>"
    if isinstance(v, tuple):
        return f"{v[0][0]}{v[1]}" if isinstance(v[1], int) else str(v[1])
    return f"t{v}" if isinstance(v, int) else str(v)


def class_label(key) -> str:
    """Compact rendering of a ceiling-table key (reset flag, pattern prefix)."""
    reset, pw = key
    parts = ["R"] if reset else []
    for r in pw:
        s = f"{r.kind}/{_ent(r.actor)}"
        if r.obj is not None and r.obj != "MASKED":
            s += f"/{_ent(r.obj)}"
        if r.related not in (None, "MASKED"):
            s += f"/r={_ent(r.related)}"
        if r.lineage not in (None, "MASKED"):
            s += f"/l={_ent(r.lineage)}"
        parts.append(s)
    return " ".join(parts)


def _third(by_field):
    """The OBJECT slot's term for the printout: "obj" at r0–r4, "relay" at r1R."""
    name = "relay" if "relay" in by_field else "obj"
    return f"{name} {by_field[name]:.2f}"


def render_window(toks, k, rung=None):
    """The window's records as strings, the (k+1)-th marked as the one predicted."""
    reset, recs = surface_records(toks, rung)
    out = ["RESET"] if reset else []
    for j, r in enumerate(recs):
        s = f"{r.kind} {_ent(r.actor)} {_ent(r.obj)} {_ent(r.related)} {_ent(r.lineage)}"
        out.append(("> " if j == k else "  ") + s)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--tables-dir", default=os.path.expanduser("~/.cache/yupi-scratch/ceilings"))
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--split", default="test")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--per-window", default=None)
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    run = Path(a.run)
    run_json = json.loads((run / "run.json").read_text())
    corpus_dir = Path(run_json["corpus_dir"])
    m = Manifest.from_json(json.loads((corpus_dir / "manifest.json").read_text()))
    law = m.law()
    k = a.k
    fn = Path(a.tables_dir) / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{m.epsilon.replace('/', '_')}-k{k}.jsonl"
    if not fn.exists():
        raise SystemExit(f"refused: prefix table {fn} is missing")
    table = load_table(fn)
    table_sha = hashlib.sha256(fn.read_bytes()).hexdigest()
    ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
    model = Decoder(ModelConfig(**run_json["model"])).to(a.device)
    model.load_state_dict(ck["model"])

    rows, keys, class_ids = [], {}, []
    def on_window(i, kk, key, ex):
        cid = keys.setdefault(key, len(keys))
        rows.append(dict(i=i, key=cid, structural=ex["structural_bits"], naming=ex["naming_bits"],
                         by_field=ex["structural_by_field"]))

    t0 = time.time()
    r = evaluate(torch_logprobs_fn(model, a.device), str(corpus_dir), law, {k: table}, (k,),
                 run_json["model"]["n_pos"], n=a.n, split=a.split, on_window=on_window, rung=m.rung)
    labels = {cid: class_label(key) for key, cid in keys.items()}
    s = summarize(rows, top=a.top)
    for c in s["classes"]:
        c["label"] = labels[c["key"]]
    split_rows = read_split(corpus_dir, a.split)
    for w in s["worst"]:
        toks, tab = split_rows[w["i"]]
        toks = tuple(VOCAB[t] for t in toks)
        w["label"] = labels[w["key"]]
        w["episode"], w["T"], w["U"] = tab["episode"], tab["T"], tab["U"]
        w["records"] = render_window(toks, k, m.rung)

    per_window = a.per_window or os.path.expanduser(f"~/.cache/yupi-scratch/census/{run.name}-k{k}-{a.split}.jsonl")
    Path(per_window).parent.mkdir(parents=True, exist_ok=True)
    with open(per_window, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    pk = r["per_k"][k]
    out = dict(run=str(run), step=ck["step"], seed=run_json["seed"], corpus=str(corpus_dir), rung=m.rung, eps=m.epsilon,
               law=dict(T_ep=law.T_ep, L=law.L, B=law.B), programs=m.programs, k=k, split=a.split, n=a.n, git=_git(),
               checkpoint_sha256=hashlib.sha256((run / "ckpt.pt").read_bytes()).hexdigest(), table_sha256=table_sha,
               aggregate=dict(structural=pk["structural_bits"], missing_classes=pk["missing_classes"], too_short=pk["too_short"]),
               per_window_file=per_window, per_window_sha256=hashlib.sha256(Path(per_window).read_bytes()).hexdigest(),
               classes_labels={str(cid): lab for cid, lab in labels.items()} if len(labels) <= 5000 else None,
               summary=s, wall_s=time.time() - t0)
    print(f"k={k}: n={s['n']} mean {s['mean']:.4f} (aggregate {pk['structural_bits']['mean']:.4f})  sd {s['sd']:.3f}  "
          f"negative {s['negative_share']:.3f}  max {s['max']:.2f}")
    print("quantiles " + "  ".join(f"q{q}={v:.3f}" for q, v in s["quantiles"].items()))
    print("tail share " + "  ".join(f"top{float(p) * 100:g}%={v:.3f}" for p, v in s["tail_share"].items()))
    print(f"classes {s['n_classes']}; top by summed excess:")
    for c in s["classes"][:10]:
        print(f"  share {c['share']:.3f}  n {c['n']:6d}  mean {c['mean']:.3f} ± {c['se']:.3f}  "
              f"kind {c['by_field']['kind']:.2f} actor {c['by_field']['actor']:.2f} {_third(c['by_field'])}  {c['label']}")
    print("worst windows:")
    for w in s["worst"][:5]:
        print(f"  #{w['i']} ep {w['episode']} T={w['T']} excess {w['structural']:.2f} "
              f"(kind {w['by_field']['kind']:.2f} actor {w['by_field']['actor']:.2f} {_third(w['by_field'])})")
        for line in w["records"]:
            print("     " + line)
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
