"""Training-corpus frequency of each eval window's k-record prefix class
(2026-09-24; the confound control named in first-results note §17.4).

  uv run python scripts/learner_class_frequency.py --corpus-dir corpus/<name>/<rid> --k 7 \\
      [--eval-split test --n 30000] [--workers 32] --out ~/.cache/yupi-scratch/probes/<name>-k7-test-classfreq.jsonl

The class is the window census's / the probe labels' class: (reset, pattern prefix
of the first k records). Counts every training window with >= k records; writes one
JSON line per eval window with >= k records: {"i", "k", "train_count", "n_train"}.
"""
import argparse
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.evaluate import surface_records
from yupi.naming import pattern_all

_K = {}


def class_key(window_ids, k):
    reset, recs = surface_records(tuple(VOCAB[t] for t in window_ids))
    if len(recs) < k:
        return None
    return (reset, pattern_all(recs[:k])[0])


def _init(k):
    _K["k"] = k


def _chunk(windows):
    c = Counter()
    for w in windows:
        key = class_key(w, _K["k"])
        if key is not None:
            c[key] += 1
    return c


def count_classes(windows, k, workers=32, chunk=20000):
    total = Counter()
    with Pool(workers, initializer=_init, initargs=(k,)) as pool:
        for c in pool.imap_unordered(_chunk, [windows[i:i + chunk] for i in range(0, len(windows), chunk)]):
            total.update(c)
    return total


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--train-split", default="train")
    ap.add_argument("--eval-split", default="test")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    train = [w for w, _ in read_split(a.corpus_dir, a.train_split)]
    counts = count_classes(train, a.k, a.workers)
    n_train = sum(counts.values())
    print(f"{len(train)} training windows, {n_train} with >= {a.k} records, {len(counts)} classes; {time.time() - t0:.0f}s", flush=True)
    rows = read_split(a.corpus_dir, a.eval_split)
    if a.n:
        rows = rows[:a.n]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    seen = unseen = 0
    with open(a.out, "w") as f:
        for i, (w, _) in enumerate(rows):
            key = class_key(w, a.k)
            if key is None:
                continue
            c = counts.get(key, 0)
            seen += c > 0; unseen += c == 0
            f.write(json.dumps(dict(i=i, k=a.k, train_count=c, n_train=n_train)) + "\n")
    print(f"wrote {a.out}: {seen + unseen} eval windows, {unseen} in classes unseen in training; {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
