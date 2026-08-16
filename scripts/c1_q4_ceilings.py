"""Statutory Q4 ceilings for C1 at a WindowLaw and forecast horizon W.

(run: python scripts/c1_q4_ceilings.py T_ep L B W [out.json])

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

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import NONE_WITHIN_W, q4_forward, q4_mixture, split_entropy
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")


def main():
    T_ep, L, B, W = (int(a) for a in sys.argv[1:5])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), W=W, rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        memo = {}
        per_state = {}
        for rung in RUNGS:
            agg = {}
            mass_T = {}   # key -> {T: law mass generated at endpoint T} (per-U, 2026-08-16)
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
                    mt = mass_T.setdefault(key, {})
                    mt[T] = mt.get(T, Fraction(0)) + w_T * prob
            m_total = m_irr = m_gap = m_none = 0.0
            by_T = {T: [0.0, 0.0, 0.0, 0.0] for T in law.endpoints()}
            for key, joint in agg.items():
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
            row = dict(eps=str(eps), rung=rung, n_windows=len(agg),
                       n_states=len(per_state), total_bits=m_total,
                       irreducible_bits=m_irr, gap_bits=m_gap, none_mass=m_none,
                       by_endpoint={str(T): dict(U=law.offset(T), total_bits=b[0] / float(w_T),
                                                 irreducible_bits=b[1] / float(w_T),
                                                 gap_bits=b[2] / float(w_T),
                                                 none_mass=b[3] / float(w_T))
                                    for T, b in by_T.items()})
            out["rows"].append(row)
            print(f"eps={row['eps']:>3} {rung} n={len(agg):>6} states={len(per_state):>4} "
                  f"total={m_total:.4f} irreducible={m_irr:.4f} gap={m_gap:.4f} "
                  f"none={m_none:.4f}", flush=True)
    if len(sys.argv) > 5:
        with open(sys.argv[5], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[5]}", flush=True)


if __name__ == "__main__":
    main()
