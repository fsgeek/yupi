"""Window uncertainty: offset (where am I) vs. state (what did the world do) — EXPLORATORY (Aug 17 2026).

(run: python scripts/c1_offset_vs_state.py T_ep L B [out.json])

Question (raised in review): under truncated, offset-unanchored windows, is the
posterior uncertainty "mostly about where in the trajectory the window sits"
(offset U) rather than about the world state S_T? Open thread 6 of
instrument-status-2026-08-14 deferred this decomposition. Per window w
(same construction as c1_predictive_targets), joint posterior over (U, S_T):
  H(U|w)        offset uncertainty
  H(S_T|w)      state uncertainty (the quantity queries live on)
  H(S_T|w,U)    state uncertainty GIVEN the position = Σ_u P(u|w) H(S_T|w,u)
  I(U;S_T|w)  = H(S_T|w) − H(S_T|w,U)
Law-mass-weighted means, per rung and ε. If H(S_T|w,U) ≈ H(S_T|w), the
uncertainty is about the unobserved prefix's dynamics, not the clock.
No predictions pre-stated: this is a decomposition of a measured quantity, run
to adjudicate a factual claim made in review; the two-path window machinery
already gates the posteriors themselves.
"""
import json, sys, math
from collections import defaultdict
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")

def H(dist):
    tot = sum(dist.values(), Fraction(0))
    return -sum(float(p / tot) * math.log2(float(p / tot)) for p in dist.values() if p > 0)

def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps); progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        for rung in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    agg.setdefault(key, defaultdict(Fraction))[(u, final)] += w_T * prob
            hU = hS = hSU = 0.0
            for key, joint in agg.items():
                mass = float(sum(joint.values(), Fraction(0)))
                offs = defaultdict(Fraction); states = defaultdict(Fraction); by_u = defaultdict(lambda: defaultdict(Fraction))
                for (u, s), m in joint.items():
                    offs[u] += m; states[s] += m; by_u[u][s] += m
                hU += mass * H(offs); hS += mass * H(states)
                tot = sum(joint.values(), Fraction(0))
                hSU += mass * sum(float(offs[u] / tot) * H(by_u[u]) for u in by_u)
            row = dict(eps=str(eps), rung=rung, n_windows=len(agg), H_U=hU, H_S=hS, H_S_given_U=hSU, I_U_S=hS - hSU,
                       frac_state_given_pos=(hSU / hS if hS > 0 else None))
            out["rows"].append(row)
            print(f"eps={row['eps']:>3} {rung} n={len(agg):>5} H(U|w)={hU:.4f} H(S|w)={hS:.4f} H(S|w,U)={hSU:.4f} "
                  f"I(U;S|w)={hS-hSU:.4f} H(S|w,U)/H(S|w)={row['frac_state_given_pos'] if row['frac_state_given_pos'] is None else round(row['frac_state_given_pos'],3)}", flush=True)
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], "w"), indent=2); print(f"raw JSON -> {sys.argv[4]}")

if __name__ == "__main__":
    main()
