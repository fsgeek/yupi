"""D8 attribution core (prereg d8-attribution-prereg-v0.1.md, commit a39f555).

These tests assert IDENTITIES, GATES, and STRUCTURAL ZEROS only — no sign or
size of any Δ at a non-null cell is asserted or printed here, because the
grid is frozen by a blind cost benchmark before any Δ is read (prereg §4).
"""
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, __import__("os").path.dirname(__file__))
from test_shuffled_window import _visible_windows          # the census helper

from yupi.attribution import (COORDS, chain_terms, check_bijection, coords,
                              envelope, joint_entropy, latent_table, losses,
                              mass, normalized, per_observation,
                              per_offset_anchored, reconstruct, shapley,
                              subset_entropy, CoordCache, value_fn,
                              visible_table)
from yupi.config import WorldConfig
from yupi.programs import c0b_programs, c1_programs
from yupi.shuffled_window import shuffled_window_filter_with_evidence
from yupi.window import WindowLaw
from yupi.window_filter import filter_window_with_evidence

C0B = [("stochastic", "r2", WindowLaw(6, 4, 2), 64), ("fifo", "r4", WindowLaw(6, 4, 2), 56),
       ("stochastic", "r2", WindowLaw(6, 3, 3), 90), ("fifo", "r4", WindowLaw(6, 3, 3), 102)]


def _tables(cfg, progs, law, rung):
    lat = latent_table(cfg, progs, law, rung)
    vis, src = visible_table(lat, law.B)
    return lat, vis, src


@pytest.mark.parametrize("disc,rung,law,expected", C0B)
def test_visible_census_matches_helper_and_mass_is_one(disc, rung, law, expected):
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    lat, vis, src = _tables(cfg, progs, law, rung)
    assert sum(mass(j) for j in lat.values()) == 1
    assert sum(mass(j) for j in vis.values()) == 1
    assert len(vis) == expected
    helper = {(tuple(tuple(b) for b in buckets), reset)
              for buckets, reset in _visible_windows(cfg, progs, law, rung)}
    assert {(v, r) for (r, v) in vis} == helper
    # every source mass is accounted for
    for v, j in vis.items():
        assert sum(src[v].values(), Fraction(0)) == mass(j)


@pytest.mark.parametrize("disc,rung,law,expected", C0B)
def test_gate2_both_paths_posterior_and_mass_every_observation(disc, rung, law, expected):
    """Prereg §5 gate 2 in table form: recursive filter == aggregated path
    table, joint (U, S_T) and law mass, for every distinct observation of
    both channels. Uncapped."""
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    lat, vis, _ = _tables(cfg, progs, law, rung)
    for (reset, buckets), joint in vis.items():
        post, ev = shuffled_window_filter_with_evidence(
            cfg, progs, law, [list(b) for b in buckets], rung, reset)
        fj = {(u, s): w * m for u, (w, b) in post.components.items() for s, m in b.items()}
        assert fj == normalized(joint) and ev == mass(joint)
    for (reset, win), joint in lat.items():
        post, ev = filter_window_with_evidence(cfg, progs, law, list(win), rung, reset)
        fj = {(u, s): w * m for u, (w, b) in post.components.items() for s, m in b.items()}
        assert fj == normalized(joint) and ev == mass(joint)


@pytest.mark.parametrize("rung", ["r1", "r2", "r3", "r4"])
def test_Z3_B1_channel_is_identity_every_loss_zero(rung):
    cfg, progs = WorldConfig.c0b(discipline="stochastic"), c0b_programs()
    lat, vis, src = _tables(cfg, progs, WindowLaw(6, 3, 1), rung)
    assert len(lat) == len(vis)
    F = losses(lat, vis)
    assert all(f == 0.0 for f in F.values())
    assert all(g == 0.0 and not inf for _, _, g, inf in per_observation(lat, vis, src))


