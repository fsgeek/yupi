"""D10 truncated-window lineage search (witnesses 3 and 6).

Contract: docs/d10-lineage-search-prereg-v0.1.md (stamped 080f937 before any
posterior). Estimand per coarse r3 history h: g_d(h) = I(Z; Λ | H₃ = h);
existence tested EXACTLY (some r4 child's conditional Z-distribution differs
from the parent's, Fraction comparison — no float in any verdict); magnitudes
in float bits at print time only.

Run: python scripts/d10_lineage_search.py [out.json]
T_ep* is computed by the prereg §4 mechanical rule and recorded.
"""
import json
import sys
from fractions import Fraction
from math import log2

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.programs import c0b_programs
from yupi.queries import all_queries, q3_inflight, q3_inflight_ids
from yupi.state import initial_state
from yupi.window import WindowLaw
from yupi.window_enumerator import posterior_by_window_paths
from yupi.window_filter import filter_window

B = 2
DISCIPLINES = ("fifo", "stochastic")
TARGETS = {"Q3": lambda s: q3_inflight_ids(s, 0), "Q3thr": lambda s: q3_inflight(s, 0)}


def entropy(dist):
    Z = sum(dist.values(), Fraction(0))
    return -sum(float(m / Z) * log2(float(m / Z)) for m in dist.values() if m)


def reachable_states(cfg, progs, H):
    seen, frontier = {initial_state(cfg)}, [initial_state(cfg)]
    for _ in range(H):
        nxt = []
        for s in frontier:
            for t, _ in enabled(s, cfg, progs):
                if t.next_state not in seen:
                    seen.add(t.next_state); nxt.append(t.next_state)
        frontier = nxt
    return seen


def gate4_matched_hazard(cfgs, progs, H):
    """P(completion this tick | n>0) == completion_p at every reachable state,
    both disciplines (prereg gate 4)."""
    for cfg in cfgs:
        for s in reachable_states(cfg, progs, H):
            if not s.dev_q[0]:
                continue
            tot = sum(p for t, p in enabled(s, cfg, progs)
                      if t.kind in ("IO_COMPLETE", "COMPLETION"))
            assert tot == cfg.completion_p, (cfg.discipline, s, tot)


def tep_star(cfg, progs, max_h=20):
    """Prereg §4: smallest even T_ep with (i) two in-flight reachable,
    (ii) non-head completion reachable (checked on the stochastic world),
    (iii) some truncated window opening strictly after an IO_ISSUE it does
    not contain (u > 0 with an IO_ISSUE at tick <= u, for some L)."""
    for T in range(2, max_h + 1, 2):
        two = nonhead = post_issue = False
        for recs, _, _ in paths(cfg, progs, T):
            q = []
            for i, r in enumerate(recs):
                if r.kind == "IO_ISSUE":
                    q.append(r.lineage)
                    if len(q) == 2:
                        two = True
                elif r.kind == "IO_COMPLETE":
                    if q and r.lineage != q[0]:
                        nonhead = True
                    q.remove(r.lineage)
            issues = [i + 1 for i, r in enumerate(recs) if r.kind == "IO_ISSUE"]
            for L in range(B, T, B):
                for Tend in range(B, T + 1, B):
                    u = max(0, Tend - L)
                    if u > 0 and any(t <= u for t in issues):
                        post_issue = True
        if two and nonhead and post_issue:
            return T
    raise RuntimeError("no T_ep satisfies the rule within max_h")


