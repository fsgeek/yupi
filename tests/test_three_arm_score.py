"""The three-arm scorer's predictions on planted gains (scripts/three_arm_score.py, prereg §3)."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from three_arm_score import score  # noqa: E402

N, NC = 40000, 4000


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(7)
    g = rng.integers(0, NC, N)
    xr = np.abs(rng.normal(0, 0.3, NC))[g]
    xd = np.abs(0.4 * xr + rng.normal(0, 0.2, N))           # correlated, as the real arms are
    zero = rng.random(N) < 0.1
    xr[zero] = 0
    xd[zero] = 0
    return rng, g, xr, xd, zero


def noise(rng, n, s=0.01):
    return rng.normal(0, s, n)


def test_planted_move(world):
    rng, g, xr, xd, zero = world
    r = score(0.02 * xr + noise(rng, N), 0.02 * xd + noise(rng, N), noise(rng, N), xr, xd, g, zero)
    assert r["reading"] == "H_move" and r["predictions"]["P_V"]
    assert 0.8 < r["ratio_D_over_R"] < 1.25


def test_planted_bind(world):
    rng, g, xr, xd, zero = world
    r = score(0.02 * xr + noise(rng, N), noise(rng, N), noise(rng, N), xr, xd, g, zero)
    assert r["reading"] == "H_bind"


def test_planted_field(world):
    rng, g, xr, xd, zero = world
    r = score(0.004 + 0.02 * xr + noise(rng, N), 0.004 + noise(rng, N), 0.004 + noise(rng, N), xr, xd, g, zero)
    assert r["reading"] == "H_field indicated" and not r["predictions"]["P_null"]


def test_intermediate_is_unresolved(world):
    rng, g, xr, xd, zero = world
    r = score(0.02 * xr + noise(rng, N), 0.008 * xd + noise(rng, N), noise(rng, N), xr, xd, g, zero)
    assert r["reading"] == "unresolved"            # ratio ~0.4: neither ≥ 0.5 nor ≤ 0.25


def test_zero_set_means_reported(world):
    rng, g, xr, xd, zero = world
    r = score(0.02 * xr, 0.02 * xd, np.zeros(N), xr, xd, g, zero)
    assert r["mean_gains"]["r1R"]["on_iota4_zero"] == 0.0
    assert r["mean_gains"]["r1D"]["off_iota4_zero"] > 0
