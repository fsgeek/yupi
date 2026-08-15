"""Predictive-state targets (Part II §5): P-next and P-horizon functionals
(next-m kinds, time-to-next-wake, next IO_COMPLETE lineage) — two-path
gated like Q4: `predict` (absorbing / fixed-length recursions) against
`predict_paths` (explicit continuation enumeration)."""

from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import NONE_WITHIN_W
from yupi.predict import (
    next_complete_lineage, next_kinds, p_next, time_to_wake,
)
from yupi.predict_paths import (
    next_complete_lineage_by_paths, next_kinds_by_paths, time_to_wake_by_paths,
)
from yupi.programs import c1_programs
from yupi.queries import entropy_bits
from yupi.state import initial_state


def _finals(eps, h=8):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    return cfg, progs, {f for _, _, f in paths(cfg, progs, h)}


def test_p_next_is_a_distribution_and_coarsens_monotonically():
    cfg, progs, finals = _finals(Fraction(1))
    for s in list(finals)[:40]:
        hs = []
        for rung in ("r1", "r2", "r3", "r4"):
            d = p_next(s, cfg, progs, rung)
            assert sum(d.values()) == 1
            hs.append(entropy_bits(d))
        # coarser projection ⇒ no more entropy (data processing)
        assert hs[0] <= hs[1] + 1e-12 <= hs[2] + 2e-12 <= hs[3] + 3e-12


def test_two_paths_agree_on_every_endpoint_state():
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg, progs, finals = _finals(eps)
        for s in finals:
            for W in (1, 2, 3, 4):
                assert time_to_wake(s, cfg, progs, W) == time_to_wake_by_paths(s, cfg, progs, W)
                assert next_complete_lineage(s, cfg, progs, W) == next_complete_lineage_by_paths(s, cfg, progs, W)
            for m in (1, 2, 3):
                assert next_kinds(s, cfg, progs, m) == next_kinds_by_paths(s, cfg, progs, m)


def test_time_to_wake_support_and_reset_control():
    cfg, progs, finals = _finals(Fraction(1))
    s0 = initial_state(cfg)
    assert time_to_wake(s0, cfg, progs, 1) == {NONE_WITHIN_W: Fraction(1)}
    for s in finals:
        d = time_to_wake(s, cfg, progs, 4)
        assert sum(d.values()) == 1
        assert all(k == NONE_WITHIN_W or 1 <= k <= 4 for k in d)
    # positive control: some endpoint state can wake at step 1
    assert any(1 in time_to_wake(s, cfg, progs, 4) for s in finals)


def test_next_kinds_matches_p_next_at_r1_kind_marginal():
    """m=1 next-kind distribution equals the kind-marginal of P-next at r1
    (record kinds are what r1 exposes, plus actor)."""
    cfg, progs, finals = _finals(Fraction(1))
    for s in list(finals)[:40]:
        d1 = next_kinds(s, cfg, progs, 1)
        pn = p_next(s, cfg, progs, "r1")
        marg = {}
        for rec, p in pn.items():
            marg[(rec.kind,)] = marg.get((rec.kind,), Fraction(0)) + p
        assert d1 == marg
