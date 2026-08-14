"""Multi-waiter habitat census — where the r2/r3 and r3/r4 distinguishers live.

(run: python scripts/c1_multiwaiter_census.py [out.json])

Motivated by c1-support-measurement-v0.1.md v0.3 open question (and
instrument-status open threads 1-2): r3/r4 do not separate in mean state
support at WindowLaw(12,6,2), and the conjectured distinguishers —
RELEASE.related under multi-waiter wake (r2/r3) and lineage (r3/r4) —
plausibly need windows that STRADDLE the events: causal antecedent
(BLOCK / IO_ISSUE) before the window, consequence (RELEASE / IO_COMPLETE)
inside it. Before buying an exact support table at a larger law, this
census answers the cheap prior questions exactly:

  1. With what probability mass does C1 produce a multi-waiter RELEASE
     (>= 2 waiters on the lock at release time), at which time indices,
     and with which wait-queue orders? (Both orders reachable is a design
     claim of c1_programs — here it is measured, with mass.)
  2. Same for completions drawn from a >= 2-deep device queue (the
     completion-order ambiguity lineage resolves), with issue->completion
     spans.
  3. For candidate window laws: does any law window GEOMETRICALLY
     straddle an event — all queue-forming BLOCKs at record times <= U
     (pre-window) and the RELEASE at time t in (U, T]? Full-order-hidden
     straddling is the necessary precondition for the r2/r3 witness; it
     is not sufficient (other visible records may still leak the order —
     sufficiency is the exact posterior computation's question, step 2).

Method: exhaustive DFS over kernel.enabled (the world definition only, per
the two-path firewall — no posterior logic here), exact Fractions, record
times 1-indexed (record i of an episode has time i, a window law's window
covers times U+1..T). Control per the witness discipline: the identical
census on C0a must report exactly zero multi-waiter events of either kind
(2 threads cannot make a 2-deep lock queue; depth-1 device queue cannot
hold 2 requests). A per-tick mass check (transition mass sums to 1) runs
throughout.
"""

import json
import sys
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.programs import c0a_programs, c1_programs
from yupi.window import WindowLaw


def census(cfg, progs, horizon):
    """Exhaustive annotated unroll. Returns dict of exact aggregates."""
    mw_release = {}     # (t, lock, waiter order, block times) -> mass
    deep_completion = {}  # (t, req_id, issue time, queue depth at completion) -> mass
    mass_any_mw = Fraction(0)
    mass_any_deep = Fraction(0)
    n_paths = 0

    def rec(state, prob, t, block_t, issue_t, seen_mw, seen_deep):
        nonlocal mass_any_mw, mass_any_deep, n_paths
        if t == horizon:
            n_paths += 1
            if seen_mw:
                mass_any_mw += prob
            if seen_deep:
                mass_any_deep += prob
            return
        step = list(enabled(state, cfg, progs))
        assert sum(p for _, p in step) == 1  # per-tick mass check
        for tr, p in step:
            bt, it = block_t, issue_t
            smw, sdp = seen_mw, seen_deep
            time = t + 1  # this transition's record time (1-indexed)
            k = tr.kind
            if k == "BLOCK" and tr.obj and tr.obj[0] == "LOCK":
                bt = dict(block_t)
                bt[tr.actor] = time
            elif k == "RELEASE":
                waiters = state.lock_wq[tr.obj[1]]
                if len(waiters) >= 2:
                    key = (
                        time,
                        tr.obj[1],
                        waiters,
                        tuple(block_t[w] for w in waiters),
                    )
                    mw_release[key] = mw_release.get(key, Fraction(0)) + prob * p
                    smw = True
                if waiters:
                    bt = dict(block_t)
                    del bt[waiters[0]]
            elif k == "IO_ISSUE":
                it = dict(issue_t)
                it[tr.lineage] = time
            elif k == "COMPLETION":
                depth = len(state.dev_q[tr.obj[1]])
                if depth >= 2:
                    key = (time, tr.lineage, issue_t[tr.lineage], depth)
                    deep_completion[key] = (
                        deep_completion.get(key, Fraction(0)) + prob * p
                    )
                    sdp = True
                it = dict(issue_t)
                del it[tr.lineage]
            rec(tr.next_state, prob * p, time, bt, it, smw, sdp)

    rec(initial(cfg), Fraction(1), 0, {}, {}, False, False)
    return dict(
        n_paths=n_paths,
        mw_release=mw_release,
        deep_completion=deep_completion,
        mass_any_mw=mass_any_mw,
        mass_any_deep=mass_any_deep,
    )


