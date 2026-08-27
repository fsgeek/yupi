"""Existence census of order-sensitive buckets in C1 from reset, by kind-multiset
and first bucket index (the D8 note's `_find_noncommuting_bucket` helper made
exhaustive). Reads NO attribution quantity — no entropy, no Δ, no posterior
value is printed or stored; it records only WHICH noncommuting bucket kinds the
channel admits at a horizon and how many (prefix, bucket) cases carry each.
Written 2026-08-27 to apply the PI's decision rule for grid expansion ("if the
instrument we have will allow us to understand the interface costs, don't
expand; if it won't, expand and explain why").

(run: python scripts/d8_bucket_census.py OUT.json)
"""
import json
import os
import sys
import time
from collections import Counter
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from yupi.config import WorldConfig  # noqa: E402
from yupi.enumerator import paths  # noqa: E402
from yupi.filter import initial_belief  # noqa: E402
from yupi.interfaces import project  # noqa: E402
from yupi.programs import c1_programs  # noqa: E402
from yupi.shuffled import multiset_key, run_buckets, step_bucket, step_ordered_bucket  # noqa: E402

CONDITIONS = [  # (eps, rung, B, H, admitted-in-v0.2 at L=T_ep=H?)
    ("1", "r1", 3, 9, True), ("1", "r4", 3, 9, True), ("1", "r1", 2, 10, True),
    ("1", "r1", 3, 12, False), ("1", "r1", 2, 12, False),
    ("1/2", "r1", 3, 9, True), ("1/2", "r1", 2, 10, True),
]


def census(eps, rung, B, H):
    cfg, progs = WorldConfig.c1(epsilon=Fraction(eps)), c1_programs()
    seen, hits = set(), Counter()
    t = time.perf_counter()
    for recs, _, _ in paths(cfg, progs, H):
        for b in range(H // B):
            vis_prefix = [[project(r, rung) for r in recs[k * B:(k + 1) * B]] for k in range(b)]
            latent = [project(r, rung) for r in recs[b * B:(b + 1) * B]]
            key = (tuple(map(tuple, vis_prefix)), multiset_key(latent))
            if len(set(latent)) < 2 or key in seen:
                continue
            seen.add(key)
            belief = run_buckets(cfg, progs, vis_prefix, rung, B, mode="ordered") if vis_prefix else initial_belief(cfg)
            if step_ordered_bucket(belief, latent, rung, cfg, progs) != step_bucket(belief, latent, rung, cfg, progs):
                hits[(b, tuple(sorted(r.kind for r in latent)))] += 1
    return hits, time.perf_counter() - t


def main():
    out = []
    for eps, rung, B, H, adm in CONDITIONS:
        hits, dt = census(eps, rung, B, H)
        bykind = {}
        for (b, kinds), n in hits.items():
            d = bykind.setdefault("+".join(kinds), dict(cases=0, first_bucket_index=b))
            d["cases"] += n
            d["first_bucket_index"] = min(d["first_bucket_index"], b)
        for d in bykind.values():
            d["first_ticks"] = [d["first_bucket_index"] * B + 1, d["first_bucket_index"] * B + B]
        rec = dict(world="c1", eps=eps, rung=rung, B=B, H=H, admitted_full_context_in_v0_2=adm,
                   cases=sum(hits.values()), kinds=dict(sorted(bykind.items(), key=lambda kv: -kv[1]["cases"])),
                   wall_s=round(dt, 1))
        out.append(rec)
        print(f"eps={eps} {rung} B={B} H={H} admitted={adm} ({dt:.0f}s): {rec['cases']} cases", flush=True)
        for k, d in rec["kinds"].items():
            print(f"    {d['cases']:6d}  {k}  first ticks {d['first_ticks']}", flush=True)
    json.dump(dict(script="scripts/d8_bucket_census.py", reads_results=False, conditions=out),
              open(sys.argv[1], "w"), indent=1)


if __name__ == "__main__":
    main()
