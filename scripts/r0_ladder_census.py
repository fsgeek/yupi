"""r0 census — does a kind-only rung below the statutory ladder give the
interface axis dynamic range at long context, and what does it cost?

(run: python scripts/r0_ladder_census.py T_ep L B [out.json]; ε from YUPI_EPS)

Exploratory (2026-09-03), enumerator side only: windows by path aggregation
at rungs r0..r4; per (ε, rung) the window count, law-mass mean state
entropy, the statutory fact-query means (Q1, Q2, Q3 ids, Q5) and the
primary-horizon predictive targets (statutory Q4@4 and the τ family:
next-2 kinds, time-to-next-wake ≤ 4, next-completion lineage ≤ 4) as
(total, irreducible, gap) splits — all exact rationals, floats only in the
presentation — plus, for r0, the support-size distribution (pricing) and
the residual census (which state fields the r0 support disagrees on and
whether r1 splits the window). The two-path filter gate is NOT run here;
a timed filter sample on the largest r0 supports is reported for pricing
only. No ceiling in this output is statutory until gated.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.eps_grid import eps_grid
from yupi.forecast import q4_forward, q4_mixture, split_entropy
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, time_to_wake
from yupi.programs import programs_for
from yupi.queries import all_queries, entropy_bits, pushforward, state_entropy_bits
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import filter_window

RUNGS = ("r0", "r1", "r2", "r3", "r4")
FIELDS = ("pc", "status", "running", "lock_owner", "lock_wq", "dev_q", "rr_cursor")
FACT_PREFIXES = ("Q1", "Q2", "Q3", "Q5")
FILTER_SAMPLE = 20


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    w_T = endpoint_prior(law)
    out: dict = dict(law=dict(T_ep=T_ep, L=L, B=B), programs=os.environ.get("YUPI_PROGRAMS", "c1"), W=4, m=2, rows=[], r0=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        progs = programs_for()
        facts = [(n, f) for n, f in all_queries(cfg) if n.startswith(FACT_PREFIXES)]
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        agg = {r: {} for r in RUNGS}
        parent01 = {}
        for T in law.endpoints():
            u = law.offset(T)
            for recs, prob, final in path_cache[T]:
                keys = {r: (u == 0, tuple(project(x, r) for x in recs[u:])) for r in RUNGS}
                for r in RUNGS:
                    d = agg[r].setdefault(keys[r], {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
                parent01[keys["r1"]] = keys["r0"]
        memo_q4, memo_k, memo_w, memo_l = {}, {}, {}, {}
        fn_state = {}

        def per_state(s):
            if s not in fn_state:
                fn_state[s] = {
                    "Q4@4": q4_forward(s, cfg, progs, 4, memo_q4),
                    "kinds2": next_kinds(s, cfg, progs, 2, memo_k),
                    "ttw4": time_to_wake(s, cfg, progs, 4, memo_w),
                    "lin4": next_complete_lineage(s, cfg, progs, 4, memo_l),
                }
            return fn_state[s]

        for r in RUNGS:
            mean_HS = 0.0
            mean_fact = {n: 0.0 for n, _ in facts}
            mean_pred = {t: [0.0, 0.0, 0.0] for t in ("Q4@4", "kinds2", "ttw4", "lin4")}
            supp_hist = defaultdict(lambda: Fraction(0))
            max_supp = 0
            for key, joint in agg[r].items():
                mass = sum(joint.values(), Fraction(0))
                belief = {s: m / mass for s, m in joint.items()}
                HS = state_entropy_bits(belief)
                mean_HS += float(mass) * HS
                for n, f in facts:
                    mean_fact[n] += float(mass) * entropy_bits(pushforward(belief, f))
                for t in mean_pred:
                    per = {s: per_state(s)[t] for s in belief}
                    tot, irr, gap = split_entropy(belief, per)
                    for i, v in enumerate((tot, irr, gap)):
                        mean_pred[t][i] += float(mass) * v
                supp_hist[len(belief)] += mass
                max_supp = max(max_supp, len(belief))
            row = dict(eps=str(eps), rung=r, n_windows=len(agg[r]),
                       mean_state_entropy_bits=mean_HS,
                       facts=mean_fact,
                       predictive={t: dict(total=v[0], irreducible=v[1], gap=v[2]) for t, v in mean_pred.items()},
                       max_support=max_supp,
                       support_hist={str(k): float(v) for k, v in sorted(supp_hist.items())})
            out["rows"].append(row)
            fq = "  ".join(f"{n}={v:.4f}" for n, v in mean_fact.items() if n.startswith(("Q1", "Q3")))
            print(f"eps={str(eps):>3} {r} n={len(agg[r]):>6} H(S)={mean_HS:.4f} maxsupp={max_supp:>5}  "
                  f"kinds2.gap={mean_pred['kinds2'][2]:.4f} Q4.gap={mean_pred['Q4@4'][2]:.4f}  {fq}", flush=True)

        # r0 residual census: what r0 does not know, and whether r1 reaches it
        children = defaultdict(int)
        for k1, k0 in parent01.items():
            children[k0] += 1
        sig = defaultdict(lambda: dict(mass=Fraction(0), n=0, split_r1=0, split_mass=Fraction(0)))
        amb = Fraction(0)
        for k0, joint in agg["r0"].items():
            if len(joint) < 2:
                continue
            mass = sum(joint.values(), Fraction(0))
            amb += mass
            states = list(joint)
            fields = tuple(f for f in FIELDS
                           if any(getattr(states[i], f) != getattr(states[j], f)
                                  for i in range(len(states)) for j in range(i + 1, len(states))))
            e = sig[fields]
            e["mass"] += mass
            e["n"] += 1
            if children[k0] > 1:
                e["split_r1"] += 1
                e["split_mass"] += mass
        residual = [dict(fields=list(k), n_windows=e["n"], mass=float(e["mass"]),
                         split_by_r1=e["split_r1"], split_mass_r1=float(e["split_mass"]))
                    for k, e in sorted(sig.items(), key=lambda kv: -kv[1]["mass"])]
        # pricing: time the filter on the largest r0 supports
        largest = sorted(agg["r0"].items(), key=lambda kv: -len(kv[1]))[:FILTER_SAMPLE]
        t0 = time.time()
        mismatches = 0
        for (reset, window), joint in largest:
            post = filter_window(cfg, progs, law, list(window), "r0", reset)
            mass = sum(joint.values(), Fraction(0))
            path_marg = {}
            for s, m in joint.items():
                path_marg[s] = path_marg.get(s, Fraction(0)) + m / mass
            filt = {}
            for u, (w, belief) in post.components.items():
                for s, m in belief.items():
                    if w * m > 0:
                        filt[s] = filt.get(s, Fraction(0)) + w * m
            if filt != path_marg:
                mismatches += 1
        dt = time.time() - t0
        out["r0"].append(dict(eps=str(eps), ambiguous_mass=float(amb), residual=residual,
                              filter_sample=dict(n=len(largest), seconds=dt,
                                                 supports=[len(j) for _, j in largest],
                                                 mismatches=mismatches)))
        print(f"eps={eps} r0 ambiguous mass {float(amb):.4f}; filter sample {len(largest)} windows "
              f"(supports {[len(j) for _, j in largest][:5]}…) {dt:.1f}s, mismatches={mismatches}", flush=True)
        for e in residual[:8]:
            print(f"   {'+'.join(e['fields']) or '(none)':45s} n={e['n_windows']:6d} mass={e['mass']:.2e} "
                  f"split by r1 {e['split_by_r1']} (mass {e['split_mass_r1']:.1e})", flush=True)
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], "w"), indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
