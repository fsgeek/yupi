"""Field-level decomposition of adjacent-rung QUERY entropy gaps at a law.

(run: python scripts/c1_query_gap_decomposition.py T_ep L B [out.json])

Same principle as c1_rung_gap_decomposition.py: an adjacent-rung gap in a
query's mean posterior entropy comes only from coarse-rung windows that
SPLIT at the finer rung. For every split, the query's gain is
    mass_coarse * H(q | coarse) - sum_children mass_child * H(q | child)
(asserted to sum to the table gap per query). Each split is attributed to
the SIGNATURE of (kind.field) pairs on which its children's records
differ — e.g. {ACQUIRE.obj}, {BLOCK.related}, {ACQUIRE.obj, BLOCK.obj} —
and the per-signature share of each query's gap is reported. Written on
day seven to check the truthsayer's field attribution independently
(receiving numbers ⇒ recompute by another path).
"""

import json
import sys
from collections import defaultdict
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.queries import all_queries, entropy_bits, pushforward
from yupi.window import WindowLaw, endpoint_prior

PAIRS = (("r1", "r2"), ("r2", "r3"), ("r3", "r4"))
FIELDS = ("obj", "related", "lineage")


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = {}
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        queries = all_queries(cfg)
        w_T = endpoint_prior(law)
        cache = {T: paths(cfg, progs, T) for T in law.endpoints()}

        def agg_at(rung):
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = agg.setdefault(key, {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
            return agg

        aggs = {r: agg_at(r) for r in ("r1", "r2", "r3", "r4")}
        # For each fine window, its coarse parent key.
        def parent_key(fine_key, coarse):
            reset, recs = fine_key
            return (reset, tuple(project(r, coarse) for r in recs))

        def H_of(joint, fn):
            mass = sum(joint.values(), Fraction(0))
            belief = {s: m / mass for s, m in joint.items()}
            return float(mass), entropy_bits(pushforward(belief, fn))

        eps_out = {}
        print(f"\n===== eps={eps} =====")
        for coarse, fine in PAIRS:
            children = defaultdict(list)
            for fk in aggs[fine]:
                children[parent_key(fk, coarse)].append(fk)
            # signature of a split: (kind.field) pairs differing among children
            gap_by_sig = {name: defaultdict(float) for name, _ in queries}
            total_gap = {name: 0.0 for name, _ in queries}
            for ck, fks in children.items():
                if len(fks) < 2:
                    continue
                sig = set()
                n = len(ck[1])
                for i in range(n):
                    kind = ck[1][i].kind
                    for f in FIELDS:
                        vals = {getattr(fk[1][i], f) for fk in fks}
                        if len(vals) > 1:
                            sig.add(f"{kind}.{f}")
                sig = tuple(sorted(sig))
                for name, fn in queries:
                    mc, Hc = H_of(aggs[coarse][ck], fn)
                    gain = mc * Hc - sum(
                        (lambda m, H: m * H)(*H_of(aggs[fine][fk], fn)) for fk in fks
                    )
                    gap_by_sig[name][sig] += gain
                    total_gap[name] += gain
            # check against table gaps
            pair_out = {}
            for name, fn in queries:
                table_gap = sum(H_of(j, fn)[0] * H_of(j, fn)[1] for j in aggs[coarse].values()) \
                    - sum(H_of(j, fn)[0] * H_of(j, fn)[1] for j in aggs[fine].values())
                assert abs(table_gap - total_gap[name]) < 1e-9, (name, table_gap, total_gap[name])
                shares = {}
                if total_gap[name] > 1e-12:
                    shares = {"+".join(s) if s else "(none)": g / total_gap[name]
                              for s, g in sorted(gap_by_sig[name].items(), key=lambda kv: -kv[1])}
                pair_out[name] = dict(gap_bits=total_gap[name], shares=shares)
                top = ", ".join(f"{k}={v:.1%}" for k, v in list(shares.items())[:3])
                print(f"{coarse}->{fine} {name:10s} gap={total_gap[name]:.5f}  {top}")
            eps_out[f"{coarse}->{fine}"] = pair_out
        out[str(eps)] = eps_out
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(dict(law=dict(T_ep=T_ep, L=L, B=B), decomposition=out), f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}")


if __name__ == "__main__":
    main()
