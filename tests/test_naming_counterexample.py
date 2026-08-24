"""Executable naming counterexample (Part II amendment v0.2.6, Clause 2′).

Naming is dynamically inert (no kernel rule reads σ) yet inferentially
live: a query takes a NAMED entity as its argument, and C1's programs give
the structural threads asymmetric roles, so the Q2 ceiling for a surface
name depends on which structural thread the name is bound to. Under a
uniform binding the name's answer distribution is the mixture of the
structural threads' distributions and coincides with none of them.

The reviewer (Codex, 2026-08-24) refuted "no Q1–Q5 query reads names" with
one exact number (1.208 bits); this file pins the exact distributions
behind it so the claim is a test, not prose. Entropies are documentary.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.programs import c1_programs
from yupi.queries import entropy_bits, pushforward, q2_status

TICK = 4


def _prior(cfg, progs, horizon):
    """Unconditioned (no observation) exact belief over S_horizon."""
    prior = {}
    for _, prob, final in paths(cfg, progs, horizon):
        prior[final] = prior.get(final, Fraction(0)) + prob
    assert sum(prior.values()) == 1
    return prior


def _q2_by_thread(cfg, progs):
    prior = _prior(cfg, progs, TICK)
    return [pushforward(prior, lambda s, i=i: q2_status(s, i))
            for i in range(cfg.n_threads)]


def _uniform_name_mixture(dists):
    """Answer distribution of a surface name bound uniformly over threads."""
    n = len(dists)
    mix = {}
    for d in dists:
        for a, m in d.items():
            mix[a] = mix.get(a, Fraction(0)) + m / n
    return mix


def test_q2_prior_distributions_at_c1_tick4_eps1():
    """The exact distributions the 1.000 / 1.483 / 1.208 figures come from."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    d = _q2_by_thread(cfg, progs)
    half = {"RUNNING": Fraction(1, 2), "RUNNABLE": Fraction(1, 2)}
    assert d[0] == half and d[1] == half and d[2] == half
    assert d[3] == {"RUNNING": Fraction(5, 12), "RUNNABLE": Fraction(5, 12),
                    "IO_BLOCKED": Fraction(1, 6)}
    mix = _uniform_name_mixture(d)
    assert mix == {"RUNNING": Fraction(23, 48), "RUNNABLE": Fraction(23, 48),
                   "IO_BLOCKED": Fraction(1, 24)}
    # documentary: the decimals cited in the amendment
    assert round(entropy_bits(d[0]), 3) == 1.000
    assert round(entropy_bits(d[3]), 3) == 1.483
    assert round(entropy_bits(mix), 3) == 1.208


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_uniformly_named_referent_matches_no_structural_thread(eps):
    """The inequality Clause 2′ rests on: the name's Q2 distribution is not
    any structural thread's, so conditioning on a canonical naming σ₀
    changes a Q2 ceiling although σ never enters the dynamics. Holds at
    both statutory ε — the counterexample is not an ε = 1 artifact."""
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    d = _q2_by_thread(cfg, progs)
    mix = _uniform_name_mixture(d)
    assert all(mix != di for di in d)
    # the asymmetry that makes naming live: the threads are not exchangeable
    assert len({tuple(sorted(di.items())) for di in d}) > 1
    # and the mixture is strictly more uncertain than the structural mean
    # (concavity), so a canonical-name track under-reports the random-name
    # Q2 entropy for this referent rather than merely relabeling it
    assert entropy_bits(mix) > sum(entropy_bits(di) for di in d) / len(d)
