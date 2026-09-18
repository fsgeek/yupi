"""The headline-position ceiling table — P*(Πr | Πw) for every pattern class
of a (law, rung, ε) by the AGGREGATE route (learner contract v0.1.1 ledger
(b), 2026-09-18): the window-process pass, re-keyed by Π_all, one kernel
step per (S, β). Gated here at C1 (8, 4, 2), both statutory ε, against the
pattern filter (`yupi.pattern_filter`, itself gated against path summation),
class by class, Fraction for Fraction — mass and distribution both. Also:
the table round-trips through its serialized form, and the per-rung mean
next-record entropy H*(Πr | Πw) is the law-mass mean of the table's entries.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.pattern_ceiling import (
    ceiling_table,
    key_from_serial,
    mean_next_entropy_bits,
    serial_key,
)
from yupi.pattern_enumerator import pattern_aggregate_by_paths
from yupi.pattern_filter import filter_pattern_window, next_pattern_dist
from yupi.programs import c1_programs
from yupi.window import WindowLaw

LAW = WindowLaw(8, 4, 2)
RUNGS = ("r0", "r1", "r2", "r3", "r4")


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_table_equals_filter_on_every_class(eps):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    tables = ceiling_table(cfg, progs, LAW, RUNGS)                 # {rung: {(reset, pw): (mass, {ρ: prob})}}
    for rung in RUNGS:
        table = tables[rung]
        classes = pattern_aggregate_by_paths(cfg, progs, LAW, rung)
        assert set(table) == set(classes)
        total = Fraction(0)
        for (reset, pw), (mass, star) in table.items():
            post, m2 = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset)
            assert mass == m2 and star == next_pattern_dist(post, cfg, progs, rung), (rung, reset, pw)
            assert sum(star.values(), Fraction(0)) == 1
            total += mass
        assert total == 1
        # r0's classes are the kind sequences; every ρ there has all entity fields MASKED
        if rung == "r0":
            for _, star in table.values():
                assert all(r.actor == "MASKED" and r.obj == "MASKED" for r in star)


def test_serial_key_round_trip():
    cfg, progs = WorldConfig.c1(), c1_programs()
    table = ceiling_table(cfg, progs, LAW, ("r4",))["r4"]
    seen = set()
    for key in table:
        s = serial_key(key)
        assert isinstance(s, str) and s not in seen
        seen.add(s)
        assert key_from_serial(s) == key


def test_mean_next_entropy_is_the_law_mass_mean():
    from yupi.queries import entropy_bits
    cfg, progs = WorldConfig.c1(), c1_programs()
    table = ceiling_table(cfg, progs, LAW, ("r2",))["r2"]
    expect = sum(float(m) * entropy_bits(star) for m, star in table.values())
    assert abs(mean_next_entropy_bits(table) - expect) < 1e-12
    # the r4 (finest) pattern observer's next-record entropy is at most r0's kind-only... no: the alphabets
    # differ (pattern records vs kinds), so no ordering is asserted; only finiteness and positivity
    assert 0 < mean_next_entropy_bits(table) < 6


def test_save_load_round_trip_is_exact(tmp_path):
    from yupi.pattern_ceiling import load_table, save_table
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs()
    table = ceiling_table(cfg, progs, LAW, ("r4",))["r4"]
    p = tmp_path / "r4.jsonl"
    save_table(table, p)
    assert load_table(p) == table                      # Fractions survive; keys and records rebuild exactly
