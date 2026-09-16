"""Generate a corpus (design v0.1 §5–§7) or regenerate one from its manifest.

  new:  python scripts/corpus_generate.py --programs c1prime-loop --law 40 8 2 --rung r1 --eps 1/2 \\
            --train 200000 --val 10000 --test 10000 --workers 32 [--root corpus] [--run-key HEX] \\
            [--manifest-copy docs/corpus-manifests]
  again: python scripts/corpus_generate.py --from-manifest docs/corpus-manifests/<file>.json [--root corpus]

The run key is 32 random bytes unless given; it is provenance, recorded in
the manifest (the model never sees the table). The manifest copy under
docs/corpus-manifests/ is the committed record; corpus/ is gitignored.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

from yupi.corpus.manifest import Manifest, Split, validate
from yupi.corpus.writer import generate


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def default_splits(n_train: int, n_val: int, n_test: int):
    return (Split("train", 0, n_train), Split("val", 1_000_000, 1_000_000 + n_val),
            Split("test", 2_000_000, 2_000_000 + n_test))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-manifest")
    ap.add_argument("--programs", default="c1prime-loop")
    ap.add_argument("--law", nargs=3, type=int, metavar=("T_EP", "L", "B"))
    ap.add_argument("--rung")
    ap.add_argument("--eps", default="1")
    ap.add_argument("--train", type=int, default=200_000)
    ap.add_argument("--val", type=int, default=10_000)
    ap.add_argument("--test", type=int, default=10_000)
    ap.add_argument("--run-key", help="hex; default os.urandom(32)")
    ap.add_argument("--root", default="corpus")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--manifest-copy", default="docs/corpus-manifests")
    a = ap.parse_args(argv)

    if a.from_manifest:
        m = Manifest.from_json(json.loads(Path(a.from_manifest).read_text()))
    else:
        if not (a.law and a.rung):
            ap.error("--law and --rung are required for a new run")
        key = bytes.fromhex(a.run_key) if a.run_key else os.urandom(32)
        m = Manifest.new(programs=a.programs, epsilon=Fraction(a.eps), T_ep=a.law[0], L=a.law[1], B=a.law[2],
                         rung=a.rung, run_key=key, splits=default_splits(a.train, a.val, a.test),
                         git_commit=git_commit())
    validate(m)
    t0 = time.time()
    d, m2 = generate(m, Path(a.root), workers=a.workers)
    dt = time.time() - t0
    copy_dir = Path(a.manifest_copy)
    copy_dir.mkdir(parents=True, exist_ok=True)
    copy = copy_dir / f"{m2.name()}-{m2.run_id()}.json"
    copy.write_text(json.dumps(m2.to_json(), indent=2, sort_keys=True) + "\n")
    print(f"{m2.name()} run {m2.run_id()}: {m2.counts} windows in {dt:.1f}s -> {d}; manifest copy {copy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
