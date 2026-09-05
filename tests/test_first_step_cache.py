"""Second exact memo in the window filter (2026-09-04): with the forward
marginals cached, a window's cost is dominated by the FIRST Bayes step,
which runs `enabled()` over the whole marginal μ_u for every compatible
offset u — and depends only on (cfg, programs, rung, u, first record).
A median-support window at (40,4,2) still cost 0.63 s for that reason.
The memo stores the unnormalized first-step belief and likelihood per
(u, first record); later steps are unchanged. Results must be
bit-identical and the kernel must not be re-run over μ_u for a
(u, record) already seen. Written before the memo."""
from fractions import Fraction

import pytest

from yupi import window_filter
from yupi.config import WorldConfig
from yupi.programs import c1_programs
from yupi.window import WindowLaw
from yupi.window_filter import (filter_window_with_evidence, first_step_cache_clear,
                                marginal_cache_clear)
from yupi.window_process import window_law_aggregate


@pytest.fixture
def world():
    marginal_cache_clear(); first_step_cache_clear()
    cfg, progs, law = WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(T_ep=12, L=4, B=2)
    agg = window_law_aggregate(cfg, progs, law, "r1")
    return cfg, progs, law, agg


def test_results_bit_identical_with_and_without_the_memo(world):
    cfg, progs, law, agg = world
    for (reset, window), joint in list(agg.items())[:60]:
        first_step_cache_clear()
        cold = filter_window_with_evidence(cfg, progs, law, list(window), "r1", reset)
        warm = filter_window_with_evidence(cfg, progs, law, list(window), "r1", reset)
        assert cold == warm
        mass = sum(joint.values(), Fraction(0))
        assert warm[1] == mass and warm[0].state_marginal() == {s: m / mass for s, m in joint.items()}


def test_second_window_with_the_same_first_record_skips_the_full_marginal_step(world, monkeypatch):
    cfg, progs, law, agg = world
    windows = [(r, w) for (r, w), _ in agg.items() if not r and len(w) == 4]
    a = windows[0]
    b = next(x for x in windows[1:] if x[1][0] == a[1][0] and x[1] != a[1])   # same first record, different window
    calls = []
    real = window_filter.enabled
    monkeypatch.setattr(window_filter, "enabled", lambda *args, **kw: (calls.append(1), real(*args, **kw))[1])
    filter_window_with_evidence(cfg, progs, law, list(a[1]), "r1", a[0])
    n_a = len(calls); calls.clear()
    filter_window_with_evidence(cfg, progs, law, list(b[1]), "r1", b[0])
    n_b = len(calls)
    # b's first step is served from the memo; the marginal at every offset has ≥ 1 state,
    # and (12,4,2) has 4 compatible offsets for a 4-record non-reset window
    assert n_b < n_a
    assert n_a - n_b >= sum(len(window_filter.state_marginal_at(cfg, progs, u)) for _, u in law.compatible_endpoints(4, False))


def test_memo_is_keyed_by_rung_and_offset(world):
    cfg, progs, law, agg = world
    (reset, window), joint = next(iter(agg.items()))
    r1 = filter_window_with_evidence(cfg, progs, law, list(window), "r1", reset)
    # the same records projected at r0 are a different observation; must not hit r1's memo
    from yupi.interfaces import project
    r0 = filter_window_with_evidence(cfg, progs, law, [project(x, "r0") for x in window], "r0", reset)
    assert r0[1] >= r1[1]                      # coarser observation, larger evidence mass
