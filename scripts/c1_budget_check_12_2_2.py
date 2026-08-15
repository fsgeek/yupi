"""D4 budget instrumentation for the (12,2,2) observer (provenance for
the numbers quoted in c1-rung-separation-geometry-v0.1.md §2).

(run: python scripts/c1_budget_check_12_2_2.py [out.json])

B1's transition form governs (d4-budget-freeze-v0.1.md): expanded
transitions per filter step, where a windowed filter step expands every
state in every live component's belief.

*(v2, same day — justification corrected, truthsayer round. v1 measured
only FIRST-step expansions and argued "evidence only prunes, so the
first step bounds later steps." That argument is invalid in general: a
kernel transition can expand a pruned support again before the next
observation, so first-step expansion is not an a priori bound for longer
windows. This version measures EVERY step of EVERY distinct window at
every rung and reports the exhaustive maximum. At this law the v1
numbers happen to be the true maxima — the worst step is the first step
of a resetless r1 window, 948 (ε=1) / 1648 (ε=1/2) — as Codex's
independent all-step measurement also found. Do not reuse the v1
argument at longer laws; measure.)*
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.programs import c1_programs
from yupi.records import record_of
from yupi.window import WindowLaw
from yupi.window_filter import state_marginal_at

LAW = WindowLaw(12, 2, 2)
B1_TRANSITIONS = 70_000  # frozen, d4-budget-freeze-v0.1.md
RUNGS = ("r1", "r2", "r3", "r4")


def main():
    out = {}
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()

        # derived priors and their first-step expansions (v1's table)
        mu = {}
        prior_rows = []
        for T in LAW.endpoints():
            u = LAW.offset(T)
            if u in mu:
                continue
            mu[u] = state_marginal_at(cfg, progs, u)
            expanded = sum(len(list(enabled(s, cfg, progs))) for s in mu[u])
            prior_rows.append(
                dict(u=u, prior_support=len(mu[u]), expanded=expanded)
            )
            print(
                f"eps={str(eps):>3} u={u:>2}: |mu_u|={len(mu[u]):>3} "
                f"expanded={expanded}"
            )

        # exhaustive all-step measurement over every distinct window
        path_cache = {T: paths(cfg, progs, T) for T in LAW.endpoints()}
        worst = {}  # step index -> max expansion over windows/rungs
        for rung in RUNGS:
            windows = set()
            for T in LAW.endpoints():
                u = LAW.offset(T)
                for recs, prob, final in path_cache[T]:
                    windows.add(
                        (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    )
            for reset, window in windows:
                # live components: one per length-compatible offset
                beliefs = [
                    dict(mu[u])
                    for _, u in LAW.compatible_endpoints(len(window), reset)
                ]
                for i, obs in enumerate(window):
                    step_exp = 0
                    nxt_beliefs = []
                    for belief in beliefs:
                        nxt = {}
                        for s in belief:
                            trs = list(enabled(s, cfg, progs))
                            step_exp += len(trs)
                            for tr, p in trs:
                                if project(record_of(tr), rung) != obs:
                                    continue
                                nxt[tr.next_state] = True
                        if nxt:
                            nxt_beliefs.append(nxt)
                    worst[i] = max(worst.get(i, 0), step_exp)
                    beliefs = nxt_beliefs
        print(
            f"eps={str(eps):>3}: worst expansion by step "
            f"{ {i + 1: w for i, w in sorted(worst.items())} } "
            f"(B1 bound {B1_TRANSITIONS})"
        )
        overall = max(worst.values())
        assert overall <= B1_TRANSITIONS
        out[str(eps)] = dict(
            per_offset_first_step=prior_rows,
            worst_expansion_by_step={
                str(i + 1): w for i, w in sorted(worst.items())
            },
            worst_expansion_overall=overall,
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
