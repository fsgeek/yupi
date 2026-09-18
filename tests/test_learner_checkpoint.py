"""Atomic checkpoints (trainer spec §2 'Checkpoint / resume'; the lease memo
of 2026-09-15: retain the previous checkpoint until the new one is durable).
The resume gate itself is in tests/test_learner_train.py."""
import pytest

torch = pytest.importorskip("torch")

from yupi.learner.checkpoint import load, rng_state, save_atomic, set_rng_state


def test_atomic_save_keeps_previous_until_new_is_durable(tmp_path):
    assert load(tmp_path) is None
    save_atomic(tmp_path, {"step": 1})
    save_atomic(tmp_path, {"step": 2})
    assert load(tmp_path)["step"] == 2
    assert torch.load(tmp_path / "ckpt.prev.pt", weights_only=False)["step"] == 1
    assert not (tmp_path / "ckpt.tmp").exists()


def test_rng_round_trip_python_numpy_torch():
    import random
    import numpy as np
    s = rng_state()
    a = (random.random(), float(np.random.rand()), torch.rand(3))
    set_rng_state(s)
    b = (random.random(), float(np.random.rand()), torch.rand(3))
    assert a[0] == b[0] and a[1] == b[1] and torch.equal(a[2], b[2])
