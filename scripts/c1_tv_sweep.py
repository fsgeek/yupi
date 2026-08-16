"""(δ_p, Δ_τ) sweep — Part II v0.2.4 §C, sweep 3 of 3.

(run: python scripts/c1_tv_sweep.py T_ep L B [out.json])

Part II §5 (v0.2.4 §D form): two histories h, h' under one condition are
(δ_p, Δ_τ)-divergent if TV(P-next(h), P-next(h')) ≤ δ_p and, for some
τ ∈ 𝒯, TV(τ(h), τ(h')) ≥ Δ_τ; prevalence = pair_prob, the probability
that two law-weighted draws form such a pair. Neither threshold is
frozen. This script computes, per (ε, rung) at one WindowLaw, the
mass-weighted DISTRIBUTIONS of pairwise TV between windows' P-next
mixtures and between their τ mixtures, and the pair_prob surface over a
(δ_p, Δ_τ) grid — the sensitivity curves the second stamped decision
needs. It is a sweep, not a ceiling: TVs are floats (mixtures are exact
Fractions, converted once); the exact δ_p = 0 corner is ALSO computed
from Fraction equality and cross-checked against
scripts/c1_predictive_targets.py's pair_prob (same recursion, same
classes) — that equality is this script's gate.

Method: windows → belief over final states (path aggregation, as in the
predictive-targets script) → P-next mixture at the rung and τ mixtures
(kinds2, ttw4, lineage4; m=2, W=4 per Part II v0.2.4) → windows collapse
to CLASSES keyed by the 4-tuple of exact mixtures, each with its law
mass. Pairs of classes (a<b) weighted 2·m_a·m_b give every window pair
with the two windows in different classes; pairs within a class have all
TVs zero and never qualify. Pairwise TVs are computed in pure Python over
sparse float dicts (class counts are hundreds to low thousands).
"""

import json
import sys
from collections import defaultdict
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import q4_mixture
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, p_next, time_to_wake
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")
M, W = 2, 4                                   # Part II v0.2.4 §5 (frozen)
TAUS = ("kinds2", "ttw4", "lineage4")
DP_GRID = [0.0, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1]
DT_GRID = [1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 5e-1]
CDF_GRID = [0.0, 1e-6, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 2e-1, 3e-1, 5e-1, 7e-1, 1.0]


def freeze(d):
    return frozenset(d.items())


def fdict(m):
    return {k: float(v) for k, v in dict(m).items()}


def tv(a, b):
    """Total variation between two float dicts (sparse)."""
    s = 0.0
    for k, v in a.items():
        s += abs(v - b.get(k, 0.0))
    for k, v in b.items():
        if k not in a:
            s += v
    return 0.5 * s


