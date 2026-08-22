"""Where does the observer step's divergent mass actually come from?

Ledger, per (eps, r_obs step) at fixed r_pred: decompose the change in
divergent mass into
  LOST      pairs divergent at coarse whose piece-pairs are not all divergent
  KEPT      coarse pair mass that survives as fine cross-piece pairs
  NEW_CROSS fine divergent pairs whose parents were NOT a divergent pair
  NEW_WITHIN fine divergent pairs sharing a parent (impossible at coarse)
Divergent = exact P-next equality + some tau differing (delta=0 corner).
"""
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
M, W = 2, 4
TAUS = ("kinds2", "ttw4", "lineage4")
freeze = lambda d: frozenset(d.items())

def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    r_pred = sys.argv[4] if len(sys.argv) > 4 else "r1"
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    print(f"law ({T_ep},{L},{B})  r_pred={r_pred}  (mass = sum 2*m_a*m_b over divergent pairs)")
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps); progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        mk, mw, ml = {}, {}, {}
        fn, pn_s = {}, {}
        agg = {}
        parent = {}
        for rung in RUNGS:
            a = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    a.setdefault(key, {})
                    a[key][final] = a[key].get(final, Fraction(0)) + w_T * prob
            agg[rung] = a
        for i in range(len(RUNGS) - 1):
            cr, fr = RUNGS[i], RUNGS[i + 1]
            pmap = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    pmap[(u == 0, tuple(project(r, fr) for r in recs[u:]))] = \
                        (u == 0, tuple(project(r, cr) for r in recs[u:]))
            def sig(joint):
                mass = sum(joint.values(), Fraction(0))
                bel = {s: m / mass for s, m in joint.items()}
                for s in bel:
                    if s not in fn:
                        fn[s] = dict(kinds2=next_kinds(s, cfg, progs, M, mk),
                                     ttw4=time_to_wake(s, cfg, progs, W, mw),
                                     lineage4=next_complete_lineage(s, cfg, progs, W, ml))
                    if (s, r_pred) not in pn_s:
                        pn_s[(s, r_pred)] = p_next(s, cfg, progs, r_pred)
                return (mass, freeze(q4_mixture(bel, {s: pn_s[(s, r_pred)] for s in bel})),
                        tuple(freeze(q4_mixture(bel, {s: fn[s][t] for s in bel})) for t in TAUS))
            C = {k: sig(j) for k, j in agg[cr].items()}
            F_ = {k: sig(j) for k, j in agg[fr].items()}
            def pairs(D):
                ks = list(D); out = {}
                for a in range(len(ks)):
                    for b in range(a + 1, len(ks)):
                        ma, pa, ta = D[ks[a]]; mb, pb, tb = D[ks[b]]
                        if pa == pb and ta != tb:
                            out[(ks[a], ks[b])] = 2 * ma * mb
                return out
            cp, fp = pairs(C), pairs(F_)
            cmass, fmass = sum(cp.values(), Fraction(0)), sum(fp.values(), Fraction(0))
            kept = new_cross = new_within = Fraction(0)
            for (a, b), m in fp.items():
                pa, pb = pmap[a], pmap[b]
                if pa == pb: new_within += m
                elif (pa, pb) in cp or (pb, pa) in cp: kept += m
                else: new_cross += m
            lost = Fraction(0)
            for (a, b), m in cp.items():
                surv = sum(mm for (x, y), mm in fp.items()
                           if {pmap[x], pmap[y]} == {a, b})
                lost += m - surv
            g = lambda x: float(x)
            print(f" eps={str(eps):>3} {cr}->{fr}: coarse {g(cmass):.6f} -> fine {g(fmass):.6f} "
                  f"({g(fmass-cmass):+.6f})  | kept {g(kept):.6f} lost {g(lost):.6f} "
                  f"new-cross {g(new_cross):.6f} new-within {g(new_within):.6f}")
        sys.stdout.flush()

main()
