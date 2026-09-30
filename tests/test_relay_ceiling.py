"""Gate C of the relay intervention (docs/relay-intervention-design-v0.1.md §3)
at the small world (8, 4, 2): the r1ʀ pattern tables DERIVED from the r1
tables by the relay map must equal, class by class and Fraction for
Fraction, the tables computed by the ordinary recursion with the relay
applied to structural windows before pattern keying — and, for full
windows, by brute-force path summation. Gates A and B (the per-class KIND
marginal and the multiset of next-record probabilities are unchanged) are
checked on the same tables.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.interfaces import drop_relay
from yupi.pattern_ceiling import ceiling_table, derive_relay_table, relay_gates
from yupi.pattern_enumerator import relay_table_by_paths
from yupi.programs import c1_prime_loop_programs, c1_programs
from yupi.window import WindowLaw

LAW = WindowLaw(8, 4, 2)
PROGS = {"c1": c1_programs, "c1prime-loop": c1_prime_loop_programs}


@pytest.mark.parametrize("progname", ["c1", "c1prime-loop"])
@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("k", [None, 1, 2, 3, 4])
def test_derived_equals_recursion_route(progname, eps, k):
    cfg, progs = WorldConfig.c1(epsilon=eps), PROGS[progname]()
    t = ceiling_table(cfg, progs, LAW, ("r1", "r1R"), prefix_len=k)
    derived = derive_relay_table(t["r1"])
    assert derived == t["r1R"]
    g = relay_gates(t["r1"], derived)
    assert g["n_classes"] == len(t["r1"]) and g["gate_A_kind"] and g["gate_B_record"]
    assert sum(m for m, _ in derived.values()) == (1 if k is None else sum(m for m, _ in t["r1"].values()))
    for key in derived:                                    # the class map is a bijection: dropping the relay inverts it
        assert (key[0], drop_relay(key[1])) in t["r1"]


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_derived_equals_brute_force(eps):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    derived = derive_relay_table(ceiling_table(cfg, progs, LAW, ("r1",))["r1"])
    assert derived == relay_table_by_paths(cfg, progs, LAW)


def test_relay_moves_information_somewhere():
    """Not a gate: at (8, 4, 2) ε = 1 at least one r1 class's relay field is not
    constant across the class's next records (the relay says something)."""
    cfg, progs = WorldConfig.c1(), c1_programs()
    derived = derive_relay_table(ceiling_table(cfg, progs, LAW, ("r1",))["r1"])
    assert any(len({r.obj for r in star}) > 1 for _, star in derived.values())


def test_gates_detect_a_broken_derivation():
    cfg, progs = WorldConfig.c1(), c1_programs()
    r1 = ceiling_table(cfg, progs, LAW, ("r1",))["r1"]
    good = derive_relay_table(r1)
    key, a, b = next((k, a, b) for k, (_, s) in good.items() for a in s for b in s
                     if a.kind != b.kind and s[a] != s[b])
    m, star = good[key]
    swapped = dict(star); swapped[a], swapped[b] = star[b], star[a]      # same multiset, KIND marginal moved
    g = relay_gates(r1, {**good, key: (m, swapped)})
    assert g["gate_B_record"] and not g["gate_A_kind"]
    merged = dict(star); merged[a] = star[a] + star[b]; del merged[b]    # entropy changed
    g = relay_gates(r1, {**good, key: (m, merged)})
    assert not g["gate_B_record"]
