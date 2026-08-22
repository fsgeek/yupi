"""Score held-out Tier 1 sync-sweep artifacts against proposal v0.3 P1–P4.

(run: python scripts/c1_heldout_score.py [out.json])

Reads docs/c1-sync-sweep-{corrected,F2-heldout,F3-heldout}-*.json and
reports, per (family, ε, rung): measure-(a) L* (law-mass mean < δ_sync),
measure-(b) L* (truncation-conditional, the v0.2.5 statutory measure),
L-axis collapse horizons per rung pair at δ = 0.01, and the max r3→r4 gap.
Same formulas as c1_sweep_rerun_comparison.py (measure_b / collapse),
generalized over ε and L sets. No thresholds are chosen here; δ = δ_sync
= 0.01 are the frozen v0.2.5 values.
"""
import glob
import json
import os
import sys

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
NON_QUERY = {"H(S)", "Q4stat.total", "Q4stat.irr"}
PAIRS = [("r1", "r2"), ("r2", "r3"), ("r3", "r4")]
DSYNC = DELTA = 0.01


def latest(prefix):
    hits = sorted(glob.glob(os.path.join(DOCS, prefix + "*.json")))
    return (json.load(open(hits[-1])), os.path.basename(hits[-1])) if hits else (None, None)


def score(d, name):
    Ls, T = d["Ls"], d["T_ep"]
    cur = {(c["eps"], c["rung"]): c["curves"] for c in d["curves"]}
    epss = sorted({k[0] for k in cur}, key=lambda s: eval(s))
    out = dict(artifact=name, T_ep=T, B=d["B"], Ls=Ls, rows=[], collapse=[], r3r4_max=None)
    worst_r3r4 = (0.0, None)
    for eps in epss:
        for rung in ("r1", "r2", "r3", "r4"):
            c = cur[(eps, rung)]
            def worst_at(i, factor=1.0):
                return max(c[q][i] * factor for q in c if q not in NON_QUERY and c[q][i] is not None)
            La = next((L for i, L in enumerate(Ls) if worst_at(i) < DSYNC), None)
            Lb = next((L for i, L in enumerate(Ls) if L != T and worst_at(i, T / (T - L)) < DSYNC), None)
            out["rows"].append(dict(eps=eps, rung=rung, Lstar_a=La, Lstar_b=Lb))
        for a, b in PAIRS:
            ca, cb = cur[(eps, a)], cur[(eps, b)]
            gaps = [max(ca[q][i] - cb[q][i] for q in ca if q not in NON_QUERY and ca[q][i] is not None) for i in range(len(Ls))]
            Lc = next((L for L, g in zip(Ls, gaps) if g < DELTA), None)
            out["collapse"].append(dict(eps=eps, pair=f"{a}->{b}", Lstar=Lc, max_gap_per_L={str(L): g for L, g in zip(Ls, gaps)}))
            if (a, b) == ("r3", "r4"):
                m = max(gaps)
                if m > worst_r3r4[0]:
                    worst_r3r4 = (m, dict(eps=eps, L=Ls[gaps.index(m)]))
    out["r3r4_max"] = dict(gap=worst_r3r4[0], at=worst_r3r4[1])
    return out


def main():
    res = {}
    for fam, prefix in [("baseline(14,·,2)", "c1-sync-sweep-corrected-"),
                        ("F2(14,·,2)", "c1-sync-sweep-F2-heldout-"),
                        ("F3'(14,·,1)", "c1-sync-sweep-F3-heldout-")]:
        d, name = latest(prefix)
        if d is None:
            print(f"{fam}: missing"); continue
        s = score(d, name); res[fam] = s
        print(f"\n===== {fam}   {name}   Ls={s['Ls']}")
        print("  measure (a) law-mass L* / measure (b) trunc-conditional L*  at δ_sync=0.01")
        for r in s["rows"]:
            print(f"    eps={r['eps']:>3} {r['rung']}   a: {str(r['Lstar_a']):>4}   b: {str(r['Lstar_b']):>4}")
        print("  L-axis collapse L*(δ=0.01):")
        for c in s["collapse"]:
            print(f"    eps={c['eps']:>3} {c['pair']}  {c['Lstar']}")
        print(f"  max r3->r4 gap: {s['r3r4_max']['gap']:.6f} at {s['r3r4_max']['at']}")
    if len(sys.argv) > 1:
        json.dump(res, open(sys.argv[1], "w"), indent=1)
        print(f"\nwrote {sys.argv[1]}")


if __name__ == "__main__":
    main()
