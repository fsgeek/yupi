"""Exact side of the relay intervention (docs/relay-intervention-design-v0.1.md §3–§4),
computed before any relay model is trained.

  uv run python scripts/relay_exact_side.py --raw docs/relay-exact-side-2026-09-30.json

1. Derived tables. For k = 1..7 and ε ∈ {1, ½} at the frozen law (40, 8, 2), the r1ʀ
   ("r1R") prefix tables are derived from the committed-route r1 tables in
   ~/.cache/yupi-scratch/ceilings by the relay push-forward and written beside them
   (c1prime-loop-40-8-2-r1R-eps<e>-k<k>.jsonl). Gate A: per class, the KIND marginal
   is identical (Fractions). Gate B: per class, the multiset of next-record
   probabilities is identical (so H* per class is), masses equal, the class map a
   bijection. The written file must load back equal to the derived table.
2. Gate C (independent route) at (8, 4, 2), c1 and c1prime-loop programs, both ε,
   full windows and k = 1..4: the table from the ordinary recursion with the relay
   applied to structural windows before pattern keying equals the derived table class
   by class; for full windows also brute-force path summation.
3. Lag profile ι_kind,m, m = 1..6, k = 7, at r1 and r1ʀ, both ε (identity gate 1e-9;
   r1's profile must reproduce docs/implicit-info-lag-kind-40-8-2-k7-2026-09-28.json).
4. Per class Δι_kind,4 = ι_kind,4(r1 class) − ι_kind,4(its r1ʀ class): cache under
   ~/.cache/yupi-scratch/relay/, summary (law-mass mean, quantiles, mass with Δι = 0
   exactly — decided on the exact order-4 mixtures — and with Δι > 0.05) in the raw.
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
from yupi.interfaces import relay_window
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
    eps, k = args
    t0 = time.time()
    src = TABLES / f"c1prime-loop-40-8-2-r1-{_tag(eps)}-k{k}.jsonl"
    dst = TABLES / f"c1prime-loop-40-8-2-r1R-{_tag(eps)}-k{k}.jsonl"
    if dst.exists():
        raise SystemExit(f"refusing to overwrite {dst}")
    r1 = load_table(src)
    rr = derive_relay_table(r1)
    gates = relay_gates(r1, rr)
    save_table(rr, dst)
    round_trip = load_table(dst) == rr
    hk1, tot1 = _kind_mean_h(r1)
    hkr, totr = _kind_mean_h(rr)
    return dict(eps=eps, k=k, r1_table=src.name, r1_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                r1R_table=dst.name, r1R_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),
                round_trip_exact=round_trip, table_mass=str(tot1), table_mass_equal=(tot1 == totr),
                H_record_r1=mean_next_entropy_bits(r1) / float(tot1), H_record_r1R=mean_next_entropy_bits(rr) / float(totr),
                H_kind_r1=hk1, H_kind_r1R=hkr, wall_s=time.time() - t0, **gates)


def gate_c(progname, eps_s, k):
    from yupi.config import WorldConfig
    from yupi.programs import programs_for
    from yupi.pattern_ceiling import ceiling_table
    from yupi.window import WindowLaw
    law = WindowLaw(8, 4, 2)
    cfg, progs = WorldConfig.c1(epsilon=Fraction(eps_s)), programs_for(progname)
    t = ceiling_table(cfg, progs, law, ("r1", "r1R"), prefix_len=k)
    derived = derive_relay_table(t["r1"])
    row = dict(programs=progname, eps=eps_s, k=k, n_classes=len(derived),
               recursion_equal=(derived == t["r1R"]), **{g: v for g, v in relay_gates(t["r1"], derived).items()
                                                        if g in ("gate_A_kind", "gate_B_record")})
    if k is None:
        from yupi.pattern_enumerator import relay_table_by_paths
        row["brute_force_equal"] = (derived == relay_table_by_paths(cfg, progs, law))
    return row


def lag_job(eps, k=7):
    """Lag profile at r1 and r1ʀ (k = 7, KIND target) and the per-class Δι_kind,4."""
    t0 = time.time()
    r1 = load_table(TABLES / f"c1prime-loop-40-8-2-r1-{_tag(eps)}-k{k}.jsonl")
    rr = load_table(TABLES / f"c1prime-loop-40-8-2-r1R-{_tag(eps)}-k{k}.jsonl")
    kind = lambda r: r.kind
    prof, per, mix4 = {}, {}, {}
    for name, table in (("r1", r1), ("r1R", rr)):
        prof[name], per[name] = {}, {}
        for m in MS:
            out = implicit_info(table, m, target=kind, keep_mix=(m == 4))
            per[name][m] = out.pop("per_class")
            if m == 4:
                mix4[name] = (out.pop("suffix_of"), out.pop("mixtures"))
            prof[name][m] = out
    RELAY.mkdir(parents=True, exist_ok=True)
    IMPLICIT.mkdir(parents=True, exist_ok=True)
    per_path = IMPLICIT / f"c1prime-loop-40-8-2-r1R-{_tag(eps)}-k{k}-kind-m123456.jsonl"
    if per_path.exists():
        raise SystemExit(f"refusing to overwrite {per_path}")
    with open(per_path, "w") as f:
        for key in rr:
            f.write(json.dumps({"k": serial_key(key), **{f"iota_{m}": per["r1R"][m][key] for m in MS}}) + "\n")
    d_path = RELAY / f"c1prime-loop-40-8-2-r1R-{_tag(eps)}-k{k}-kind-diota4.jsonl"
    if d_path.exists():
        raise SystemExit(f"refusing to overwrite {d_path}")
    (s1, mx1), (sr, mxr) = mix4["r1"], mix4["r1R"]
    pairs, zero_exact_mass, zero_float_mass, disagree = [], Fraction(0), Fraction(0), 0
    pos05, neg_mass, total = Fraction(0), Fraction(0), Fraction(0)
    n_zero_exact = n_zero_float = 0
    with open(d_path, "w") as f:
        for key, (mass, _) in r1.items():
            kr = (key[0], relay_window(key[1]))
            a, b = per["r1"][4][key], per["r1R"][4][kr]
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
            f.write(json.dumps({"k": serial_key(key), "kR": serial_key(kr), "iota4_r1": a, "iota4_r1R": b,
                                "d_iota4": d, "zero_exact": exact0}) + "\n")
    mean = sum(float(m) * d for d, m in pairs) / float(total)
    summary = dict(eps=eps, n_classes=len(pairs), table_mass=str(total), mean_d_iota4=mean,
                   mean_check=(prof["r1"][4]["mean_iota_kl"] - prof["r1R"][4]["mean_iota_kl"]),
                   quantiles=dict(zip([str(q) for q in QS], weighted_quantiles(pairs, QS))),
                   mass_zero_exact=float(zero_exact_mass / total), n_zero_exact=n_zero_exact,
                   mass_zero_float_1e12=float(zero_float_mass / total), n_zero_float_1e12=n_zero_float,
                   n_exact_float_disagree=disagree,
                   mass_gt_0_05=float(pos05 / total), mass_negative=float(neg_mass / total),
                   per_class_file=str(d_path), per_class_sha256=hashlib.sha256(d_path.read_bytes()).hexdigest(),
                   r1R_iota_file=str(per_path), r1R_iota_sha256=hashlib.sha256(per_path.read_bytes()).hexdigest(),
                   wall_s=time.time() - t0)
    return eps, prof, summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--workers", type=int, default=14)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts", "tests"], capture_output=True, text=True).stdout.strip()
    ok = True

    jobs = [(e, k) for e in ("1", "1/2") for k in range(1, 8)]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        derived = list(ex.map(derive_job, jobs))
    for r in derived:
        g = (r["gate_A_kind"] and r["gate_B_record"] and r["round_trip_exact"] and r["table_mass_equal"]
             and abs(r["H_kind_r1"] - r["H_kind_r1R"]) < 1e-12 and abs(r["H_record_r1"] - r["H_record_r1R"]) < 1e-12)
        r["gate"] = g
        ok &= g
        print(f"derive eps={r['eps']:3} k={r['k']}: classes {r['n_classes']} A={r['gate_A_kind']} B={r['gate_B_record']} "
              f"rt={r['round_trip_exact']} H*rec {r['H_record_r1']:.6f}/{r['H_record_r1R']:.6f} "
              f"H*kind {r['H_kind_r1']:.6f}/{r['H_kind_r1R']:.6f} ({r['wall_s']:.0f}s) {'ok' if g else 'GATE FAIL'}", flush=True)

    cjobs = [(p, e, k) for p in ("c1", "c1prime-loop") for e in ("1", "1/2") for k in (None, 1, 2, 3, 4)]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        gc = list(ex.map(gate_c, *zip(*cjobs)))
    for r in gc:
        g = r["recursion_equal"] and r["gate_A_kind"] and r["gate_B_record"] and r.get("brute_force_equal", True)
        r["gate"] = g
        ok &= g
        print(f"gate C {r['programs']:12} eps={r['eps']:3} k={r['k']}: classes {r['n_classes']} recursion={r['recursion_equal']} "
              f"brute={r.get('brute_force_equal', '-')} {'ok' if g else 'GATE FAIL'}", flush=True)

    ref = json.load(open(LAG_RAW))
    ref = {(r["eps"], r["m"]): r for r in ref["rows"] if r["rung"] == "r1"}
    with ProcessPoolExecutor(max_workers=2) as ex:
        lags = list(ex.map(lag_job, ("1", "1/2")))
    profiles, dsum = [], []
    for eps, prof, summ in lags:
        for rung in ("r1", "r1R"):
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
        summ["gate"] = g
        ok &= g
        dsum.append(summ)
        print(f"Δι_kind,4 eps={eps}: mean {summ['mean_d_iota4']:.4f} (check {summ['mean_check']:.4f}); "
              f"mass Δι=0 exact {summ['mass_zero_exact']:.4f} (float {summ['mass_zero_float_1e12']:.4f}, "
              f"disagree {summ['n_exact_float_disagree']}); mass Δι>0.05 {summ['mass_gt_0_05']:.4f}; "
              f"mass Δι<0 {summ['mass_negative']:.4f}; quantiles {summ['quantiles']}", flush=True)

    out = dict(design="docs/relay-intervention-design-v0.1.md", law=dict(T_ep=40, L=8, B=2), programs="c1prime-loop",
               rung_name="r1R", relay_slot="OBJECT (a KIND token; NONE when no earlier same-actor record in the window)",
               git=git + ("+dirty" if dirty else ""), all_gates=ok,
               derived_tables=derived, gate_C_small_world=gc, lag_profiles=profiles, d_iota_kind_4=dsum,
               notes=("means normalized by the k=7 table mass (windows with at least 7 records); "
                      "Δι=0 'exact' means the r1 and r1R order-4 KIND mixtures for the class are equal as Fractions"))
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print("ALL GATES PASSED" if ok else "GATE FAILED", "->", a.raw, flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
