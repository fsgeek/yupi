"""Whole-draft review W3 (2026-10-13): per rung and eps, the exact state entropy H(S | window), Log20's kind of
quantity (identifiability), beside the next-record predictive entropy split into the irreducible part H(next | S)
and the observation-induced gap (Part I's decomposition). Canonical structural observer, window aggregation, from
the frozen-law raws of 2026-09-05/06. Output: docs/state-vs-predictive-40-8-2-2026-10-13.json.
  python3 scripts/state_vs_predictive_table.py
"""
import glob
import json

rows = []
for e, tag in (("1", False), ("1/2", True)):
    for g in ["r0", "r1", "r2", "r3", "r4"]:
        def pick(pat):
            return [x for x in glob.glob(pat) if ("eps1_2" in x) == tag][0]
        qf = pick(f"docs/c1prime-loop-query-ceilings-40-8-2-{g}-2026-09-0*.json")
        pf = pick(f"docs/c1prime-loop-predictive-targets-40-8-2-{g}-2026-09-0*.json")
        q = json.load(open(qf))["rows"][0]
        p = json.load(open(pf))["rows"][0]["means"]["pnext"]
        rows.append(dict(eps=e, rung=g, state_entropy=q["mean_state_entropy_bits"], pnext_total=p["total"],
                         pnext_irreducible=p["irreducible"], pnext_gap=p["gap"], sources=[qf, pf]))
json.dump(rows, open("docs/state-vs-predictive-40-8-2-2026-10-13.json", "w"), indent=1)
for r in rows:
    print(r["eps"], r["rung"], round(r["state_entropy"], 4), round(r["pnext_gap"], 4))
