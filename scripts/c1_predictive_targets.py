"""P-next, P-horizon functionals, and the divergent-history search for C1.

(run: python scripts/c1_predictive_targets.py T_ep L B [out.json];
 YUPI_AGG=paths (default) | window (the window-process recursion, 2026-09-04);
 YUPI_RUNGS default r1,r2,r3,r4; YUPI_PROGRAMS default c1; ε grid from
 yupi.eps_grid)

v0.2 (day seven, second truthsayer pass): adds pair_prob — the probability
that two independent law-weighted window draws form a divergent pair — and
tv_pair_prob, the same weighted by the largest total-variation distance
among the differing tau mixtures. `class_pairs` counts pairs of distinct
joint tau-signature classes within a P-next class (NOT state pairs).

Windows by path aggregation; per-state functionals via `predict`
(one memo per eps); per window the (total, irreducible, gap) split of
each functional; divergent-pair search per (eps, rung): windows grouped
by exact P-next mixture, pairs within a group with unequal mixture on
any tau. m=2, W=4 (primary; W=8 secondary) were EXPLORATORY selections
when this script's day-seven runs were made; frozen at Part II v0.2.4
(2026-08-15, enacted from docs/part2-amendment-proposal-v0.2.4.md). Runs
before that stamp are exploratory; runs after it are confirmatory w.r.t.
m/W/T (thresholds still await the second stamped decision).
"""

import json
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import combinations

from yupi.config import WorldConfig
from yupi.aggregation import aggregate_by_rung
from yupi.eps_grid import eps_grid
from yupi.forecast import q4_mixture, split_entropy
from yupi.predict import next_complete_lineage, next_kinds, p_next, time_to_wake
from yupi.programs import programs_for
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")
M, W = 2, 4


def freeze(d):
    return frozenset(d.items())


def _tv(a, b):
    keys = set(a) | set(b)
    return sum(abs(a.get(k, Fraction(0)) - b.get(k, Fraction(0))) for k in keys) / 2


def compute_rows(law, eps, cfg, progs, rungs, agg="paths"):
    """One ε: per-rung rows (P-next and τ-family splits, divergent-pair
    search), windows from `aggregate_by_rung` in the chosen mode."""
    by_rung = aggregate_by_rung(cfg, progs, law, rungs, agg)
    memo_k, memo_w, memo_l = {}, {}, {}
    fn_state = {}   # state -> {tau: dist}
    pnext_state = {}  # (state, rung) -> dist
    rows = []
    for rung in rungs:
        agg_r, _ = by_rung[rung]
        taus = ("kinds2", "ttw4", "lineage4")
        means = {t: [0.0, 0.0, 0.0] for t in taus + ("pnext",)}
        groups = defaultdict(list)  # pnext mixture -> [(key, mass, {tau: mixture})]
        for key, joint in agg_r.items():
            mass = sum(joint.values(), Fraction(0))
            belief = {s: m / mass for s, m in joint.items()}
            for s in belief:
                if s not in fn_state:
                    fn_state[s] = dict(
                        kinds2=next_kinds(s, cfg, progs, M, memo_k),
                        ttw4=time_to_wake(s, cfg, progs, W, memo_w),
                        lineage4=next_complete_lineage(s, cfg, progs, W, memo_l),
                    )
                if (s, rung) not in pnext_state:
                    pnext_state[(s, rung)] = p_next(s, cfg, progs, rung)
            mixes = {}
            for t in taus:
                per = {s: fn_state[s][t] for s in belief}
                tot, irr, gap = split_entropy(belief, per)
                for i, v in enumerate((tot, irr, gap)):
                    means[t][i] += float(mass) * v
                mixes[t] = freeze(q4_mixture(belief, per))
            per = {s: pnext_state[(s, rung)] for s in belief}
            tot, irr, gap = split_entropy(belief, per)
            for i, v in enumerate((tot, irr, gap)):
                means["pnext"][i] += float(mass) * v
            groups[freeze(q4_mixture(belief, per))].append((key, mass, mixes))
        n_pairs = 0
        n_class_pairs = 0
        pair_prob = Fraction(0)
        tv_pair_prob = Fraction(0)
        sep_by_tau = {t: 0 for t in taus}
        windows_in = set()
        mass_in = Fraction(0)
        for g in groups.values():
            if len(g) < 2:
                continue
            classes = defaultdict(list)
            for key, mass, mixes in g:
                classes[tuple(mixes[t] for t in taus)].append((key, mass))
            if len(classes) < 2:
                continue
            items = list(classes.items())
            for (sa, wa), (sb, wb) in combinations(items, 2):
                n_class_pairs += 1
                n_pairs += len(wa) * len(wb)
                ma = sum((m for _, m in wa), Fraction(0))
                mb = sum((m for _, m in wb), Fraction(0))
                pair_prob += 2 * ma * mb
                tv = max(_tv(dict(sa[i]), dict(sb[i])) for i in range(len(taus)))
                tv_pair_prob += 2 * ma * mb * tv
                for i, t in enumerate(taus):
                    if sa[i] != sb[i]:
                        sep_by_tau[t] += len(wa) * len(wb)
            for _, ws in items:
                for key, mass in ws:
                    if key not in windows_in:
                        windows_in.add(key)
                        mass_in += mass
        mass_in = float(mass_in)
        rows.append(dict(eps=str(eps), rung=rung, n_windows=len(agg_r),
                         n_pnext_classes=len(groups),
                         means={t: dict(total=v[0], irreducible=v[1], gap=v[2]) for t, v in means.items()},
                         divergent=dict(pairs=n_pairs, class_pairs=n_class_pairs, windows=len(windows_in), mass=mass_in,
                                        pair_prob=float(pair_prob), tv_pair_prob=float(tv_pair_prob), separated_by=sep_by_tau),
                         aggregation=agg))
    return rows


def main():
    import os
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    agg = os.environ.get("YUPI_AGG", "paths")
    rungs = tuple(os.environ.get("YUPI_RUNGS", "r1,r2,r3,r4").split(","))
    programs_name = os.environ.get("YUPI_PROGRAMS", "c1")
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), m=M, W=W, aggregation=agg, programs=programs_name, rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        for row in compute_rows(law, eps, cfg, programs_for(programs_name), rungs, agg):
            out["rows"].append(row)
            m = row["means"]; dv = row["divergent"]
            print(f"eps={row['eps']:>3} {row['rung']} n={row['n_windows']:>6} pnext-classes={row['n_pnext_classes']:>5} "
                  f"pnext(tot/irr/gap)={m['pnext']['total']:.4f}/{m['pnext']['irreducible']:.4f}/{m['pnext']['gap']:.4f} "
                  f"kinds2 gap={m['kinds2']['gap']:.4f} ttw4 gap={m['ttw4']['gap']:.4f} lin4 gap={m['lineage4']['gap']:.4f} | "
                  f"divergent pairs={dv['pairs']} windows={dv['windows']} mass={dv['mass']:.4f} pair_prob={dv['pair_prob']:.3e} "
                  f"tv_pair_prob={dv['tv_pair_prob']:.3e} by={dv['separated_by']}", flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
