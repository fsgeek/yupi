"""Implicit information ι_m and the exact order-m ceiling for every (40, 8, 2)
cell at one prefix position (docs/implicit-information-design-v0.1.md §3).

Gates, per cell and m: the identity (mean per-class KL = H_m − H̄ to 1e-9) and
the cross-check against the committed ceiling raw (H* × table mass equals the
raw's mean_next_record_entropy_bits, which is an unnormalized law-mass sum).
Per-class ι goes to the cache for the per-window join; its sha256 goes in the raw.

    uv run python scripts/implicit_info.py --k 7 --raw docs/implicit-info-40-8-2-k7-2026-09-28.json
"""
import argparse
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from yupi.implicit_info import implicit_info
from yupi.pattern_ceiling import load_table, serial_key

TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
CACHE = Path.home() / ".cache/yupi-scratch/implicit"
CELLS = [(r, e) for e in ("1", "1/2") for r in ("r0", "r1", "r2", "r3", "r4")]


def run_cell(args):
    rung, eps, k, ms = args
    tag = f"{rung}-eps{eps.replace('/', '_')}"
    table = load_table(TABLES / f"c1prime-loop-40-8-2-{tag}-k{k}.jsonl")
    rows, per = {}, {}
    for m in ms:
        out = implicit_info(table, m)
        per[m] = out.pop("per_class")
        rows[m] = out
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"c1prime-loop-40-8-2-{tag}-k{k}.jsonl"
    with open(path, "w") as f:
        for key in table:
            f.write(json.dumps({"k": serial_key(key), **{f"iota_{m}": per[m][key] for m in ms}}) + "\n")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return rung, eps, rows, str(path), sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--m", default="1,2")
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    ms = tuple(int(x) for x in a.m.split(","))
    ceil = json.load(open(f"docs/pattern-ceilings-40-8-2-k{a.k}-2026-09-18.json"))
    ref = {(r["rung"], r["eps"]): r["mean_next_record_entropy_bits"] for r in ceil["rows"]}
    with ProcessPoolExecutor(max_workers=len(CELLS)) as ex:
        res = list(ex.map(run_cell, [(r, e, a.k, ms) for r, e in CELLS]))
    rows, ok = [], True
    for rung, eps, byM, path, sha in res:
        for m, o in byM.items():
            xcheck = o["H_star"] * o["mass"] - ref[(rung, eps)]
            gate = abs(o["identity_diff"]) < 1e-9 and abs(xcheck) < 1e-9
            ok &= gate
            rows.append({"rung": rung, "eps": eps, "k": a.k, "m": m, **o,
                         "xcheck_vs_ceiling_raw": xcheck, "gate": gate, "per_class_file": path, "per_class_sha256": sha})
            print(f"{rung} eps={eps:3} m={m}: H*={o['H_star']:.4f} Hbar={o['H_bar']:.4f} H_m={o['H_m']:.4f} "
                  f"iota={o['mean_iota_kl']:.4f} (id {o['identity_diff']:+.1e}, x {xcheck:+.1e}) "
                  f"mass>{o['threshold']}={o['mass_frac_iota_gt']:.3f} groups={o['n_groups']}/{o['n_classes']} "
                  f"{'ok' if gate else 'GATE FAIL'}", flush=True)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    json.dump({"design": "docs/implicit-information-design-v0.1.md", "law": {"T_ep": 40, "L": 8, "B": 2},
               "git": git + ("+dirty" if dirty else ""), "ceiling_raw": f"docs/pattern-ceilings-40-8-2-k{a.k}-2026-09-18.json",
               "all_gates": ok, "rows": rows}, open(a.raw, "w"), indent=1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
