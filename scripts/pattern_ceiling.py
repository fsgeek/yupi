"""Produce the headline-position ceiling tables P*(Πr | Πw) for the ten
(rung, ε) cells of a law (learner contract v0.1.1 ledger (b), 2026-09-18),
and gate each against the pattern filter on a random sample of the cell's
test windows.

  python scripts/pattern_ceiling.py T_ep L B [--programs c1prime-loop] [--rungs r0,...]
         [--eps 1,1/2] [--tables ~/.cache/yupi-scratch/ceilings] [--gate-n 200]
         [--corpus corpus] [--manifests docs/corpus-manifests] [--raw docs/<name>.json]

One window-process pass per ε (the D4-priced recursion; peak RSS
reported), re-keyed by Π_all, one kernel step per (S, β). Tables are
written as exact JSON lines under --tables (NOT under docs/: ~10^5–10^6
lines each; the committed record is the summary raw). The summary raw
holds, per cell: the number of pattern classes, the law-mass mean
H*(Πr | Πw), the gate (n sampled test windows, all exact-equal in mass
and distribution, or the first mismatch), wall times, and the table file's
sha256. Every test window's class must be present in the table (a missing
class is a finding, reported, never coerced).
"""
import argparse
import hashlib
import json
import os
import random
import resource
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

from yupi.config import WorldConfig
from yupi.corpus.manifest import Manifest
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import VOCAB
from yupi.corpus.windows import deserialize
from yupi.corpus.writer import read_split
from yupi.naming import pattern_all
from yupi.pattern_ceiling import ceiling_table, mean_next_entropy_bits, save_table
from yupi.pattern_filter import filter_pattern_window, next_pattern_dist
from yupi.programs import programs_for
from yupi.window import WindowLaw

RUNGS = ("r0", "r1", "r2", "r3", "r4")


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def _manifest(manifests: Path, programs: str, law: WindowLaw, rung: str, eps: Fraction):
    tag = f"{programs}-{law.T_ep}-{law.L}-{law.B}-{rung}-eps{str(eps).replace('/', '_')}-"
    hits = sorted(manifests.glob(tag + "*.json"))
    if len(hits) != 1:
        raise SystemExit(f"expected one manifest for {tag}*, found {hits}")
    return Manifest.from_json(json.loads(hits[0].read_text())), hits[0].name


def gate_sample(table, cfg, progs, law, rung, m: Manifest, corpus_root: Path, n: int, seed: int):
    d = corpus_root / m.name() / m.run_id()
    wins = read_split(d, "test")
    rng = random.Random(seed)
    idx = rng.sample(range(len(wins)), min(n, len(wins)))
    t0 = time.time()
    missing, mism = [], None
    for i in idx:
        toks, tab = wins[i]
        reset, recs = deserialize(tuple(VOCAB[t] for t in toks), EpisodeTable.from_json(tab))
        pw, _ = pattern_all(recs)
        key = (reset, pw)
        if key not in table:
            missing.append(i)
            continue
        mass, star = table[key]
        post, m2 = filter_pattern_window(cfg, progs, law, list(pw), rung, reset)
        s2 = next_pattern_dist(post, cfg, progs, rung)
        if not (mass == m2 and star == s2):
            mism = dict(window=i, table_mass=str(mass), filter_mass=str(m2), equal_dist=(star == s2))
            break
    return dict(n=len(idx), seed=seed, missing_classes=missing, first_mismatch=mism,
                all_exact=(not missing and mism is None), wall_s=time.time() - t0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("law", nargs=3, type=int, metavar=("T_EP", "L", "B"))
    ap.add_argument("--programs", default="c1prime-loop")
    ap.add_argument("--rungs", default=",".join(RUNGS))
    ap.add_argument("--eps", default="1,1/2")
    ap.add_argument("--tables", default=os.path.expanduser("~/.cache/yupi-scratch/ceilings"))
    ap.add_argument("--gate-n", type=int, default=200)
    ap.add_argument("--gate-seed", type=int, default=20260918)
    ap.add_argument("--corpus", default="corpus")
    ap.add_argument("--manifests", default="docs/corpus-manifests")
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    law = WindowLaw(*a.law)
    rungs = tuple(a.rungs.split(","))
    progs = programs_for(a.programs)
    tables_dir = Path(a.tables); tables_dir.mkdir(parents=True, exist_ok=True)
    out = dict(law=dict(T_ep=law.T_ep, L=law.L, B=law.B), programs=a.programs, git=_git(),
               route="window-process pass -> Π_all re-key -> one kernel step per (S, β)",
               observer="pattern (all four entity types renamed)", position="last record of the window (contract §2.2)",
               tables_dir=str(tables_dir), rows=[])
    for eps_s in a.eps.split(","):
        eps = Fraction(eps_s)
        cfg = WorldConfig.c1(epsilon=eps)
        stats = {}
        t0 = time.time()
        tables = ceiling_table(cfg, progs, law, rungs, stats)
        wall_pass = time.time() - t0
        print(f"eps={eps}: pass+rekey+step {wall_pass:.0f}s, frontier {stats.get('max_pairs')}, "
              f"RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6:.2f} GB", flush=True)
        for rung in rungs:
            table = tables[rung]
            fn = tables_dir / f"{a.programs}-{law.T_ep}-{law.L}-{law.B}-{rung}-eps{eps_s.replace('/', '_')}.jsonl"
            save_table(table, fn)
            sha = hashlib.sha256(fn.read_bytes()).hexdigest()
            H = mean_next_entropy_bits(table)
            if a.gate_n > 0:
                m, mname = _manifest(Path(a.manifests), a.programs, law, rung, eps)
                gate = gate_sample(table, cfg, progs, law, rung, m, Path(a.corpus), a.gate_n, a.gate_seed)
            else:
                mname, gate = None, dict(n=0, all_exact=None, missing_classes=[], first_mismatch=None, wall_s=0.0)
            row = dict(eps=str(eps), rung=rung, n_pattern_classes=len(table), mean_next_record_entropy_bits=H,
                       table_file=fn.name, table_sha256=sha, manifest=mname, gate=gate)
            out["rows"].append(row)
            print(f"  {rung}: classes {len(table)}  H*(Πr|Πw) {H:.4f} bits  gate n={gate['n']} exact={gate['all_exact']} "
                  f"missing={len(gate['missing_classes'])} ({gate['wall_s']:.0f}s)", flush=True)
        out.setdefault("wall_pass_s", {})[str(eps)] = wall_pass
        out.setdefault("frontier", {})[str(eps)] = stats.get("max_pairs")
        del tables
    out["peak_rss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2) + "\n")
        print(f"raw -> {a.raw}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
