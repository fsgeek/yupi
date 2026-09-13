"""Corpus-track counterparts of the ceilings at a WindowLaw (Part II v0.2.9
PROPOSAL, 2026-09-13; EXPLORATORY until v0.2.9 is enacted — every number
here says so).

(run: python scripts/c1_corpus_track.py T_ep L B [out.json];
 YUPI_PROGRAMS (default c1), YUPI_EPS, YUPI_RUNGS default r0..r4;
 YUPI_GATE=external (default: the sharded gate raws in docs/ for (law,
 rung, ε), refused if absent, as in c1_query_ceilings.py) | inline (every
 window through the exact filter; small laws))

Method: one window-process pass per ε (the gated aggregate), then per rung
a RE-KEYING by the equality pattern Π (yupi.naming): every (RESET, window)
class maps to (RESET, Π(window)) with the binding β kept in the value, so
the pattern aggregate is {pattern class: {(state, β): law mass}} — a sum of
the gated windows' unnormalized exact masses (v0.2.9 Clause 3). Reported
per rung, law-mass means in bits:
  canonical  H(S | w)            — the same aggregate before re-keying (for comparison)
  corpus     H(S | Πw)           — structural state given the pattern window
             H(q | Πw)           — the state in the window's names (yupi.naming.quotient; cursor excluded at ε = 1)
             H(q\pc | Πw)        — the same with program counters dropped (pc is meaningful only given the program = the binding)
             H(β | Πw)           — the binding (who is structurally who)
             H(S, β | Πw)
  Q2[k]      status of the k-th named thread (k = 0..n−1); on a class that names
             fewer than k+1 threads the query is about an unnamed token and
             its answer is the UNSEEN mixture (uniform over unnamed threads)
  Q2[unseen] the UNSEEN mixture on every class ("NONE" when every thread is named)
  canonical Q2[T_i] means from the same aggregate, for comparison.
Thread naming only (locks, devices, request ids structural) — the lemma's
executable scope. Not priced by E3 (runs after the pass); RSS reported.
"""
import json
import os
import resource
import sys
import time
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.eps_grid import eps_grid
from yupi.naming import pattern, quotient
from yupi.programs import programs_for
from yupi.queries import entropy_bits, q2_status, state_entropy_bits
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregates

sys.path.insert(0, os.path.dirname(__file__))
from c1_query_ceilings import _external_gate_ok  # noqa: E402
from yupi.window_filter import filter_window_with_evidence  # noqa: E402

RUNGS = ("r0", "r1", "r2", "r3", "r4")


def _H(d):
    tot = sum(d.values(), Fraction(0))
    return state_entropy_bits({k: m / tot for k, m in d.items()})


