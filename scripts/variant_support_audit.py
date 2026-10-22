"""§4.2 support table and §4.3 exact kind sweep, generalised for the world-variant gate
(docs/world-variant-gate-declared-2026-10-22.md). At V0 it must reproduce scripts/support_audit_table.py
(docs/support-audit-table-40-8-2-k7-2026-10-15.json) on the shared fields; the generalised fields are new.

Generalised definitions (declared in the gate note):
- device template: a pure class whose exact next-KIND law is x on IO_COMPLETE and 1 - x on one other kind (any x);
- law mechanisms: the matched pure side grouped by exact next-KIND law; reports the laws carrying >= 10 % of
  matched pure mass and the largest law's share (also over all pure mass);
- binnings: floor(H*/0.05) ("base", as in v3) and floor(H*/0.05 + 1/2) ("offset").

  python scripts/variant_support_audit.py --rows-dir DIR [--out FILE]
"""
import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

H13 = 0.9182958340544896
BINNINGS = {"base": lambda h: int(h / 0.05), "offset": lambda h: int(h / 0.05 + 0.5)}


def wq(xs, ws, q):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); t = sum(ws); a = 0.0
    for i in o:
        a += ws[i]
        if a >= q * t:
            return xs[i]
    return xs[o[-1]]


def device_template(x):
    law = dict(x["p_star"])
    return "IO_COMPLETE" in law and len(law) == 2


def cell(rows):
    M = sum(x["mass"] for x in rows)
    pos = [x for x in rows if x["h_star"] > 1e-12]
    pure = [x for x in pos if abs(x["g"]) < 1e-12]
    high = [x for x in pos if x["g"] / x["h_star"] >= 0.5]
    pure_m = sum(x["mass"] for x in pure)
    line: dict = dict(pure_eligible=pure_m / M,
                coin_share_of_pure=sum(x["mass"] for x in pure if abs(x["h_star"] - H13) < 1e-4) / pure_m,
                device_template_share_of_pure=sum(x["mass"] for x in pure if device_template(x)) / pure_m,
                high_eligible=sum(x["mass"] for x in high) / M)
    for name, b in BINNINGS.items():
        pb = {b(x["h_star"]) for x in pure}
        hb = {b(x["h_star"]) for x in high}
        mp = [x for x in pure if b(x["h_star"]) in hb]
        mp_m = sum(x["mass"] for x in mp)
        laws = {}
        for x in mp:
            k = tuple(sorted(map(tuple, x["p_star"])))
            laws[k] = laws.get(k, 0.0) + x["mass"]
        top = sorted(laws.values(), reverse=True)
        line[name] = dict(pure_matched=mp_m / M,
                          high_matched=sum(x["mass"] for x in high if b(x["h_star"]) in pb) / M,
                          n_shared_bins=len(pb & hb),
                          matched_pure_laws_ge_10pct=sum(1 for v in top if mp_m and v / mp_m >= 0.10),
                          matched_pure_largest_law_share=(top[0] / mp_m) if top else None,
                          matched_pure_device_template_share=(sum(x["mass"] for x in mp if device_template(x)) / mp_m) if mp_m else None)
    laws_all = {}
    for x in pure:
        k = tuple(sorted(map(tuple, x["p_star"])))
        laws_all[k] = laws_all.get(k, 0.0) + x["mass"]
    line["pure_largest_law_share"] = max(laws_all.values()) / pure_m if laws_all else None
    # graded variation (v3 definition, base binning)
    bins = {}
    for x in pos:
        bins.setdefault(int(x["h_star"] / 0.05), []).append(x)
    g_all = g_res = 0.0
    for xs in bins.values():
        m = sum(x["mass"] for x in xs)
        f = [x["g"] / x["h_star"] for x in xs]; w = [x["mass"] for x in xs]
        if wq(f, w, 0.9) - wq(f, w, 0.1) >= 0.30:
            g_all += m
            if m / M >= 0.005 and len(xs) >= 5:
                g_res += m
    line.update(graded=g_all / M, graded_restricted=g_res / M)
    # exact kind sweep (v3 definition)
    kinds = sorted({k for x in rows for k, _ in x["p_star"]})
    kind_of = lambda x: ("pure" if x["h_star"] > 1e-12 and abs(x["g"]) < 1e-12 else "withheld" if x["g"] >= 0.1 else None)
    agg = {}
    for x in rows:
        kd = kind_of(x)
        if kd is None:
            continue
        key = (tuple(sorted(map(tuple, x["p_star"]))), kd)
        agg[key] = agg.get(key, 0.0) + x["mass"]
    keys = list(agg)
    P = np.array([[float(Fraction(dict(k[0]).get(c, "0"))) for c in kinds] for k in keys])
    K = np.array([k[1] == "pure" for k in keys]); W = np.array([agg[k] for k in keys])
    for d in (0.01, 0.02, 0.05):
        hit = np.zeros(len(keys), bool)
        for i0 in range(0, len(keys), 512):
            tv = 0.5 * np.abs(P[i0:i0 + 512, None, :] - P[None, :, :]).sum(-1)
            other = K[i0:i0 + 512, None] != K[None, :]
            hit[i0:i0 + 512] = ((tv <= d + 1e-15) & other).any(1)
        line[f"kind_exist_{d}"] = float(W[hit].sum() / M)
    line["kind_carried"] = float(W.sum() / M)
    return line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows-dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = []
    for eps in ("1", "1_2"):
        for rung in ("r1", "r2", "r3", "r4"):
            f = Path(a.rows_dir) / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl"
            line = dict(eps=eps.replace("_", "/"), rung=rung, **cell([json.loads(l) for l in open(f)]))
            out.append(line)
            print(json.dumps(line), flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(rows_dir=a.rows_dir, rows=out), indent=1))


if __name__ == "__main__":
    main()
