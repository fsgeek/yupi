"""Residual-ambiguity census for C1 windows — what is still unknown at r1
after L visible records, and which rung field (if any) reaches it.

(run: python scripts/c1_residual_ambiguity_census.py T_ep L B [out.json];
 ε from YUPI_EPS)

For every r1 window with support > 1: the set of state fields in which its
support states differ (pc / status / running / lock_owner / lock_wq /
dev_q / rr_cursor), the law mass, and whether the r2, r3, r4 refinements
split the window at all. Aggregated by field-signature so the answer to
"what does a long r1 window still not know, and can any field fix it?" is
one table per (ε, L). Exploratory diagnostic for the Part C intervention
discussion (2026-09-03); no ceiling or verdict.
"""
import json
import os
import sys
from collections import defaultdict
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.eps_grid import eps_grid
from yupi.interfaces import project
from yupi.programs import programs_for
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_process import window_law_aggregates

RUNGS = ("r1", "r2", "r3", "r4")
FIELDS = ("pc", "status", "running", "lock_owner", "lock_wq", "dev_q", "rr_cursor")


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    w_T = endpoint_prior(law)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), programs=os.environ.get("YUPI_PROGRAMS", "c1"), aggregation=os.environ.get("YUPI_AGG", "paths"), rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        progs = programs_for()
        if os.environ.get("YUPI_AGG", "paths") == "window":
            agg = window_law_aggregates(cfg, progs, law, RUNGS)   # one r4 recursion, keys projected down
            parent = {r: {kb: (kb[0], tuple(project(x, "r1") for x in kb[1])) for kb in agg[r]}
                      for r in RUNGS[1:]}
        else:
            agg = {r: {} for r in RUNGS}
            parent = {r: {} for r in RUNGS[1:]}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in paths(cfg, progs, T):
                    keys = {r: (u == 0, tuple(project(x, r) for x in recs[u:])) for r in RUNGS}
                    for r in RUNGS:
                        d = agg[r].setdefault(keys[r], {})
                        d[final] = d.get(final, Fraction(0)) + w_T * prob
                    for r in RUNGS[1:]:
                        parent[r][keys[r]] = keys["r1"]
        children = {r: defaultdict(int) for r in RUNGS[1:]}
        for r in RUNGS[1:]:
            for kb, ka in parent[r].items():
                children[r][ka] += 1
        sig_mass = defaultdict(lambda: dict(mass=Fraction(0), n=0, split_by={r: 0 for r in RUNGS[1:]},
                                            split_mass={r: Fraction(0) for r in RUNGS[1:]}))
        total_amb = Fraction(0)
        for ka, joint in agg["r1"].items():
            if len(joint) < 2:
                continue
            mass = sum(joint.values(), Fraction(0))
            total_amb += mass
            states = list(joint)
            sig = tuple(f for f in FIELDS
                        if any(getattr(states[i], f) != getattr(states[j], f)
                               for i in range(len(states)) for j in range(i + 1, len(states))))
            e = sig_mass[sig]
            e["mass"] += mass
            e["n"] += 1
            for r in RUNGS[1:]:
                if children[r][ka] > 1:
                    e["split_by"][r] += 1
                    e["split_mass"][r] += mass
        rows = []
        for sig, e in sorted(sig_mass.items(), key=lambda kv: -kv[1]["mass"]):
            rows.append(dict(fields=list(sig), n_windows=e["n"], mass=float(e["mass"]),
                             split_by={r: e["split_by"][r] for r in RUNGS[1:]},
                             split_mass={r: float(e["split_mass"][r]) for r in RUNGS[1:]}))
        out["rows"].append(dict(eps=str(eps), n_r1_windows=len(agg["r1"]),
                                ambiguous_mass=float(total_amb), signatures=rows))
        print(f"eps={eps} L={L}: r1 windows {len(agg['r1'])}, ambiguous mass {float(total_amb):.4f}")
        for row in rows[:12]:
            print(f"   {'+'.join(row['fields']) or '(none)':45s} n={row['n_windows']:6d} mass={row['mass']:.2e}  "
                  f"split r2/r3/r4 = {row['split_by']['r2']}/{row['split_by']['r3']}/{row['split_by']['r4']}  "
                  f"(mass {row['split_mass']['r2']:.1e}/{row['split_mass']['r3']:.1e}/{row['split_mass']['r4']:.1e})", flush=True)
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], "w"), indent=2)
        print(f"raw JSON -> {sys.argv[4]}")


if __name__ == "__main__":
    main()
