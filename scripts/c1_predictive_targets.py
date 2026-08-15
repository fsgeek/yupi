"""P-next, P-horizon functionals, and the divergent-history search for C1.

(run: python scripts/c1_predictive_targets.py T_ep L B [out.json])

Windows by path aggregation; per-state functionals via `predict`
(one memo per eps); per window the (total, irreducible, gap) split of
each functional; divergent-pair search per (eps, rung): windows grouped
by exact P-next mixture, pairs within a group with unequal mixture on
any tau. m=2, W=4 frozen (note v0.1).
"""

import json
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import combinations

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import q4_mixture, split_entropy
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, p_next, time_to_wake
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")
M, W = 2, 4


def freeze(d):
    return frozenset(d.items())


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), m=M, W=W, rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        memo_k, memo_w, memo_l = {}, {}, {}
        fn_state = {}   # state -> {tau: dist}
        pnext_state = {}  # (state, rung) -> dist
        for rung in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
            taus = ("kinds2", "ttw4", "lineage4")
            means = {t: [0.0, 0.0, 0.0] for t in taus + ("pnext",)}
            groups = defaultdict(list)  # pnext mixture -> [(key, mass, {tau: mixture})]
            for key, joint in agg.items():
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
            # divergent search: within a P-next group, class windows by their
            # tau-mixture signature; divergent pairs are pairs of DISTINCT
            # classes (window pairs = sum n_a*n_b, no enumeration).
            n_pairs = 0
            n_class_pairs = 0
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
                    for i, t in enumerate(taus):
                        if sa[i] != sb[i]:
                            sep_by_tau[t] += len(wa) * len(wb)
                for _, ws in items:
                    for key, mass in ws:
                        if key not in windows_in:
                            windows_in.add(key)
                            mass_in += mass
            mass_in = float(mass_in)
            row = dict(eps=str(eps), rung=rung, n_windows=len(agg),
                       n_pnext_classes=len(groups),
                       means={t: dict(total=v[0], irreducible=v[1], gap=v[2]) for t, v in means.items()},
                       divergent=dict(pairs=n_pairs, class_pairs=n_class_pairs, windows=len(windows_in), mass=mass_in, separated_by=sep_by_tau))
            out["rows"].append(row)
            print(f"eps={row['eps']:>3} {rung} n={len(agg):>6} pnext-classes={len(groups):>5} "
                  f"pnext(tot/irr/gap)={means['pnext'][0]:.4f}/{means['pnext'][1]:.4f}/{means['pnext'][2]:.4f} "
                  f"kinds2 gap={means['kinds2'][2]:.4f} ttw4 gap={means['ttw4'][2]:.4f} lin4 gap={means['lineage4'][2]:.4f} | "
                  f"divergent pairs={n_pairs} windows={len(windows_in)} mass={mass_in:.4f} by={sep_by_tau}", flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
