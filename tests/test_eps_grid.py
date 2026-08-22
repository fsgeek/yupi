"""Witnesses for the held-out ε override (held-out-laws-proposal v0.3, Selection E).

The five ceilings/sweep scripts historically hard-coded ε ∈ (1, ½). Tier 1's
F2 family runs at drawn ε ∈ {¼, ⅝}; the override must (i) default to the
historical pair bit-for-bit so every prior artifact remains reproducible,
(ii) parse an explicit list exactly as Fractions, (iii) refuse garbage.
"""
from fractions import Fraction

import pytest

from yupi.eps_grid import eps_grid


def test_default_is_historical_pair(monkeypatch):
    monkeypatch.delenv("YUPI_EPS", raising=False)
    assert eps_grid() == (Fraction(1), Fraction(1, 2))


def test_env_override_parses_exact_fractions(monkeypatch):
    monkeypatch.setenv("YUPI_EPS", "1/4,5/8")
    assert eps_grid() == (Fraction(1, 4), Fraction(5, 8))


def test_env_override_tolerates_spaces_and_integers(monkeypatch):
    monkeypatch.setenv("YUPI_EPS", " 1 , 1/2 ")
    assert eps_grid() == (Fraction(1), Fraction(1, 2))


@pytest.mark.parametrize("bad", ["", "0.25", "2", "-1/2", "1/0", "a"])
def test_env_override_rejects_out_of_range_or_unparseable(monkeypatch, bad):
    monkeypatch.setenv("YUPI_EPS", bad)
    with pytest.raises(ValueError):
        eps_grid()
