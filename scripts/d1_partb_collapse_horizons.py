"""D1 Part B — rung-collapse horizons under the frozen δ (Part II v0.2.5 §6).

Reads the corrected-kernel (14, L, 2) sync-sweep artifact and applies the
statutory criterion verbatim: adjacent rungs r, r′ collapse at context L if
max over the COMPLETE statutory query set {Q1, Q2, Q3, Q4 (statutory, gap
part — the rung difference of the total equals that of the gap part since the
irreducible term is rung-invariant), Q5 per pair} of H_r(q | L) − H_r′(q | L)
is < δ. H(S) is a diagnostic, not a statutory query, and is excluded.

L* is the smallest measured L at which the pair is collapsed; the table also
reports whether every statutory gap is exactly 0.0 at that L (the witness-11
candidate condition: "Q1–Q5 unchanged" holding exactly while L < T_ep).

Usage: python scripts/d1_partb_collapse_horizons.py [artifact.json] [delta]
"""
from __future__ import annotations

import json
import sys

DEFAULT = "docs/c1-sync-sweep-corrected-2026-08-21.json"
STATUTORY_PREFIXES = ("Q1", "Q2", "Q3", "Q4", "Q5")
PAIRS = (("r1", "r2"), ("r2", "r3"), ("r3", "r4"))


def main(path: str = DEFAULT, delta: float = 0.01) -> int:
    d = json.load(open(path, encoding="utf-8"))
    Ls = d["Ls"]
    by = {(c["eps"], c["rung"]): c["curves"] for c in d["curves"]}
    queries = [q for q in by[("1", "r1")] if q.startswith(STATUTORY_PREFIXES)]
    print(f"artifact {path}  T_ep={d['T_ep']} B={d['B']}  delta={delta}  "
          f"statutory queries={len(queries)}  Ls={Ls}")
    for eps in ("1", "1/2"):
        for a, b in PAIRS:
            A, B = by[(eps, a)], by[(eps, b)]
            lstar = None
            cells = []
            for i, L in enumerate(Ls):
                gaps = {q: A[q][i] - B[q][i] for q in queries}
                q = max(gaps, key=gaps.get)
                g = gaps[q]
                exact_zero = all(v == 0.0 for v in gaps.values())
                worst_neg = min(gaps.values())
                cells.append((L, g, q, exact_zero, worst_neg))
                if lstar is None and g < delta:
                    lstar = L
            print(f"\neps={eps}  {a}->{b}  L*={lstar}")
            for L, g, q, z, neg in cells:
                flag = "  ALL STATUTORY GAPS EXACTLY 0" if z else ""
                negs = f"  (min residual {neg:.1e})" if neg < 0 else ""
                print(f"  L={L:2d}  max_gap={g:.6f}  argmax={q:10s}{negs}{flag}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(*(args[:1] or [DEFAULT]), *([float(args[1])] if len(args) > 1 else [])))
