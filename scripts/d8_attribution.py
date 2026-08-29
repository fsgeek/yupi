"""D8 order-mode attribution measurement runner (prereg a39f555).

(run: python scripts/d8_attribution.py FREEZE.json OUT.jsonl [--workers N] [--only c0b|c1] [--B 3]
      [--law T_ep,L] [--per-cell]
      python scripts/d8_attribution.py --consolidate OUT.jsonl OUT.json)

FREEZE.json is the stamped grid freeze (list of admitted cells). The runner
REFUSES any cell not in it. Cells are grouped by (world, discipline, ε,
T_ep) so each worker enumerates paths once per group. Results append to
OUT.jsonl (resumable); a gate failure is recorded as the cell's result with
the gate named. --consolidate turns the JSONL into the committed JSON
artifact (schema: {prereg, freeze, cells: [...]}, one file per world).
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from yupi.d8_benchmark import candidate_cells  # noqa: E402
from yupi.d8_measure import GateFailure, measure_cell  # noqa: E402
from yupi.window import WindowLaw  # noqa: E402

PREREG = "d8-attribution-prereg-v0.1.md@a39f555"


def cell_key(c):
    law = c["law"] if isinstance(c.get("law"), WindowLaw) else WindowLaw(c["T_ep"], c["L"], c["B"])
    return (c["world"], c["discipline"], c["eps"], law.T_ep, law.L, law.B, c["rung"])


def run_group(args):
    group, cells, out = args
    cache = {}
    results = []
    for c in cells:
        t = time.perf_counter()
        try:
            r = measure_cell(c, cache)
        except AssertionError as e:                      # GateFailure or gate F
            r = dict(world=c["world"], discipline=c["discipline"], eps=c["eps"],
                     T_ep=c["law"].T_ep, L=c["law"].L, B=c["law"].B, rung=c["rung"],
                     gates=dict(all_passed=False, failed=str(e)[:500]))
        r["wall_s"] = time.perf_counter() - t
        r["prereg"] = PREREG
        with open(out, "a") as fh:
            fh.write(json.dumps(r, default=str) + "\n")
        results.append((cell_key(c), r["gates"]["all_passed"], r["wall_s"]))
        print(f"[{time.strftime('%H:%M:%S')}] {'|'.join(map(str, cell_key(c)))}: "
              f"{'ok' if r['gates']['all_passed'] else 'GATE FAIL ' + r['gates'].get('failed', '')[:80]} "
              f"{r['wall_s']:.1f}s", flush=True)
    return results


def consolidate(jsonl, out_json, freeze_ref):
    rows = [json.loads(l) for l in open(jsonl)]
    seen = {}
    for r in rows:
        seen[cell_key(r)] = r                            # last write wins (append-only file; reruns append)
    cells = sorted(seen.values(), key=cell_key)
    worlds = sorted({r["world"] for r in cells})
    for w in worlds:
        path = out_json.replace("<world>", w)
        json.dump(dict(prereg=PREREG, freeze=freeze_ref,
                       cells=[r for r in cells if r["world"] == w]), open(path, "w"), indent=1)
        print(f"{path}: {sum(1 for r in cells if r['world'] == w)} cells")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("freeze")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--only", choices=["c0b", "c1"])
    ap.add_argument("--B", type=int, help="run only admitted cells with this bucket size (prereg §4 order: C1 B=3 first)")
    ap.add_argument("--law", help="run only admitted cells at this law, as T_ep,L (e.g. 12,12)")
    ap.add_argument("--per-cell", action="store_true",
                    help="one job per cell instead of one per (world, discipline, ε, T_ep) group — re-enumerates "
                         "paths per cell (≤ ~70 s at T_ep = 16) so long groups spread across workers")
    ap.add_argument("--consolidate", nargs=2, metavar=("JSONL", "OUT_JSON"))
    ap.add_argument("--freeze-ref", default="")
    a = ap.parse_args()
    if a.consolidate:
        consolidate(a.consolidate[0], a.consolidate[1], a.freeze_ref or a.freeze)
        return
    frozen = json.load(open(a.freeze))
    admitted = {cell_key(c) for c in frozen["admitted"]}
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            r = json.loads(line)
            if r["gates"]["all_passed"]:
                done.add(cell_key(r))
    todo = [c for c in candidate_cells()
            if cell_key(c) in admitted and cell_key(c) not in done
            and (not a.only or c["world"] == a.only)
            and (a.B is None or c["law"].B == a.B)
            and (a.law is None or (c["law"].T_ep, c["law"].L) == tuple(int(x) for x in a.law.split(",")))]
    refused = [c for c in candidate_cells() if cell_key(c) not in admitted]
    print(f"freeze {a.freeze}: {len(admitted)} admitted; {len(refused)} candidate cells refused by the "
          f"freeze and NOT run; {len(done)} done; {len(todo)} to run", flush=True)
    groups = {}
    for c in todo:
        key = (c["world"], c["discipline"], c["eps"], c["law"].T_ep)
        if a.per_cell:
            key = key + (c["law"].L, c["law"].B, c["rung"])
        groups.setdefault(key, []).append(c)
    jobs = [(g, cs, a.out) for g, cs in sorted(groups.items(), key=lambda kv: -kv[0][3])]
    with Pool(a.workers) as pool:
        for res in pool.imap_unordered(run_group, jobs):
            pass
    print("done", flush=True)


if __name__ == "__main__":
    main()
