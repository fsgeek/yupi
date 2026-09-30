"""ι on the (KIND, ACTOR) target and the actor's chain-rule term ι_{A|K},m for every (40, 8, 2)
cell at one prefix position (docs/actor-long-lag-design-prereg-v0.1.md, "Quantity").

Per class c and m:  ι_{(K,A)},m(c) from implicit_info on target kind_actor (the actor pushed
through the suffix binding exactly as the whole-record target is), and

    ι_{A|K},m(c) = ι_{(K,A)},m(c) − ι_K,m(c)

with ι_K,m read from the COMMITTED kind caches (*-k7-kind-m123456.jsonl, sha256 checked against
docs/implicit-info-lag-kind-40-8-2-k7-2026-09-28.json). Gates, per cell and m:
  identity   mean KL = H_m − H̄ on the joint target, to 1e-9;
  nonneg     min over classes of ι_{A|K},m ≥ −1e-12 (a chain-rule term; negative = bug);
  direct     ι_{A|K},m equals Σ_k q(k) KL(q(A|k) ‖ p(A|k)) formed from the exact laws, to 1e-9;
  kind       ι_K,m recomputed from the joint laws' exact kind marginals equals the cache, to 1e-9;
and per class H(ACTOR | KIND) exact (Fraction ratios) equals H(K,A) − H(K), to 1e-12.
Per-class output goes to NEW caches *-k<k>-actorgk-m123456.jsonl; the committed caches are
only read.

    uv run python scripts/implicit_info_actor.py --raw docs/actor-iota-40-8-2-k7-2026-09-30.json
"""
import argparse
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from yupi.implicit_info import _h, _kl, _kind_marginal, h_actor_given_kind, implicit_info, iota_actor_given_kind, kind_actor
from yupi.pattern_ceiling import load_table, serial_key

TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
CACHE = Path.home() / ".cache/yupi-scratch/implicit"
KIND_RAW = "docs/implicit-info-lag-kind-40-8-2-k7-2026-09-28.json"
CELLS = [(r, e) for e in ("1", "1/2") for r in ("r0", "r1", "r2", "r3", "r4")]
MS = (1, 2, 3, 4, 5, 6)


def actor_cell(table, kind_iota, ms=MS):
    """(rows {m: summary}, per_class {key: {field: value}}) for one table. kind_iota maps
    each table key to {m: ι_K,m} (the committed cache)."""
    per = {key: {} for key in table}
    rows = {}
    for m in ms:
        out = implicit_info(table, m, target=kind_actor, keep_laws=True, keep_mix=True)
        laws, mixes, suffix_of = out.pop("laws"), out.pop("mixtures"), out.pop("suffix_of")
        joint = out.pop("per_class")
        tot = sum_k = sum_agk = 0.0
        min_agk, max_direct, max_kind = float("inf"), 0.0, 0.0
        for key, (mass, _) in table.items():
            mix = mixes[suffix_of[key]]
            ik = kind_iota[key][m]
            agk = joint[key] - ik
            direct = iota_actor_given_kind(laws[key], mix)
            ik_re = _kl(_kind_marginal(laws[key]), _kind_marginal(mix))
            per[key][f"iota_ka_{m}"] = joint[key]
            per[key][f"iota_agk_{m}"] = agk
            per[key][f"iota_agk_direct_{m}"] = direct
            w = float(mass)
            tot += w
            sum_k += w * ik
            sum_agk += w * agk
            min_agk = min(min_agk, agk)
            max_direct = max(max_direct, abs(agk - direct))
            max_kind = max(max_kind, abs(ik_re - ik))
        gate = (abs(out["identity_diff"]) < 1e-9 and min_agk >= -1e-12 and max_direct < 1e-9 and max_kind < 1e-9)
        rows[m] = {**out, "mean_iota_kind_cache": sum_k / tot, "mean_iota_agk": sum_agk / tot,
                   "min_iota_agk": min_agk, "max_abs_agk_minus_direct": max_direct,
                   "max_abs_kind_recomputed_minus_cache": max_kind, "gate": gate}
    h_tot, max_h = 0.0, 0.0
    for key, (mass, star) in table.items():
        h = h_actor_given_kind(star)
        joint_law, kind_law = {}, {}
        for r, p in star.items():
            joint_law[(r.kind, r.actor)] = joint_law.get((r.kind, r.actor), Fraction(0)) + p
            kind_law[r.kind] = kind_law.get(r.kind, Fraction(0)) + p
        max_h = max(max_h, abs(h - (_h(joint_law) - _h(kind_law))))
        per[key]["H_agk"] = h
        h_tot += float(mass) * h
    tot = float(sum((mass for mass, _ in table.values()), Fraction(0)))
    h_row = {"mean_H_actor_given_kind": h_tot / tot, "max_abs_H_agk_two_routes": max_h, "gate": max_h < 1e-12}
    return rows, per, h_row