def classes_for(cfg, progs, law):
    """Path aggregation: r3 coarse classes -> r4 children -> exact Z dists."""
    out = {}   # r3key -> {r4key: {"mass": F, targets: {name: {val: F}}}}
    cache = {T: paths(cfg, progs, T) for T in law.endpoints()}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, final in cache[T]:
            w3 = tuple(project(r, "r3") for r in recs[u:T])
            w4 = tuple(project(r, "r4") for r in recs[u:T])
            assert tuple(project(r, "r3") for r in w4) == w3, "gate 3"
            k3, k4 = (u == 0, w3), (u == 0, w4)
            node = out.setdefault(k3, {}).setdefault(
                k4, {"mass": Fraction(0), "targets": {n: {} for n in TARGETS},
                     "by_u": {}})
            node["mass"] += prob
            bu = node["by_u"].setdefault(u, {"mass": Fraction(0),
                                             "targets": {n: {} for n in TARGETS}})
            bu["mass"] += prob
            for name, q in TARGETS.items():
                v = q(final)
                node["targets"][name][v] = node["targets"][name].get(v, Fraction(0)) + prob
                bu["targets"][name][v] = bu["targets"][name].get(v, Fraction(0)) + prob
    return out


def analyze(classes, total_mass):
    """Per-target: exact existence + float magnitudes + prereg §3 prevalence."""
    res = {}
    for name in TARGETS:
        rows = []
        for k3, children in classes.items():
            parent = {}
            m3 = sum(c["mass"] for c in children.values())
            for c in children.values():
                for v, m in c["targets"][name].items():
                    parent[v] = parent.get(v, Fraction(0)) + m
            # exact informativeness: any child conditional differs from parent
            informative = any(
                {v: m / c["mass"] for v, m in c["targets"][name].items()}
                != {v: m / m3 for v, m in parent.items()}
                for c in children.values())
            g = entropy(parent) - sum(
                float(c["mass"] / m3) * entropy(c["targets"][name])
                for c in children.values())
            assert g >= -1e-12                                     # gate 5
            assert informative or abs(g) < 1e-12
            rows.append(dict(mass=m3, informative=informative, g=max(g, 0.0),
                             n_children=len(children)))
        inf = [r for r in rows if r["informative"]]
        pm = sum((r["mass"] for r in inf), Fraction(0))
        # mass-weighted quantiles of g over ALL coarse histories (prereg §3)
        srt = sorted(rows, key=lambda r: r["g"]); acc = Fraction(0); qs = {}
        for r in srt:
            acc += r["mass"]
            for q in (50, 90, 99):
                if q not in qs and acc >= total_mass * Fraction(q, 100):
                    qs[q] = r["g"]
        n_children = sum(r["n_children"] for r in rows)
        n_inf_children = sum(r["n_children"] for r in inf)
        res[name] = dict(
            prevalence=float(pm / total_mass),
            n_informative_histories=len(inf),
            n_histories=len(rows),
            delta=sum(float(r["mass"] / total_mass) * r["g"] for r in rows),
            e_g_given_pos=(sum(float(r["mass"] / pm) * r["g"] for r in inf) if inf else 0.0),
            max_g=max((r["g"] for r in inf), default=0.0),
            g_quantiles={str(q): qs.get(q, 0.0) for q in (50, 90, 99)},
            r4_child_fraction_secondary=(n_inf_children / n_children if n_children else 0.0),
        )
    return res


def anchored_decomposition(classes, total_mass, name="Q3"):
    """Per prereg-correction round (Codex, 2026-08-24): chain-rule split of
    the unanchored gain. Per coarse history h: I(Z;Λ|H₃=h) [unanchored],
    I(Z;Λ|H₃=h,U) [anchored], I(U;Λ|H₃=h); law means of each; and
    per-generating-endpoint mass contributions."""
    anch = 0.0; iu = 0.0; by_u_mass = {}
    for k3, children in classes.items():
        m3 = sum(c["mass"] for c in children.values())
        w3 = float(m3 / total_mass)
        # I(U;Λ|H₃=h): H(U|h) - Σ_λ P(λ|h) H(U|h,λ)
        u_par = {}
        for c in children.values():
            for u, bu in c["by_u"].items():
                u_par[u] = u_par.get(u, Fraction(0)) + bu["mass"]
        h_u = entropy(u_par)
        h_u_given = sum(float(c["mass"] / m3) *
                        entropy({u: bu["mass"] for u, bu in c["by_u"].items()})
                        for c in children.values())
        iu += w3 * (h_u - h_u_given)
        # anchored: within each (h, u)
        for u in u_par:
            mu = u_par[u]
            par = {}
            kids = []
            for c in children.values():
                bu = c["by_u"].get(u)
                if bu is None:
                    continue
                kids.append(bu)
                for v, m in bu["targets"][name].items():
                    par[v] = par.get(v, Fraction(0)) + m
            ga = entropy(par) - sum(float(b["mass"] / mu) * entropy(b["targets"][name])
                                    for b in kids)
            anch += float(m3 / total_mass) * float(mu / m3) * max(ga, 0.0)
        for u, mu in u_par.items():
            by_u_mass[u] = by_u_mass.get(u, 0.0) + float(mu / total_mass)
    return dict(anchored_delta=anch, I_U_given_H3=iu,
                offset_mass={str(u): m for u, m in sorted(by_u_mass.items())})


