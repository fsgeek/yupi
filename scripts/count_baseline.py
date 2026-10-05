"""The canonicalize-and-count KIND baseline on one cell (docs/count-baseline-design-v0.1.md).

  uv run --extra learner python scripts/count_baseline.py --corpus corpus/<cell>/<id> \\
      --raw docs/count-baseline-<cell>-<date>.json [--per-window ~/.cache/yupi-scratch/census/count-<cell>-k7-test.jsonl]

Counts come from `train` only. The prediction mode (wb, or add-α for α in ALPHAS) is chosen on `val` by mean KIND
excess (by_field.kind) at k = 7, then frozen. Test: evaluate() at k = 1..7, plus a k = 7 per-window file in the
census format ({i, key, structural, naming, by_field}). ONLY by_field.kind and kind_kl_bits are meaningful for
this learner, and the raw says so.
"""
import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import numpy as np

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.count_baseline import CountKind
from yupi.learner.evaluate import evaluate
from yupi.pattern_ceiling import load_table

TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
ALPHAS = (0.05, 0.2, 0.5, 1.0)
SEQ = 42


def table_path(m, k):
    law = m.law()
    return TABLES / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{m.epsilon.replace('/', '_')}-k{k}.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--per-window", default=None)
    ap.add_argument("--max-order", type=int, default=6)
    a = ap.parse_args()
    d = Path(a.corpus)
    m = Manifest.from_json(json.loads((d / "manifest.json").read_text()))
    law = m.law()
    t0 = time.time()
    model = CountKind(rung=m.rung, max_order=a.max_order)
    n_train = 0
    for w, _ in read_split(d, "train"):
        model.add_window(tuple(VOCAB[t] for t in w))
        n_train += 1
    t_train = time.time() - t0
    tabs, shas = {}, {}
    for k in range(1, 8):
        fn = table_path(m, k)
        if not fn.exists():
            raise SystemExit(f"refused: table {fn} missing")
        tabs[k], shas[k] = load_table(fn), hashlib.sha256(fn.read_bytes()).hexdigest()

    val = {}
    for mode, alpha in [("wb", None)] + [("add", al) for al in ALPHAS]:
        if alpha is not None:
            model.alpha = alpha
        r = evaluate(model.logprobs_fn(mode), str(d), law, {7: tabs[7]}, (7,), SEQ, split="val", rung=m.rung)
        val[f"{mode}" + (f"-{alpha}" if alpha is not None else "")] = r["per_k"][7]["structural_by_field"]["kind"]["mean"]
    best = min(val, key=val.get)
    mode = best.split("-")[0]
    if mode == "add":
        model.alpha = float(best.split("-")[1])
    print(f"val KIND excess at k=7: { {k: round(v, 5) for k, v in val.items()} } -> {best}", flush=True)

    rows, keys = [], {}

    def on_window(i, kk, key, ex):
        if kk == 7:
            rows.append(dict(i=i, key=keys.setdefault(key, len(keys)), structural=ex["structural_bits"],
                             naming=ex["naming_bits"], by_field=ex["structural_by_field"]))

    r = evaluate(model.logprobs_fn(mode), str(d), law, tabs, tuple(range(1, 8)), SEQ, split="test",
                 on_window=on_window, rung=m.rung)
    pw = a.per_window or os.path.expanduser(f"~/.cache/yupi-scratch/census/count-{d.parent.name}-k7-test.jsonl")
    Path(pw).parent.mkdir(parents=True, exist_ok=True)
    with open(pw, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    kind7 = np.array([row["by_field"]["kind"] for row in rows])
    full7 = {key for key in keys}
    unseen = sum(1 for key in full7 if model.full.get(key) is None)
    out = dict(status="EXPLORATORY baseline (docs/count-baseline-design-v0.1.md); ONLY by_field.kind and kind_kl_bits "
                      "are meaningful for this learner",
               corpus=str(d), rung=m.rung, eps=m.epsilon, git=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                                                          text=True).stdout.strip(),
               table_sha256={str(k): v for k, v in shas.items()}, max_order=a.max_order, val_kind_excess_k7=val,
               chosen=best, n_train_windows=n_train,
               n_full_classes=len(model.full), n_suffix_classes=len(model.suffix),
               test_k7=dict(n=int(len(kind7)), kind_mean=float(kind7.mean()),
                            kind_se=float(kind7.std(ddof=1) / np.sqrt(len(kind7))),
                            classes=len(full7), classes_unseen_in_train=unseen),
               per_k={str(k): dict(kind=v["structural_by_field"]["kind"], kind_kl_bits=v["kind_kl_bits"],
                                   missing_classes=v["missing_classes"]) for k, v in r["per_k"].items()},
               per_window_file=pw, per_window_sha256=hashlib.sha256(Path(pw).read_bytes()).hexdigest(),
               wall_s=dict(train=t_train, total=time.time() - t0))
    json.dump(out, open(a.raw, "w"), indent=1)
    print(f"test k=7 KIND excess {out['test_k7']['kind_mean']:.5f} ± {out['test_k7']['kind_se']:.5f}  "
          f"classes {len(full7)} unseen {unseen}  train {t_train:.0f}s total {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
