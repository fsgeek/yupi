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


def test_unscore_fields_drops_object_slot_targets_only():
    # 2026-10-13: the loss-masked relay arm. OBJECT is field 2 of each five-token record; a leading RESET shifts
    # the record grid by one. Only the named fields' target positions leave the mask; the end-of-window PAD stays.
    from yupi.learner.data import unscore_fields
    rec = [TOKEN_ID["DISPATCH"], TOKEN_ID["T03"], TOKEN_ID["NONE"], TOKEN_ID["NONE"], TOKEN_ID["NONE"]]
    w_reset = tuple([TOKEN_ID["RESET"]] + rec + rec)            # 11 tokens
    w_plain = tuple(rec + rec)                                  # 10 tokens
    x, y, m = frame([w_reset, w_plain])
    m2 = unscore_fields([w_reset, w_plain], m, ("OBJECT",))
    assert m.sum() == 12 + 11 and m2.sum() == 12 + 11 - 4      # two OBJECT slots per window removed
    assert not m2[0, 3] and not m2[0, 8] and m2[0, [0, 1, 2, 4, 5, 6, 7, 9, 10, 11]].all()
    assert not m2[1, 2] and not m2[1, 7] and m2[1, [0, 1, 3, 4, 5, 6, 8, 9, 10]].all()
    assert m2[0, 11] and m2[1, 10]                              # the end-of-window target is kept
    assert (unscore_fields([w_reset, w_plain], m, ()) == m).all()
    assert m.sum() == 23                                        # the input mask is not modified in place
    with pytest.raises(ValueError):
        unscore_fields([w_plain], m[1:], ("KIND", "NOPE"))


def test_paired_targets_accepts_object_only_differences_and_refuses_others():
    # 2026-10-13: the supervision-without-presence arm (r1 inputs, r1R targets). Targets may come from a paired corpus
    # only if the masks are identical and the token streams differ only at the named fields' slots.
    from yupi.learner.data import paired_targets
    a = [TOKEN_ID["DISPATCH"], TOKEN_ID["T03"], TOKEN_ID["MASKED"], TOKEN_ID["MASKED"], TOKEN_ID["MASKED"]]
    b = [TOKEN_ID["DISPATCH"], TOKEN_ID["T03"], TOKEN_ID["DISPATCH"], TOKEN_ID["MASKED"], TOKEN_ID["MASKED"]]
    _, ya, ma = frame([tuple(a + a)])
    _, yb, mb = frame([tuple(a + b)])
    y = paired_targets(ya, ma, yb, mb, ("OBJECT",))
    assert (y == yb).all() and y is not yb
    c = list(b); c[1] = TOKEN_ID["T04"]                       # an ACTOR difference
    _, yc, mc = frame([tuple(a + c)])
    with pytest.raises(ValueError):
        paired_targets(ya, ma, yc, mc, ("OBJECT",))
    _, yd, md = frame([tuple(a)])                              # a different length: masks differ
    with pytest.raises(ValueError):
        paired_targets(ya, ma, yd, md, ("OBJECT",))
    with pytest.raises(ValueError):                            # identical corpora: an r1 replicate mislabelled
        paired_targets(ya, ma, ya.copy(), ma, ("OBJECT",))
