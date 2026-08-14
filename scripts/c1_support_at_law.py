"""Exact C1 windowed mean/max support at a parameterized WindowLaw.

(run: python scripts/c1_support_at_law.py T_ep L B [out.json])

Generalizes c1_support_exact.py (which is kept frozen at the day-five law
it documents) to an arbitrary law on the command line. Same method,
verbatim: one pass of path aggregation per (eps, rung, T) — group episode
paths by (reset_observed, projected window), accumulate law mass and the
set of final states over all compatible endpoints; E[support] is exact
over the full law with the RESET partition.

Regression (run before first use, day six): at (12,6,2) this script
reproduces the cross-verified v0.3 table of c1-support-measurement-v0.1.md
in all 16 cells. The (12,2,2) table it produced was independently
cross-checked against `window_filter` (recursive-mixture side of the
two-path firewall): every distinct window's state-marginal support and
both means matched exactly (see c1-rung-separation-geometry-v0.1.md).
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    results = []
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        for rung in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    if key not in agg:
                        agg[key] = [Fraction(0), set()]
                    agg[key][0] += w_T * prob
                    agg[key][1].add(final)
            total = sum((m for m, _ in agg.values()), Fraction(0))
            assert total == 1  # every window the law produces is covered
            mean = sum((m * len(s) for m, s in agg.values()), Fraction(0))
            mx = max(len(s) for _, s in agg.values())
            row = dict(
                eps=str(eps), rung=rung, n_windows=len(agg),
                mean_support_exact=str(mean), mean_support=float(mean),
                max_support=mx,
            )
            results.append(row)
            print(
                f"eps={row['eps']:>3} {rung}  n={row['n_windows']:>6}  "
                f"E[supp]={row['mean_support']:.6f}  max={mx}",
                flush=True,
            )
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(
                dict(law=dict(T_ep=T_ep, L=L, B=B), rows=results), f, indent=2
            )
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