def initial(cfg):
    from yupi.state import initial_state

    return initial_state(cfg)


def straddles(law, blocks_last, t):
    """Endpoints T of `law` whose window fully hides the queue-forming
    BLOCKs (all block times <= U) while containing the release (U < t <= T).
    Necessary geometric precondition for the windowed r2/r3 witness."""
    return [
        T
        for T in law.endpoints()
        if law.offset(T) >= blocks_last and law.offset(T) < t <= T
    ]


def main():
    horizon = 12  # the statute's T_ep for every law considered here
    out = {}

    # Control first: C0a must show zero events of either kind.
    ctrl = census(WorldConfig.c0a(), c0a_programs(), horizon)
    assert not ctrl["mw_release"] and not ctrl["deep_completion"], (
        "control violated: C0a produced a multi-waiter event"
    )
    print(f"control C0a: {ctrl['n_paths']} paths, zero events (as required)")

    laws = [
        WindowLaw(12, 6, 2),  # the measured day-five law
        WindowLaw(12, 4, 2),
        WindowLaw(12, 2, 2),
    ]

    for eps in (Fraction(1), Fraction(1, 2)):
        cfg = WorldConfig.c1(epsilon=eps)
        c = census(cfg, c1_programs(), horizon)
        print(
            f"\n=== C1 eps={eps}  ({c['n_paths']} paths, horizon {horizon}) ==="
        )
        print(
            f"P(path has multi-waiter RELEASE)   = {c['mass_any_mw']} "
            f"~ {float(c['mass_any_mw']):.4f}"
        )
        print(
            f"P(path has depth>=2 completion)    = {c['mass_any_deep']} "
            f"~ {float(c['mass_any_deep']):.4f}"
        )

        by_order = {}
        for (t, lock, order, btimes), m in sorted(c["mw_release"].items()):
            by_order[order] = by_order.get(order, Fraction(0)) + m
        print("wait-queue orders at multi-waiter RELEASE (total mass):")
        for order, m in sorted(by_order.items()):
            print(f"  order {order}: {m} ~ {float(m):.4f}")

        print("multi-waiter RELEASE events (t, lock, order, block times, mass):")
        rel_rows = []
        for (t, lock, order, btimes), m in sorted(c["mw_release"].items()):
            row = dict(
                t=t, lock=lock, order=list(order), block_times=list(btimes),
                mass=str(m), mass_f=float(m),
                straddled_by={
                    f"({law.T_ep},{law.L},{law.B})": straddles(law, max(btimes), t)
                    for law in laws
                },
            )
            rel_rows.append(row)
            print(
                f"  t={t:>2} lock={lock} order={order} blocks={btimes} "
                f"mass~{float(m):.5f} straddles: "
                + ", ".join(
                    f"L={law.L}:{row['straddled_by'][f'({law.T_ep},{law.L},{law.B})']}"
                    for law in laws
                )
            )

        comp_rows = []
        print("depth>=2 completions (t, req, issued, depth, mass) [first 10 by t]:")
        for (t, req, issued, depth), m in sorted(c["deep_completion"].items())[:10]:
            comp_rows.append(
                dict(t=t, req=req, issued=issued, depth=depth,
                     mass=str(m), mass_f=float(m))
            )
            print(f"  t={t:>2} req={req} issued@{issued} depth={depth} mass~{float(m):.5f}")
        n_comp = len(c["deep_completion"])
        print(f"  ({n_comp} distinct deep-completion signatures total)")

        out[str(eps)] = dict(
            n_paths=c["n_paths"],
            mass_any_mw=str(c["mass_any_mw"]),
            mass_any_deep=str(c["mass_any_deep"]),
            orders={str(k): str(v) for k, v in by_order.items()},
            mw_release=rel_rows,
            deep_completion_first10=comp_rows,
            n_deep_completion_signatures=n_comp,
        )

    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f:
            json.dump(dict(horizon=horizon, results=out), f, indent=2)
        print(f"\nraw JSON -> {sys.argv[1]}", flush=True)


if __name__ == "__main__":
    main()
