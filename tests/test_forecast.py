"""Statutory Q4 (Part II §5): first directly-woken thread within horizon W.

Two-path gate for the forward sum: `forecast.q4_forward` (recursive
absorbing sum, memoized on (state, k)) against `forecast_paths.q4_by_paths`
(explicit enumeration of every W-step continuation, tag scanned along the
path). They share the WORLD (kernel.enabled) and nothing else.
"""

from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import NONE_WITHIN_W, q4_forward, q4_mixture, split_entropy
from yupi.forecast_paths import q4_by_paths
from yupi.programs import COMPUTE, acquire, c1_programs, release
from yupi.state import initial_state


def _c1(eps=Fraction(1)):
    return WorldConfig.c1(epsilon=eps), c1_programs()


def test_distribution_sums_to_one_and_none_at_w0():
    cfg, progs = _c1()
    s0 = initial_state(cfg)
    assert q4_forward(s0, cfg, progs, 0) == {NONE_WITHIN_W: Fraction(1)}
    for W in (1, 2, 3):
        d = q4_forward(s0, cfg, progs, W)
        assert sum(d.values()) == 1
        assert all(v > 0 for v in d.values())


def test_no_wake_possible_in_short_horizon_from_reset():
    # From reset nothing is held or in flight: no completion or handoff can
    # occur on the very first tick (a DISPATCH or IDLE must come first).
    cfg, progs = _c1()
    assert q4_forward(initial_state(cfg), cfg, progs, 1) == {NONE_WITHIN_W: Fraction(1)}


def test_two_paths_agree_on_every_endpoint_state():
    """Every distinct final state of every C1 path to horizon 8, both ε,
    W ∈ {1..4} AND W = 8 (the measurement's secondary horizon; made
    exhaustive on the second truthsayer pass — ~6 s): forward sum ==
    explicit path enumeration, Fraction-exact."""
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg, progs = _c1(eps)
        finals = {f for _, _, f in paths(cfg, progs, 8)}
        assert len(finals) > 10
        memo = {}
        for s in finals:
            for W in (1, 2, 3, 4, 8):
                assert q4_forward(s, cfg, progs, W, memo) == q4_by_paths(s, cfg, progs, W)


def test_wake_is_witnessed_somewhere():
    """Positive control: at horizon 8 in C1 some endpoint state has a
    non-NONE first-wake mass within W=4 (locks are held, IO is in flight)."""
    cfg, progs = _c1()
    finals = {f for _, _, f in paths(cfg, progs, 8)}
    assert any(
        any(k != NONE_WITHIN_W for k in q4_forward(s, cfg, progs, 4)) for s in finals
    )


def test_mixture_and_split():
    cfg, progs = _c1()
    finals = list({f for _, _, f in paths(cfg, progs, 8)})[:6]
    belief = {s: Fraction(1, len(finals)) for s in finals}
    per_state = {s: q4_forward(s, cfg, progs, 4) for s in finals}
    mix = q4_mixture(belief, per_state)
    assert sum(mix.values()) == 1
    total, irreducible, gap = split_entropy(belief, per_state)
    assert total >= irreducible - 1e-12 and gap >= -1e-12
    assert total == pytest.approx(irreducible + gap)
    # point mass: no observation gap
    pm = {finals[0]: Fraction(1)}
    t, i, g = split_entropy(pm, {finals[0]: per_state[finals[0]]})
    assert g == pytest.approx(0.0) and t == pytest.approx(i)


def test_two_paths_agree_at_w8_on_representative_states():
    """Representative W=8 check kept as documentation of the second
    truthsayer pass (six structurally selected horizon-8 endpoint states
    per ε: held lock + waiter / request in flight / neither). It is
    SUBSUMED by the exhaustive W=8 gate in the preceding test."""
    for eps in (Fraction(1), Fraction(1, 2)):
        cfg, progs = _c1(eps)
        finals = sorted({f for _, _, f in paths(cfg, progs, 8)}, key=repr)
        a = [s for s in finals if any(o is not None for o in s.lock_owner) and any(s.lock_wq)]
        b = [s for s in finals if any(s.dev_q)]
        c = [s for s in finals if not any(s.dev_q) and not any(s.lock_wq)]
        picks = a[:2] + b[:2] + c[:2]
        assert len(picks) == 6
        for s in picks:
            assert q4_forward(s, cfg, progs, 8) == q4_by_paths(s, cfg, progs, 8)
