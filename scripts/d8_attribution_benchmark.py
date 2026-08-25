"""Blind cost benchmark over the D8 attribution candidate grid (prereg §4).

(run: python scripts/d8_attribution_benchmark.py out.jsonl [--only c0b|c1] [--max-tep N])

Append-only JSONL, one cost record per cell; resumable (cells already in
the file are skipped). Prints cost and verdicts only. Cells sharing
(world, discipline, ε, T_ep) reuse one path enumeration. B4′ is checked on
path count BEFORE any table is built: a (world, ε, T) whose path count
exceeds the line refuses all its cells without pricing them further.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from yupi.d8_benchmark import B4P_PATHS, benchmark_cell, candidate_cells, world_of  # noqa: E402
from yupi.enumerator import paths  # noqa: E402


def cell_id(c):
    return f"{c['world']}|{c['discipline']}|{c['eps']}|{c['law'].T_ep}|{c['law'].L}|{c['law'].B}|{c['rung']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--only", choices=["c0b", "c1"])
    ap.add_argument("--max-tep", type=int, default=16)
    a = ap.parse_args()
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            r = json.loads(line)
            done.add(f"{r['world']}|{r['discipline']}|{r['eps']}|{r['T_ep']}|{r['L']}|{r['B']}|{r['rung']}")
    cells = [c for c in candidate_cells()
             if (not a.only or c["world"] == a.only) and c["law"].T_ep <= a.max_tep]
    print(f"{len(cells)} candidate cells, {len(done)} already priced", flush=True)
    cache_key, cache = None, {}
    for c in cells:
        cid = cell_id(c)
        if cid in done:
            continue
        key = (c["world"], c["discipline"], c["eps"], c["law"].T_ep)
        if key != cache_key:
            cache_key, cache = key, {}
            cfg, progs = world_of(c)
            t = time.perf_counter()
            cache[c["law"].T_ep] = paths(cfg, progs, c["law"].T_ep)
            print(f"[{time.strftime('%H:%M:%S')}] paths {key}: {len(cache[c['law'].T_ep])} "
                  f"in {time.perf_counter() - t:.1f}s", flush=True)
        n_max = len(cache[c["law"].T_ep])
        if n_max > B4P_PATHS:
            rec = dict(world=c["world"], discipline=c["discipline"], eps=c["eps"], T_ep=c["law"].T_ep,
                       L=c["law"].L, B=c["law"].B, rung=c["rung"], n_paths_max=n_max,
                       admitted=False, refused_by=["B4'_paths"], priced=False)
        else:
            rec = benchmark_cell(c, cache)
            rec["priced"] = True
        with open(a.out, "a") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        print(f"[{time.strftime('%H:%M:%S')}] {cid}: n_vis={rec.get('n_vis')} "
              f"wall={rec.get('projected_gate2_wall_s', 0):.1f}s "
              f"{'ADMIT' if rec['admitted'] else 'REFUSE ' + ','.join(rec['refused_by'])}", flush=True)


if __name__ == "__main__":
    main()
