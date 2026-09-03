"""Price the window-process recursion (yupi.window_process) at horizons the
path enumerator cannot reach.

(run: python scripts/window_process_pricing.py T_ep L B rung [out.json];
 programs from YUPI_PROGRAMS, ε from YUPI_EPS)

Reports per-tick (state, window) pair counts, the window count, the mean
state entropy (enumerator-side, ungated beyond the equality tests), wall
clock and peak RSS. Exploratory; feeds the D4 re-pricing for M1 scale.
"""
import json
import os
import resource
import sys
import time
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.eps_grid import eps_grid
from yupi.programs import programs_for
from yupi.queries import state_entropy_bits
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregate


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    rung = sys.argv[4]
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), rung=rung,
               programs=os.environ.get("YUPI_PROGRAMS", "c1"), rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        progs = programs_for()
        stats = {}
        t0 = time.time()
        agg = window_law_aggregate(cfg, progs, law, rung, stats)
        wall = time.time() - t0
        H = 0.0
        amb = Fraction(0)
        max_supp = 0
        for j in agg.values():
            mass = sum(j.values(), Fraction(0))
            H += float(mass) * state_entropy_bits({s: m / mass for s, m in j.items()})
            if len(j) > 1:
                amb += mass
            max_supp = max(max_supp, len(j))
        rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        row = dict(eps=str(eps), n_windows=len(agg), max_pairs=stats["max_pairs"],
                   pairs_per_tick=stats["pairs_per_tick"], mean_state_entropy_bits=H,
                   ambiguous_mass=float(amb), max_support=max_supp, wall_s=wall,
                   peak_rss_kb=rss_kb)
        out["rows"].append(row)
        print(f"eps={str(eps):>3} {rung} T_ep={T_ep} L={L}: windows={len(agg)} max_pairs={stats['max_pairs']} "
              f"H(S)={H:.4f} amb={float(amb):.4f} maxsupp={max_supp} wall={wall:.1f}s rss={rss_kb/1e6:.2f}GB", flush=True)
    if len(sys.argv) > 5:
        json.dump(out, open(sys.argv[5], "w"), indent=1)
        print(f"raw JSON -> {sys.argv[5]}", flush=True)


if __name__ == "__main__":
    main()
