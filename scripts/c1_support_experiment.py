"""C1 windowed support growth vs the frozen D4 budget; D9 rule inputs.

(run: python scripts/c1_support_experiment.py [out.json])

The D4 measurement (Part I D4, D4/D9 precedence rule), run AFTER the
budget freeze (docs/d4-budget-freeze-v0.1.md, commit e921c74): support and
per-step cost of exact windowed inference on C1 under the interface rungs,
across the ε grid {1, 1/2}. Full-context support is identically 1 (the
injectivity theorem, witnessed by test_w6); the D4-relevant growth lives in
windowed observers, so the measured observer is the statute's base
(offset-unanchored, derived prior) under WindowLaw(T_ep=12, L=6, B=2).

Coverage: exhaustive over distinct windows at endpoints T<=10 for r1 (the
binding sparsest rung); deterministic stride samples elsewhere (documented
in the output). Instrumentation drives window_filter's own primitives
(state_marginal_at, _step_unnorm) step by step, so costs are those of the
real implementation.

Reported per (eps, rung): law-weighted mean and max of state-marginal
support, joint (U,S) support, worst single-step expanded transitions
(vs B1's 70k), worst single-step wall (vs B3's 1s).
"""

import json
import sys
import time
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import _step_unnorm, state_marginal_at

LAW = WindowLaw(T_ep=12, L=6, B=2)
EPS_GRID = (Fraction(1), Fraction(1, 2))
RUNGS = ("r1", "r2", "r3", "r4")
SAMPLE_TARGET = 200  # per endpoint, for non-exhaustive cells


def windows_for(cfg, progs, rung, exhaustive):
    """(window, law-weight) for distinct windows, per endpoint."""
    w_T = endpoint_prior(LAW)
    path_cache = {}
    for T in LAW.endpoints():
        u = LAW.offset(T)
        if T not in path_cache:
            path_cache[T] = paths(cfg, progs, T)
        agg = {}
        for recs, prob, _ in path_cache[T]:
            win = (u == 0, tuple(project(r, rung) for r in recs[u:]))
            agg[win] = agg.get(win, Fraction(0)) + w_T * prob
        items = sorted(agg.items(), key=lambda kv: kv[0].__repr__())
        cap = 2 * SAMPLE_TARGET if exhaustive and T == 12 else (
            None if exhaustive else SAMPLE_TARGET
        )
        if cap is not None and len(items) > cap:
            stride = max(1, len(items) // cap)
            items = items[::stride]
        yield items


def filter_instrumented(cfg, progs, mu_cache, obs_seq, rung, reset_observed):
    """window_filter's mixture loop, instrumented, using its primitives."""
    compatible = LAW.compatible_endpoints(len(obs_seq), reset_observed)
    comps = {}
    worst_step_transitions = 0
    worst_step_wall = 0.0
    for _, u in compatible:
        if u not in mu_cache:
            mu_cache[u] = state_marginal_at(cfg, progs, u)
        belief = mu_cache[u]
        weight = Fraction(1)
        dead = False
        for obs in obs_seq:
            t0 = time.perf_counter()
            expanded = sum(len(enabled(s, cfg, progs)) for s in belief)
            belief, lik = _step_unnorm(belief, obs, rung, cfg, progs)
            wall = time.perf_counter() - t0
            worst_step_transitions = max(worst_step_transitions, expanded)
            worst_step_wall = max(worst_step_wall, wall)
            if lik == 0:
                dead = True
                break
            weight *= lik
            belief = {s: m / lik for s, m in belief.items()}
        if not dead:
            comps[u] = (weight, belief)
    total = sum((w for w, _ in comps.values()), Fraction(0))
    comps = {u: (w / total, b) for u, (w, b) in comps.items()}
    marginal = {}
    for _, (w, b) in comps.items():
        for s, m in b.items():
            marginal[s] = marginal.get(s, Fraction(0)) + w * m
    joint_support = sum(len(b) for _, b in comps.values())
    return len(marginal), joint_support, worst_step_transitions, worst_step_wall


def main():
    results = []
    for eps in EPS_GRID:
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        for rung in RUNGS:
            exhaustive = rung == "r1"
            mu_cache = {}
            stats = dict(
                n=0, w_total=Fraction(0),
                mean_support=Fraction(0), max_support=0,
                mean_joint=Fraction(0), max_joint=0,
                max_step_transitions=0, max_step_wall=0.0,
            )
            for items in windows_for(cfg, progs, rung, exhaustive):
                for (reset, win), w in items:
                    ms, js, mt, mw = filter_instrumented(
                        cfg, progs, mu_cache, list(win), rung, reset
                    )
                    stats["n"] += 1
                    stats["w_total"] += w
                    stats["mean_support"] += w * ms
                    stats["mean_joint"] += w * js
                    stats["max_support"] = max(stats["max_support"], ms)
                    stats["max_joint"] = max(stats["max_joint"], js)
                    stats["max_step_transitions"] = max(stats["max_step_transitions"], mt)
                    stats["max_step_wall"] = max(stats["max_step_wall"], mw)
            row = dict(
                eps=str(eps), rung=rung, exhaustive_r1=exhaustive,
                n_windows=stats["n"],
                mean_support=float(stats["mean_support"] / stats["w_total"]),
                max_support=stats["max_support"],
                mean_joint_support=float(stats["mean_joint"] / stats["w_total"]),
                max_joint_support=stats["max_joint"],
                max_step_transitions=stats["max_step_transitions"],
                max_step_wall_s=stats["max_step_wall"],
            )
            results.append(row)
            print(
                f"eps={row['eps']:>3} {rung}  n={row['n_windows']:>5}  "
                f"E[supp]={row['mean_support']:.3f}  max_supp={row['max_support']:>3}  "
                f"E[joint]={row['mean_joint_support']:.3f}  max_joint={row['max_joint_support']:>3}  "
                f"max_step_trans={row['max_step_transitions']:>6}  "
                f"max_step_wall={row['max_step_wall_s']*1000:.1f}ms",
                flush=True,
            )
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(dict(law=dict(T_ep=LAW.T_ep, L=LAW.L, B=LAW.B), rows=results), f, indent=2)
        print(f"raw JSON -> {sys.argv[1]}", flush=True)


if __name__ == "__main__":
    main()
