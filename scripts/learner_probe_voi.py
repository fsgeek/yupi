"""Need, not presence: the exact value of the lock owner for the next record
(2026-09-24; companion to scripts/learner_probe_labels.py, same classes).

  uv run python scripts/learner_probe_voi.py --corpus-dir corpus/<name>/<rid> --k 7 --split test \\
      [--n N] [--workers 60] --per-window ~/.cache/yupi-scratch/probes/<name>-k7-test-voi.jsonl \\
      --raw docs/learner-probe-voi-<cell>-k7-<date>.json

Per window with >= k records and per lock l visible in its k-record prefix, from
the pattern filter's joint belief over (state, binding): H(next) = entropy of the
ceiling next-record distribution; I_owner = I(next; owner of l); I_held = I(next;
is l held); I_kind_owner, I_kind_held = the same with the next record coarsened
to its kind; H(kind). Bits. Also the RELEVANCE of lock l to the next record where
the owner is determined and I is zero by construction: p_lock = P*(next record's
object is l), p_block = P*(next record is BLOCK on l), p_acquire, p_release. The summary averages over (window, lock) examples,
over windows (summing locks), and over the examples whose owner is uncertain.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.evaluate import surface_records
from yupi.learner.probe import mutual_information, next_dist_by_owner
from yupi.naming import pattern_all
from yupi.pattern_filter import filter_pattern_window

_W = {}


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def _init(corpus_dir, rung):
    m = Manifest.from_json(json.loads((Path(corpus_dir) / "manifest.json").read_text()))
    _W["cfg"], _W["progs"] = m.world()
    _W["law"] = m.law(); _W["rung"] = rung


def held(z):
    return z if z in ("none", "invisible") else "held"


def _one(item):
    key, beta = item
    reset, pw = key
    post, _ = filter_pattern_window(_W["cfg"], _W["progs"], _W["law"], list(pw), _W["rung"], reset, prefix=True)
    joint = post.joint_marginal()
    out = {}
    for l in range(len(beta[1])):
        by_z = next_dist_by_owner(joint, _W["cfg"], _W["progs"], _W["rung"], l)
        i_owner, h_next = mutual_information(by_z)
        i_held, _ = mutual_information(by_z, fold=held)
        i_kind_owner, h_kind = mutual_information(by_z, proj=lambda r: r.kind)
        i_kind_held, _ = mutual_information(by_z, fold=held, proj=lambda r: r.kind)
        pz = np.array([float(w) for w, _ in by_z.values()])
        star = {}
        for w, dist in by_z.values():
            for r, q in dist.items():
                star[r] = star.get(r, 0) + w * q
        on_l = {r: q for r, q in star.items() if r.obj == ("LOCK", l)}
        kind_mass = lambda kind: float(sum(q for r, q in on_l.items() if r.kind == kind))
        out[l] = dict(h_next=h_next, h_kind=h_kind, i_owner=i_owner, i_held=i_held,
                      i_kind_owner=i_kind_owner, i_kind_held=i_kind_held,
                      h_owner=float(-(pz * np.log2(pz)).sum()), n_classes=len(by_z),
                      p_lock=float(sum(on_l.values())), p_block=kind_mass("BLOCK"),
                      p_acquire=kind_mass("ACQUIRE"), p_release=kind_mass("RELEASE"))
        assert 0.0 <= out[l]["p_lock"] <= 1.0 + 1e-12
    return key, out


def _mean(xs):
    return float(np.mean(xs)) if len(xs) else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus-dir", required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--per-window", required=True)
    ap.add_argument("--raw")
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
        per_window.append((i, key))
    print(f"{len(per_window)} windows with >= {a.k} records, {len(classes)} classes; {a.workers} workers", flush=True)
    with Pool(a.workers, initializer=_init, initargs=(a.corpus_dir, m.rung)) as pool:
        done = dict(pool.imap_unordered(_one, list(classes.items()), chunksize=8))
    Path(a.per_window).parent.mkdir(parents=True, exist_ok=True)
    ex = {f: [] for f in ("h_next", "h_kind", "i_owner", "i_held", "i_kind_owner", "i_kind_held", "h_owner",
                          "p_lock", "p_block", "p_acquire", "p_release")}
    unc = {f: [] for f in ex}
    det = {f: [] for f in ex}
    win = {f: [] for f in ("h_next", "i_owner", "i_held", "i_kind_owner", "i_kind_held", "p_lock", "p_block")}
    with open(a.per_window, "w") as f:
        for i, key in per_window:
            locks = done[key]
            f.write(json.dumps(dict(i=i, k=a.k, reset=key[0], locks=locks)) + "\n")
            for l, d in locks.items():
                for k2 in ex:
                    ex[k2].append(d[k2])
                if d["n_classes"] > 1:
                    for k2 in unc:
                        unc[k2].append(d[k2])
                else:
                    for k2 in det:
                        det[k2].append(d[k2])
            if locks:
                any_l = next(iter(locks.values()))
                win["h_next"].append(any_l["h_next"])
                for k2 in ("i_owner", "i_held", "i_kind_owner", "i_kind_held", "p_lock", "p_block"):
                    win[k2].append(sum(d[k2] for d in locks.values()))
    summary = dict(n_windows=len(per_window), n_classes=len(classes), n_examples=len(ex["h_next"]),
                   n_uncertain=len(unc["h_next"]), frac_uncertain=len(unc["h_next"]) / max(1, len(ex["h_next"])),
                   per_example={k2: _mean(v) for k2, v in ex.items()},
                   per_uncertain_example={k2: _mean(v) for k2, v in unc.items()},
                   per_determined_example={k2: _mean(v) for k2, v in det.items()},
                   per_window_summing_locks={k2: _mean(v) for k2, v in win.items()},
                   max={k2: float(np.max(v)) if v else None for k2, v in ex.items()})
    print(json.dumps(summary, indent=1))
    if a.raw:
        out = dict(corpus=a.corpus_dir, rung=m.rung, eps=str(m.epsilon), k=a.k, split=a.split, n=a.n, git=_git(),
                   per_window=a.per_window, per_window_sha256=hashlib.sha256(Path(a.per_window).read_bytes()).hexdigest(),
                   summary=summary, wall_s=time.time() - t0)
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    print(f"{time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
