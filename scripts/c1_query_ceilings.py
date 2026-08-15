"""Exact query ceilings (Q1–Q5) for C1 at a parameterized WindowLaw.

(run: python scripts/c1_query_ceilings.py T_ep L B [out.json])

Method: path aggregation by (reset_observed, projected window) → law mass
and belief over final states per window (enumerator side); every distinct
window ALSO recomputed through `window_filter` and its joint (U, S_T)
compared Fraction-for-Fraction (filter side) — the two-path gate, applied
before any query is pushed forward. Then each query's answer distribution
is the pushforward of the window's state marginal; the reported figure is
the law-mass-weighted mean entropy in bits, per (eps, rung, query), plus
the mean state entropy and the fraction of law mass on which the query is
fully resolved (H = 0). Invariants asserted: rung monotonicity per query,
H(Q|w) <= H(S|w) per window.
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.queries import (
    all_queries, entropy_bits, pushforward, state_entropy_bits,
)
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import filter_window

RUNGS = ("r1", "r2", "r3", "r4")


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        queries = all_queries(cfg)
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        prev_mean = None
        for rung in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[(u, final)] = d.get((u, final), Fraction(0)) + w_T * prob
            total_mass = sum(
                (sum(j.values(), Fraction(0)) for j in agg.values()), Fraction(0)
            )
            assert total_mass == 1

            mean_H = {name: 0.0 for name, _ in queries}
            resolved = {name: Fraction(0) for name, _ in queries}
            mean_HS = 0.0
            mismatches = 0
            for (reset, window), joint_mass in agg.items():
                mass = sum(joint_mass.values(), Fraction(0))
                path_joint = {k: m / mass for k, m in joint_mass.items()}
                post = filter_window(cfg, progs, law, list(window), rung, reset)
                filter_joint = {
                    (u, s): w * m
                    for u, (w, belief) in post.components.items()
                    for s, m in belief.items()
                    if w * m > 0
                }
                if filter_joint != path_joint:
                    mismatches += 1
                    continue
                belief = {}
                for (_, s), m in path_joint.items():
                    belief[s] = belief.get(s, Fraction(0)) + m
                HS = state_entropy_bits(belief)
                mean_HS += float(mass) * HS
                for name, fn in queries:
                    H = entropy_bits(pushforward(belief, fn))
                    assert H <= HS + 1e-9, (name, H, HS)
                    mean_H[name] += float(mass) * H
                    if H == 0.0:
                        resolved[name] += mass
            assert mismatches == 0, f"two-path mismatches: {mismatches}"
            if prev_mean is not None:
                for name in mean_H:
                    assert mean_H[name] <= prev_mean[name] + 1e-9, (rung, name)
            prev_mean = mean_H
            row = dict(
                eps=str(eps), rung=rung, n_windows=len(agg),
                mean_state_entropy_bits=mean_HS,
                queries={
                    name: dict(mean_bits=mean_H[name],
                               resolved_mass=float(resolved[name]))
                    for name in mean_H
                },
            )
            out["rows"].append(row)
            qs = "  ".join(f"{n}={mean_H[n]:.4f}" for n in mean_H)
            print(f"eps={row['eps']:>3} {rung} n={len(agg):>6} "
                  f"H(S)={mean_HS:.4f}  {qs}", flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
