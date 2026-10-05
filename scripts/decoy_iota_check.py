"""Exploratory exact-side check (docs/decoy-iota-check-v0.1.md): is the skeleton-v0.2 §3 item 3 decoy
(decoy_t = KIND of record t−1, window-local, in the relay's OBJECT slot) a Δι = 0 control?

  uv run python scripts/decoy_iota_check.py --raw docs/decoy-iota-check-2026-10-05.json

For (40, 8, 2) r1 k = 7 tables, both ε: derive the decoy table (class and next-record push-forward, collision
refused), compute ι_kind,m (m = 1..6) for r1 and the decoy, per-class Δι_kind,4 = ι4(r1) − ι4(decoy), and its
law-mass correlation with the relay's per-class Δι_kind,4 (the cached file of scripts/relay_exact_side.py).
No learner, no GPU. Scratch only; no table is written to the cache.
"""
import argparse
import json
import math
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from yupi.implicit_info import implicit_info
from yupi.interfaces import MASKED, Lit
from yupi.pattern_ceiling import load_table, serial_key
from yupi.records import Record

TABLES = Path.home() / ".cache/yupi-scratch/ceilings"
RELAY = Path.home() / ".cache/yupi-scratch/relay"


def _tag(eps):
    return "eps" + eps.replace("/", "_")


def _dec(rec, prev_kind):
    return Record(kind=rec.kind, actor=rec.actor, obj=Lit(prev_kind) if prev_kind else None,
                  related=MASKED, lineage=MASKED)


def decoy_window(pw):
    out, prev = [], None
    for r in pw:
        out.append(_dec(r, prev))
        prev = r.kind
    return tuple(out)


def derive_decoy_table(table):
    out = {}
    for (reset, pw), (mass, star) in table.items():
        key = (reset, decoy_window(pw))
        if key in out:
            raise ValueError(f"decoy class collision at {key!r}")
        last = pw[-1].kind if pw else None
        nstar = {}
        for r, q in star.items():
            d = _dec(r, last)
            if d in nstar:
                raise ValueError("decoy next-record collision")
            nstar[d] = q
        out[key] = (mass, nstar)
    return out


def _strip(key):
    return (key[0], tuple(Record(r.kind, r.actor, MASKED, MASKED, MASKED) for r in key[1]))


def job(args):
    eps, which, m = args
    t = load_table(TABLES / f"c1prime-loop-40-8-2-r1-{_tag(eps)}-k7.jsonl")
    if which == "decoy":
        t = derive_decoy_table(t)
    o = implicit_info(t, m, target=lambda r: r.kind)
    pc = o.pop("per_class")
    summ = {k: o[k] for k in ("mean_iota_kl", "n_groups", "identity_diff")}
    if m != 4:
        return eps, which, m, summ, None
    return eps, which, m, summ, {serial_key(_strip(k) if which == "decoy" else k): v for k, v in pc.items()}


def compare(eps, pc_r1, pc_dec):
    mass = {serial_key(k): float(v[0]) for k, v in load_table(TABLES / f"c1prime-loop-40-8-2-r1-{_tag(eps)}-k7.jsonl").items()}
    rows = [json.loads(l) for l in open(RELAY / f"c1prime-loop-40-8-2-r1R-{_tag(eps)}-k7-kind-diota4.jsonl")]
    W = X = Y = XX = YY = XY = 0.0
    zero = big_pos = big_neg = agree = zr1 = zr1_dec = 0.0
    for r in rows:
        k, w = r["k"], mass[r["k"]]
        assert abs(pc_r1[k] - r["iota4_r1"]) < 1e-9, "r1 ι4 does not reproduce the relay raw"
        x, y = r["d_iota4"], pc_r1[k] - pc_dec[k]
        W += w; X += w * x; Y += w * y; XX += w * x * x; YY += w * y * y; XY += w * x * y
        zero += w * (abs(y) < 1e-12); big_pos += w * (y > 0.05); big_neg += w * (y < -0.05)
        agree += w * ((x > 1e-12) == (y > 1e-12) and (x < -1e-12) == (y < -1e-12))
        if pc_r1[k] == 0:
            zr1 += w; zr1_dec += w * pc_dec[k]
    mx, my = X / W, Y / W
    cov, vx, vy = XY / W - mx * my, XX / W - mx * mx, YY / W - my * my
    return dict(n_classes=len(rows), mean_d_iota4_relay=mx, mean_d_iota4_decoy=my,
                corr_decoy_relay=cov / math.sqrt(vx * vy), slope_decoy_on_relay=cov / vx,
                mass_frac_decoy_zero_1e12=zero / W, mass_frac_decoy_gt_0_05=big_pos / W,
                mass_frac_decoy_lt_neg_0_05=big_neg / W, mass_frac_sign_agree=agree / W,
                mass_frac_iota4_r1_zero=zr1 / W, mean_decoy_iota4_on_r1_zero=zr1_dec / zr1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    t0 = time.time()
    jobs = [(e, w, m) for e in ("1", "1/2") for w in ("r1", "decoy") for m in range(1, 7)]
    with ProcessPoolExecutor(24) as ex:
        res = list(ex.map(job, jobs))
    prof, pcs = {}, {}
    for eps, w, m, s, pc in res:
        prof.setdefault(eps, {}).setdefault(w, {})[m] = s
        if pc is not None:
            pcs[(eps, w)] = pc
    out = dict(design="docs/decoy-iota-check-v0.1.md", law="(40, 8, 2) c1prime-loop, k = 7, target KIND",
               git=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
               profiles=prof, comparison={e: compare(e, pcs[(e, "r1")], pcs[(e, "decoy")]) for e in ("1", "1/2")},
               wall_s=time.time() - t0)
    Path(a.raw).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["comparison"], indent=1))


if __name__ == "__main__":
    main()
