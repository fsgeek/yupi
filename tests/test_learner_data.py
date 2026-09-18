"""Window corpus -> model tensors (trainer spec §2 'Sequence framing';
plan Task 2). BOS is a model-side input index (156), never a target; each
window contributes exactly len(window) + 1 scored targets — its tokens and
one PAD, the end-of-window event (contract §1 item 3); the epoch order is a
permutation that is a function of (seed, epoch) alone."""
import numpy as np
import pytest

pytest.importorskip("torch")

from yupi.corpus.vocab import PAD, TOKEN_ID
from yupi.learner.data import BOS, SEQ, batches, epoch_order, frame


def test_frame_bos_one_pad_target_and_mask():
    w = (TOKEN_ID["RESET"], TOKEN_ID["DISPATCH"], TOKEN_ID["T03"], TOKEN_ID["NONE"], TOKEN_ID["NONE"], TOKEN_ID["NONE"])
    x, y, m = frame([w])
    assert x.shape == y.shape == m.shape == (1, SEQ) and x.dtype == np.int64 and y.dtype == np.int64 and m.dtype == bool
    assert x[0, 0] == BOS and list(x[0, 1:7]) == list(w) and (x[0, 7:] == TOKEN_ID[PAD]).all()
    assert list(y[0, :6]) == list(w) and y[0, 6] == TOKEN_ID[PAD]          # the end-of-window target
    assert m[0, :7].all() and not m[0, 7:].any() and m.sum() == len(w) + 1
    assert BOS == 156 and SEQ == 42


def test_frame_custom_seq_len_and_refusal():
    w = tuple(range(1, 21))
    x, y, m = frame([w], seq_len=22)
    assert x.shape == (1, 22) and m.sum() == 21
    with pytest.raises(ValueError):
        frame([tuple(range(1, 23))], seq_len=22)                            # 22 tokens need 23 positions


def test_epoch_order_is_a_seeded_permutation():
    a, b, c = epoch_order(1000, 7, 0), epoch_order(1000, 7, 0), epoch_order(1000, 7, 1)
    assert (a == b).all() and not (a == c).all() and sorted(a.tolist()) == list(range(1000))
    bs = list(batches(a, 256))
    assert [len(x) for x in bs] == [256, 256, 256, 232] and np.concatenate(bs).tolist() == a.tolist()
