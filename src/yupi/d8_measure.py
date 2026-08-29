"""D8 order-mode attribution measurement, per cell (prereg
docs/d8-attribution-prereg-v0.1.md, commit a39f555; §5 gates, §7 reporting).

`measure_cell` builds both tables (enumerator side), runs every gate the
prereg lists as executable — uncapped — and only then computes the §7
quantities. A gate failure raises GateFailure naming the gate; the runner
records it as the cell's result. Gate 6 (ordered mode = per-record filter)
holds by construction in this codebase — the ordered window observation
model IS `filter_window` — and is witnessed by
`tests/test_shuffled_channel.py::test_ordered_bucket_equals_per_record_filter`;
it is recorded, not re-run, per cell.
"""
import time
from fractions import Fraction
from math import fsum
from typing import Dict, List

from yupi.attribution import (_n_obs, COORDS, SEMANTIC_ORDER, CoordCache, chain_terms,
                              check_bijection, entropy_bits, envelope,
                              joint_entropy, latent_table, losses, mass,
                              normalized, per_observation, per_offset_anchored,
                              shapley, subset_entropy, value_fn, visible_table)
from yupi.d8_benchmark import world_of
from yupi.shuffled_window import shuffled_window_filter_with_evidence
from yupi.window import WindowLaw
from yupi.window_filter import filter_window_with_evidence

DELTA = 0.01                      # Part II v0.2.5 collapse threshold
TOL = 1e-9
# Gate 6 (prereg §5.6) is NOT executed per cell: the ordered path here is
# `filter_window`, a per-record recursive step by construction, and the suite
# witness below asserts the identity at one law. The artifact records the
# witness, not an execution — a preregistration deviation named by the
# truthsayer review of 2026-08-29 (Finding 3) and recorded in the C1 note.
GATE6_WITNESS = ("by construction, not executed per cell: "
                 "tests/test_shuffled_channel.py::test_ordered_bucket_equals_per_record_filter")


class GateFailure(AssertionError):
    pass


def _gate(cond, name, detail=""):
    if not cond:
        raise GateFailure(f"{name}: {detail}")


def _quantiles(rows, qs=(50, 90, 99)):
    """Law-mass quantiles of g over observations."""
    srt = sorted(((g, float(m)) for _, m, g, _ in rows), key=lambda x: x[0])
    total = fsum(m for _, m in srt)
    out = {}
    for q in qs:
        acc = 0.0
        val = srt[-1][0] if srt else 0.0
        for g, m in srt:
            acc += m
            if acc >= q / 100 * total:
                val = g
                break
        out[str(q)] = val
    return out


def per_offset_unanchored(latent, visible, law) -> Dict[int, float]:
    """Unanchored gain restricted to windows generated at each endpoint T
    (prereg §7): the observer's posterior on the merged observation (marginal
    over U), averaged over the mass generated at T. An entry (u, s) in a key
    of observation length n was generated at T = u + n; the pre-2026-08-29
    code selected by u alone and pooled every endpoint T ≤ L (truthsayer
    review 2026-08-29, Finding 1)."""
    out = {}
    for T in law.endpoints():
        pu = Fraction(0)
        hs, ho = [], []
        for v, joint in visible.items():
            n = _n_obs(v)
            mu = sum((m for (uu, _), m in joint.items() if uu + n == T), Fraction(0))
            if mu:
                pu += mu
                hs.append(float(mu) * entropy_bits(joint.values()))
        for w, joint in latent.items():
            n = _n_obs(w)
            mu = sum((m for (uu, _), m in joint.items() if uu + n == T), Fraction(0))
            if mu:
                ho.append(float(mu) * entropy_bits(joint.values()))
        out[T] = (fsum(hs) - fsum(ho)) / float(pu) if pu else 0.0
    return out


