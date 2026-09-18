"""Prefix-length variant of the window-process pass (learner contract v0.1.2,
2026-09-18): the first k records of every window whose law window runs at
least k records (T − U ≥ k), with the state after the k-th record; RESET
prefixes weighted by the number of open endpoints. Gated Fraction for
Fraction against the enumerator's canonical prefix aggregate and, through
`ceiling_table(prefix_len=k)`, against the pattern filter in prefix mode,
at C1 (8, 4, 2), both statutory ε, every rung."""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.pattern_ceiling import ceiling_table
from yupi.pattern_enumerator import pattern_aggregate_by_paths
from yupi.pattern_filter import filter_pattern_window, next_pattern_dist
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_process import prefix_law_aggregate, prefix_law_aggregates, window_law_aggregate

LAW = WindowLaw(8, 4, 2)
RUNGS = ("r0", "r1", "r2", "r3", "r4")


def _canonical_prefix_by_paths(cfg, progs, law, k, rung):
    w_T = endpoint_prior(law)
    out = {}
    for T in law.endpoints():
        u = law.offset(T)
        if T - u < k:
            continue
        for recs, prob, final in paths(cfg, progs, u + k):
            key = (u == 0, tuple(project(r, rung) for r in recs[u:u + k]))
            d = out.setdefault(key, {})
            d[final] = d.get(final, Fraction(0)) + w_T * prob
    return out


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_prefix_aggregate_equals_paths(eps, k):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    aggs = prefix_law_aggregates(cfg, progs, LAW, k, RUNGS)
    for rung in RUNGS:
        assert aggs[rung] == _canonical_prefix_by_paths(cfg, progs, LAW, k, rung), (rung, k)
        assert aggs[rung] == prefix_law_aggregate(cfg, progs, LAW, k, rung)
    total = sum((m for d in aggs["r4"].values() for m in d.values()), Fraction(0))
    # total prefix mass = P(T − U ≥ k): every non-RESET window (U > 0) plus the RESET endpoints ≥ k
    n_ok = sum(1 for T in LAW.endpoints() if T - LAW.offset(T) >= k)
    assert total == Fraction(n_ok, len(LAW.endpoints()))
    if k == LAW.L:   # at k = L the non-RESET classes coincide with the full-window aggregate's
        full = window_law_aggregate(cfg, progs, LAW, "r4")
        assert {kk: v for kk, v in aggs["r4"].items() if not kk[0]} == {kk: v for kk, v in full.items() if not kk[0]}


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("k", [1, 3])
def test_prefix_ceiling_table_equals_prefix_filter(eps, k):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    tables = ceiling_table(cfg, progs, LAW, RUNGS, prefix_len=k)
    for rung in RUNGS:
        by_paths = pattern_aggregate_by_paths(cfg, progs, LAW, rung, prefix_len=k)
        assert set(tables[rung]) == set(by_paths)
        for (reset, pw), (mass, star) in tables[rung].items():
            post, m2 = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset, prefix=True)
            assert mass == m2 and star == next_pattern_dist(post, cfg, progs, rung), (rung, reset, pw)


def test_prefix_length_out_of_range_refused():
    cfg, progs = WorldConfig.c1(), c1_programs()
    with pytest.raises(ValueError):
        prefix_law_aggregate(cfg, progs, LAW, 0, "r4")
    with pytest.raises(ValueError):
        prefix_law_aggregate(cfg, progs, LAW, LAW.L + 1, "r4")
