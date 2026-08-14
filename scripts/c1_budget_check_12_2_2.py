"""D4 budget instrumentation for the (12,2,2) observer (provenance for
the numbers quoted in c1-rung-separation-geometry-v0.1.md §2).

(run: python scripts/c1_budget_check_12_2_2.py [out.json])

B1's transition form governs (d4-budget-freeze-v0.1.md): expanded
transitions per filter step. A windowed filter step expands every state
in every live component's belief; evidence only prunes, so the worst
step is bounded by the first step from the derived priors — per
component, sum over states of mu_u of |enabled(s)|; for a whole window,
the sum of that over all length-compatible offsets. Reported here: the
per-offset expansions, the worst single component, and the worst full
resetless mixture (a 2-record window is compatible with every u > 0 on
the grid).
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.programs import c1_programs
from yupi.window import WindowLaw
from yupi.window_filter import state_marginal_at

LAW = WindowLaw(12, 2, 2)
B1_TRANSITIONS = 70_000  # frozen, d4-budget-freeze-v0.1.md


def main():
    out = {}
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        rows = []
        for T in LAW.endpoints():
            u = LAW.offset(T)
            mu = state_marginal_at(cfg, progs, u)
            expanded = sum(len(list(enabled(s, cfg, progs))) for s in mu)
            rows.append(dict(u=u, prior_support=len(mu), expanded=expanded))
            print(
                f"eps={str(eps):>3} u={u:>2}: |mu_u|={len(mu):>3} "
                f"expanded={expanded}"
            )
        worst_component = max(r["expanded"] for r in rows)
        resetless_mixture = sum(r["expanded"] for r in rows if r["u"] > 0)
        print(
            f"eps={str(eps):>3}: worst component={worst_component}, "
            f"worst resetless mixture={resetless_mixture} "
            f"(B1 bound {B1_TRANSITIONS})"
        )
        assert resetless_mixture <= B1_TRANSITIONS
        out[str(eps)] = dict(
            per_offset=rows,
            worst_component=worst_component,
            worst_resetless_mixture=resetless_mixture,
        )
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(
                dict(
                    law=dict(T_ep=LAW.T_ep, L=LAW.L, B=LAW.B),
                    b1_transitions=B1_TRANSITIONS,
                    results=out,
                ),
                f,
                indent=2,
            )
        print(f"raw JSON -> {sys.argv[1]}", flush=True)


if __name__ == "__main__":
    main()
