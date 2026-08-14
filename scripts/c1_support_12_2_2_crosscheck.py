"""Two-path cross-check of the (12,2,2) support table (day six).

(run: python scripts/c1_support_12_2_2_crosscheck.py)

The (12,2,2) table of c1_support_at_law.py is a path-aggregation result
(window_enumerator's side of the firewall). This script recomputes every
distinct window's posterior through `window_filter` (the recursive-mixture
side, which shares only the world definition and the window law) and
requires: (a) each window's state-marginal support equals the
path-aggregation support exactly, and (b) E[support] rebuilt from
filter-side supports with law masses equals the table. Any mismatch is a
hard failure. All 971 distinct windows (186+209+283+293), both eps.
"""

from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import filter_window

LAW = WindowLaw(12, 2, 2)
RUNGS = ("r1", "r2", "r3", "r4")


def main():
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(LAW)
        path_cache = {T: paths(cfg, progs, T) for T in LAW.endpoints()}
        for rung in RUNGS:
            agg = {}
            for T in LAW.endpoints():
                u = LAW.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    if key not in agg:
                        agg[key] = [Fraction(0), set()]
                    agg[key][0] += w_T * prob
                    agg[key][1].add(final)

            mismatches = 0
            mean_filter = Fraction(0)
            for (reset, window), (mass, finals) in agg.items():
                post = filter_window(
                    cfg, progs, LAW, list(window), rung, reset
                )
                supp = sum(
                    1 for m in post.state_marginal().values() if m > 0
                )
                if supp != len(finals):
                    mismatches += 1
                    print(
                        f"  MISMATCH {rung} eps={eps}: "
                        f"filter={supp} paths={len(finals)}"
                    )
                mean_filter += mass * supp
            print(
                f"eps={str(eps):>3} {rung}: {len(agg)} windows, "
                f"mismatches={mismatches}, "
                f"E[supp] via filter = {float(mean_filter):.6f}",
                flush=True,
            )
            assert mismatches == 0


if __name__ == "__main__":
    main()