def test_gate_F_bijection_and_full_coordinate_identity():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs()
    lat, vis, _ = _tables(cfg, progs, WindowLaw(8, 4, 2), "r1")
    n = check_bijection(lat, vis)
    assert n > 100
    cache = CoordCache()
    for t in (lat, vis):
        assert subset_entropy(t, COORDS, cache) == joint_entropy(t)   # same partition, same floats
    # a hand case: two waiters queued in reverse index order, one in-flight request
    from yupi.state import RUNNABLE, RUNNING, State, io_blocked, lock_blocked
    s = State(pc=(1, 1, 2, 3), status=(RUNNING, lock_blocked(0), lock_blocked(0), io_blocked(1)),
              running=frozenset({0}), lock_owner=(0, None), lock_wq=((2, 1), ()),
              dev_q=(((3, 1),),), rr_cursor=2)
    c = coords(3, s)
    assert c["WQ"] == ((1, 0), ()) and c["DQ"] == ((0,),) and c["REQ"] == (((3, 1),),)
    assert c["kappa"] == 2 and c["U"] == 3 and c["rho"][1][3] == ("IO_BLOCKED",)
    assert reconstruct(c) == (3, s)


@pytest.mark.parametrize("cfg,progs,law,rung", [
    (WorldConfig.c0b(discipline="stochastic"), c0b_programs(), WindowLaw(6, 3, 3), "r2"),
    (WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs(), WindowLaw(8, 4, 2), "r1"),
    (WorldConfig.c1(epsilon=Fraction(1)), c1_programs(), WindowLaw(8, 4, 2), "r3"),
])
def test_gates_A_chain_shapley_envelope_identities(cfg, progs, law, rung):
    lat, vis, src = _tables(cfg, progs, law, rung)
    F = losses(lat, vis)
    d_un, off = F[frozenset(COORDS)], F[frozenset({"U"})]
    d_an = d_un - off
    assert d_un >= -1e-12 and off >= -1e-12 and d_an >= -1e-12
    for cond, players, total in ((frozenset(), COORDS, d_un),
                                 (frozenset({"U"}), COORDS[1:], d_an)):
        v = value_fn(F, cond)
        ch = chain_terms(v, players)
        assert all(t >= -1e-12 for t in ch.values())
        assert abs(sum(ch.values()) - total) < 1e-9
        sh = shapley(v, players)
        assert abs(sum(sh.values()) - total) < 1e-9
        env = envelope(v, players)
        for k in players:
            assert env[k][0] - 1e-12 <= ch[k] <= env[k][1] + 1e-12
            assert env[k][0] - 1e-12 <= sh[k] <= env[k][1] + 1e-12
    # per-observation gains integrate to Δ_un
    rows = per_observation(lat, vis, src)
    assert abs(sum(float(m) * g for _, m, g, _ in rows) - d_un) < 1e-9
    prev = sum((m for _, m, _, inf in rows if inf), Fraction(0))
    assert 0 <= prev <= 1
    assert all((g > 1e-12) <= inf for _, _, g, inf in rows)      # positive gain ⇒ exactly informative
    # per-endpoint anchored gains are law-mass consistent with Δ_an
    pe = per_offset_anchored(lat, vis, src, law)
    assert abs(sum(pe.values()) / len(pe) - d_an) < 1e-9


def test_Z1_kappa_term_exactly_zero_at_eps1_under_every_prefix():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    lat, vis, _ = _tables(cfg, progs, WindowLaw(8, 4, 2), "r1")
    F = losses(lat, vis)
    for A in F:
        if "kappa" not in A:
            assert F[A | {"kappa"}] == F[A]


def test_Z2_WQ_term_exactly_zero_at_c0b_under_every_prefix():
    cfg, progs = WorldConfig.c0b(discipline="fifo"), c0b_programs()
    lat, vis, _ = _tables(cfg, progs, WindowLaw(6, 3, 3), "r1")
    F = losses(lat, vis)
    for A in F:
        if "WQ" not in A:
            assert F[A | {"WQ"}] == F[A]
