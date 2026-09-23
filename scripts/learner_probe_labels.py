"""Exact lock-owner labels for the probe (design 2026-09-23 §Target Z): per
window of a split and prefix length k, the posterior over the owner of each
visible lock, computed once per pattern class in parallel and shared across
windows (and across every seed of the cell).

  uv run python scripts/learner_probe_labels.py --corpus-dir corpus/<name>/<rid> --k 7 --split val \\
      [--n N] [--workers 60] --out ~/.cache/yupi-scratch/probes/<name>-k7-val.jsonl

Output: one JSON line per window that has >= k records: {"i", "k", "reset",
"p0" (input position of the state after k records), "locks": {l: {class: "p/q"}}}.
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.evaluate import surface_records
from yupi.learner.probe import label_window
from yupi.naming import pattern_all

_W = {}


def _init(corpus_dir, rung):
    m = Manifest.from_json(json.loads((Path(corpus_dir) / "manifest.json").read_text()))
    _W["cfg"], _W["progs"] = m.world()
    _W["law"] = m.law(); _W["rung"] = rung


def _one(item):
    key, beta = item
    reset, pw = key
    labels = label_window(_W["cfg"], _W["progs"], _W["law"], _W["rung"], reset, pw, beta)
    return key, {l: {z: str(q) for z, q in d.items()} for l, d in labels.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--split", default="val")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    m = Manifest.from_json(json.loads((Path(a.corpus_dir) / "manifest.json").read_text()))
    rows = read_split(a.corpus_dir, a.split)
    if a.n:
        rows = rows[:a.n]
    t0 = time.time()
    per_window, classes = [], {}
    for i, (w, _) in enumerate(rows):
        reset, recs = surface_records(tuple(VOCAB[t] for t in w))
        if len(recs) < a.k:
            continue
        pw, beta = pattern_all(recs[:a.k])
        key = (reset, pw)
        classes.setdefault(key, beta)
        per_window.append((i, key, (1 if reset else 0) + 5 * a.k))
    print(f"{len(per_window)} windows with >= {a.k} records, {len(classes)} classes; labeling with {a.workers} workers", flush=True)
    with Pool(a.workers, initializer=_init, initargs=(a.corpus_dir, m.rung)) as pool:
        labeled = dict(pool.imap_unordered(_one, list(classes.items()), chunksize=8))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for i, key, p0 in per_window:
            f.write(json.dumps(dict(i=i, k=a.k, reset=key[0], p0=p0, locks=labeled[key])) + "\n")
    print(f"wrote {a.out}: {len(per_window)} lines, {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