def gate2_two_path(cfg, progs, law, classes, limit=None):
    n = 0
    for (reset, w3), children in classes.items():
        for rung, w in [("r3", w3)] + [("r4", w4) for (_, w4) in children]:
            assert filter_window(cfg, progs, law, list(w), rung, reset) == \
                posterior_by_window_paths(cfg, progs, law, list(w), rung, reset)
            n += 1
            if limit and n >= limit:
                return n
    return n


def main():
    progs = c0b_programs()
    cfg_s = WorldConfig.c0b(discipline="stochastic")
    cfg_f = WorldConfig.c0b(discipline="fifo")
    T0 = tep_star(cfg_s, progs)
    horizons = [T0, T0 + 2, T0 + 4]
    gate4_matched_hazard((cfg_f, cfg_s), progs, max(horizons))
    out = dict(prereg="d10-lineage-search-prereg-v0.1.md@080f937",
               B=B, tep_star=T0, horizons=horizons, laws=[])
    for T_ep in horizons:
        for L in range(B, T_ep + 1, B):
            law = WindowLaw(T_ep=T_ep, L=L, B=B)
            row = dict(T_ep=T_ep, L=L, disciplines={})
            for cfg in (cfg_f, cfg_s):
                global TARGETS
                TARGETS = {"Q3": lambda s: q3_inflight_ids(s, 0),
                           "Q3thr": lambda s: q3_inflight(s, 0)}
                TARGETS.update({n: q for n, q in all_queries(cfg)
                                if n not in ("Q3[D0]", "Q3thr[D0]")})
                cls = classes_for(cfg, progs, law)
                total = sum(c["mass"] for ch in cls.values() for c in ch.values())
                r = analyze(cls, total)
                r["anchored_Q3"] = anchored_decomposition(cls, total, "Q3")
                if L == T_ep:                                      # gate 1
                    for name in TARGETS:
                        assert r[name]["n_informative_histories"] == 0, (cfg.discipline, name)
                gates = gate2_two_path(cfg, progs, law, cls)
                r["two_path_windows_checked"] = gates
                row["disciplines"][cfg.discipline] = r
            row["delta_interaction_Q3"] = (
                row["disciplines"]["stochastic"]["Q3"]["delta"]
                - row["disciplines"]["fifo"]["Q3"]["delta"])
            out["laws"].append(row)
            d = row["disciplines"]
            print(f"T_ep={T_ep} L={L}: "
                  f"fifo Q3 prev={d['fifo']['Q3']['prevalence']:.4f} Δ={d['fifo']['Q3']['delta']:.5f} | "
                  f"stoch Q3 prev={d['stochastic']['Q3']['prevalence']:.4f} Δ={d['stochastic']['Q3']['delta']:.5f} | "
                  f"stoch Q3thr Δ={d['stochastic']['Q3thr']['delta']:.5f}", flush=True)
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
        print(f"wrote {sys.argv[1]}")


if __name__ == "__main__":
    main()
