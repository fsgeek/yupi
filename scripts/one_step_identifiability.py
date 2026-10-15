"""Declared check: docs/one-step-identifiability-check-2026-10-15.md. Groups classes by exact P*(KIND)
(Fraction strings, exact equality) and reports the law mass in groups whose observation gap G spans >= 0.1
and >= 0.25 bits.
  python scripts/one_step_identifiability.py [rows_dir] [--out docs/<name>.json]
"""
import json
import sys
from pathlib import Path

rows_dir = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else Path.home() / ".cache/yupi-scratch/split-v2")
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
res = []
for eps in ("1", "1_2"):
    for rung in ("r0", "r1", "r2", "r3", "r4"):
        f = rows_dir / f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl"
        groups, M = {}, 0.0
        for line in open(f):
            x = json.loads(line)
            M += x["mass"]
            groups.setdefault(tuple(map(tuple, x["p_star"])), []).append((x["mass"], x["g"]))
        def span_mass(t):
            n, m, big = 0, 0.0, 0.0
            for g in groups.values():
                gs = [y for _, y in g]
                s = max(gs) - min(gs)
                big = max(big, s)
                if s >= t:
                    n += 1
                    m += sum(w for w, _ in g)
            return n, m / M, big
        n1, m1, big = span_mass(0.1)
        n25, m25, _ = span_mass(0.25)
        r = dict(eps=eps.replace("_", "/"), rung=rung, n_classes=sum(len(g) for g in groups.values()), n_groups=len(groups),
                 groups_span_ge_0_1=n1, mass_span_ge_0_1=m1, groups_span_ge_0_25=n25, mass_span_ge_0_25=m25, largest_span=big)
        res.append(r)
        print(f"eps {r['eps']:>3} {rung}: classes {r['n_classes']:>6} groups {r['n_groups']:>6} | span>=0.1: {n1:>4} groups, mass {m1:.3f} | "
              f"span>=0.25: {n25:>4} groups, mass {m25:.3f} | largest span {big:.3f}")
for eps in ("1", "1/2"):
    c = [r for r in res if r["eps"] == eps and r["rung"] != "r0"]
    sup = sum(r["mass_span_ge_0_1"] >= 0.05 for r in c)
    none = all(r["mass_span_ge_0_1"] < 0.01 for r in c)
    print(f"eps {eps}: content rungs with >=5% mass at span>=0.1: {sup}/4 -> " + ("SUPPORTED" if sup >= 3 else "NOT SUPPORTED" if none else "BETWEEN"))
if out:
    Path(out).write_text(json.dumps(dict(declared="docs/one-step-identifiability-check-2026-10-15.md", rows_dir=str(rows_dir), rows=res), indent=1))