def corpus_rows(law, eps, cfg, progs, rungs, docs_dir, programs_name, gate="external"):
    n = cfg.n_threads
    stats = {}
    t0 = time.time()
    aggs = window_law_aggregates(cfg, progs, law, tuple(rungs), stats)
    wall_pass = time.time() - t0
    rows = []
    qcache = {}
    for rung in rungs:
        t1 = time.time()
        agg = aggs[rung]
        if gate == "external":
            files = _external_gate_ok(docs_dir, law, rung, eps, programs_name)
            if files is None:
                raise RuntimeError(f"({law.T_ep},{law.L},{law.B}) {rung} eps={eps} is not gated externally; refused")
            gate_label = "external:" + ",".join(files)
        elif gate == "inline":                    # every window through the exact filter (small laws)
            for (reset, window), joint in agg.items():
                mass = sum(joint.values(), Fraction(0))
                post, evidence = filter_window_with_evidence(cfg, progs, law, list(window), rung, reset)
                assert evidence == mass and post.state_marginal() == {s: m / mass for s, m in joint.items()}, (rung, window)
            gate_label = "inline-marginal"
        else:
            raise ValueError(gate)
        # canonical comparison figures from the same aggregate
        can_HS, can_Q2 = 0.0, [0.0] * n
        for joint in agg.values():
            mass = sum(joint.values(), Fraction(0))
            belief = {s: m / mass for s, m in joint.items()}
            can_HS += float(mass) * state_entropy_bits(belief)
            for i in range(n):
                d = {}
                for s, p in belief.items():
                    a = q2_status(s, i); d[a] = d.get(a, Fraction(0)) + p
                can_Q2[i] += float(mass) * entropy_bits(d)
        # re-keying by Π
        patt = {}
        for (reset, win), joint in agg.items():
            pw, order = pattern(win)
            d = patt.setdefault((reset, pw), {})
            for s, m in joint.items():
                d[(s, order)] = d.get((s, order), Fraction(0)) + m
        total = sum((sum(v.values(), Fraction(0)) for v in patt.values()), Fraction(0))
        assert total == 1, total
        H_S = H_q = H_q2 = H_b = H_joint = 0.0
        Q2 = [0.0] * n
        Q2_unseen = 0.0
        named_mass = [Fraction(0)] * (n + 1)          # law mass by number of named threads
        for joint in patt.values():
            mass = sum(joint.values(), Fraction(0))
            f = float(mass)
            s_m, b_m, q_m, q_m2 = {}, {}, {}, {}
            q2 = [dict() for _ in range(n)]
            un = {}
            for (s, order), m in joint.items():
                s_m[s] = s_m.get(s, Fraction(0)) + m
                b_m[order] = b_m.get(order, Fraction(0)) + m
                key = (s, order)
                qq = qcache.get(key)
                if qq is None:
                    qq = (quotient(s, order, cfg), quotient(s, order, cfg, with_pc=False)); qcache[key] = qq
                q_m[qq[0]] = q_m.get(qq[0], Fraction(0)) + m
                q_m2[qq[1]] = q_m2.get(qq[1], Fraction(0)) + m
                unnamed = [t for t in range(n) if t not in order]
                for k in range(n):
                    if k < len(order):
                        a = q2_status(s, order[k]); q2[k][a] = q2[k].get(a, Fraction(0)) + m
                    else:
                        for t in unnamed:
                            a = q2_status(s, t); q2[k][a] = q2[k].get(a, Fraction(0)) + m / len(unnamed)
                if unnamed:
                    for t in unnamed:
                        a = q2_status(s, t); un[a] = un.get(a, Fraction(0)) + m / len(unnamed)
                else:
                    un["NONE"] = un.get("NONE", Fraction(0)) + m
            k_named = len(next(iter(joint))[1])
            named_mass[k_named] += mass
            H_S += f * _H(s_m); H_q += f * _H(q_m); H_q2 += f * _H(q_m2); H_b += f * _H(b_m); H_joint += f * _H(joint)
            for k in range(n):
                Q2[k] += f * _H(q2[k])
            Q2_unseen += f * _H(un)
        rows.append(dict(
            eps=str(eps), rung=rung, status="EXPLORATORY (v0.2.9 not enacted)", gate=gate_label,
            n_windows_canonical=len(agg), n_pattern_classes=len(patt),
            canonical=dict(mean_state_entropy_bits=can_HS, Q2={f"T{i}": can_Q2[i] for i in range(n)}),
            corpus=dict(H_S_given_pattern=H_S, H_quotient_given_pattern=H_q, H_quotient_no_pc_given_pattern=H_q2, H_binding_given_pattern=H_b,
                        H_state_binding_given_pattern=H_joint,
                        Q2={f"named{k}": Q2[k] for k in range(n)}, Q2_unseen=Q2_unseen,
                        law_mass_by_named_count={str(k): float(named_mass[k]) for k in range(n + 1)}),
            wall_rekey_s=time.time() - t1))
        print(f"eps={eps} {rung}: canonical n={len(agg)} H(S|w)={can_HS:.4f}  corpus classes={len(patt)} H(S|Πw)={H_S:.4f} H(q|Πw)={H_q:.4f} H(q\\pc|Πw)={H_q2:.4f} H(β|Πw)={H_b:.4f}  "
              f"Q2 canonical T0={can_Q2[0]:.4f} corpus named0={Q2[0]:.4f} unseen={Q2_unseen:.4f}  ({time.time()-t1:.0f}s)", flush=True)
    return rows, wall_pass


def main():
    T_ep, L, B = (int(a) for a in sys.argv[1:4])
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    rungs = tuple(os.environ.get("YUPI_RUNGS", ",".join(RUNGS)).split(","))
    programs_name = os.environ.get("YUPI_PROGRAMS", "c1")
    gate = os.environ.get("YUPI_GATE", "external")
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), programs=programs_name, aggregation="window", track="corpus (thread naming only)",
               status="EXPLORATORY (Part II v0.2.9 proposal, not enacted)", rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        rows, wall_pass = corpus_rows(law, eps, cfg, programs_for(programs_name), rungs, "docs", programs_name, gate)
        out["rows"].extend(rows)
        out.setdefault("wall_pass_s", {})[str(eps)] = wall_pass
    out["peak_rss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], "w"), indent=2)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