def bisect_bin(grid, x):
    """Index of the first grid value >= x (grid ascending), clipped."""
    for i, g in enumerate(grid):
        if x <= g + 1e-12:
            return i
    return len(grid) - 1


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), m=M, W=W,
               dp_grid=DP_GRID, dt_grid=DT_GRID, cdf_grid=CDF_GRID, rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        memo_k, memo_w, memo_l = {}, {}, {}
        fn_state, pnext_state = {}, {}
        for rung in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
            classes = defaultdict(lambda: [Fraction(0), 0])   # key -> [mass, n_windows]
            for key, joint in agg.items():
                mass = sum(joint.values(), Fraction(0))
                belief = {s: m / mass for s, m in joint.items()}
                for s in belief:
                    if s not in fn_state:
                        fn_state[s] = dict(
                            kinds2=next_kinds(s, cfg, progs, M, memo_k),
                            ttw4=time_to_wake(s, cfg, progs, W, memo_w),
                            lineage4=next_complete_lineage(s, cfg, progs, W, memo_l))
                    if (s, rung) not in pnext_state:
                        pnext_state[(s, rung)] = p_next(s, cfg, progs, rung)
                pn = freeze(q4_mixture(belief, {s: pnext_state[(s, rung)] for s in belief}))
                tm = tuple(freeze(q4_mixture(belief, {s: fn_state[s][t] for s in belief}))
                           for t in TAUS)
                c = classes[(pn,) + tm]
                c[0] += mass
                c[1] += 1
            keys = list(classes.keys())
            masses = [float(classes[k][0]) for k in keys]
            n_cls = len(keys)
            # exact δ_p = 0 corner from Fraction equality (gate vs predictive-targets)
            by_pn = defaultdict(list)
            for i, k in enumerate(keys):
                by_pn[k[0]].append(i)
            exact_pair_prob = Fraction(0)
            for idxs in by_pn.values():
                if len(idxs) < 2:
                    continue
                ms = [classes[keys[i]][0] for i in idxs]
                tot = sum(ms, Fraction(0))
                exact_pair_prob += tot * tot - sum(m * m for m in ms)   # 2·Σ_{a<b} m_a m_b
            # float mixtures per class
            fp = [fdict(k[0]) for k in keys]
            ft = [[fdict(k[1 + j]) for k in keys] for j in range(len(TAUS))]
            nD, nT, nC = len(DP_GRID), len(DT_GRID), len(CDF_GRID)
            surface = [[0.0] * nT for _ in range(nD)]
            surface_by_tau = [[[0.0] * nT for _ in range(nD)] for _ in TAUS]
            cdf_p = [0.0] * nC
            cdf_t = [0.0] * nC
            joint_bins = [[0.0] * nC for _ in range(nC)]
            total_pair_mass = 0.0
            for i in range(n_cls - 1):
                mi = masses[i]
                fpi = fp[i]
                fti = [ft[j][i] for j in range(len(TAUS))]
                for k2 in range(i + 1, n_cls):
                    w = 2.0 * mi * masses[k2]
                    total_pair_mass += w
                    tvp = tv(fpi, fp[k2])
                    tvts = [tv(fti[j], ft[j][k2]) for j in range(len(TAUS))]
                    tvt_max = max(tvts)
                    for a, dp in enumerate(DP_GRID):
                        if tvp > dp + 1e-12:
                            continue          # qualifies only for grid values >= its TV
                        for b, dt in enumerate(DT_GRID):
                            if tvt_max >= dt - 1e-12:
                                surface[a][b] += w
                            for j in range(len(TAUS)):
                                if tvts[j] >= dt - 1e-12:
                                    surface_by_tau[j][a][b] += w
                    for a, x in enumerate(CDF_GRID):
                        if tvp <= x + 1e-12:
                            cdf_p[a] += w
                        if tvt_max <= x + 1e-12:
                            cdf_t[a] += w
                    joint_bins[bisect_bin(CDF_GRID, tvp)][bisect_bin(CDF_GRID, tvt_max)] += w
            distinct_pair_mass = 1.0 - float(sum(m * m for m in (classes[k][0] for k in keys)))
            row = dict(eps=str(eps), rung=rung, n_windows=len(agg), n_classes=n_cls,
                       n_pnext_classes=len(by_pn),
                       exact_corner_pair_prob=float(exact_pair_prob),
                       distinct_class_pair_mass=distinct_pair_mass,
                       total_pair_mass_numeric=total_pair_mass,
                       cdf_tv_pnext=cdf_p, cdf_tv_tau_max=cdf_t,
                       joint_bins=joint_bins,
                       surface=surface,
                       surface_by_tau={t: surface_by_tau[j] for j, t in enumerate(TAUS)})
            out["rows"].append(row)
            print(f"\neps={row['eps']:>3} {rung} windows={len(agg)} classes={n_cls} "
                  f"pnext-classes={len(by_pn)} distinct-class pair mass={distinct_pair_mass:.4f} "
                  f"(numeric {total_pair_mass:.4f}); exact δp=0 corner pair_prob={float(exact_pair_prob):.3e}")
            print("  CDF of TV(P-next) over class pairs (mass):  " +
                  " ".join(f"{x:g}:{v:.3f}" for x, v in zip(CDF_GRID, cdf_p)))
            print("  CDF of max_tau TV over class pairs (mass):  " +
                  " ".join(f"{x:g}:{v:.3f}" for x, v in zip(CDF_GRID, cdf_t)))
            print("  pair_prob(δp, Δτ) surface  rows=δp " + str(DP_GRID) + " cols=Δτ " + str(DT_GRID))
            for a, dp in enumerate(DP_GRID):
                print(f"   δp={dp:<6g} " + " ".join(f"{v:.2e}" for v in surface[a]))
            sys.stdout.flush()
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {sys.argv[4]}")


if __name__ == "__main__":
    main()