def run_cell(args):
    rung, eps, k, kind_sha = args
    tag = f"{rung}-eps{eps.replace('/', '_')}"
    table = load_table(TABLES / f"c1prime-loop-40-8-2-{tag}-k{k}.jsonl")
    kpath = CACHE / f"c1prime-loop-40-8-2-{tag}-k{k}-kind-m123456.jsonl"
    sha_ok = hashlib.sha256(kpath.read_bytes()).hexdigest() == kind_sha
    kc = {}
    for line in open(kpath):
        d = json.loads(line)
        kc[d["k"]] = {m: d[f"iota_{m}"] for m in MS}
    if set(kc) != {serial_key(key) for key in table}:
        raise SystemExit(f"GATE: kind cache keys differ from the table for {tag}")
    rows, per, h_row = actor_cell(table, {key: kc[serial_key(key)] for key in table})
    path = CACHE / f"c1prime-loop-40-8-2-{tag}-k{k}-actorgk-m123456.jsonl"
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path}")
    with open(path, "w") as f:
        for key in table:
            f.write(json.dumps({"k": serial_key(key), **per[key]}) + "\n")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return rung, eps, rows, h_row, sha_ok, str(kpath), str(path), sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    kraw = json.load(open(KIND_RAW))
    ksha = {(r["rung"], r["eps"]): r["per_class_sha256"] for r in kraw["rows"] if r["k"] == a.k}
    with ProcessPoolExecutor(max_workers=len(CELLS)) as ex:
        res = list(ex.map(run_cell, [(r, e, a.k, ksha[(r, e)]) for r, e in CELLS]))
    rows, cells, ok = [], [], True
    for rung, eps, byM, h_row, sha_ok, kpath, path, sha in res:
        ok &= sha_ok and h_row["gate"]
        cells.append({"rung": rung, "eps": eps, "k": a.k, "kind_cache": kpath, "kind_cache_sha256_ok": sha_ok,
                      **h_row, "per_class_file": path, "per_class_sha256": sha})
        print(f"{rung} eps={eps:3}: kind cache sha {'ok' if sha_ok else 'MISMATCH'} "
              f"mean H(A|K)={h_row['mean_H_actor_given_kind']:.4f} (2 routes {h_row['max_abs_H_agk_two_routes']:.1e})",
              flush=True)
        for m, o in byM.items():
            ok &= o["gate"]
            rows.append({"rung": rung, "eps": eps, "k": a.k, "m": m, **o})
            print(f"  m={m}: H*={o['H_star']:.4f} Hbar={o['H_bar']:.4f} H_m={o['H_m']:.4f} "
                  f"iota_KA={o['mean_iota_kl']:.4f} (id {o['identity_diff']:+.1e}) iota_K={o['mean_iota_kind_cache']:.4f} "
                  f"iota_A|K={o['mean_iota_agk']:.4f} min={o['min_iota_agk']:+.1e} "
                  f"direct {o['max_abs_agk_minus_direct']:.1e} kind {o['max_abs_kind_recomputed_minus_cache']:.1e} "
                  f"{'ok' if o['gate'] else 'GATE FAIL'}", flush=True)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    json.dump({"design": "docs/actor-long-lag-design-prereg-v0.1.md", "law": {"T_ep": 40, "L": 8, "B": 2},
               "git": git + ("+dirty" if dirty else ""), "target": "(KIND, ACTOR), actor suffix-coarsened",
               "kind_raw": KIND_RAW, "all_gates": ok, "cells": cells, "rows": rows}, open(a.raw, "w"), indent=1)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
