"""Corrected-kernel sweep rerun comparison — old (buggy-kernel, -raw-2026-08-15)
versus new (-corrected-*) for the three Part II §C sweeps, plus the two derived
quantities threshold proposal v0.3.1 cites from sweep curves:

  (i)  L-axis rung-collapse horizons at T_ep=14 (v0.3.1 §A: max adjacent-rung
       statutory gap per L, from the sync-sweep curves; Q4 enters by its gap
       part, which at fixed L equals the total's rung difference because the
       irreducible term is rung-invariant);
  (ii) measure-(b) truncation-conditional sync horizons (v0.3.1 §B1:
       E[H | U>0] = H_law * T_ep/(T_ep - L), L = T_ep excluded as the
       full-context control).

(run: python scripts/c1_sweep_rerun_comparison.py [out.json])

A READ of existing sweep artifacts; missing files are reported, not fatal.
"""

import glob
import json
import os
import sys

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
PAIRS = [("r1", "r2"), ("r2", "r3"), ("r3", "r4")]
NON_QUERY = ("H(S)", "Q4stat.total", "Q4stat.irr")


def load(name):
    p = os.path.join(DOCS, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def load_latest(prefix):
    hits = sorted(glob.glob(os.path.join(DOCS, prefix + "-corrected-*.json")))
    if not hits:
        return None, None
    with open(hits[-1]) as f:
        return json.load(f), os.path.basename(hits[-1])


def sync_compare(out):
    old = load("c1-sync-sweep-raw-2026-08-15.json")
    new, new_name = load_latest("c1-sync-sweep")
    if old is None or new is None:
        print("sync sweep: missing artifact — skipped")
        return
    print(f"\n===== SYNC SWEEP  old=c1-sync-sweep-raw-2026-08-15.json  new={new_name}")
    assert old["Ls"] == new["Ls"], (old["Ls"], new["Ls"])
    Ls = old["Ls"]
    T = old["T_ep"]
    res = dict(new=new_name, Ls=Ls, horizon_changes=[], curve_drift=None,
               collapse=dict(old=[], new=[], changes=[]),
               measure_b=dict(old=[], new=[], changes=[]))

    oh = {(h["eps"], h["rung"]): h["horizons"] for h in old["horizons"]}
    nh = {(h["eps"], h["rung"]): h["horizons"] for h in new["horizons"]}
    for key in oh:
        for d in old["dsync_grid"]:
            a, b = oh[key][str(d)]["all_queries"], nh[key][str(d)]["all_queries"]
            if a != b:
                res["horizon_changes"].append(dict(eps=key[0], rung=key[1],
                                                   dsync=d, old=a, new=b))
    print(f"  L*(all statutory) changes across full dsync grid: "
          f"{len(res['horizon_changes'])}"
          + "".join(f"\n    {c}" for c in res["horizon_changes"]))

    oc = {(c["eps"], c["rung"]): c["curves"] for c in old["curves"]}
    nc = {(c["eps"], c["rung"]): c["curves"] for c in new["curves"]}
    md = (0.0, None)
    for key in oc:
        for q in oc[key]:
            for L, va, vb in zip(Ls, oc[key][q], nc[key][q]):
                if va is None or vb is None:
                    continue
                if abs(va - vb) > md[0]:
                    md = (abs(va - vb), dict(eps=key[0], rung=key[1], query=q,
                                             L=L, old=va, new=vb))
    res["curve_drift"] = dict(max=md[0], at=md[1])
    print(f"  max curve drift: {md[0]:.6f} at {md[1]}")

    # (i) L-axis collapse horizons from curves (statutory queries + Q4 gap part)
    def collapse(curves_by_key, label, store):
        for eps in ("1", "1/2"):
            for a, b in PAIRS:
                ca, cb = curves_by_key[(eps, a)], curves_by_key[(eps, b)]
                maxgap = []
                for i, L in enumerate(Ls):
                    g = max(ca[q][i] - cb[q][i] for q in ca
                            if q not in NON_QUERY and ca[q][i] is not None)
                    maxgap.append(g)
                Lstar = next((L for L, g in zip(Ls, maxgap) if g < 0.01), None)
                store.append(dict(eps=eps, pair=f"{a}->{b}",
                                  max_gap_per_L={str(L): g for L, g in zip(Ls, maxgap)},
                                  Lstar_at_001=Lstar))
        return store

    collapse(oc, "old", res["collapse"]["old"])
    collapse(nc, "new", res["collapse"]["new"])
    print("  L-axis collapse horizons L*(delta=0.01) per (eps, pair), old -> new:")
    for o, n in zip(res["collapse"]["old"], res["collapse"]["new"]):
        ch = "" if o["Lstar_at_001"] == n["Lstar_at_001"] else "   <-- CHANGED"
        if ch:
            res["collapse"]["changes"].append(dict(eps=o["eps"], pair=o["pair"],
                                                   old=o["Lstar_at_001"],
                                                   new=n["Lstar_at_001"]))
        print(f"    eps={o['eps']:>3} {o['pair']}  {o['Lstar_at_001']} -> "
              f"{n['Lstar_at_001']}{ch}")

    # (ii) measure (b): truncation-conditional horizons at dsync=0.01
    def measure_b(curves_by_key, store):
        for eps in ("1", "1/2"):
            for rung in ("r1", "r2", "r3", "r4"):
                cur = curves_by_key[(eps, rung)]
                Lstar = None
                for i, L in enumerate(Ls):
                    if L == T:
                        continue          # full-context control, excluded
                    factor = T / (T - L)
                    worst = max(cur[q][i] * factor for q in cur
                                if q not in NON_QUERY and cur[q][i] is not None)
                    if worst < 0.01:
                        Lstar = L
                        break
                store.append(dict(eps=eps, rung=rung, Lstar_b_at_001=Lstar))
        return store

    measure_b(oc, res["measure_b"]["old"])
    measure_b(nc, res["measure_b"]["new"])
    print("  measure-(b) sync horizons L*(dsync=0.01, trunc-conditional), old -> new:")
    for o, n in zip(res["measure_b"]["old"], res["measure_b"]["new"]):
        ch = "" if o["Lstar_b_at_001"] == n["Lstar_b_at_001"] else "   <-- CHANGED"
        if ch:
            res["measure_b"]["changes"].append(dict(eps=o["eps"], rung=o["rung"],
                                                    old=o["Lstar_b_at_001"],
                                                    new=n["Lstar_b_at_001"]))
        print(f"    eps={o['eps']:>3} {o['rung']}  {o['Lstar_b_at_001']} -> "
              f"{n['Lstar_b_at_001']}{ch}")
    out["sync"] = res


def delta_compare(out):
    old = load("c1-delta-sweep-raw-2026-08-15.json")
    new, new_name = load_latest("c1-delta-sweep")
    if old is None or new is None:
        print("\n===== DELTA SWEEP: missing artifact — skipped "
              f"(old={'ok' if old else 'MISSING'}, new={'ok' if new else 'MISSING'})")
        return
    print(f"\n===== DELTA SWEEP  old=c1-delta-sweep-raw-2026-08-15.json  new={new_name}")
    ok = {(tuple(c["law"].values()) if isinstance(c["law"], dict) else tuple(c["law"]),
           c["eps"], c["pair"], c["W"]): c for c in old["cell_max"]}
    nk = {(tuple(c["law"].values()) if isinstance(c["law"], dict) else tuple(c["law"]),
           c["eps"], c["pair"], c["W"]): c for c in new["cell_max"]}
    res = dict(new=new_name, cells=[], argmax_changes=[], coverage_changes=[])
    both = sorted(set(ok) & set(nk))
    only = sorted(set(ok) ^ set(nk))
    if only:
        print(f"  cells present in only one artifact: {only}")
        res["asymmetric_cells"] = [list(map(str, k)) for k in only]
    mx = (0.0, None)
    for k in both:
        a, b = ok[k]["max_gap"], nk[k]["max_gap"]
        d = abs(a - b)
        if d > mx[0]:
            mx = (d, k)
        if ok[k]["argmax"] != nk[k]["argmax"]:
            res["argmax_changes"].append(dict(cell=list(map(str, k)),
                                              old=ok[k]["argmax"], new=nk[k]["argmax"]))
        res["cells"].append(dict(cell=list(map(str, k)), old=a, new=b, drift=d))
    print(f"  cells compared: {len(both)}; max |max_gap| drift: {mx[0]:.6f} at {mx[1]}")
    print(f"  argmax-query changes: {len(res['argmax_changes'])}"
          + "".join(f"\n    {c}" for c in res["argmax_changes"]))
    for dlt in old["delta_grid"]:
        co = {tuple(map(str, (c['law'], c['eps'], c['pair'], c['W'])))
              for c in old["coverage"][str(dlt)]}
        cn = {tuple(map(str, (c['law'], c['eps'], c['pair'], c['W'])))
              for c in new["coverage"][str(dlt)]}
        if co != cn:
            res["coverage_changes"].append(dict(delta=dlt,
                                                gained=sorted(cn - co),
                                                lost=sorted(co - cn)))
    print(f"  collapsed-cell coverage changes across delta grid: "
          f"{len(res['coverage_changes'])}"
          + "".join(f"\n    {c}" for c in res["coverage_changes"]))
    out["delta"] = res


def tv_compare(out):
    res = []
    print("\n===== TV SWEEP")
    for law in ("12-2-2", "12-12-2", "14-2-2", "14-4-2"):
        old = load(f"c1-tv-sweep-{law}-raw-2026-08-15.json")
        new, new_name = load_latest(f"c1-tv-sweep-{law}")
        if old is None or new is None:
            print(f"  {law}: missing artifact — skipped "
                  f"(old={'ok' if old else 'MISSING'}, new={'ok' if new else 'MISSING'})")
            continue
        print(f"  --- law {law}  new={new_name}")
        orow = {(r["eps"], r["rung"]): r for r in old["rows"]}
        nrow = {(r["eps"], r["rung"]): r for r in new["rows"]}
        for key in sorted(orow):
            a, b = orow[key], nrow[key]
            surf_d = max(abs(x - y) for ra, rb in zip(a["surface"], b["surface"])
                         for x, y in zip(ra, rb))
            corner_a, corner_b = a["exact_corner_pair_prob"], b["exact_corner_pair_prob"]
            cls = (a["n_classes"], b["n_classes"])
            r = dict(law=law, eps=key[0], rung=key[1],
                     n_classes_old=cls[0], n_classes_new=cls[1],
                     corner_old=corner_a, corner_new=corner_b,
                     max_surface_drift=surf_d)
            res.append(r)
            flag = "" if cls[0] == cls[1] else "  <-- class count changed"
            print(f"    eps={key[0]:>3} {key[1]} classes {cls[0]}->{cls[1]}{flag}  "
                  f"corner {corner_a:.3e}->{corner_b:.3e}  "
                  f"max surface drift {surf_d:.3e}")
    out["tv"] = res


def tv_claims(out, side="new"):
    """Re-verify the specific v0.3.1 §C/§D sentences on the TV surfaces.

    side="old" runs the identical checks on the buggy-kernel artifacts so
    every old/new difference is kernel drift, not a definition mismatch.

    Grids are the tv-sweep script's: DP_GRID rows, DT_GRID cols.
    §C flatness window: Δτ ∈ [1e-3, 3e-2] = cols 1..4 at the δp=1e-2 row (4).
    §D ratio: col 3 (Δτ=1e-2); rows 0 (δp=0), 1 (1e-4), 4 (1e-2), 6 (1e-1).
    """
    DP = [0.0, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1]
    DT = [1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 5e-1]
    res = dict(flatness=[], monotone_violations=[], ratios=[], jump_1e4=[],
               full_context_invariance=[])
    print(f"\n===== v0.3.1 §C/§D CLAIM RE-CHECKS on {side} TV surfaces")
    arts = {}
    for law in ("12-2-2", "12-12-2", "14-2-2", "14-4-2"):
        if side == "new":
            d, name = load_latest(f"c1-tv-sweep-{law}")
        else:
            d = load(f"c1-tv-sweep-{law}-raw-2026-08-15.json")
        if d is None:
            print(f"  {law}: {side} artifact missing — claims not checkable")
            continue
        assert d["dp_grid"] == DP and d["dt_grid"] == DT, law
        arts[law] = d
    # §C: flatness of the δp=1e-2 row over Δτ ∈ [1e-3, 3e-2]
    for law, d in arts.items():
        if law == "12-12-2":
            continue                      # full-context law: §D invariance instead
        for r in d["rows"]:
            vals = r["surface"][4][1:5]
            top = max(vals)
            spread = 0.0 if top == 0 else (top - min(vals)) / top
            res["flatness"].append(dict(law=law, eps=r["eps"], rung=r["rung"],
                                        values=vals, rel_spread=spread))
    flat = [f for f in res["flatness"] if f["rel_spread"] == 0.0]
    l2 = [f for f in res["flatness"] if f["law"] in ("12-2-2", "14-2-2")]
    l2flat = [f for f in l2 if f["rel_spread"] == 0.0]
    w42 = [f for f in res["flatness"] if f["law"] == "14-4-2"]
    print(f"  §C flatness (δp=1e-2, Δτ∈[1e-3,3e-2]): L=2 cells exactly flat "
          f"{len(l2flat)}/{len(l2)}; max rel spread L=2 "
          f"{max(f['rel_spread'] for f in l2):.4f}; at (14,4,2) "
          f"{max(f['rel_spread'] for f in w42):.4f}" if w42 else "  §C: (14,4,2) missing")
    # §D: monotone in δp; ratio span at Δτ=1e-2; largest 1e-4 jump; full-context invariance
    for law, d in arts.items():
        for r in d["rows"]:
            col = [r["surface"][a][3] for a in range(len(DP))]
            for a in range(1, len(col)):
                if col[a] < col[a - 1] - 1e-15:
                    res["monotone_violations"].append(
                        dict(law=law, eps=r["eps"], rung=r["rung"], dp=DP[a],
                             prev=col[a - 1], val=col[a]))
            if law != "12-12-2" and col[0] > 0:
                res["ratios"].append(dict(law=law, eps=r["eps"], rung=r["rung"],
                                          at_1e2=col[4] / col[0],
                                          at_1e4=col[1] / col[0]))
            elif law != "12-12-2":
                res["ratios"].append(dict(law=law, eps=r["eps"], rung=r["rung"],
                                          at_1e2=None, at_1e4=None,
                                          note="pair_prob(0)=0"))
    print(f"  §D monotone in δp at Δτ=1e-2: violations {len(res['monotone_violations'])}")
    fin = [x for x in res["ratios"] if x["at_1e2"] is not None]
    if fin:
        big = max(fin, key=lambda x: x["at_1e4"])
        print(f"  §D ratio pair_prob(1e-2)/pair_prob(0) at Δτ=1e-2 spans "
              f"{min(x['at_1e2'] for x in fin):.2f}–{max(x['at_1e2'] for x in fin):.1f}; "
              f"largest δp=1e-4 jump {big['at_1e4']:.1f}x at "
              f"({big['law']}) eps={big['eps']} {big['rung']}")
    if "12-12-2" in arts:
        worst = 0.0
        for r in arts["12-12-2"]["rows"]:
            for b in range(len(DT)):
                col = [r["surface"][a][b] for a in range(7)]   # δp = 0 .. 1e-1
                top = max(col)
                if top > 0:
                    worst = max(worst, (top - min(col)) / top)
        res["full_context_invariance"] = dict(max_rel_spread_dp0_to_0p1=worst)
        print(f"  §D full-context (12,12,2) δp-invariance up to 0.1: "
              f"max rel spread {worst:.2e}")
    out[f"tv_claims_{side}"] = res


def main():
    out = {}
    sync_compare(out)
    delta_compare(out)
    tv_compare(out)
    tv_claims(out, side="old")
    tv_claims(out, side="new")
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {sys.argv[1]}")


if __name__ == "__main__":
    main()
