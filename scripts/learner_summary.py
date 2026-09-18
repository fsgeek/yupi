"""Summarize learner evaluation raws (scripts/learner_evaluate.py output) into
per-cell tables: per seed and pooled across seeds, the structural / naming /
kind-KL / end excess at the headline position k = L−1 and the per-k curve.

  uv run python scripts/learner_summary.py docs/learner-eval-*.json [--k-head 7] [--md out.md]

Pooled across seeds: the mean of the per-seed means, the between-seed
standard deviation (ddof=1), and the standard error of the pooled mean
(between-seed sd / sqrt(n_seeds)); the within-seed test-set standard error
is shown beside it. The seed count the contract asks for (§2.4) is the
smallest n with between-seed sd / sqrt(n) ≤ δ/3 = 0.01/3 bits.
"""
import argparse
import json
import math
import sys
from collections import defaultdict


def load(paths):
    rows = []
    for p in paths:
        r = json.load(open(p))
        rows.append((p, r))
    return rows


def cell_of(r):
    return f"{r['rung']} eps={r['eps']}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raws", nargs="+")
    ap.add_argument("--k-head", type=int, default=7)
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    rows = load(a.raws)
    by_cell = defaultdict(list)
    for p, r in rows:
        by_cell[cell_of(r)].append((p, r))
    out = []
    kh = str(a.k_head)
    out.append(f"| cell | seed | step | n | structural (bits) ± se | naming ± se | kind KL | end | token |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    pooled = {}
    for cell in sorted(by_cell):
        vals = defaultdict(list)
        for p, r in sorted(by_cell[cell], key=lambda x: x[1]["seed"]):
            pk = r["per_k"][kh]
            s, nm, kk, e, t = pk["structural_bits"], pk["naming_bits"], pk["kind_kl_bits"], pk["end_bits"], pk["token_bits"]
            out.append(f"| {cell} | {r['seed']} | {r['step']} | {s['n']} | {s['mean']:.4f} ± {s['se']:.4f} | {nm['mean']:.4f} ± {nm['se']:.4f} | "
                       f"{kk['mean']:.4f} | {e['mean']:.4f} | {t['mean']:.4f} |")
            for key, v in (("structural", s), ("naming", nm), ("kind_kl", kk), ("end", e), ("token", t)):
                vals[key].append(v["mean"])
            vals["within_se"].append(s["se"])
        n = len(vals["structural"])
        if n:
            mean = sum(vals["structural"]) / n
            sd = math.sqrt(sum((x - mean) ** 2 for x in vals["structural"]) / (n - 1)) if n > 1 else float("nan")
            pooled[cell] = dict(n_seeds=n, structural_mean=mean, between_seed_sd=sd, pooled_se=(sd / math.sqrt(n) if n > 1 else float("nan")),
                                within_se=sum(vals["within_se"]) / n, naming_mean=sum(vals["naming"]) / n,
                                kind_kl_mean=sum(vals["kind_kl"]) / n, end_mean=sum(vals["end"]) / n)
    out.append("")
    out.append(f"| cell | seeds | structural mean | between-seed sd | pooled se | within-seed se | seeds for se ≤ δ/3 | naming mean | kind KL | end |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for cell, p in pooled.items():
        need = math.ceil((p["between_seed_sd"] / (0.01 / 3)) ** 2) if p["between_seed_sd"] == p["between_seed_sd"] and p["between_seed_sd"] > 0 else 1
        out.append(f"| {cell} | {p['n_seeds']} | {p['structural_mean']:.4f} | {p['between_seed_sd']:.4f} | {p['pooled_se']:.4f} | {p['within_se']:.4f} | "
                   f"{max(3, need)} | {p['naming_mean']:.4f} | {p['kind_kl_mean']:.4f} | {p['end_mean']:.4f} |")
    # per-k curves (structural), one row per raw
    ks = sorted({int(k) for _, r in rows for k in r["per_k"]})
    if ks:
        out.append("")
        out.append("| cell | seed | " + " | ".join(f"k={k}" for k in ks) + " |")
        out.append("|---|---|" + "---|" * len(ks))
        for cell in sorted(by_cell):
            for p, r in sorted(by_cell[cell], key=lambda x: x[1]["seed"]):
                cells = []
                for k in ks:
                    pk = r["per_k"].get(str(k))
                    cells.append(f"{pk['structural_bits']['mean']:.4f}" if pk and pk["structural_bits"]["mean"] is not None else "—")
                out.append(f"| {cell} | {r['seed']} | " + " | ".join(cells) + " |")
    text = "\n".join(out) + "\n"
    print(text)
    if a.md:
        open(a.md, "w").write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
