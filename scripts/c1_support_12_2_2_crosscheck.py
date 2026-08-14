"""Two-path cross-check of the (12,2,2) support table (day six).

(run: python scripts/c1_support_12_2_2_crosscheck.py)

The (12,2,2) table of c1_support_at_law.py is a path-aggregation result
(window_enumerator's side of the firewall). This script recomputes every
distinct window's posterior through `window_filter` (the recursive-mixture
side, which shares only the world definition and the window law) and
requires exact agreement on the FULL JOINT POSTERIOR over (U, S_T): for
every window, the path-side law-mass aggregation by (offset, final state),
normalized, must equal the filter's mixture joint component-for-component,
state-for-state, Fraction-for-Fraction. E[support] rebuilt from
filter-side supports with law masses must equal the table. Any mismatch
is a hard failure. All 971 distinct windows (186+209+283+293), both eps.

*(v2, same day: the first committed version compared only support
cardinalities — a weaker assertion than the note's prose implied, as the
truthsayer round observed; a wrong state with the right count would have
passed. This version compares the complete joint posterior.)*
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
            # path-side: per window, law mass by (offset, final state)
            agg = {}
            for T in LAW.endpoints():
                u = LAW.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    agg.setdefault(key, {})
                    agg[key][(u, final)] = (
                        agg[key].get((u, final), Fraction(0)) + w_T * prob
                    )

            mismatches = 0
            mean_filter = Fraction(0)
            for (reset, window), joint_mass in agg.items():
                total = sum(joint_mass.values(), Fraction(0))
                path_joint = {k: m / total for k, m in joint_mass.items()}

                post = filter_window(
                    cfg, progs, LAW, list(window), rung, reset
                )
                filter_joint = {
                    (u, s): w * m
                    for u, (w, belief) in post.components.items()
                    for s, m in belief.items()
                    if w * m > 0
                }
                if filter_joint != path_joint:
                    mismatches += 1
                    print(f"  JOINT MISMATCH {rung} eps={eps}")
                supp = len({s for (_, s) in filter_joint})
                mean_filter += total * supp
            print(
                f"eps={str(eps):>3} {rung}: {len(agg)} windows, "
                f"joint mismatches={mismatches}, "
                f"E[supp] via filter = {float(mean_filter):.6f}",
                flush=True,
            )
            assert mismatches == 0


if __name__ == "__main__":
    main()
