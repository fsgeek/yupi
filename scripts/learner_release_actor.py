"""Exposure of the owner's identity at the point of need (probe design amendment
v0.5, 2026-09-24): on windows whose realized record k + 1 is a RELEASE (or BLOCK,
ACQUIRE), the model's ACTOR-field excess against the ceiling's own residual
uncertainty about the actor given the kind.

  uv run --extra learner python scripts/learner_release_actor.py --run <run dir> --k 7 \\
      --census ~/.cache/yupi-scratch/census/<run>-k7-test.jsonl [--tables-dir ~/.cache/yupi-scratch/ceilings] \\
      [--labels ~/.cache/yupi-scratch/probes/<name>-k7-test.jsonl] --raw docs/learner-release-actor-<cell>-seed<s>-<date>.json

Per kind: n, share of windows, mean ACTOR-field excess (bits; the census row's
by_field.actor, a realized-record estimate of KL(P*(actor | kind) || P~(actor | kind))),
its se, mean H*(actor | kind, prefix) from the k-record ceiling table, and the
exposure ratio 1 - excess / H* (1: the model's actor distribution matches the
ceiling's; 0: it carries none of the trace-available information about the actor).
With --labels (the §16 owner posteriors), RELEASE / BLOCK / ACQUIRE windows are also
split by whether the record's lock has a prefix-determined owner. **That split is
selected on the realized record's lock, an outcome correlated with the actor, and the
realized-record estimator is BIASED on it (first-results note §18 correction, §19);
it is kept only so the §18 raws can be reproduced. Use scripts/learner_actor_shape.py
(exact per-window KL, prefix-only splits) for any owner-conditioned reading.**
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

from yupi.corpus.manifest import Manifest
from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.evaluate import actor_entropy_given_kind, kind_marginal, surface_records
from yupi.naming import pattern_all
from yupi.pattern_ceiling import load_table

KINDS = ("RELEASE", "BLOCK", "ACQUIRE", "DISPATCH", "IO_ISSUE", "IO_COMPLETE", "STEP", "IDLE")


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def group_stats(items):
    """items: [(actor_excess, h_actor, kind_excess)] -> n, means, se, exposure ratio."""
    a = np.array(items, dtype=np.float64)
    if len(a) == 0:
        return None
    ex, h, kx = a.T
    mh = float(h.mean())
    return dict(n=int(len(a)), actor_excess=float(ex.mean()), actor_excess_se=float(ex.std(ddof=1) / math.sqrt(len(a))) if len(a) > 1 else 0.0,
                h_actor=mh, exposure_ratio=(1.0 - float(ex.mean()) / mh) if mh > 0 else None, kind_excess=float(kx.mean()))


def owner_entropy(label_row, l):
    d = label_row["locks"].get(str(l))
    if not d:
        return None
    ps = [float(Fraction(q)) for q in d.values()]
    return float(-sum(p * math.log2(p) for p in ps if p > 0))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--census", required=True)
    ap.add_argument("--tables-dir", default=str(Path.home() / ".cache/yupi-scratch/ceilings"))
    ap.add_argument("--labels")
    ap.add_argument("--split", default="test")
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    run_json = json.loads((Path(a.run) / "run.json").read_text())
    m = Manifest.from_json(json.loads((Path(run_json["corpus_dir"]) / "manifest.json").read_text()))
    law = m.law()
    fn = Path(a.tables_dir) / f"{m.programs}-{law.T_ep}-{law.L}-{law.B}-{m.rung}-eps{m.epsilon.replace('/', '_')}-k{a.k}.jsonl"
    table = load_table(fn)
    census = {}
    for line in Path(a.census).read_text().splitlines():
        r = json.loads(line); census[r["i"]] = r
    labels = {}
    if a.labels:
        for line in Path(a.labels).read_text().splitlines():
            r = json.loads(line); labels[r["i"]] = r
    rows = read_split(run_json["corpus_dir"], a.split)
    by_kind = defaultdict(list); by_kind_det = defaultdict(lambda: defaultdict(list))
    n_used = n_missing = 0
    for i, (w, _) in enumerate(rows):
        if i not in census:
            continue
        reset, recs = surface_records(tuple(VOCAB[t] for t in w))
        if len(recs) < a.k + 1:
            continue
        pw, _ = pattern_all(recs[:a.k])
        entry = table.get((reset, pw))
        if entry is None:
            n_missing += 1
            continue
        star = entry[1]
        rho = pattern_all(recs[:a.k + 1])[0][-1]
        h = actor_entropy_given_kind(star, rho.kind)
        if h is None:
            n_missing += 1
            continue
        c = census[i]
        item = (c["by_field"]["actor"], h, c["by_field"]["kind"])
        by_kind[rho.kind].append(item); n_used += 1
        if labels and i in labels and rho.obj is not None and rho.obj[0] == "LOCK":
            he = owner_entropy(labels[i], rho.obj[1])
            if he is not None:
                by_kind_det[rho.kind]["determined" if he == 0.0 else "uncertain"].append(item)
    out = dict(run=a.run, seed=run_json["seed"], rung=m.rung, eps=str(m.epsilon), k=a.k, census=a.census,
               census_sha256=hashlib.sha256(Path(a.census).read_bytes()).hexdigest(), table=str(fn),
               table_sha256=hashlib.sha256(fn.read_bytes()).hexdigest(), labels=a.labels, git=_git(),
               n_windows=n_used, n_missing=n_missing, by_kind={}, by_kind_owner={})
    for kind in KINDS:
        if kind in by_kind:
            s = group_stats(by_kind[kind]); s["frac"] = s["n"] / n_used; out["by_kind"][kind] = s
    for kind, d in by_kind_det.items():
        out["by_kind_owner"][kind] = {which: group_stats(items) for which, items in d.items()}
    f = lambda v: "—" if v is None else f"{v:.3f}"
    print(f"{Path(a.run).name} k={a.k}: {n_used} windows ({n_missing} missing class / zero-mass kind)")
    for kind, s in out["by_kind"].items():
        print(f"  {kind:11s} n={s['n']:6d} frac {s['frac']:.3f}  actor excess {s['actor_excess']:.4f} ± {s['actor_excess_se']:.4f}  "
              f"H*(actor|kind) {s['h_actor']:.3f}  exposure {f(s['exposure_ratio'])}  kind excess {s['kind_excess']:.4f}")
        if kind in out["by_kind_owner"]:
            for which, t in out["by_kind_owner"][kind].items():
                if t:
                    print(f"     [outcome-selected, biased — see §18 correction] owner {which:10s} n={t['n']:6d}  actor excess {t['actor_excess']:.4f} ± {t['actor_excess_se']:.4f}  H* {t['h_actor']:.3f}  exposure {f(t['exposure_ratio'])}")
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
