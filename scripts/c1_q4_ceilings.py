"""Statutory Q4 ceilings for C1 at a WindowLaw and forecast horizon W.

(run: python scripts/c1_q4_ceilings.py T_ep L B W [out.json];
 YUPI_AGG=paths (default) | window (the window-process recursion, 2026-09-04);
 YUPI_RUNGS default r1,r2,r3,r4; YUPI_PROGRAMS default c1)

Per (eps, rung): windows by path aggregation (as c1_query_ceilings.py);
per-state Q4 forecast by `forecast.q4_forward` with ONE memo per eps (the
per-state distribution does not depend on the window); per window the
(total, irreducible, gap) split; law-mass-weighted means. Also reports
the mean NONE_WITHIN_W mass. The forward-sum algorithm's two-path gate
lives in tests/test_forecast.py (exhaustive over horizon-8 endpoint
states, W <= 4); this script does not re-run it.
"""

import json
import sys
from fractions import Fraction

from yupi.eps_grid import eps_grid
from yupi.config import WorldConfig
from yupi.aggregation import aggregate_by_rung
from yupi.forecast import NONE_WITHIN_W, q4_forward, q4_mixture, split_entropy
from yupi.programs import programs_for
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")


def compute_rows(law, W, eps, cfg, progs, rungs, agg="paths"):
    """One ε: per-rung Q4 rows (total / irreducible / gap split, NONE mass,
    per-endpoint means), windows from `aggregate_by_rung` in the chosen mode."""
    w_T = endpoint_prior(law)
    by_rung = aggregate_by_rung(cfg, progs, law, rungs, agg)
    memo = {}
    per_state = {}
    rows = []
    for rung in rungs:
        a, mass_T = by_rung[rung]
        m_total = m_irr = m_gap = m_none = 0.0
        by_T = {T: [0.0, 0.0, 0.0, 0.0] for T in law.endpoints()}
        for key, joint in a.items():
            mass = sum(joint.values(), Fraction(0))
            belief = {s: m / mass for s, m in joint.items()}
            for s in belief:
                if s not in per_state:
                    per_state[s] = q4_forward(s, cfg, progs, W, memo)
            total, irr, gap = split_entropy(belief, per_state)
            mix = q4_mixture(belief, per_state)
            m_total += float(mass) * total
            m_irr += float(mass) * irr
            m_gap += float(mass) * gap
            m_none += float(mass) * float(mix.get(NONE_WITHIN_W, Fraction(0)))
            for T, mT in mass_T[key].items():
                f = float(mT)
                b = by_T[T]
                b[0] += f * total; b[1] += f * irr; b[2] += f * gap
                b[3] += f * float(mix.get(NONE_WITHIN_W, Fraction(0)))
        rows.append(dict(eps=str(eps), rung=rung, n_windows=len(a),
                         n_states=len(per_state), total_bits=m_total,
                         irreducible_bits=m_irr, gap_bits=m_gap, none_mass=m_none,
                         by_endpoint={str(T): dict(U=law.offset(T), total_bits=b[0] / float(w_T),
                                                   irreducible_bits=b[1] / float(w_T),
                                                   gap_bits=b[2] / float(w_T),
                                                   none_mass=b[3] / float(w_T))
                                      for T, b in by_T.items()},
                         aggregation=agg))
    return rows


def main():
    import os
    T_ep, L, B, W = (int(a) for a in sys.argv[1:5])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    agg = os.environ.get("YUPI_AGG", "paths")
    rungs = tuple(os.environ.get("YUPI_RUNGS", "r1,r2,r3,r4").split(","))
    programs_name = os.environ.get("YUPI_PROGRAMS", "c1")
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), W=W, aggregation=agg, programs=programs_name, rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        for row in compute_rows(law, W, eps, cfg, programs_for(programs_name), rungs, agg):
            out["rows"].append(row)
            print(f"eps={row['eps']:>3} {row['rung']} n={row['n_windows']:>6} states={row['n_states']:>4} "
                  f"total={row['total_bits']:.4f} irreducible={row['irreducible_bits']:.4f} gap={row['gap_bits']:.4f} "
                  f"none={row['none_mass']:.4f}", flush=True)
    if len(sys.argv) > 5:
        with open(sys.argv[5], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[5]}", flush=True)


if __name__ == "__main__":
    main()
