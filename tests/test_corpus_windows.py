"""Part II §2(a): the window is the last L records ending on a bucket endpoint,
RESET present iff U = 0 and not charged against L; design v0.1 §2 serialization."""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.corpus import windows as W
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import RESET
from yupi.interfaces import project
from yupi.programs import c1_prime_loop_programs, c1_programs
from yupi.simulator import sample_episode
from yupi.window import WindowLaw

KEY = bytes(range(32))
SMALL = WindowLaw(T_ep=8, L=4, B=2)
FROZEN = WindowLaw(T_ep=40, L=8, B=2)


def test_endpoint_is_on_the_grid_and_keyed():
    ends = set(SMALL.endpoints())
    assert all(W.draw_endpoint(KEY, e, SMALL) in ends for e in range(500))
    assert W.draw_endpoint(KEY, 5, SMALL) == W.draw_endpoint(KEY, 5, SMALL)


def test_reset_rule_for_every_endpoint_of_8_4_2():
    """Every endpoint T ∈ {2,4,6,8}: U = max(0, T−4); RESET iff U = 0."""
    cfg, progs = WorldConfig.c1(), c1_programs()
    seen = set()
    for ep in range(400):
        w = W.draw_window(cfg, progs, SMALL, "r4", KEY, ep)
        seen.add(w.T)
        assert w.U == max(0, w.T - 4) and w.reset == (w.U == 0)
        assert len(w.records) == w.T - w.U
        toks = W.serialize(w, EpisodeTable.draw(KEY, ep, cfg))
        assert (toks[0] == RESET) == w.reset
        assert len(toks) == 5 * (w.T - w.U) + (1 if w.reset else 0)   # design gate 5
    assert seen == {2, 4, 6, 8}


def test_window_is_the_episode_slice_projected():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_prime_loop_programs()
    w = W.draw_window(cfg, progs, FROZEN, "r2", KEY, 42)
    ep = sample_episode(cfg, progs, 40, 42)
    assert w.records == tuple(project(r, "r2") for _, r in ep[w.U:w.T])
    assert len(w.records) == w.T - w.U <= 8      # T < L gives a short window with RESET (Part II §2(a))


@pytest.mark.parametrize("rung", ["r0", "r1", "r2", "r3", "r4"])
@pytest.mark.parametrize("law,progs,eps", [(SMALL, c1_programs(), Fraction(1)),
                                           (FROZEN, c1_prime_loop_programs(), Fraction(1, 2))])
def test_serialize_deserialize_round_trip(rung, law, progs, eps):
    cfg = WorldConfig.c1(epsilon=eps)
    for ep in range(200):
        w = W.draw_window(cfg, progs, law, rung, KEY, ep)
        t = EpisodeTable.draw(KEY, ep, cfg)
        toks = W.serialize(w, t)
        assert len(toks) <= W.max_tokens(law)
        assert W.deserialize(toks, t) == (w.reset, w.records)


def test_max_tokens():
    assert W.max_tokens(FROZEN) == 41 and W.max_tokens(SMALL) == 21
