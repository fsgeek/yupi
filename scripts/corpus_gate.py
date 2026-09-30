"""Corpus generator gates 2–4 (design v0.1 §8) at C1 (8, 4, 2), c1 programs,
both statutory ε, rungs r1/r3 (the pinned corpus-track cells) and r4.

  python scripts/corpus_gate.py [--n 1000000] [--workers 32] [--root ~/.cache/yupi-scratch/corpus-gate]

Generates N windows per cell with the real pools through the writer, reads
them back, un-renames through the table, re-keys by Π (yupi.naming.pattern)
and compares with the exact pattern aggregate built from the enumerator's
paths (the construction of tests/test_naming_bridge.py). Writes
docs/corpus-gate-8-4-2-<date>.json; exit 1 if any gate fails.

Gates, as stated in the plan (docs/superpowers/plans/2026-09-15-corpus-generator.md):
  G2 window law: TV(empirical, exact) ≤ 2·sqrt(K_exact / N); every exact class with
     mass ≥ 1e-4 present; no empirical class outside the exact support; endpoint
     chi-square (df 3) < 16.3; |RESET frequency − ½| ≤ 3·sqrt(¼ / N).
  G3 rendering (real pool; design §8.3 amended — per-injection is infeasible there):
     per-position thread-token chi-square over the 56 drawable tokens (df 55) < 98.4;
     (position 0, position 1) pair chi-square over 56·55 cells (df 3079) < 3400;
     no reserved token of any type in any table line.
  G4 corpus-track reproduction: Σ_k f̂_k·H(q | class k) within h_tol of the pinned
     H(q | Πw) (tests/test_naming_bridge.py), where f̂ is empirical and the beliefs exact.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

from yupi.config import WorldConfig
from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import ENTITY_TYPES, RESERVED, VOCAB, pool_tokens
from yupi.corpus.windows import deserialize
from yupi.corpus.writer import generate, read_split
from yupi.enumerator import paths
from yupi.interfaces import project_window
from yupi.naming import pattern, quotient
from yupi.programs import c1_programs
from yupi.queries import state_entropy_bits
from yupi.window import WindowLaw, endpoint_prior

LAW = WindowLaw(8, 4, 2)
PINNED_HQ = {(Fraction(1), "r1"): 0.6238, (Fraction(1), "r3"): 0.4565,
             (Fraction(1, 2), "r1"): 1.3078, (Fraction(1, 2), "r3"): 1.1287}   # tests/test_naming_bridge.py
# the relay rung's classes are r1's relayed, one to one, with the same (state, binding) joints
# (relay design v0.1 §3), so its pinned H(q | Πw) is r1's
PINNED_HQ[(Fraction(1), "r1R")] = PINNED_HQ[(Fraction(1), "r1")]
PINNED_HQ[(Fraction(1, 2), "r1R")] = PINNED_HQ[(Fraction(1, 2), "r1")]
DEFAULT_CELLS = [(Fraction(1), "r1"), (Fraction(1), "r3"), (Fraction(1), "r4"), (Fraction(1, 2), "r1"), (Fraction(1, 2), "r3")]


def parse_cells(spec):
    """'1:r1R,1/2:r1R' -> [(ε, rung)]; None -> the default five cells."""
    if spec is None:
        return DEFAULT_CELLS
    return [(Fraction(e), r) for e, r in (c.split(":") for c in spec.split(","))]


def exact_pattern_aggregate(cfg, progs, law, rung):
    """{(reset, Π(window)): {(state, binding): law mass}} — Fraction-exact."""
    w_T = endpoint_prior(law)
    agg = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            pw, order = pattern(project_window(recs[u:], rung))
            d = agg.setdefault((u == 0, pw), {})
            d[(final, order)] = d.get((final, order), Fraction(0)) + w_T * prob
    return agg


def _H(dist):
    tot = sum(dist.values(), Fraction(0))
    return state_entropy_bits({k: m / tot for k, m in dist.items()})


def _chi2(counts, n_cells, total):
    e = total / n_cells
    return sum((c - e) ** 2 / e for c in counts.values()) + (n_cells - len(counts)) * e


def run_gate(eps, rung, n_windows, root, workers, h_tol=0.01):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    key = bytes.fromhex("5b" * 32)                       # a fixed gate key; the gate is about the law, not the key
    m = Manifest.new(programs="c1", epsilon=eps, T_ep=8, L=4, B=2, rung=rung, run_key=key,
                     splits=(Split("gate", 0, n_windows),), git_commit="gate")
    t0 = time.time()
    d, _ = generate(m, Path(root) / f"eps{str(eps).replace('/', '_')}-{rung}", workers=workers)
    rows = read_split(d, "gate")
    exact = exact_pattern_aggregate(cfg, progs, LAW, rung)
    emp, ends, resets = Counter(), Counter(), 0
    pos = [Counter() for _ in range(cfg.n_threads)]
    pair = Counter()
    reserved = {tok for et in ENTITY_TYPES for tok in pool_tokens(et)[-RESERVED[et]:]}
    reserved_hits = 0
    for ids, table in rows:
        t = EpisodeTable.from_json(table)
        reset, recs = deserialize(tuple(VOCAB[i] for i in ids), t)
        pw, _ = pattern(recs)
        emp[(reset, pw)] += 1
        ends[table["T"]] += 1
        resets += reset
        for k, tok in enumerate(t.thread):
            pos[k][tok] += 1
        pair[(t.thread[0], t.thread[1])] += 1
        reserved_hits += sum(1 for et in ENTITY_TYPES for tok in getattr(t, et) if tok in reserved)
    N = len(rows)
    exact_mass = {k: float(sum(v.values(), Fraction(0))) for k, v in exact.items()}
    tv = 0.5 * (sum(abs(exact_mass.get(k, 0.0) - c / N) for k, c in emp.items())
                + sum(p for k, p in exact_mass.items() if k not in emp))
    tv_bound = 2 * math.sqrt(len(exact) / N)
    missing = [k for k, p in exact_mass.items() if p >= 1e-4 and k not in emp]
    unknown = [k for k in emp if k not in exact]
    end_chi2 = _chi2(ends, len(list(LAW.endpoints())), N)
    reset_dev = abs(resets / N - 0.5)
    drawable = 64 - RESERVED["thread"]
    pos_chi2 = [_chi2(c, drawable, N) for c in pos]
    pair_chi2 = _chi2(pair, drawable * (drawable - 1), N)
    hq_hat = 0.0                                          # Σ_k f̂_k · H(q | class k), beliefs exact, weights empirical
    for k, c in emp.items():
        if k not in exact:
            continue
        q = {}
        for (st, b), mass in exact[k].items():
            qq = quotient(st, b, cfg)
            q[qq] = q.get(qq, Fraction(0)) + mass
        hq_hat += (c / N) * _H(q)
    hq_pin = PINNED_HQ.get((eps, rung))
    rep = dict(eps=str(eps), rung=rung, N=N, seconds=round(time.time() - t0, 1),
               K_exact=len(exact), K_empirical=len(emp),
               g2_tv=tv, g2_tv_bound=tv_bound, g2_missing_above_1e4=len(missing), g2_unknown_classes=len(unknown),
               g2_endpoint_chi2=end_chi2, g2_reset_dev=reset_dev, g2_reset_tol=3 * math.sqrt(0.25 / N),
               g3_pos_chi2=pos_chi2, g3_pair_chi2=pair_chi2, g3_reserved_hits=reserved_hits,
               g4_hq_hat=hq_hat, g4_hq_pinned=hq_pin, g4_tol=h_tol)
    rep["passed"] = (tv <= tv_bound and not missing and not unknown and end_chi2 < 16.3
                     and reset_dev <= rep["g2_reset_tol"] and all(c < 98.4 for c in pos_chi2)
                     and pair_chi2 < 3400 and reserved_hits == 0
                     and (hq_pin is None or abs(hq_hat - hq_pin) <= h_tol))
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--root", default=os.path.expanduser("~/.cache/yupi-scratch/corpus-gate"))
    ap.add_argument("--out")
    ap.add_argument("--cells", help="e.g. 1:r1R,1/2:r1R (default: the five pinned cells)")
    a = ap.parse_args(argv)
    date = subprocess.check_output(["date", "+%Y-%m-%d"], text=True).strip()
    out = Path(a.out or f"docs/corpus-gate-8-4-2-{date}.json")
    cells = parse_cells(a.cells)
    reports = []
    for eps, rung in cells:
        r = run_gate(eps, rung, a.n, a.root, a.workers)
        reports.append(r)
        print(json.dumps(r, default=str), flush=True)
    doc = dict(law="C1 (8,4,2) c1 programs", date=date,
               git=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               n=a.n, cells=reports, all_passed=all(r["passed"] for r in reports))
    out.write_text(json.dumps(doc, indent=2, default=str) + "\n")
    print("ALL PASSED" if doc["all_passed"] else "GATE FAILED", "->", out)
    return 0 if doc["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
