"""D2 witness for the r0 → r1 adjacency (Part II proposal v0.2.7.1, Owed
item 2; Codex review 2 finding 33): D2 requires, for each adjacent rung
pair, an EXHIBITED history class on which the added field changes (a) the
posterior on a named query in Q1–Q5 or (b) a preregistered finite-horizon
predictive distribution. Aggregate gaps (the r0 census) show such classes
exist; this file exhibits one and pins it.

Construction: at the committed law (14, 4, 2), ε = 1, take the r0 window
classes and their r1 refinements. A class witnesses (a) if some refinement's
Q1[L0] posterior differs from the class's own, and (b) if some refinement's
next-2-kind distribution differs from the class's own. The exhibited class
is the heaviest (by law mass) that witnesses both. Exact rationals
throughout; the pinned strings are exact.
"""
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.predict import next_kinds
from yupi.programs import c1_programs
from yupi.queries import q1_owner
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregates

LAW = WindowLaw(T_ep=14, L=4, B=2)


def _mix(joint, f):
    """Law-mass mixture of a per-state distribution f(state) under `joint`."""
    mass = sum(joint.values(), Fraction(0))
    out = {}
    for s, m in joint.items():
        for k, p in f(s).items():
            out[k] = out.get(k, Fraction(0)) + (m / mass) * p
    return {k: v for k, v in out.items() if v}


def r0_r1_witness(eps=Fraction(1)):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    aggs = window_law_aggregates(cfg, progs, LAW, ("r0", "r1"))
    by_r0 = {}
    for (reset, win), joint in aggs["r1"].items():
        by_r0.setdefault((reset, tuple(project(r, "r0") for r in win)), []).append(((reset, win), joint))
    q1 = lambda s: {q1_owner(s, 0): Fraction(1)}
    k2 = lambda s: next_kinds(s, cfg, progs, 2)
    best = None
    for key, refinements in by_r0.items():
        if len(refinements) < 2:
            continue
        coarse = aggs["r0"][key]
        q1_r0, k2_r0 = _mix(coarse, q1), _mix(coarse, k2)
        a = any(_mix(j, q1) != q1_r0 for _, j in refinements)
        b = any(_mix(j, k2) != k2_r0 for _, j in refinements)
        if a and b:
            mass = sum(coarse.values(), Fraction(0))
            if best is None or mass > best["mass"]:
                best = dict(key=key, mass=mass, n_refinements=len(refinements),
                            q1_r0=q1_r0, k2_r0=k2_r0,
                            q1_r1=[_mix(j, q1) for _, j in refinements],
                            k2_r1=[_mix(j, k2) for _, j in refinements])
    return best


def test_r0_to_r1_has_an_exhibited_d2_class_for_both_clauses():
    w = r0_r1_witness()
    assert w is not None
    assert w["n_refinements"] >= 2 and w["mass"] > 0
    # (a): at least one refinement moves the Q1[L0] posterior
    assert any(d != w["q1_r0"] for d in w["q1_r1"])
    # (b): at least one refinement moves the next-2-kind distribution
    assert any(d != w["k2_r0"] for d in w["k2_r1"])


def test_exhibited_class_is_pinned():
    """The heaviest class witnessing both clauses at (14, 4, 2), ε = 1, from
    reset: kinds DISPATCH, DISPATCH, ACQUIRE, DISPATCH — one thread acquired
    lock 0 after two dispatches, a third dispatch followed. Kind-only cannot
    say whether thread 0 or thread 1 acquired (Q1[L0] = ½ / ½); every one of
    the 36 actor-visible refinements says which (a point mass). Next-2-kinds
    under kind-only is a five-way mixture; no refinement has more than three
    outcomes."""
    w = r0_r1_witness()
    reset, win = w["key"]
    assert reset is True
    assert tuple(r.kind for r in win) == ("DISPATCH", "DISPATCH", "ACQUIRE", "DISPATCH")
    assert all(r.actor == "MASKED" for r in win)
    assert w["mass"] == Fraction(1, 14) and w["n_refinements"] == 36
    assert w["q1_r0"] == {0: Fraction(1, 2), 1: Fraction(1, 2)}
    assert all(len(d) == 1 and set(d.values()) == {Fraction(1)} for d in w["q1_r1"])
    assert sum(1 for d in w["q1_r1"] if 0 in d) == 18 and sum(1 for d in w["q1_r1"] if 1 in d) == 18
    assert w["k2_r0"] == {
        ("ACQUIRE", "DISPATCH"): Fraction(1, 12), ("BLOCK", "DISPATCH"): Fraction(5, 18),
        ("IO_ISSUE", "DISPATCH"): Fraction(5, 27), ("IO_ISSUE", "IO_COMPLETE"): Fraction(5, 54),
        ("STEP", "DISPATCH"): Fraction(13, 36)}
    assert all(1 <= len(d) <= 3 and sum(d.values()) == 1 for d in w["k2_r1"])
    assert all(d != w["k2_r0"] for d in w["k2_r1"])       # every refinement moves clause (b)