def measure_cell(cell: dict, path_cache: dict = None) -> dict:
    cfg, progs = world_of(cell)
    law, rung = cell["law"], cell["rung"]
    t0 = time.perf_counter()
    lat = latent_table(cfg, progs, law, rung, path_cache)
    vis, src = visible_table(lat, law.B)
    t_tables = time.perf_counter() - t0

    # --- gates (prereg §5), uncapped
    _gate(sum(mass(j) for j in lat.values()) == 1, "mass_lat")
    _gate(sum(mass(j) for j in vis.values()) == 1, "mass_vis")
    t1 = time.perf_counter()
    st_s, st_o = {}, {}
    for (reset, buckets), joint in vis.items():
        post, ev = shuffled_window_filter_with_evidence(
            cfg, progs, law, [list(b) for b in buckets], rung, reset, st_s)
        fj = {(u, s): w * m for u, (w, b) in post.components.items() for s, m in b.items()}
        _gate(fj == normalized(joint) and ev == mass(joint), "two_path_shuffled", repr(buckets)[:200])
    for (reset, win), joint in lat.items():
        post, ev = filter_window_with_evidence(cfg, progs, law, list(win), rung, reset, st_o)
        fj = {(u, s): w * m for u, (w, b) in post.components.items() for s, m in b.items()}
        _gate(fj == normalized(joint) and ev == mass(joint), "two_path_ordered", repr(win)[:200])
    t_gate2 = time.perf_counter() - t1
    n_bij = check_bijection(lat, vis)                       # gate F (raises)
    cache = CoordCache()
    for t in (lat, vis):
        _gate(subset_entropy(t, COORDS, cache) == joint_entropy(t), "full_coordinate_identity")

    # --- functionals (prereg §3)
    t2 = time.perf_counter()
    F = losses(lat, vis)
    d_un, off = F[frozenset(COORDS)], F[frozenset({"U"})]
    d_an = d_un - off
    _gate(d_un >= -TOL and off >= -TOL and d_an >= -TOL, "nonnegativity", f"{d_un} {off} {d_an}")
    games = {"un": (frozenset(), COORDS, d_un), "an": (frozenset({"U"}), COORDS[1:], d_an)}
    chain, shap, env = {}, {}, {}
    for tag, (cond, players, total) in games.items():
        v = value_fn(F, cond)
        order = tuple(p for p in SEMANTIC_ORDER if p in players)
        ch, sh, en = chain_terms(v, order), shapley(v, players), envelope(v, players)
        _gate(all(t >= -TOL for t in ch.values()), f"chain_nonneg_{tag}", repr(ch))
        _gate(abs(fsum(ch.values()) - total) < TOL, f"chain_sum_{tag}")
        _gate(abs(fsum(sh.values()) - total) < TOL, f"shapley_sum_{tag}")
        _gate(all(en[k][0] - TOL <= ch[k] <= en[k][1] + TOL for k in players), f"envelope_{tag}")
        chain[tag], shap[tag], env[tag] = ch, sh, {k: list(b) for k, b in en.items()}
    if law.B == 1:                                          # Z3
        _gate(all(f == 0.0 for f in F.values()), "Z3_B1_null")
    if cell["eps"] == "1":                                  # Z1
        _gate(all(F[A | {"kappa"}] == F[A] for A in F if "kappa" not in A), "Z1_kappa")
    if cell["world"] == "c0b":                              # Z2
        _gate(all(F[A | {"WQ"}] == F[A] for A in F if "WQ" not in A), "Z2_WQ")
    rows = per_observation(lat, vis, src)
    _gate(abs(fsum(float(m) * g for _, m, g, _ in rows) - d_un) < TOL, "per_observation_integral")
    _gate(all((g > TOL) <= inf for _, _, g, inf in rows), "informative_consistency")
    prevalence = sum((m for _, m, _, inf in rows if inf), Fraction(0))
    pe_an = per_offset_anchored(lat, vis, src, law)
    pe_un = per_offset_unanchored(lat, vis, law)
    t_func = time.perf_counter() - t2

    return dict(
        world=cell["world"], discipline=cell["discipline"], eps=cell["eps"],
        T_ep=law.T_ep, L=law.L, B=law.B, rung=rung,
        gates=dict(two_path_n_vis=len(vis), two_path_n_lat=len(lat), bijection_n=n_bij,
                   Z3=(law.B == 1), Z1=(cell["eps"] == "1"), Z2=(cell["world"] == "c0b"),
                   gate6=GATE6_WITNESS, all_passed=True),
        delta_un=d_un, delta_an=d_an, offset_term=off,
        chain_semantic_un=chain["un"], chain_semantic_an=chain["an"],
        shapley_un=shap["un"], shapley_an=shap["an"],
        envelope_un=env["un"], envelope_an=env["an"],
        prevalence=float(prevalence), prevalence_exact=str(prevalence),
        n_vis=len(vis), n_vis_informative=sum(1 for *_, inf in rows if inf), n_lat=len(lat),
        max_g=max((g for _, _, g, _ in rows), default=0.0), g_quantiles=_quantiles(rows),
        per_endpoint_an={str(T): g for T, g in pe_an.items()},
        per_endpoint_un={str(T): g for T, g in pe_un.items()},
        collapsed_un=(d_un < DELTA), collapsed_an=(d_an < DELTA),
        cost=dict(t_tables_s=t_tables, t_gate2_s=t_gate2, t_functionals_s=t_func,
                  max_support_shuf=st_s.get("max_support", 0), max_frontier_shuf=st_s.get("max_frontier", 0),
                  max_support_ord=st_o.get("max_support", 0)),
    )
