"""Divergent mass decomposed by window resolution — EXPLORATORY (Aug 16 2026).

(run: python scripts/c1_divergent_resolution.py T_ep L B [out.json])

Question: is "divergent mass rises with rung (r1→r4), not monotone"
(c1-predictive-targets-v0.1, truthsayer-corrected) explained by two
opposing forces — (up) finer rungs RESOLVE windows toward point masses,
whose P-next is P(next|s), so pairs of resolved windows are divergent iff
their endpoint states are a state-level divergent pair (mass ~0.95 at full
context); (down) finer rungs make the next record a finer variable, so
P-next equality is harder even between resolved windows (state-level
divergent mass FALLS with rung at full context: 0.9776→0.9478)?

Pre-stated predictions (written before the first run):
  R1  resolved law mass rises with rung at every windowed law; at (12,2,2)
      the r3→r4 increment is ~0.
  R2  the r1→r4 rise in divergent mass is carried mostly (>50%) by
      resolved windows entering pairs.
  R3  divergent mass on resolved windows ≤ state-level divergent mass under
      the endpoint marginal at that rung.
  R4  at (12,2,2) the r3→r4 dip occurs with resolved-window divergent mass
      flat.

v0.1.1 (Aug 16 2026, truthsayer round): the state-level column is now
ASSERTED equal to the (T_ep,T_ep,B) full-context divergent mass from the
day-seven v0.2 raw file when it exists (T_ep=12), instead of merely printed.
R1 was scored "held" though only (12,2,2) was measured; see note v0.1.1.

Same window construction and divergent-pair criterion (exact P-next
equality, any tau mixture unequal; m=2, W=4) as scripts/c1_predictive_targets.py.
Adds: per window resolved flag (|support|=1); divergent mass split
resolved/unresolved; pair mass by type (res-res / res-unres / unres-unres,
as pair_prob contributions); state-level divergent mass under the endpoint
marginal P(s) at each rung; number of P-next classes among states.
"""

import json
import os
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import combinations

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import q4_mixture
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, p_next, time_to_wake
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")
M, W = 2, 4
TAUS = ("kinds2", "ttw4", "lineage4")


def freeze(d):
    return frozenset(d.items())


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), m=M, W=W, rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        memo_k, memo_w, memo_l = {}, {}, {}
        fn_state, pnext_state = {}, {}
        # endpoint-state marginal (rung-free)
        P_s = defaultdict(Fraction)
        for T in law.endpoints():
            for recs, prob, final in path_cache[T]:
                P_s[final] += w_T * prob
        for rung in RUNGS:
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
            for s in P_s:
                if s not in fn_state:
                    fn_state[s] = dict(
                        kinds2=next_kinds(s, cfg, progs, M, memo_k),
                        ttw4=time_to_wake(s, cfg, progs, W, memo_w),
                        lineage4=next_complete_lineage(s, cfg, progs, W, memo_l),
                    )
                if (s, rung) not in pnext_state:
                    pnext_state[(s, rung)] = p_next(s, cfg, progs, rung)
            # state-level divergent mass under P(s)
            sgroups = defaultdict(list)
            for s, m in P_s.items():
                sgroups[freeze(pnext_state[(s, rung)])].append((s, m))
            state_div_mass = Fraction(0)
            for g in sgroups.values():
                sigs = {tuple(freeze(fn_state[s][t]) for t in TAUS) for s, _ in g}
                if len(sigs) >= 2:
                    # a state is in a pair iff some other state in the group has a different sig
                    for s, m in g:
                        my = tuple(freeze(fn_state[s][t]) for t in TAUS)
                        if any(tuple(freeze(fn_state[s2][t]) for t in TAUS) != my for s2, _ in g if s2 != s):
                            state_div_mass += m
            # windows
            groups = defaultdict(list)
            resolved_mass = Fraction(0)
            for key, joint in agg.items():
                mass = sum(joint.values(), Fraction(0))
                belief = {s: m / mass for s, m in joint.items()}
                res = len(belief) == 1
                if res:
                    resolved_mass += mass
                mixes = tuple(freeze(q4_mixture(belief, {s: fn_state[s][t] for s in belief})) for t in TAUS)
                pn = freeze(q4_mixture(belief, {s: pnext_state[(s, rung)] for s in belief}))
                groups[pn].append((key, mass, mixes, res))
            div_res = Fraction(0)
            div_unres = Fraction(0)
            pp = {"res-res": Fraction(0), "res-unres": Fraction(0), "unres-unres": Fraction(0)}
            seen = set()
            for g in groups.values():
                if len(g) < 2:
                    continue
                classes = defaultdict(list)
                for key, mass, mixes, res in g:
                    classes[mixes].append((key, mass, res))
                if len(classes) < 2:
                    continue
                items = list(classes.values())
                for wa, wb in combinations(items, 2):
                    for (ka, ma, ra) in wa:
                        for (kb, mb, rb) in wb:
                            typ = "res-res" if ra and rb else ("unres-unres" if not ra and not rb else "res-unres")
                            pp[typ] += 2 * ma * mb
                for ws in items:
                    for key, mass, res in ws:
                        if key not in seen:
                            seen.add(key)
                            if res:
                                div_res += mass
                            else:
                                div_unres += mass
            # v0.1.1 gate: the state-level column must equal the full-context
            # divergent mass at (T_ep, T_ep, B) — same endpoint marginal — when
            # that day-seven raw file exists (it does for T_ep=12 only).
            fc = f"docs/c1-predictive-targets-{T_ep}-{T_ep}-{B}-raw-2026-08-15-v0.2.json"
            if os.path.exists(fc):
                ref = [r for r in json.load(open(fc))["rows"] if r["eps"] == str(eps) and r["rung"] == rung]
                assert ref and abs(ref[0]["divergent"]["mass"] - float(state_div_mass)) < 1e-9, \
                    f"state-level column != full-context divergent mass at eps={eps} {rung}"
            row = dict(eps=str(eps), rung=rung, n_windows=len(agg),
                       resolved_mass=float(resolved_mass),
                       div_mass=float(div_res + div_unres),
                       div_mass_resolved=float(div_res),
                       div_mass_unresolved=float(div_unres),
                       state_div_mass=float(state_div_mass),
                       n_state_pnext_classes=len(sgroups),
                       pair_prob_by_type={k: float(v) for k, v in pp.items()})
            out["rows"].append(row)
            print(f"eps={row['eps']:>3} {rung} n={len(agg):>6} resolved={row['resolved_mass']:.4f} "
                  f"div={row['div_mass']:.4f} (res {row['div_mass_resolved']:.4f} / unres {row['div_mass_unresolved']:.4f}) "
                  f"state-div={row['state_div_mass']:.4f} classes={len(sgroups)} "
                  f"pp={{{', '.join(f'{k}:{v:.2e}' for k, v in row['pair_prob_by_type'].items())}}}", flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
