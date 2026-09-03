"""Witness 11 — predictive rung discrimination (Part II §9 item 11).

(run: python scripts/w11_predictive_rung_search.py T_ep L B [out.json])

Statute: "an adjacent interface pair distinguished by a P-horizon test
while all Q1–Q5 posteriors are unchanged — the D2 disjunctive clause (b)
exercised." Read per window class, not per law-mass mean: for an
adjacent pair (r, r′), an r-window w whose r′-refinement SPLITS it into
sub-windows w_1..w_k is a candidate iff every statutory fact query's
pushforward is exactly unchanged on every piece — Q1, Q2, Q3 (ids), Q5
(per pair), plus statutory Q4 (the wake forecast, §5) — exact rationals;
it is a witness iff some τ ∈ 𝒯 = {next-2 EVENT_KINDs, time-to-next-wake
≤ W, LINEAGE of the next IO_COMPLETE ≤ W} (frozen v0.2.4: m = 2, W = 4
primary / 8 secondary) has TV(τ(b_j), τ(b_w)) > 0 for some piece j.

Two readings are reported, because the statute names no separation
threshold for this witness and Q4 carries the same horizon parameter as
two of the three τ:

  * PRIMARY (W = 4): unchanged = {Q1, Q2, Q3, Q5, Q4@4}; τ ∈ {kinds2,
    ttw4, lin4}. Reported at TV > 0 (the exact, δ = 0 corner) and at
    TV ≥ Δ_τ = 0.01 (the v0.2.5 divergence threshold, borrowed — not
    frozen for this witness).
  * SECONDARY, STRICT (W = 8): unchanged additionally requires Q4@8;
    τ ∈ {ttw8, lin8}. Same two thresholds.
  * SECONDARY, LOOSE: unchanged = the primary set only, τ at W = 8. This
    is the asymmetric reading (fact forecast held at W = 4 while the
    predictive test runs to W = 8); reported so the reader can see it,
    not claimed.

Why the region is L ≤ 10 (2026-09-03): the map-v4 candidate region
(14,12,2) was chosen because the law-mass MEAN gaps on Q1–Q5 are exactly
zero there. But at L = 12 (and 14) the r1 partition of windows already
coincides with the r4 partition (`n_windows` identical across rungs in
`c1-query-ceilings-14-{12,14}-2-corrected-2026-08-20.json`; r4 refines r1,
so equal counts ⇒ equal partitions ⇒ identical per-window beliefs). Every
τ is a function of the belief, so no P-horizon test can separate rungs
there: the region is empty a priori. This script executes that claim
(n_split = 0 at L = 12, 14) rather than arguing it.

Mechanism the search is looking for: state coordinates outside Q1–Q5's
reach — program counters, the running set, the cursor κ, wait-queue
ORDER — pinned by the added field yet invisible to every fact query, but
visible to the kernel's future. Every candidate window is dumped in full
(pieces, support, the state fields in which the support differs, whether
the pieces' beliefs are identical to the parent's — an "inert" split —
and every TV as an exact rational string).

Consistency gate: the per-rung distinct-window counts are asserted equal
to `n_windows` in the committed ceilings artifact for the same law when
that file is present.

Exact rationals throughout; floats only in the JSON presentation.
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import q4_forward, q4_mixture
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, time_to_wake
from yupi.programs import c1_programs
from yupi.queries import all_queries, pushforward
from yupi.window import WindowLaw, endpoint_prior

RUNGS = ("r1", "r2", "r3", "r4")
PAIRS = tuple(zip(RUNGS[:-1], RUNGS[1:]))
M = 2
W_PRIMARY, W_SECONDARY = 4, 8
DELTA_TAU = Fraction(1, 100)
FACT_PREFIXES = ("Q1", "Q2", "Q3", "Q5")
STATE_FIELDS = ("pc", "status", "running", "lock_owner", "lock_wq", "dev_q", "rr_cursor")
TAUS_PRIMARY = ("kinds2", "ttw4", "lin4")
TAUS_SECONDARY = ("ttw8", "lin8")
TAUS = TAUS_PRIMARY + TAUS_SECONDARY
MAX_DUMP = 64


def _tv(a, b):
    keys = set(a) | set(b)
    return sum(abs(a.get(k, Fraction(0)) - b.get(k, Fraction(0))) for k in keys) / 2


def _rec(r):
    return [str(r.kind), str(r.actor), str(r.obj), str(r.related), str(r.lineage)]


def _dist(d):
    return {str(k): str(v) for k, v in sorted(d.items(), key=lambda kv: str(kv[0]))}


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    ceilings_path = f"docs/c1-query-ceilings-{T_ep}-{L}-{B}-corrected-2026-08-20.json"
    ceilings = json.load(open(ceilings_path)) if os.path.exists(ceilings_path) else None
    out: dict = dict(law=dict(T_ep=T_ep, L=L, B=B), m=M, W=[W_PRIMARY, W_SECONDARY],
                     delta_tau=str(DELTA_TAU),
                     ceilings_gate=ceilings_path if ceilings else None, rows=[])
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        progs = c1_programs()
        facts = [(n, f) for n, f in all_queries(cfg) if n.startswith(FACT_PREFIXES)]
        w_T = endpoint_prior(law)
        path_cache = {T: paths(cfg, progs, T) for T in law.endpoints()}

        agg = {r: {} for r in RUNGS}
        parent = {(a, b): {} for a, b in PAIRS}
        for T in law.endpoints():
            u = law.offset(T)
            for recs, prob, final in path_cache[T]:
                keys = {r: (u == 0, tuple(project(x, r) for x in recs[u:])) for r in RUNGS}
                for r in RUNGS:
                    d = agg[r].setdefault(keys[r], {})
                    d[final] = d.get(final, Fraction(0)) + w_T * prob
                for a, b in PAIRS:
                    parent[(a, b)][keys[b]] = keys[a]
        for r in RUNGS:
            assert sum((sum(j.values(), Fraction(0)) for j in agg[r].values()), Fraction(0)) == 1
            if ceilings:
                n_ref = next(row["n_windows"] for row in ceilings["rows"]
                             if row["eps"] == str(eps) and row["rung"] == r)
                assert len(agg[r]) == n_ref, (eps, r, len(agg[r]), n_ref)

        memo_q4, memo_k, memo_w, memo_l = {}, {}, {}, {}
        fn_state = {}

        def per_state(s):
            if s not in fn_state:
                fn_state[s] = {
                    "Q4@4": q4_forward(s, cfg, progs, W_PRIMARY, memo_q4),
                    "Q4@8": q4_forward(s, cfg, progs, W_SECONDARY, memo_q4),
                    "kinds2": next_kinds(s, cfg, progs, M, memo_k),
                    "ttw4": time_to_wake(s, cfg, progs, W_PRIMARY, memo_w),
                    "lin4": next_complete_lineage(s, cfg, progs, W_PRIMARY, memo_l),
                    "ttw8": time_to_wake(s, cfg, progs, W_SECONDARY, memo_w),
                    "lin8": next_complete_lineage(s, cfg, progs, W_SECONDARY, memo_l),
                }
            return fn_state[s]

        def belief_of(joint):
            mass = sum(joint.values(), Fraction(0))
            return mass, {s: m / mass for s, m in joint.items()}

        def mix(belief, name):
            return q4_mixture(belief, {s: per_state(s)[name] for s in belief})

        def fact_signature(belief):
            return {n: frozenset(pushforward(belief, f).items()) for n, f in facts}

        for a, b in PAIRS:
            children = {}
            for kb, ka in parent[(a, b)].items():
                children.setdefault(ka, []).append(kb)
            n_split, mass_split = 0, Fraction(0)
            n_cand, mass_cand = 0, Fraction(0)          # primary fact set unchanged
            n_cand_strict, mass_cand_strict = 0, Fraction(0)   # ... and Q4@8 unchanged
            n_inert = 0
            counts = {k: 0 for k in ("primary_exact", "primary_delta",
                                     "secondary_strict_exact", "secondary_strict_delta",
                                     "secondary_loose_exact", "secondary_loose_delta")}
            masses = {k: Fraction(0) for k in counts}
            max_tv = {t: Fraction(0) for t in TAUS + ("Q4@8",)}
            dump = []
            for ka, kbs in children.items():
                if len(kbs) < 2:
                    continue
                n_split += 1
                mass_w, bel_w = belief_of(agg[a][ka])
                mass_split += mass_w
                sig_w = fact_signature(bel_w)
                q4w_4, q4w_8 = mix(bel_w, "Q4@4"), mix(bel_w, "Q4@8")
                pieces = []
                unchanged = True
                for kb in kbs:
                    mass_j, bel_j = belief_of(agg[b][kb])
                    if fact_signature(bel_j) != sig_w or mix(bel_j, "Q4@4") != q4w_4:
                        unchanged = False
                        break
                    pieces.append((kb, mass_j, bel_j))
                if not unchanged:
                    continue
                n_cand += 1
                mass_cand += mass_w
                strict = all(mix(bel_j, "Q4@8") == q4w_8 for _, _, bel_j in pieces)
                if strict:
                    n_cand_strict += 1
                    mass_cand_strict += mass_w
                inert = all(bel_j == bel_w for _, _, bel_j in pieces)
                if inert:
                    n_inert += 1
                tau_w = {t: mix(bel_w, t) for t in TAUS}
                tv = {t: Fraction(0) for t in TAUS + ("Q4@8",)}
                piece_rows = []
                for kb, mass_j, bel_j in pieces:
                    tv_j = {t: _tv(mix(bel_j, t), tau_w[t]) for t in TAUS}
                    tv_j["Q4@8"] = _tv(mix(bel_j, "Q4@8"), q4w_8)
                    for t in tv:
                        tv[t] = max(tv[t], tv_j[t])
                    piece_rows.append(dict(window_at_child=[_rec(x) for x in kb[1]],
                                           mass=str(mass_j), mass_float=float(mass_j),
                                           support=len(bel_j),
                                           belief_equals_parent=(bel_j == bel_w),
                                           tv={t: str(v) for t, v in tv_j.items()},
                                           tv_float={t: float(v) for t, v in tv_j.items()}))
                for t in tv:
                    max_tv[t] = max(max_tv[t], tv[t])
                verdict = dict(
                    primary_exact=any(tv[t] > 0 for t in TAUS_PRIMARY),
                    primary_delta=any(tv[t] >= DELTA_TAU for t in TAUS_PRIMARY),
                    secondary_strict_exact=strict and any(tv[t] > 0 for t in TAUS_SECONDARY),
                    secondary_strict_delta=strict and any(tv[t] >= DELTA_TAU for t in TAUS_SECONDARY),
                    secondary_loose_exact=any(tv[t] > 0 for t in TAUS_SECONDARY),
                    secondary_loose_delta=any(tv[t] >= DELTA_TAU for t in TAUS_SECONDARY),
                )
                for k, v in verdict.items():
                    if v:
                        counts[k] += 1
                        masses[k] += mass_w
                states = list(bel_w)
                differing = sorted({f for i in range(len(states)) for j in range(i + 1, len(states))
                                    for f in STATE_FIELDS
                                    if getattr(states[i], f) != getattr(states[j], f)})
                if len(dump) < MAX_DUMP:
                    reset, win = ka
                    dump.append(dict(
                        reset_observed=reset,
                        window_at_parent=[_rec(x) for x in win],
                        parent_mass=str(mass_w), parent_mass_float=float(mass_w),
                        parent_support=len(bel_w),
                        support_differs_in=differing,
                        inert=inert, q4_secondary_unchanged=strict,
                        verdict=verdict,
                        max_tv={t: str(v) for t, v in tv.items()},
                        pieces=piece_rows,
                        tau_parent={t: _dist(tau_w[t]) for t in TAUS if tv[t] > 0},
                        tau_pieces=[{t: _dist(mix(bel_j, t)) for t in TAUS if tv[t] > 0}
                                    for _, _, bel_j in pieces],
                    ))
            row = dict(
                eps=str(eps), pair=f"{a}->{b}",
                n_windows_parent=len(agg[a]), n_windows_child=len(agg[b]),
                n_split=n_split, mass_split=float(mass_split),
                n_candidates=n_cand, mass_candidates=float(mass_cand),
                n_candidates_strict=n_cand_strict, mass_candidates_strict=float(mass_cand_strict),
                n_inert=n_inert,
                counts=counts, masses={k: float(v) for k, v in masses.items()},
                max_tv={t: float(v) for t, v in max_tv.items()},
                witness_primary_exact=counts["primary_exact"] > 0,
                witness_primary_delta=counts["primary_delta"] > 0,
                witness_secondary_strict_exact=counts["secondary_strict_exact"] > 0,
                witness_secondary_strict_delta=counts["secondary_strict_delta"] > 0,
                candidates=dump,
            )
            out["rows"].append(row)
            print(f"eps={str(eps):>3} {a}->{b}  windows {len(agg[a])}->{len(agg[b])}  "
                  f"split={n_split} (mass {float(mass_split):.4f})  cand={n_cand} "
                  f"(strict {n_cand_strict}, inert {n_inert}, mass {float(mass_cand):.2e})  "
                  f"counts={counts}  maxTV={ {t: round(float(v), 5) for t, v in max_tv.items()} }",
                  flush=True)
    if len(sys.argv) > 4:
        with open(sys.argv[4], "w") as f:
            json.dump(out, f, indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
