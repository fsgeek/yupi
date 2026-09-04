"""r0 identity-residual check — owed by Part II proposal v0.2.7.1 (statement 2).

(run: python scripts/r0_identity_residual.py T_ep B L1,L2,... [out.json];
 programs from YUPI_PROGRAMS, ε grid from yupi.eps_grid)

Question: when the kind-only observer's support has more than one state, do
the states differ ONLY in which thread is in which condition (thread
attribution / identity), or also in the anonymous configuration itself?

The Codex review (2026-09-04, v0.2.7 finding 4) asked for a permutation-orbit
computation. C1's programs are not kernel symmetries (no two threads run the
same program; the round-robin cursor is index-ordered), so "closed under a
program-preserving thread permutation" is trivially true and says nothing.
The meaningful test anonymizes the state: each thread is replaced by its
signature — the multiset of EVENT_KINDs it has executed so far (its pc
projected through its program), its status kind and object, the locks it
holds — and every thread id inside a wait queue, device queue or the cursor
is replaced by that signature. Two states with the same anonymized form are
the same situation with the threads relabeled. A support whose states all
share one anonymized form has an identity-only residual.

Reports, per (ε, L): ambiguous law mass; the share of it whose r0 support
is identity-only; and, for the remainder, which anonymized features differ.
Exploratory; exact rationals throughout, floats only in the presentation.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.eps_grid import eps_grid
from yupi.programs import programs_for
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregates

KIND_OF = {"COMPUTE": "STEP", "ACQUIRE": "ACQUIRE", "RELEASE": "RELEASE", "IO": "IO_ISSUE"}


def _executed_kinds(programs, i, pc):
    return tuple(sorted(KIND_OF[ins[0]] for ins in programs[i][:pc]))


def thread_signature(state, programs, i):
    held = tuple(sorted(l for l, o in enumerate(state.lock_owner) if o == i))
    return (_executed_kinds(programs, i, state.pc[i]), state.status[i], held)


def anonymize(state, programs, cursor_live):
    """cursor_live: at ε = 1 the round-robin cursor is never written (kernel
    `_epsilon_policy`: "absent from the effective state"), so it must not
    enter the anonymized form — including it would re-identify thread 0."""
    sig = [thread_signature(state, programs, i) for i in range(len(state.pc))]
    form = dict(
        threads=tuple(sorted(sig)),
        lock_wq=tuple(tuple(sig[t] for t in wq) for wq in state.lock_wq),
        dev_q=tuple(tuple((sig[t], r) for t, r in q) for q in state.dev_q),
    )
    if cursor_live:
        form["cursor"] = sig[state.rr_cursor]
    return form


def main():
    T_ep, B = int(sys.argv[1]), int(sys.argv[2])
    Ls = [int(x) for x in sys.argv[3].split(",")]
    progs = programs_for()
    out = dict(T_ep=T_ep, B=B, programs=os.environ.get("YUPI_PROGRAMS", "c1"), rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        for L in Ls:
            agg = window_law_aggregates(cfg, progs, WindowLaw(T_ep=T_ep, L=L, B=B), ("r0",))["r0"]
            amb = Fraction(0)
            ident = Fraction(0)
            by_feature = defaultdict(Fraction)
            n_amb = n_ident = 0
            for joint in agg.values():
                if len(joint) < 2:
                    continue
                mass = sum(joint.values(), Fraction(0))
                amb += mass
                n_amb += 1
                forms = [anonymize(s, progs, cfg.epsilon != 1) for s in joint]
                differing = tuple(sorted(f for f in forms[0] if any(g[f] != forms[0][f] for g in forms)))
                if not differing:
                    ident += mass
                    n_ident += 1
                else:
                    by_feature[differing] += mass
            row = dict(eps=str(eps), L=L, ambiguous_mass=float(amb), n_ambiguous_windows=n_amb,
                       identity_only_mass=float(ident), identity_only_share=float(ident / amb) if amb else None,
                       n_identity_only_windows=n_ident,
                       non_identity_by_feature={"+".join(k): float(v / amb) for k, v in sorted(by_feature.items(), key=lambda kv: -kv[1])})
            out["rows"].append(row)
            print(f"eps={str(eps):>3} L={L:>2}: amb={float(amb):.4f} ({n_amb} windows) identity-only={row["identity_only_share"]} "
                  f"({n_ident}) rest={row['non_identity_by_feature']}", flush=True)
    if len(sys.argv) > 4:
        json.dump(out, open(sys.argv[4], "w"), indent=1)
        print(f"raw JSON -> {sys.argv[4]}", flush=True)


if __name__ == "__main__":
    main()
