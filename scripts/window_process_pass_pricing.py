"""Price ONE producer pass of the window-process recursion — the unit the
corrected D4 rule binds (Codex review of v0.2.8, 2026-09-04, finding 8):
`window_law_aggregates()` runs a single r4 recursion per (law, ε) and
materializes every requested rung from it, so the admitting rule must be
stated per pass, with the maximum live pair count of the r4 recursion and
the whole-process peak RSS INCLUDING the projected aggregates.

(run: python scripts/window_process_pass_pricing.py T_ep L B [out.json];
 programs from YUPI_PROGRAMS, ε grid from yupi.eps_grid; YUPI_RUNGS to
 restrict the materialized rungs, default all five)

Also retains what the older single-rung pricing did not: reachable states
per tick and their maximum, so that a proposal citing a state count has a
raw to point at. Exploratory instrument; nothing here is a ceiling.

Metric definitions (Codex review 2, 2026-09-04, finding 16):
- `max_pairs` = max_t |frontier_t|, the size of the (state, window)
  dictionary after tick t. During tick t+1 the old and new frontiers
  coexist, so simultaneously live entries reach up to
  |frontier_t| + |frontier_{t+1}|; the rule binds the frontier size.
- `peak_rss_kb` = ru_maxrss of a FRESH process per ε (each ε pass runs in
  its own subprocess, so the high-water mark is that pass's own), in the
  kernel's unit (KiB on Linux). "GB" in the notes' tables is
  peak_rss_kb / 10⁶, i.e. units of 10⁶ KiB ≈ 1.024 GB; the D4 line
  "8 GB" is 8 × 10⁶ KiB in this unit.
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
from yupi.window_process import window_law_aggregates


def _summarize(agg):
    H, amb, max_supp = 0.0, Fraction(0), 0
    for j in agg.values():
        mass = sum(j.values(), Fraction(0))
        H += float(mass) * state_entropy_bits({s: m / mass for s, m in j.items()})
        if len(j) > 1:
            amb += mass
        max_supp = max(max_supp, len(j))
    return dict(n_windows=len(agg), mean_state_entropy_bits=H,
                ambiguous_mass=float(amb), max_support=max_supp)


def one_pass(eps: Fraction, law: WindowLaw, rungs):
    cfg = WorldConfig.c1(epsilon=eps)
    progs = programs_for()
    stats = {}
    t0 = time.time()
    aggs = window_law_aggregates(cfg, progs, law, rungs, stats)
    wall = time.time() - t0
    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    row = dict(eps=str(eps), max_pairs=stats["max_pairs"], pairs_per_tick=stats["pairs_per_tick"],
               max_states=stats["max_states"], states_per_tick=stats["states_per_tick"],
               wall_s=wall, peak_rss_kb=rss_kb, rss_isolated_per_eps=True,
               per_rung={r: _summarize(aggs[r]) for r in rungs})
    return row


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--one":
        # child: one ε pass in a fresh process; row as JSON on stdout
        eps = Fraction(sys.argv[2]); T_ep, L, B = (int(a) for a in sys.argv[3:6])
        rungs = tuple(sys.argv[6].split(","))
        print(json.dumps(one_pass(eps, WindowLaw(T_ep=T_ep, L=L, B=B), rungs)))
        return
    import subprocess
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    rungs = tuple(os.environ.get("YUPI_RUNGS", "r0,r1,r2,r3,r4").split(","))
    out = dict(law=dict(T_ep=T_ep, L=L, B=B),
               unit="one window_law_aggregates() pass per eps in a fresh process (r4 recursion + projections); max_pairs = max_t |frontier_t|; peak_rss_kb = ru_maxrss (KiB) of that process",
               rungs=list(rungs), programs=os.environ.get("YUPI_PROGRAMS", "c1"), rows=[])
    for eps in eps_grid():
        res = subprocess.run([sys.executable, __file__, "--one", str(eps), str(T_ep), str(L), str(B), ",".join(rungs)],
                             capture_output=True, text=True, check=True, env=os.environ)
        row = json.loads(res.stdout.strip().splitlines()[-1])
        out["rows"].append(row)
        r1 = row["per_rung"].get("r1") or row["per_rung"][rungs[0]]
        print(f"eps={str(eps):>3} T_ep={T_ep} L={L}: max_pairs={row['max_pairs']} max_states={row['max_states']} "
              f"windows(r1)={r1['n_windows']} H(S|r1)={r1['mean_state_entropy_bits']:.4f} "
              f"wall={row['wall_s']:.1f}s rss={row['peak_rss_kb']/1e6:.2f}GB (fresh process)", flush=True)
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], "w"), indent=1)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
