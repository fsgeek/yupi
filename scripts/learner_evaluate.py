"""Evaluate a trained run against the prefix ceiling tables (contract v0.1.2;
plan Task 7).

  uv run --extra learner python scripts/learner_evaluate.py --run <run dir> \\
      [--tables-dir ~/.cache/yupi-scratch/ceilings] [--k 1,2,3,4,5,6,7] [--n N] [--device cpu] \\
      --raw docs/learner-eval-<cell>-seed<s>-<date>.json

Refuses a table whose law, rung or ε differ from the run's corpus, or a
missing table file. Records the git commit, the checkpoint's sha256 and each
table's sha256 in the raw. Per k: n, mean, sd, se of structural / naming /
token / kind-KL / end excess (bits), missing classes, too-short windows.
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
from yupi.learner.evaluate import evaluate, torch_logprobs_fn
from yupi.learner.model import Decoder, ModelConfig
from yupi.pattern_ceiling import load_table


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--tables-dir", default=os.path.expanduser("~/.cache/yupi-scratch/ceilings"))
    ap.add_argument("--k", default="1,2,3,4,5,6,7")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--split", default="test")
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    run = Path(a.run)
    run_json = json.loads((run / "run.json").read_text())
    m = Manifest.from_json(json.loads((Path(run_json["corpus_dir"]) / "manifest.json").read_text()))
    law = m.law()
    k_list = tuple(int(k) for k in a.k.split(","))
    tables, shas = {}, {}
    for k in k_list:
        fn = Path(a.tables_dir) / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{m.epsilon.replace('/', '_')}-k{k}.jsonl"
        if not fn.exists():
            raise SystemExit(f"refused: prefix table {fn} is missing")
        tables[k] = load_table(fn)
        shas[str(k)] = hashlib.sha256(fn.read_bytes()).hexdigest()
    ck = torch.load(run / "ckpt.pt", weights_only=False, map_location="cpu")
    model = Decoder(ModelConfig(**run_json["model"])).to(a.device)
    model.load_state_dict(ck["model"])
    t0 = time.time()
    r = evaluate(torch_logprobs_fn(model, a.device), run_json["corpus_dir"], law, tables, k_list,
                 run_json["model"]["n_pos"], n=a.n, split=a.split)
    r.update(run=str(run), step=ck["step"], seed=run_json["seed"], corpus=run_json["corpus_dir"], rung=m.rung,
             eps=m.epsilon, law=dict(T_ep=law.T_ep, L=law.L, B=law.B), programs=m.programs, git=_git(),
             checkpoint_sha256=hashlib.sha256((run / "ckpt.pt").read_bytes()).hexdigest(), table_sha256=shas,
             wall_s=time.time() - t0, split=a.split)
    for k in k_list:
        pk = r["per_k"][k]
        s, nm, kk = pk["structural_bits"], pk["naming_bits"], pk["kind_kl_bits"]
        print(f"k={k}: n={s['n']} structural {s['mean']:.4f} ± {s['se']:.4f}  naming {nm['mean']:.4f} ± {nm['se']:.4f}  "
              f"kindKL {kk['mean']:.4f}  end {pk['end_bits']['mean']:.4f}  missing {pk['missing_classes']}", flush=True)
    print(f"final end-of-window excess {r['final_end_bits']['mean']:.4f} ± {r['final_end_bits']['se']:.4f}")
    if a.raw:
        Path(a.raw).write_text(json.dumps(r, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
