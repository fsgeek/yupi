"""δ sweep (Part II v0.2.4 §C, first of three) — a READ of the day-seven
raw ceilings, not a new measurement.

(run: python scripts/c1_delta_sweep.py [out.json])

Part II §6 rung-collapse criterion: adjacent rungs r, r' collapse at
context L if  max_{q in Q} [H_r(q|L) - H_{r'}(q|L)] < δ  bits, with Q the
COMPLETE statutory query set {Q1[l], Q2[i], Q3[dev], Q4 (statutory, W),
Q5[i_b,i_r] per ordered pair}. δ is NOT frozen (v0.2.4 §C); this script
prints every adjacent-rung gap for every statutory query in every
(law, ε) cell that exists, then the per-cell max (the quantity δ is
compared against), then a coverage table: for a grid of candidate δ,
which (law, ε, rung pair) cells would be declared collapsed.

Non-statutory diagnostics (Q3thr, Q4proxy, Q5joint) are printed in a
separate table and do NOT enter the max.

Inputs (float mean_bits as stored — presentation floats of exact
rationals; the freeze will be stated in bits at 3 significant figures,
far coarser than float error):
  docs/c1-query-ceilings-{T}-{L}-{B}-raw-2026-08-15.json    Q1,Q2,Q3,Q5
  docs/c1-q4-ceilings-{T}-{L}-{B}-W{W}-raw-2026-08-15.json  Q4 statutory
"""

import json
import os
import sys

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
LAWS = [(12, 2, 2), (14, 2, 2), (14, 4, 2), (12, 12, 2)]
RUNGS = ("r1", "r2", "r3", "r4")
PAIRS = [("r1", "r2"), ("r2", "r3"), ("r3", "r4")]
DELTA_GRID = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1]


