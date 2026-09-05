"""Exact query ceilings (Q1–Q5) for C1 at a parameterized WindowLaw.

(run: python scripts/c1_query_ceilings.py T_ep L B [out.json];
 YUPI_AGG=paths (default, the committed method) | window (the window-process
 recursion, one r4 pass projected to every rung — 2026-09-04);
 YUPI_GATE=inline (default) | external (rely on the sharded gate raws in
 docs/ for (law, rung, ε); refused if they are absent or not all-exact);
 YUPI_RUNGS default r1,r2,r3,r4 (r0 may be prepended per v0.2.7.1);
 YUPI_PROGRAMS default c1)

Method: path aggregation by (reset_observed, projected window) → law mass
and belief over final states per window (enumerator side); every distinct
window ALSO recomputed through `window_filter` and its joint (U, S_T)
compared Fraction-for-Fraction (filter side) — the two-path gate, applied
before any query is pushed forward. Then each query's answer distribution
is the pushforward of the window's state marginal; the reported figure is
the law-mass-weighted mean entropy in bits, per (eps, rung, query), plus
the mean state entropy and the fraction of law mass on which the query is
fully resolved (H = 0). Invariants asserted: rung monotonicity per query,
H(Q|w) <= H(S|w) per window.
"""

import json
import sys
from fractions import Fraction

from yupi.eps_grid import eps_grid
from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c1_programs, programs_for
from yupi.queries import (
    all_queries, entropy_bits, pushforward, state_entropy_bits,
)
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import filter_window, filter_window_with_evidence
from yupi.window_process import window_law_aggregates

RUNGS = ("r1", "r2", "r3", "r4")


def _external_gate_ok(docs_dir, law, rung, eps, programs_name):
    """The sharded full gate for (law, rung, ε): eight shard raws, every
    mismatches list empty, shard counts summing to the recursion's total."""
    import glob, os
    tag = "" if eps == Fraction(1) else "-eps" + str(eps).replace("/", "_")
    pat = os.path.join(str(docs_dir), f"window-gate-{programs_name}-{law.T_ep}-{law.L}-{law.B}-{rung}-*-full{tag}-shard*.json")
    files = sorted(glob.glob(pat))
    if len(files) != 8:
        return None
    total, n = None, 0
    for f in files:
        d = json.load(open(f))
        (r,) = d["rows"]
        if r["mismatches"] or d["rung"] != rung or r["eps"] != str(eps):
            return None
        total = r["n_windows_total"]
        n += r["n"]
    return [os.path.basename(f) for f in files] if n == total else None


