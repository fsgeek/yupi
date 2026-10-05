"""Exact side of the three-arm intervention (docs/three-arm-design-v0.1.md §4) for one new arm, r1D (decoy) or
r1S (self-copy), computed before any corpus or model. Derived from scripts/relay_exact_side.py (frozen; r1R) with
the rung passed explicitly to every job.

  uv run python scripts/three_arm_exact_side.py --rung r1D --raw docs/three-arm-exact-side-r1D-2026-10-05.json
  uv run python scripts/three_arm_exact_side.py --rung r1S --raw docs/three-arm-exact-side-r1S-2026-10-05.json

Same steps and gates as the relay's: derived tables k = 1..7, both ε, with gates A/B and an exact round trip; gate
C at (8, 4, 2) (recursion route and brute force); the lag profile ι_kind,m, m = 1..6 at k = 7 (r1 must reproduce the
committed lag raw); per-class Δι_kind,4 = ι4(r1) − ι4(arm) cached beside the relay's. Extra gate for r1S: Δι_kind,4
is exactly 0 (equal Fraction mixtures) for every class.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from yupi.implicit_info import implicit_info, weighted_quantiles
from yupi.interfaces import WINDOW_RUNGS, window_map
from yupi.pattern_ceiling import (derive_relay_table, load_table, mean_next_entropy_bits, relay_gates,
                                  save_table, serial_key)

TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
IMPLICIT = Path.home() / ".cache/yupi-scratch/implicit"
RELAY = Path.home() / ".cache/yupi-scratch/relay"
LAG_RAW = "docs/implicit-info-lag-kind-40-8-2-k7-2026-09-28.json"
MS = (1, 2, 3, 4, 5, 6)
QS = (0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0)


def _tag(eps):
    return "eps" + eps.replace("/", "_")


def _kind_mean_h(table):
    from math import log2
    tot = sum((m for m, _ in table.values()), Fraction(0))
    h = 0.0
    for m, star in table.values():
        km = {}
        for r, q in star.items():
            km[r.kind] = km.get(r.kind, Fraction(0)) + q
        h += float(m) * -sum(float(q) * log2(float(q)) for q in km.values() if q > 0)
    return h / float(tot), tot


def derive_job(args):
    rung, eps, k = args
    t0 = time.time()
    src = TABLES / f"c1prime-loop-40-8-2-r1-{_tag(eps)}-k{k}.jsonl"
    dst = TABLES / f"c1prime-loop-40-8-2-{rung}-{_tag(eps)}-k{k}.jsonl"
    if dst.exists():
        raise SystemExit(f"refusing to overwrite {dst}")
    r1 = load_table(src)
    rr = derive_relay_table(r1, rung=rung)
    gates = relay_gates(r1, rr, rung=rung)
    save_table(rr, dst)
    round_trip = load_table(dst) == rr
    hk1, tot1 = _kind_mean_h(r1)
    hkr, totr = _kind_mean_h(rr)
    return dict(eps=eps, k=k, r1_table=src.name, r1_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                arm_table=dst.name, arm_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),
                round_trip_exact=round_trip, table_mass=str(tot1), table_mass_equal=(tot1 == totr),
                H_record_r1=mean_next_entropy_bits(r1) / float(tot1), H_record_arm=mean_next_entropy_bits(rr) / float(totr),
                H_kind_r1=hk1, H_kind_arm=hkr, wall_s=time.time() - t0, **gates)


def gate_c(rung, progname, eps_s, k):
    from yupi.config import WorldConfig
    from yupi.programs import programs_for
    from yupi.pattern_ceiling import ceiling_table
    from yupi.window import WindowLaw
    law = WindowLaw(8, 4, 2)
    cfg, progs = WorldConfig.c1(epsilon=Fraction(eps_s)), programs_for(progname)
    t = ceiling_table(cfg, progs, law, ("r1", rung), prefix_len=k)
    derived = derive_relay_table(t["r1"], rung=rung)
    row = dict(programs=progname, eps=eps_s, k=k, n_classes=len(derived),
               recursion_equal=(derived == t[rung]), **{g: v for g, v in relay_gates(t["r1"], derived, rung=rung).items()
                                                        if g in ("gate_A_kind", "gate_B_record")})
    if k is None:
        from yupi.pattern_enumerator import relay_table_by_paths
        row["brute_force_equal"] = (derived == relay_table_by_paths(cfg, progs, law, rung=rung))
    return row


def lag_job(rung, eps, k=7):
    """Lag profile at r1 and the arm (k = 7, KIND target) and the per-class Δι_kind,4."""
    t0 = time.time()
    r1 = load_table(TABLES / f"c1prime-loop-40-8-2-r1-{_tag(eps)}-k{k}.jsonl")
    rr = load_table(TABLES / f"c1prime-loop-40-8-2-{rung}-{_tag(eps)}-k{k}.jsonl")
    kind = lambda r: r.kind
    prof, per, mix4 = {}, {}, {}
    for name, table in (("r1", r1), (rung, rr)):
        prof[name], per[name] = {}, {}
        for m in MS:
            out = implicit_info(table, m, target=kind, keep_mix=(m == 4))
            per[name][m] = out.pop("per_class")
            if m == 4:
                mix4[name] = (out.pop("suffix_of"), out.pop("mixtures"))
            prof[name][m] = out
    RELAY.mkdir(parents=True, exist_ok=True)
    IMPLICIT.mkdir(parents=True, exist_ok=True)
    per_path = IMPLICIT / f"c1prime-loop-40-8-2-{rung}-{_tag(eps)}-k{k}-kind-m123456.jsonl"
    if per_path.exists():
        raise SystemExit(f"refusing to overwrite {per_path}")
    with open(per_path, "w") as f:
        for key in rr:
            f.write(json.dumps({"k": serial_key(key), **{f"iota_{m}": per[rung][m][key] for m in MS}}) + "\n")
    d_path = RELAY / f"c1prime-loop-40-8-2-{rung}-{_tag(eps)}-k{k}-kind-diota4.jsonl"
    if d_path.exists():
        raise SystemExit(f"refusing to overwrite {d_path}")
    (s1, mx1), (sr, mxr) = mix4["r1"], mix4[rung]
    pairs, zero_exact_mass, zero_float_mass, disagree = [], Fraction(0), Fraction(0), 0
    pos05, neg_mass, total = Fraction(0), Fraction(0), Fraction(0)
    n_zero_exact = n_zero_float = 0
    with open(d_path, "w") as f:
        for key, (mass, _) in r1.items():
            kr = (key[0], window_map(rung)(key[1]))
            a, b = per["r1"][4][key], per[rung][4][kr]
            d = a - b
            exact0 = mx1[s1[key]] == mxr[sr[kr]]
            float0 = abs(d) <= 1e-12
            total += mass
            if exact0:
                zero_exact_mass += mass; n_zero_exact += 1
            if float0:
                zero_float_mass += mass; n_zero_float += 1
            disagree += exact0 != float0
            if d > 0.05:
                pos05 += mass
            if d < -1e-12:
                neg_mass += mass
            pairs.append((d, mass))
            f.write(json.dumps({"k": serial_key(key), "kR": serial_key(kr), "iota4_r1": a, "iota4_arm": b, "arm": rung,
                                "d_iota4": d, "zero_exact": exact0}) + "\n")
    mean = sum(float(m) * d for d, m in pairs) / float(total)
    summary = dict(eps=eps, n_classes=len(pairs), table_mass=str(total), mean_d_iota4=mean,
                   mean_check=(prof["r1"][4]["mean_iota_kl"] - prof[rung][4]["mean_iota_kl"]),
                   quantiles=dict(zip([str(q) for q in QS], weighted_quantiles(pairs, QS))),
                   mass_zero_exact=float(zero_exact_mass / total), n_zero_exact=n_zero_exact,
                   mass_zero_float_1e12=float(zero_float_mass / total), n_zero_float_1e12=n_zero_float,
                   n_exact_float_disagree=disagree,
                   mass_gt_0_05=float(pos05 / total), mass_negative=float(neg_mass / total),
                   per_class_file=str(d_path), per_class_sha256=hashlib.sha256(d_path.read_bytes()).hexdigest(),
                   arm_iota_file=str(per_path), arm_iota_sha256=hashlib.sha256(per_path.read_bytes()).hexdigest(),
                   wall_s=time.time() - t0)
    return eps, prof, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rung", required=True, choices=("r1D", "r1S"))
    ap.add_argument("--raw", required=True)
    ap.add_argument("--workers", type=int, default=14)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts", "tests"], capture_output=True, text=True).stdout.strip()
    ok = True

    assert a.rung in WINDOW_RUNGS
    jobs = [(a.rung, e, k) for e in ("1", "1/2") for k in range(1, 8)]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        derived = list(ex.map(derive_job, jobs))
    for r in derived:
        g = (r["gate_A_kind"] and r["gate_B_record"] and r["round_trip_exact"] and r["table_mass_equal"]
             and abs(r["H_kind_r1"] - r["H_kind_arm"]) < 1e-12 and abs(r["H_record_r1"] - r["H_record_arm"]) < 1e-12)
        r["gate"] = g
        ok &= g
        print(f"derive eps={r['eps']:3} k={r['k']}: classes {r['n_classes']} A={r['gate_A_kind']} B={r['gate_B_record']} "
              f"rt={r['round_trip_exact']} H*rec {r['H_record_r1']:.6f}/{r['H_record_arm']:.6f} "
              f"H*kind {r['H_kind_r1']:.6f}/{r['H_kind_arm']:.6f} ({r['wall_s']:.0f}s) {'ok' if g else 'GATE FAIL'}", flush=True)

    cjobs = [(p, e, k) for p in ("c1", "c1prime-loop") for e in ("1", "1/2") for k in (None, 1, 2, 3, 4)]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        gc = list(ex.map(gate_c, *zip(*[(a.rung,) + j for j in cjobs])))
    for r in gc:
        g = r["recursion_equal"] and r["gate_A_kind"] and r["gate_B_record"] and r.get("brute_force_equal", True)
        r["gate"] = g
        ok &= g
        print(f"gate C {r['programs']:12} eps={r['eps']:3} k={r['k']}: classes {r['n_classes']} recursion={r['recursion_equal']} "
              f"brute={r.get('brute_force_equal', '-')} {'ok' if g else 'GATE FAIL'}", flush=True)

    ref = json.load(open(LAG_RAW))
    ref = {(r["eps"], r["m"]): r for r in ref["rows"] if r["rung"] == "r1"}
    with ProcessPoolExecutor(max_workers=2) as ex:
        lags = list(ex.map(lag_job, (a.rung, a.rung), ("1", "1/2")))
    profiles, dsum = [], []
    for eps, prof, summ in lags:
        for rung in ("r1", a.rung):
            for m in MS:
                o = prof[rung][m]
                row = dict(rung=rung, eps=eps, k=7, m=m, **o)
                g = abs(o["identity_diff"]) < 1e-9
                if rung == "r1":
                    row["xcheck_vs_lag_raw"] = o["mean_iota_kl"] - ref[(eps, m)]["mean_iota_kl"]
                    g &= abs(row["xcheck_vs_lag_raw"]) < 1e-12
                else:
                    row["H_star_minus_r1"] = o["H_star"] - prof["r1"][m]["H_star"]
                    row["H_m_minus_r1"] = o["H_m"] - prof["r1"][m]["H_m"]
                    g &= abs(row["H_star_minus_r1"]) < 1e-12 and row["H_m_minus_r1"] <= 1e-12   # refinement: H_m can only fall
                row["gate"] = g
                ok &= g
                profiles.append(row)
                print(f"lag {rung:3} eps={eps:3} m={m}: H*={o['H_star']:.4f} H_m={o['H_m']:.4f} iota={o['mean_iota_kl']:.4f} "
                      f"groups={o['n_groups']}/{o['n_classes']} {'ok' if g else 'GATE FAIL'}", flush=True)
        g = abs(summ["mean_d_iota4"] - summ["mean_check"]) < 1e-9 and summ["n_exact_float_disagree"] == 0
        if a.rung == "r1S":                       # design §2: the self-copy moves nothing, exactly, in every class
            summ["self_copy_all_zero_exact"] = summ["n_zero_exact"] == summ["n_classes"]
            g &= summ["self_copy_all_zero_exact"]
        summ["gate"] = g
        ok &= g
        dsum.append(summ)
        print(f"Δι_kind,4 eps={eps}: mean {summ['mean_d_iota4']:.4f} (check {summ['mean_check']:.4f}); "
              f"mass Δι=0 exact {summ['mass_zero_exact']:.4f} (float {summ['mass_zero_float_1e12']:.4f}, "
              f"disagree {summ['n_exact_float_disagree']}); mass Δι>0.05 {summ['mass_gt_0_05']:.4f}; "
              f"mass Δι<0 {summ['mass_negative']:.4f}; quantiles {summ['quantiles']}", flush=True)

    out = dict(design="docs/three-arm-design-v0.1.md", law=dict(T_ep=40, L=8, B=2), programs="c1prime-loop",
               rung_name=a.rung, slot=("OBJECT: KIND of record t-1 (NONE for t = 1)" if a.rung == "r1D" else "OBJECT: KIND of record t"),
               git=git + ("+dirty" if dirty else ""), all_gates=ok,
               derived_tables=derived, gate_C_small_world=gc, lag_profiles=profiles, d_iota_kind_4=dsum,
               notes=("means normalized by the k=7 table mass (windows with at least 7 records); "
                      "Δι=0 'exact' means the r1 and arm order-4 KIND mixtures for the class are equal as Fractions"))
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print("ALL GATES PASSED" if ok else "GATE FAILED", "->", a.raw, flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
