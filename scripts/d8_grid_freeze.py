"""Turn a blind benchmark JSONL into a grid-freeze JSON + a cost summary
(prereg §4). Reads cost and verdicts only; prints no result-shaped field.

(run: python scripts/d8_grid_freeze.py BENCH.jsonl FREEZE.json [--world c1])
"""
import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from yupi.d8_benchmark import (B1_FRONTIER, B1_SUPPORT, B3_STEP_S, B4P_PATHS,  # noqa: E402
                               COST_KEYS_FORBIDDEN, WALL_CAP_S)

CELL = ("world", "discipline", "eps", "T_ep", "L", "B", "rung")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bench")
    ap.add_argument("out")
    ap.add_argument("--world")
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.bench)]
    if a.world:
        rows = [r for r in rows if r["world"] == a.world]
    assert not any(bad in k for r in rows for k in r for bad in COST_KEYS_FORBIDDEN)
    seen = {}
    for r in rows:
        seen[tuple(r[k] for k in CELL)] = r          # last record per cell
    rows = list(seen.values())
    adm = [r for r in rows if r["admitted"]]
    ref = [r for r in rows if not r["admitted"]]
    json.dump(dict(benchmark=os.path.basename(a.bench), prereg="d8-attribution-prereg-v0.1.md@a39f555",
                   rule=dict(B1_support=B1_SUPPORT, B1_frontier=B1_FRONTIER, B3_step_s=B3_STEP_S,
                             B4p_paths=B4P_PATHS, wall_cap_s=WALL_CAP_S),
                   frozen_at=time.strftime("%Y-%m-%d %H:%M %Z"),
                   admitted=[{k: r[k] for k in CELL} for r in adm],
                   refused=[dict({k: r[k] for k in CELL}, refused_by=r["refused_by"],
                                 stage=r.get("stage"), n_lat=r.get("n_lat"), n_vis=r.get("n_vis"),
                                 projected_gate2_wall_s=r.get("projected_gate2_wall_s")) for r in ref]),
              open(a.out, "w"), indent=0)
    print(f"{len(rows)} cells: {len(adm)} admitted, {len(ref)} refused")
    print("refused_by:", dict(Counter(tuple(r["refused_by"]) for r in ref)))
    print("stage of refusals:", dict(Counter(r.get("stage") for r in ref)))
    by = defaultdict(lambda: [0, 0])
    for r in rows:
        by[(r["eps"], r["B"], r["T_ep"])][0 if r["admitted"] else 1] += 1
    print("(eps, B, T_ep): admitted/refused")
    for k in sorted(by, key=lambda k: (k[0], k[1], k[2])):
        print("  ", k, by[k][0], "/", by[k][1])
    priced = [r for r in adm if r.get("priced")]
    if priced:
        mx = lambda k: max(r[k] for r in priced)
        print(f"admitted extremes: n_paths<= {mx('n_paths_max')}, n_vis<= {mx('n_vis')}, n_lat<= {mx('n_lat')}, "
              f"support<= {max(mx('max_support_shuf'), mx('max_support_ord'))}, frontier<= {mx('max_frontier_shuf')}, "
              f"step<= {max(mx('t_step_shuf_s'), mx('t_step_ord_s')) * 1000:.0f} ms, peak<= {mx('peak_build_bytes') / 1e6:.0f} MB, "
              f"max cell wall {mx('projected_gate2_wall_s'):.0f} s, total {sum(r['projected_gate2_wall_s'] for r in priced) / 3600:.2f} h")
    # admitted L per (eps, B, T_ep): the shape of the admitted grid
    shape = defaultdict(set)
    for r in adm:
        shape[(r["eps"], r["B"], r["T_ep"])].add(r["L"])
    print("admitted L by (eps, B, T_ep):")
    for k in sorted(shape):
        print("  ", k, sorted(shape[k]))


if __name__ == "__main__":
    main()
