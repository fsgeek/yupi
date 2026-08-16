"""Divergent mass on the (observer rung × predicted-record rung) grid — EXPLORATORY (Aug 16 2026).

(run: python scripts/c1_divergent_grid.py T_ep L B [out.json])

P-next in c1_predictive_targets is diagonal: a rung-r observer predicts a
rung-r next record. This script crosses the two: r_obs = rung of the window
partition (what the observer saw); r_pred = rung of the next record whose
distribution it predicts. Divergent pair (as before): same P-next mixture
(exact), unequal mixture on some tau (kinds2/ttw4/lineage4; m=2, W=4).

Pre-stated (before first run):
  G1 (theorem) at fixed r_obs, divergent mass is NON-INCREASING in r_pred:
     equal fine-record P-next implies equal coarse-record P-next
     (pushforward), and the tau criterion does not involve r_pred, so the
     divergent-pair set is nested. A violation is a code bug.
  G2 at fixed r_pred, mass rises r_obs r1->r4 (not necessarily monotone);
     r_obs r3->r4 increment ~0 at (12,2,2).
  G3 the diagonal r3->r4 dip at (12,2,2) = (~0 from the r_obs step) +
     (<0 from the r_pred step).
"""

import json
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import combinations

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import q4_mixture
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, p_next, time_to_wake
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")
M, W = 2, 4
TAUS = ("kinds2", "ttw4", "lineage4")


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
        fn_state, pnext_state = {}, {}
        grid = {}
        for r_obs in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, r_obs) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
            windows = []
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
                mixes = tuple(freeze(q4_mixture(belief, {s: fn_state[s][t] for s in belief})) for t in TAUS)
                windows.append((key, mass, belief, mixes))
            for r_pred in RUNGS:
                groups = defaultdict(list)
                for key, mass, belief, mixes in windows:
                    for s in belief:
                        if (s, r_pred) not in pnext_state:
                            pnext_state[(s, r_pred)] = p_next(s, cfg, progs, r_pred)
                    pn = freeze(q4_mixture(belief, {s: pnext_state[(s, r_pred)] for s in belief}))
                    groups[pn].append((key, mass, mixes))
                seen, mass_in, n_pairs = set(), Fraction(0), 0
                for g in groups.values():
                    if len(g) < 2:
                        continue
                    classes = defaultdict(list)
                    for key, mass, mixes in g:
                        classes[mixes].append((key, mass))
                    if len(classes) < 2:
                        continue
                    items = list(classes.values())
                    for wa, wb in combinations(items, 2):
                        n_pairs += len(wa) * len(wb)
                    for ws in items:
                        for key, mass in ws:
                            if key not in seen:
                                seen.add(key)
                                mass_in += mass
                grid[(r_obs, r_pred)] = (float(mass_in), n_pairs, len(seen))
                out["rows"].append(dict(eps=str(eps), r_obs=r_obs, r_pred=r_pred,
                                        n_windows=len(agg), div_mass=float(mass_in),
                                        pairs=n_pairs, windows_in=len(seen)))
        print(f"eps={eps}  divergent mass, rows=r_obs, cols=r_pred (pairs)")
        print("        " + "".join(f"{r:>18}" for r in RUNGS))
        for r_obs in RUNGS:
            print(f"  {r_obs}  " + "".join(f"{grid[(r_obs, r_pred)][0]:>10.4f} ({grid[(r_obs, r_pred)][1]:>4})" for r_pred in RUNGS))
        # G1 check
        viol = [(r_obs, RUNGS[i], RUNGS[i + 1]) for r_obs in RUNGS for i in range(3)
                if grid[(r_obs, RUNGS[i + 1])][0] > grid[(r_obs, RUNGS[i])][0] + 1e-12]
        print(f"  G1 (non-increasing in r_pred) violations: {viol}", flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