def compute_rows(law, eps, cfg, progs, rungs, agg="paths", gate="inline", docs_dir="docs", programs_name=None):
    """One ε: the per-rung rows of the artifact. `agg` selects the
    enumerator-side aggregation (path aggregation, or the window-process
    recursion with every rung projected from one r4 pass); `gate` selects
    the filter-side check — inline (every window through the exact filter:
    joint (U, S) compare on the paths side, state-marginal + law-mass
    compare on the recursion side, which has no per-U split) or external
    (the sharded full-gate raws for this (law, rung, ε) must exist in
    `docs_dir` with zero mismatches; refused otherwise)."""
    queries = all_queries(cfg)
    w_T = endpoint_prior(law)
    rows = []
    if agg == "paths":
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
        per_rung = {}
        for rung in rungs:
            a, mT = {}, {}
            for T in law.endpoints():
                u = law.offset(T)
                for recs, prob, final in path_cache[T]:
                    key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
                    d = a.setdefault(key, {})
                    d[(u, final)] = d.get((u, final), Fraction(0)) + w_T * prob
                    e = mT.setdefault(key, {})
                    e[T] = e.get(T, Fraction(0)) + w_T * prob
            per_rung[rung] = (a, mT)
    elif agg == "window":
        stats = {}
        aggs = window_law_aggregates(cfg, progs, law, tuple(rungs), stats)
        per_rung = {rung: (aggs[rung], stats["mass_T_by_rung"][rung]) for rung in rungs}
    else:
        raise ValueError(agg)
    prev_mean = None
    for rung in rungs:
        a, mass_T = per_rung[rung]
        total_mass = sum((sum(j.values(), Fraction(0)) for j in a.values()), Fraction(0))
        assert total_mass == 1
        gate_label = None
        if gate == "external":
            files = _external_gate_ok(docs_dir, law, rung, eps, programs_name or "c1")
            if files is None:
                raise RuntimeError(f"({law.T_ep},{law.L},{law.B}) {rung} eps={eps} is not gated: no all-exact 8-shard gate raws in {docs_dir}")
            gate_label = "external:" + ",".join(files)
        mean_H = {name: 0.0 for name, _ in queries}
        resolved = {name: Fraction(0) for name, _ in queries}
        mean_HS = 0.0
        by_T = {T: dict(mass=Fraction(0), HS=0.0, H={name: 0.0 for name, _ in queries}) for T in law.endpoints()}
        mismatches = 0
        for (reset, window), joint_mass in a.items():
            mass = sum(joint_mass.values(), Fraction(0))
            if gate == "inline":
                if agg == "paths":
                    path_joint = {k: m / mass for k, m in joint_mass.items()}
                    post = filter_window(cfg, progs, law, list(window), rung, reset)
                    filter_joint = {(u, s): w * m for u, (w, belief) in post.components.items()
                                    for s, m in belief.items() if w * m > 0}
                    if filter_joint != path_joint:
                        mismatches += 1
                        continue
                    gate_label = "inline-joint"
                else:
                    post, evidence = filter_window_with_evidence(cfg, progs, law, list(window), rung, reset)
                    if evidence != mass or post.state_marginal() != {s: m / mass for s, m in joint_mass.items()}:
                        mismatches += 1
                        continue
                    gate_label = "inline-marginal"
            belief = {}
            if agg == "paths":
                for (_, s), m in joint_mass.items():
                    belief[s] = belief.get(s, Fraction(0)) + m / mass
            else:
                belief = {s: m / mass for s, m in joint_mass.items()}
            HS = state_entropy_bits(belief)
            mean_HS += float(mass) * HS
            for T, mT in mass_T[(reset, window)].items():
                by_T[T]["mass"] += mT
                by_T[T]["HS"] += float(mT) * HS
            for name, fn in queries:
                H = entropy_bits(pushforward(belief, fn))
                assert H <= HS + 1e-9, (name, H, HS)
                mean_H[name] += float(mass) * H
                if H == 0.0:
                    resolved[name] += mass
                for T, mT in mass_T[(reset, window)].items():
                    by_T[T]["H"][name] += float(mT) * H
        assert mismatches == 0, f"two-path mismatches: {mismatches}"
        if prev_mean is not None:
            for name in mean_H:
                assert mean_H[name] <= prev_mean[name] + 1e-9, (rung, name)
        prev_mean = mean_H
        for T in by_T:
            assert by_T[T]["mass"] == w_T, (T, by_T[T]["mass"], w_T)
        rows.append(dict(
            eps=str(eps), rung=rung, n_windows=len(a),
            mean_state_entropy_bits=mean_HS,
            queries={name: dict(mean_bits=mean_H[name], resolved_mass=float(resolved[name])) for name in mean_H},
            by_endpoint={str(T): dict(U=law.offset(T), mean_state_entropy_bits=by_T[T]["HS"] / float(w_T),
                                      queries={name: by_T[T]["H"][name] / float(w_T) for name in mean_H})
                         for T in by_T},
            aggregation=agg, gate=gate_label,
        ))
    return rows


def main():
    import os
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    agg = os.environ.get("YUPI_AGG", "paths")
    gate = os.environ.get("YUPI_GATE", "inline")
    rungs = tuple(os.environ.get("YUPI_RUNGS", "r1,r2,r3,r4").split(","))
    programs_name = os.environ.get("YUPI_PROGRAMS", "c1")
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), aggregation=agg, gate=gate, programs=programs_name, rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        progs = programs_for(programs_name)
        for row in compute_rows(law, eps, cfg, progs, rungs, agg, gate, "docs", programs_name):
            out["rows"].append(row)
            qs = "  ".join(f"{n}={row['queries'][n]['mean_bits']:.4f}" for n in row["queries"])
            print(f"eps={row['eps']:>3} {row['rung']} n={row['n_windows']:>6} "
                  f"H(S)={row['mean_state_entropy_bits']:.4f}  {qs}", flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
