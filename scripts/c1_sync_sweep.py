"""δ_sync sweep (Part II v0.2.4 §C, sweep 2 of 3) — posterior entropy versus
context length L at fixed T_ep, per rung and statutory query; a READ of
query-ceilings and Q4-ceilings artifacts at (T_ep, L, B) for several L.

Repointed 2026-08-21 to the corrected-kernel raws (-corrected-*.json,
latest date wins; filenames actually read are recorded in the output).
The buggy-kernel inputs (-raw-2026-08-15.json) and this script's prior
form are in git history.

(run: python scripts/c1_sync_sweep.py T_ep B L1 L2 ... [--out out.json])

Part II §6: synchronization horizon = smallest L at which a rung's
posterior entropy on a query falls below δ_sync (bits). δ_sync is NOT
frozen (v0.2.4 §C). This script prints, for each (ε, rung, query), the
mean posterior entropy at each available L, then for a grid of candidate
δ_sync the synchronization horizon L*(δ_sync) per (ε, rung, query), and
a summary: for each δ_sync, the max over statutory queries of L* per
(ε, rung) — the L at which the rung has synchronized on EVERY statutory
query.

Q4 statutory: the total is irreducible + gap, and the irreducible term is
L- and rung-invariant (given the exact state the forecast is still
stochastic), so Q4 can never fall below its irreducible term; the
synchronizing quantity for Q4 is its GAP part (observation-induced),
which is what is used here. Both are printed.
"""

import glob
import json
import os
import sys

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
RUNGS = ("r1", "r2", "r3", "r4")
DSYNC_GRID = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]


def load_latest(prefix):
    """Latest docs/{prefix}-corrected-*.json, or (None, None)."""
    hits = sorted(glob.glob(os.path.join(DOCS, prefix + "-corrected-*.json")))
    if not hits:
        return None, None
    with open(hits[-1]) as f:
        return json.load(f), os.path.basename(hits[-1])


def statutory(q):
    if q.startswith(("Q3thr", "Q3ids", "Q4proxy", "Q4[")):
        return False
    if q in ("Q5joint", "Q5"):
        return False
    return True


def main():
    args = sys.argv[1:]
    out_path = None
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    T_ep, B = int(args[0]), int(args[1])
    Ls = [int(a) for a in args[2:]]
    data = {}
    inputs = {}
    for L in Ls:
        qc, qc_name = load_latest(f"c1-query-ceilings-{T_ep}-{L}-{B}")
        q4, q4_name = load_latest(f"c1-q4-ceilings-{T_ep}-{L}-{B}-W4")
        if qc is None:
            print(f"L={L}: no corrected query-ceilings artifact — skipped")
            continue
        print(f"L={L}: reading {qc_name}" + (f" + {q4_name}" if q4_name else " (no Q4)"))
        data[L] = (qc, q4)
        inputs[L] = dict(query=qc_name, q4=q4_name)
    Ls = sorted(data)
    out = dict(T_ep=T_ep, B=B, Ls=Ls, inputs=inputs,
               dsync_grid=DSYNC_GRID, curves=[], horizons=[])
    for eps in ("1", "1/2"):
        for rung in RUNGS:
            # gather curves
            curves = {}     # query -> [H at each L]
            for L in Ls:
                qc, q4 = data[L]
                row = next(r for r in qc["rows"] if r["eps"] == eps and r["rung"] == rung)
                for q, v in row["queries"].items():
                    if statutory(q):
                        curves.setdefault(q, []).append(v["mean_bits"])
                curves.setdefault("H(S)", []).append(row["mean_state_entropy_bits"])
                if q4 is not None:
                    r4 = next(r for r in q4["rows"] if r["eps"] == eps and r["rung"] == rung)
                    curves.setdefault("Q4stat.gap", []).append(r4["gap_bits"])
                    curves.setdefault("Q4stat.total", []).append(r4["total_bits"])
                    curves.setdefault("Q4stat.irr", []).append(r4["irreducible_bits"])
                else:
                    for k in ("Q4stat.gap", "Q4stat.total", "Q4stat.irr"):
                        curves.setdefault(k, []).append(None)
            print(f"\n=== T_ep={T_ep} B={B} eps={eps:>3} {rung}   H (bits) vs L = {Ls}")
            for q, vals in curves.items():
                print(f"  {q:<13} " + " ".join("   n/a  " if v is None else f"{v:8.5f}" for v in vals))
            out["curves"].append(dict(eps=eps, rung=rung, curves=curves))
            # horizons
            print(f"  --- L*(δ_sync): smallest L with H < δ_sync   (∞ = not within measured L)")
            stat_qs = [q for q in curves if q not in ("H(S)", "Q4stat.total", "Q4stat.irr")]
            hz = {}
            for d in DSYNC_GRID:
                per_q = {}
                for q in stat_qs:
                    Lstar = None
                    for L, v in zip(Ls, curves[q]):
                        if v is not None and v < d:
                            Lstar = L
                            break
                    per_q[q] = Lstar
                worst = None
                for q, Ls_ in per_q.items():
                    if Ls_ is None:
                        worst = None
                        break
                    worst = Ls_ if worst is None else max(worst, Ls_)
                hz[str(d)] = dict(per_query=per_q, all_queries=worst)
                binding = [q for q, v in per_q.items() if v == worst] if worst is not None else \
                          [q for q, v in per_q.items() if v is None]
                print(f"  δ_sync={d:<6g} L*(all statutory) = {'∞' if worst is None else worst:<3}"
                      f"  binding: {', '.join(binding)}")
            out["horizons"].append(dict(eps=eps, rung=rung, horizons=hz))
    if out_path:
        with open(out_path, "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
