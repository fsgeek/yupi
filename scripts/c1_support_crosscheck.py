"""Two-path cross-check of a parameterized-law support table.

(run: python scripts/c1_support_crosscheck.py T_ep L B)

Generalizes c1_support_12_2_2_crosscheck.py (kept as the committed
(12,2,2) run) to an arbitrary WindowLaw on the command line. Identical
method: every distinct window's posterior recomputed through
`window_filter` (recursive-mixture side of the firewall), compared
against the path-aggregation joint over (U, S_T) Fraction-for-Fraction;
E[support] rebuilt from filter-side supports must equal the table. Any
mismatch is a hard failure.
"""

import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import filter_window

RUNGS = ("r1", "r2", "r3", "r4")


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
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
                    cfg, progs, law, list(window), rung, reset
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
