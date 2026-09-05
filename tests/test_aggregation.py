"""`yupi.aggregation.aggregate_by_rung` — one entry point for the statutory
producers' enumerator-side aggregation: per rung, the law mass over final
states per (reset, projected window) and the per-endpoint split, from path
aggregation (the committed method) or from the window-process recursion
(one r4 pass, every rung projected). Both must agree exactly wherever both
run. Written before the module (2026-09-04)."""
from fractions import Fraction

import pytest

from yupi.aggregation import aggregate_by_rung
from yupi.config import WorldConfig
from yupi.programs import COMPUTE, Loop, acquire, c1_programs, io, release
from yupi.window import WindowLaw

RUNGS = ("r0", "r1", "r2", "r3", "r4")


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_paths_and_window_modes_agree_exactly_on_c1(eps):
    cfg, progs, law = WorldConfig.c1(epsilon=eps), c1_programs(), WindowLaw(T_ep=8, L=4, B=2)
    a = aggregate_by_rung(cfg, progs, law, RUNGS, "paths")
    b = aggregate_by_rung(cfg, progs, law, RUNGS, "window")
    assert set(a) == set(b) == set(RUNGS)
    for r in RUNGS:
        assert a[r][0] == b[r][0], r          # {key: {state: mass}}
        assert a[r][1] == b[r][1], r          # {key: {T: mass}}
        assert sum(sum(j.values(), Fraction(0)) for j in a[r][0].values()) == 1


def test_modes_agree_on_a_looping_world():
    cfg = WorldConfig(n_threads=2, n_cpus=1, n_locks=1, n_devices=1, queue_depth=1, req_pool=2,
                      completion_p=Fraction(1, 3), epsilon=Fraction(1, 2), discipline="stochastic")
    progs = (Loop((acquire(0), release(0), io(0))), Loop((COMPUTE, acquire(0), release(0))))
    law = WindowLaw(T_ep=10, L=3, B=1)
    assert aggregate_by_rung(cfg, progs, law, ("r1", "r4"), "paths") == aggregate_by_rung(cfg, progs, law, ("r1", "r4"), "window")


def test_unknown_mode_is_refused():
    with pytest.raises(ValueError):
        aggregate_by_rung(WorldConfig.c1(), c1_programs(), WindowLaw(T_ep=4, L=2, B=2), ("r1",), "guess")
