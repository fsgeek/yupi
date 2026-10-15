"""Exact split of the next-KIND uncertainty an interface leaves, per pattern class at position k
(exposure review 2026-10-15, Decision step 1; exact side, EXPLORATORY feasibility gate).

For a class c (the pattern observer's (reset, Πw) after k records) with posterior P(S | c):
  H*(c) = H(Σ_s P(s|c) P(kind | s))         the Bayes next-KIND entropy (the ceiling's class term)
  R(c)  = Σ_s P(s|c) H(kind | s)             transition randomness: what an observer of S would still face
  G(c)  = H*(c) − R(c) = I(kind; S | c) ≥ 0  the observation gap: uncertainty from state the interface withholds
The next KIND depends on S only (bindings do not change it), so the class joint over (S, β) is summed over β.

Gate: the law-mass mean of H* per rung must reproduce paper 1 §3.1's KIND ceilings at k = 7
(ε = 1: 1.176 0.999 0.955 0.911 0.911; ε = ½: 1.104 0.873 0.823 0.784 0.784) to the printed precision.

  python scripts/kind_uncertainty_split.py --eps 1 [--k 7] [--out docs/kind-uncertainty-split-...json]
Per-class rows go to ~/.cache/yupi-scratch/split/ (not docs/); the summary raw holds sha256s.
"""
import argparse
import hashlib
import json
import math
import resource
import subprocess
import time
from fractions import Fraction
from pathlib import Path

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.naming import pattern_all
from yupi.programs import programs_for
from yupi.records import record_of
from yupi.window import WindowLaw
from yupi.window_process import prefix_law_aggregates

RUNGS = ("r0", "r1", "r2", "r3", "r4")
EXPECT = {"1": (1.176, 0.999, 0.955, 0.911, 0.911), "1/2": (1.104, 0.873, 0.823, 0.784, 0.784)}


def h_bits(ps) -> float:
    return -sum(float(p) * math.log2(float(p)) for p in ps if p > 0)


def kind_dist(s, cfg, progs, memo):
    d = memo.get(s)
    if d is None:
        d = {}
        for tr, p in enabled(s, cfg, progs):
            k = record_of(tr).kind
            d[k] = d.get(k, Fraction(0)) + p
        memo[s] = d
    return d


def wq(xs, ws, q):
    """Weighted quantile (lower), weights need not be normalised."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    tot, acc = sum(ws), 0.0
    for i in order:
        acc += ws[i]
        if acc >= q * tot:
            return xs[i]
    return xs[order[-1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eps", default="1")
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--law", nargs=3, type=int, default=(40, 8, 2))
    ap.add_argument("--programs", default="c1prime-loop")
    ap.add_argument("--rows-dir", default=str(Path.home() / ".cache/yupi-scratch/split"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    eps = Fraction(a.eps)
    law, progs, cfg = WindowLaw(*a.law), programs_for(a.programs), WorldConfig.c1(epsilon=eps)
    t0 = time.time()
    aggs = prefix_law_aggregates(cfg, progs, law, a.k, RUNGS, None)
    t_pass = time.time() - t0
    memo: dict = {}
    rows_dir = Path(a.rows_dir); rows_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for ri, rung in enumerate(RUNGS):
        cls: dict = {}
        for (reset, win), joint in aggs[rung].items():
            pw, _ = pattern_all(win)
            d = cls.setdefault((reset, pw), {})
            for s, m in joint.items():
                d[s] = d.get(s, Fraction(0)) + m
        rows = []
        for key, post in cls.items():
            mass = sum(post.values(), Fraction(0))
            star: dict = {}
            r = 0.0
            for s, m in post.items():
                kd = kind_dist(s, cfg, progs, memo)
                w = m / mass
                r += float(w) * h_bits(kd.values())
                for k, p in kd.items():
                    star[k] = star.get(k, Fraction(0)) + w * p
            hs = h_bits(star.values())
            rows.append((float(mass), hs, r, hs - r))
        M = sum(x[0] for x in rows)
        mean = lambda j: sum(x[0] * x[j] for x in rows) / M
        H, R, G = mean(1), mean(2), mean(3)
        pos = [x for x in rows if x[1] > 1e-12]
        frac = [x[3] / x[1] for x in pos]
        wpos = [x[0] for x in pos]
        # feasibility: among classes with comparable H*, does the gap share vary?
        bins = []
        if pos:
            cuts = [wq([x[1] for x in pos], wpos, q) for q in (0.25, 0.5, 0.75)]
            edges = [0.0] + cuts + [float("inf")]
            for lo, hi in zip(edges, edges[1:]):
                sel = [i for i, x in enumerate(pos) if lo < x[1] <= hi] if lo > 0 else [i for i, x in enumerate(pos) if x[1] <= hi]
                if not sel:
                    continue
                f, w = [frac[i] for i in sel], [wpos[i] for i in sel]
                bins.append(dict(h_star_range=[lo, hi], mass=sum(w) / M, n_classes=len(sel),
                                 gap_share_q10=wq(f, w, 0.1), gap_share_q50=wq(f, w, 0.5), gap_share_q90=wq(f, w, 0.9),
                                 mass_share_gap_zero=sum(wi for fi, wi in zip(f, w) if fi < 1e-12) / sum(w)))
        min_gap = min(x[3] for x in rows)
        p = rows_dir / f"{a.programs}-{'-'.join(map(str, a.law))}-{rung}-eps{a.eps.replace('/', '_')}-k{a.k}.jsonl"
        with open(p, "w") as fh:
            for x in rows:
                fh.write(json.dumps(dict(mass=x[0], h_star=x[1], r=x[2], g=x[3])) + "\n")
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        ok = round(H, 3) == EXPECT[a.eps][ri] if a.eps in EXPECT and a.k == 7 else None
        summary.append(dict(rung=rung, n_classes=len(rows), h_star=H, transition_randomness=R, observation_gap=G,
                            gate_h_star_matches_s31=ok, min_class_gap=min_gap, mass_h_star_zero=1 - sum(wpos) / M,
                            gap_share_by_h_star_quartile=bins, rows_file=str(p), rows_sha256=sha))
        print(f"{rung} H*={H:.4f} R={R:.4f} G={G:.4f} gate={ok} min_gap={min_gap:.2e} classes={len(rows)}", flush=True)
        for b in bins:
            print(f"    H* in ({b['h_star_range'][0]:.3f},{b['h_star_range'][1]:.3f}] mass {b['mass']:.3f}: gap share q10/50/90 "
                  f"{b['gap_share_q10']:.3f}/{b['gap_share_q50']:.3f}/{b['gap_share_q90']:.3f}, zero-gap mass {b['mass_share_gap_zero']:.3f}", flush=True)
    git = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out = dict(status="EXPLORATORY exact side; feasibility gate for the random-vs-hidden question "
                      "(docs/exposure-prereg-review-2026-10-15.md, Decision)",
               law=dict(zip(("T_ep", "L", "B"), a.law)), programs=a.programs, eps=a.eps, k=a.k, observer="pattern",
               git=git, wall_pass_s=t_pass, wall_total_s=time.time() - t0,
               peak_rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, rungs=summary)
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
