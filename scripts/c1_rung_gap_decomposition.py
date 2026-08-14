"""Exact decomposition of adjacent-rung mean-support gaps at a WindowLaw.

(run: python scripts/c1_rung_gap_decomposition.py T_ep L B [out.json])

An adjacent-rung gap can come ONLY from coarse-rung windows that SPLIT at
the finer rung: a window that does not split matches the identical path
set at both rungs, so its posterior (hence support) is unchanged. This
script therefore (a) finds every split and its exact gap contribution
    mass_coarse * supp_coarse - sum_children(mass_child * supp_child),
asserting the contributions sum to the table gap; (b) attributes the
r2->r3 gap between windows that contain a RELEASE (the conjectured
multi-waiter-wake mechanism of c1-support-measurement-v0.1.md finding 3)
and windows that do not (BLOCK.related revealing the hidden lock owner);
and (c) for every r3->r4 split, prints the actor/lineage fields of each
child so the differing field is identified by inspection, and checks two
claims mechanically: does any split's children differ on a field other
than an IO_ISSUE lineage, and does any in-window IO_COMPLETE carry a
lineage different from an in-window IO_ISSUE of the same window (the
completion-matching mechanism)?
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior

PAIRS = (("r1", "r2"), ("r2", "r3"), ("r3", "r4"))


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = {}
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        w_T = endpoint_prior(law)
        cache = {T: paths(cfg, progs, T) for T in law.endpoints()}

        def agg_at(rung):
            agg = {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    if key not in agg:
                        agg[key] = [Fraction(0), set()]
                    agg[key][0] += w_T * prob
                    agg[key][1].add(final)
            return agg

        aggs = {r: agg_at(r) for r in ("r1", "r2", "r3", "r4")}
        eps_out = {}
        print(f"\n===== eps={eps} =====")
        for coarse, fine in PAIRS:
            children = {}
            for key in aggs[fine]:
                ck = (key[0], tuple(project(r, coarse) for r in key[1]))
                children.setdefault(ck, []).append(key)
            splits = []
            total_gap = Fraction(0)
            release_gap = Fraction(0)
            for ck, kids in children.items():
                if len(kids) == 1:
                    continue
                cm, cf = aggs[coarse][ck]
                contrib = cm * len(cf) - sum(
                    aggs[fine][k][0] * len(aggs[fine][k][1]) for k in kids
                )
                total_gap += contrib
                if any(r.kind == "RELEASE" for r in ck[1]):
                    release_gap += contrib
                splits.append((contrib, ck, kids, cm, len(cf)))
            table_gap = sum(m * len(s) for m, s in aggs[coarse].values()) - sum(
                m * len(s) for m, s in aggs[fine].values()
            )
            assert total_gap == table_gap, (coarse, fine, total_gap, table_gap)
            print(
                f"{coarse}->{fine}: gap={float(total_gap):.6f} exact={total_gap} "
                f"({len(splits)} splits; sum matches table)"
            )
            if (coarse, fine) == ("r2", "r3"):
                print(
                    f"  windows containing RELEASE: {float(release_gap):.6f} "
                    f"({float(release_gap / total_gap) * 100:.1f}%); "
                    f"rest (BLOCK.related owner channel): "
                    f"{float(total_gap - release_gap):.6f}"
                )
            if (coarse, fine) == ("r3", "r4"):
                non_issue_diff = False
                completion_mismatch = False
                diff_kinds = set()
                for contrib, ck, kids, cm, csupp in sorted(
                    splits, key=lambda s: s[0], reverse=True
                ):
                    print(
                        f"  split kinds={tuple(r.kind for r in ck[1])} "
                        f"mass~{float(cm):.6f} supp={csupp} "
                        f"gap~{float(contrib):.6f}"
                    )
                    for k in sorted(kids, key=lambda k: -aggs['r4'][k][0]):
                        m, f = aggs["r4"][k]
                        fields = tuple(
                            (r.kind, r.actor, r.lineage) for r in k[1]
                        )
                        print(
                            f"     mass~{float(m):.6f} supp={len(f):>3} "
                            f"{fields}"
                        )
                    # mechanical claim checks: differing records may differ
                    # ONLY in their lineage field (kind/actor/obj/related
                    # identical) — record which kinds carry the difference
                    base = kids[0][1]
                    for k in kids[1:]:
                        for r0, r1 in zip(base, k[1]):
                            if r0 == r1:
                                continue
                            if (
                                r0.kind != r1.kind
                                or r0.actor != r1.actor
                                or r0.obj != r1.obj
                                or r0.related != r1.related
                            ):
                                non_issue_diff = True
                            else:
                                diff_kinds.add(r0.kind)
                    for k in kids:
                        issues = {
                            r.lineage for r in k[1] if r.kind == "IO_ISSUE"
                        }
                        for r in k[1]:
                            if r.kind == "IO_COMPLETE" and issues and (
                                r.lineage not in issues
                            ):
                                completion_mismatch = True
                print(
                    f"  any child pair differing outside a lineage field: "
                    f"{non_issue_diff}; kinds carrying lineage differences: "
                    f"{sorted(diff_kinds)}"
                )
                print(
                    f"  any in-window completion with lineage != its "
                    f"window's issue: {completion_mismatch}"
                )
            eps_out[f"{coarse}->{fine}"] = dict(
                gap=str(total_gap),
                gap_f=float(total_gap),
                n_splits=len(splits),
                release_gap=str(release_gap),
            )
        out[str(eps)] = eps_out

    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(dict(law=dict(T_ep=T_ep, L=L, B=B), gaps=out), f, indent=2)
        print(f"\nraw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