def load(name):
    p = os.path.join(DOCS, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def statutory(qname):
    # v0.2 labels: Q3thr, Q4proxy[l], Q5joint are diagnostics.  The control
    # law's artifact still carries v0.1 labels: Q3ids (=Q3thr), Q4[l] (=Q4proxy),
    # and an aggregate "Q5" (not per pair) — excluded likewise.
    if qname.startswith(("Q3thr", "Q3ids", "Q4proxy", "Q4[")):
        return False
    if qname in ("Q5joint", "Q5"):
        return False
    return True


def main():
    out = dict(criterion="max_q [H_r(q) - H_r'(q)] < delta, statutory Q",
               laws=[], delta_grid=DELTA_GRID)
    cell_max = []   # (law, eps, pair, W-tag, max_gap, argmax_query)
    all_gaps = []   # every statutory per-query gap
    for T, L, B in LAWS:
        qc = load(f"c1-query-ceilings-{T}-{L}-{B}-raw-2026-08-15.json")
        if qc is None:
            print(f"law ({T},{L},{B}): no query-ceilings artifact — skipped")
            continue
        q4s = {W: load(f"c1-q4-ceilings-{T}-{L}-{B}-W{W}-raw-2026-08-15.json")
               for W in (4, 8)}
        q4s = {W: d for W, d in q4s.items() if d is not None}
        rows = {(r["eps"], r["rung"]): r for r in qc["rows"]}
        law_out = dict(law=dict(T_ep=T, L=L, B=B), cells=[])
        print(f"\n=== law (T_ep={T}, L={L}, B={B})  Q4 W available: {sorted(q4s)}")
        for eps in ("1", "1/2"):
            qnames = list(rows[(eps, "r1")]["queries"].keys())
            for a, b in PAIRS:
                ra, rb = rows[(eps, a)], rows[(eps, b)]
                print(f"\n--- eps={eps:>3}  {a}->{b}   (bits; H_{a} - H_{b})")
                gaps = {}
                for q in qnames:
                    g = ra["queries"][q]["mean_bits"] - rb["queries"][q]["mean_bits"]
                    gaps[q] = g
                    tag = "  " if statutory(q) else " *"
                    print(f"  {q:<12}{tag} {ra['queries'][q]['mean_bits']:.6f} - "
                          f"{rb['queries'][q]['mean_bits']:.6f} = {g: .6f}")
                # Q4 statutory, per W
                for W, d in sorted(q4s.items()):
                    q4rows = {(r["eps"], r["rung"]): r for r in d["rows"]}
                    xa, xb = q4rows[(eps, a)], q4rows[(eps, b)]
                    g_tot = xa["total_bits"] - xb["total_bits"]
                    g_gap = xa["gap_bits"] - xb["gap_bits"]
                    g_irr = xa["irreducible_bits"] - xb["irreducible_bits"]
                    gaps[f"Q4stat[W{W}]"] = g_tot
                    print(f"  Q4stat[W{W}]    {xa['total_bits']:.6f} - {xb['total_bits']:.6f} = {g_tot: .6f}"
                          f"   (gap-part diff {g_gap: .6f}; irreducible diff {g_irr: .2e})")
                stat = {q: g for q, g in gaps.items() if statutory(q)}
                neg = [q for q, g in stat.items() if g < -1e-9]
                if neg:
                    print(f"  !! negative statutory gaps (monotonicity violation?): {neg}")
                # per-W max: statutory non-Q4 plus Q4 at that W; if no Q4, note it
                if q4s:
                    for W in sorted(q4s):
                        pool = {q: g for q, g in stat.items()
                                if not q.startswith("Q4stat") or q == f"Q4stat[W{W}]"}
                        qm = max(pool, key=pool.get)
                        cell_max.append(((T, L, B), eps, f"{a}->{b}", f"W{W}", pool[qm], qm))
                        print(f"  MAX over statutory (Q4 at W={W}): {pool[qm]:.6f}  <- {qm}")
                        law_out["cells"].append(dict(eps=eps, pair=f"{a}->{b}", W=W,
                                                     max_gap=pool[qm], argmax=qm,
                                                     gaps=pool))
                        all_gaps.extend((((T, L, B), eps, f"{a}->{b}", f"W{W}", q, g)
                                         for q, g in pool.items()))
                else:
                    qm = max(stat, key=stat.get)
                    cell_max.append(((T, L, B), eps, f"{a}->{b}", "noQ4", stat[qm], qm))
                    print(f"  MAX over statutory (no Q4 artifact): {stat[qm]:.6f}  <- {qm}")
                    law_out["cells"].append(dict(eps=eps, pair=f"{a}->{b}", W=None,
                                                 max_gap=stat[qm], argmax=qm, gaps=stat))
                    all_gaps.extend((((T, L, B), eps, f"{a}->{b}", "noQ4", q, g)
                                     for q, g in stat.items()))
        out["laws"].append(law_out)

    print("\n\n===== per-cell MAX statutory gap (the quantity δ is compared against), sorted")
    for law, eps, pair, W, g, q in sorted(cell_max, key=lambda x: x[4]):
        print(f"  {g:.6f}  law={law} eps={eps:>3} {pair} {W:<5} <- {q}")
    out["cell_max"] = [dict(law=law, eps=eps, pair=pair, W=W, max_gap=g, argmax=q)
                       for law, eps, pair, W, g, q in cell_max]

    print("\n===== coverage: cells declared COLLAPSED (max < δ) per candidate δ")
    for dlt in DELTA_GRID:
        col = [c for c in cell_max if c[4] < dlt]
        print(f"  δ={dlt:<7g} collapsed {len(col):>2}/{len(cell_max)}: "
              + ", ".join(f"{c[0]}/{c[1]}/{c[2]}/{c[3]}" for c in col))
    out["coverage"] = {str(dlt): [dict(law=c[0], eps=c[1], pair=c[2], W=c[3])
                                  for c in cell_max if c[4] < dlt] for dlt in DELTA_GRID}

    print("\n===== ALL statutory per-query gaps, sorted (smallest 25 and largest 10)")
    all_gaps.sort(key=lambda x: x[5])
    for law, eps, pair, W, q, g in all_gaps[:25]:
        print(f"  {g: .6e}  law={law} eps={eps:>3} {pair} {W} {q}")
    print("  ...")
    for law, eps, pair, W, q, g in all_gaps[-10:]:
        print(f"  {g: .6e}  law={law} eps={eps:>3} {pair} {W} {q}")
    # simple gap histogram in decades
    print("\n===== decade histogram of statutory per-query gaps (all cells)")
    import math
    buckets = {}
    for *_, g in all_gaps:
        k = "<=0" if g <= 1e-12 else f"1e{math.floor(math.log10(g))}"
        buckets[k] = buckets.get(k, 0) + 1
    for k in sorted(buckets, key=lambda s: -99 if s == "<=0" else int(s[2:])):
        print(f"  {k:>6}: {buckets[k]}")
    out["gap_histogram"] = buckets

    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {sys.argv[1]}")


if __name__ == "__main__":
    main()
