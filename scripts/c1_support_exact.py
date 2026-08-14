"""Exact C1 windowed mean/max support — exhaustive, no sampling.

(run: python scripts/c1_support_exact.py [out.json])

Replaces the biased means of c1_support_experiment.py v1 (which kept
law weights but renormalized over a stride sample — an estimator of
nothing; external review finding, Codex, Aug 14). Method: one pass of
path aggregation per (ε, rung, T) — group full episode paths by
(reset_observed, projected window), accumulate law mass and the set of
final states across all compatible endpoints. A window's posterior
support is exactly the number of distinct final states with nonzero
matched mass (all masses are positive rationals), so

    E[support] = Σ_windows P(window) · |support(window)|

is computed exactly, over every window the law can produce, with the
RESET partition (a reset window never shares a key with a resetless one).
This is the window_enumerator's aggregation, used for the support metric
only; the filter/enumerator agreement is established by the gate tests.
Budget instrumentation (worst step transitions/wall) is not recomputed
here — those came from instrumented filter runs and were verified
separately.
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

LAW = WindowLaw(T_ep=12, L=6, B=2)
EPS_GRID = (Fraction(1), Fraction(1, 2))
RUNGS = ("r1", "r2", "r3", "r4")


def main():
    results = []
    for eps in EPS_GRID:
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(LAW)
        path_cache = {T: paths(cfg, progs, T) for T in LAW.endpoints()}
        for rung in RUNGS:
            agg = {}  # (reset, window) -> [mass, set(final states)]
            for T in LAW.endpoints():
                u = LAW.offset(T)
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
                f"E[supp]={row['mean_support']:.4f}  max={mx}",
                flush=True,
            )
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(dict(law=dict(T_ep=LAW.T_ep, L=LAW.L, B=LAW.B), rows=results), f, indent=2)
        print(f"raw JSON -> {sys.argv[1]}", flush=True)


if __name__ == "__main__":
    main()
