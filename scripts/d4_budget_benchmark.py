"""D4 budget pricing sweep (run: python scripts/d4_budget_benchmark.py [out.json]).

Prices filter.step against support size on the dynamometer world and
enumerator.paths against horizon on C0a, on the host hardware. Emits a
markdown table to stdout and raw JSON to the optional output path. See
src/yupi/benchmark.py for why this is not an observability measurement.
"""

import json
import sys

from yupi.benchmark import (
    dyno_config,
    dyno_programs,
    make_belief,
    price_enumerator,
    price_filter_step,
    reachable_states,
)
from yupi.config import WorldConfig
from yupi.programs import c0a_programs

SUPPORT_GRID = [1, 10, 100, 1_000, 5_000, 20_000, 50_000, 100_000]
ENUM_WALL_STOP_S = 20.0
RUNG = "r1"  # the sparsest rung is the binding D4 condition


def main() -> None:
    cfg = dyno_config()
    programs = dyno_programs()

    print(f"## filter.step pricing (dynamometer world, rung {RUNG})\n")
    print("| support | transitions | wall_s (median) | peak_mem_MB | s per 1k transitions |")
    print("|---|---|---|---|---|")
    filter_rows = []
    states_max = reachable_states(cfg, programs, cap=max(SUPPORT_GRID))
    for n in SUPPORT_GRID:
        if n > len(states_max):
            print(f"| {n} | (reachable space exhausted at {len(states_max)}) | | | |")
            break
        belief = make_belief(states_max[:n])
        p = price_filter_step(belief, cfg, programs, rung=RUNG, repeats=3)
        per_1k = p.wall_s / (p.transitions_expanded / 1000)
        filter_rows.append(
            dict(
                support_in=p.support_in,
                support_out=p.support_out,
                transitions_expanded=p.transitions_expanded,
                wall_s=p.wall_s,
                peak_mem_bytes=p.peak_mem_bytes,
            )
        )
        print(
            f"| {p.support_in} | {p.transitions_expanded} | {p.wall_s:.4f} "
            f"| {p.peak_mem_bytes / 1e6:.1f} | {per_1k:.4f} |"
        )

    print("\n## enumerator.paths pricing (C0a)\n")
    print("| horizon | paths | wall_s | paths/s |")
    print("|---|---|---|---|")
    enum_rows = []
    c0a = WorldConfig.c0a()
    c0a_progs = c0a_programs()
    horizon = 2
    while True:
        e = price_enumerator(c0a, c0a_progs, horizon)
        enum_rows.append(dict(horizon=e.horizon, n_paths=e.n_paths, wall_s=e.wall_s))
        print(f"| {e.horizon} | {e.n_paths} | {e.wall_s:.3f} | {e.n_paths / e.wall_s:.0f} |")
        if e.wall_s > ENUM_WALL_STOP_S:
            break
        horizon += 2

    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(dict(filter=filter_rows, enumerator=enum_rows), f, indent=2)
        print(f"\nraw JSON -> {sys.argv[1]}")


if __name__ == "__main__":
    main()
