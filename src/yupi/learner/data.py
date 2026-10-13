"""Window corpus -> model tensors (trainer spec §2 'Sequence framing').

Input  [BOS] + window tokens, padded with PAD to seq_len;
target window tokens + [PAD] (the end-of-window event, contract §1 item 3);
mask   exactly len(window) + 1 positions scored per window.
BOS is a model-side input index (156 = len(VOCAB)); the output head is over
the 156 corpus tokens and never predicts BOS. One window per sequence; never
packed (design v0.1 §2). Imports from yupi only the corpus vocabulary and
reader: this module must not be able to see the exact side.
"""
from pathlib import Path

import numpy as np

from yupi.corpus.vocab import PAD, TOKEN_ID, VOCAB
from yupi.corpus.writer import read_split

BOS = len(VOCAB)          # 156
SEQ = 42                  # BOS + 41 (the frozen law's max_tokens)
PAD_ID = TOKEN_ID[PAD]    # 0


def frame(windows, seq_len: int = SEQ):
    n = len(windows)
    x = np.full((n, seq_len), PAD_ID, dtype=np.int64)
    y = np.full((n, seq_len), PAD_ID, dtype=np.int64)
    m = np.zeros((n, seq_len), dtype=bool)
    for i, w in enumerate(windows):
        L = len(w)
        if L > seq_len - 1:
            raise ValueError(f"window of {L} tokens needs {L + 1} positions; seq_len is {seq_len}")
        x[i, 0] = BOS
        x[i, 1:L + 1] = w
        y[i, :L] = w
        y[i, L] = PAD_ID                      # one end-of-window target
        m[i, :L + 1] = True
    return x, y, m


FIELDS = ("KIND", "ACTOR", "OBJECT", "RELATED", "LINEAGE")    # the five-token record (Part I D5)
RESET_ID = TOKEN_ID["RESET"]


def unscore_fields(windows, m, fields):
    """A copy of mask `m` with the target positions of the named record fields removed (2026-10-13: the
    loss-masked relay arm). Record grids start after a leading RESET. The end-of-window target is kept."""
    bad = [f for f in fields if f not in FIELDS]
    if bad:
        raise ValueError(f"unknown record fields {bad!r}; expected a subset of {FIELDS}")
    out = m.copy()
    slots = [FIELDS.index(f) for f in fields]
    for i, w in enumerate(windows):
        off = 1 if len(w) and w[0] == RESET_ID else 0
        for j in range(off, len(w)):
            if (j - off) % 5 in slots:
                out[i, j] = False
    return out


def paired_targets(y, m, y2, m2, fields):
    """Targets `y2` from a paired corpus, for training on inputs from another (2026-10-13: the supervision-without-
    presence arm). Refused unless the masks are identical and the target streams differ only at the named fields'
    slots."""
    if y.shape != y2.shape or not (m == m2).all():
        raise ValueError("paired corpora must have identical masks")
    slots = ~unscore_fields([y[i, :m[i].sum() - 1] for i in range(len(y))], m, fields) & m
    if ((y != y2) & m & ~slots).any():
        raise ValueError(f"paired corpora differ outside the fields {tuple(fields)}")
    if not ((y != y2) & slots).any():
        raise ValueError(f"paired targets never differ at {tuple(fields)}: is the target corpus the input corpus?")
    return y2.copy()


def load_split(corpus_dir, name: str, seq_len: int = SEQ):
    """(inputs, targets, mask, per-window table dicts) for a corpus split."""
    rows = read_split(Path(corpus_dir), name)
    x, y, m = frame([w for w, _ in rows], seq_len)
    return x, y, m, [t for _, t in rows]


def epoch_order(n: int, seed: int, epoch: int) -> np.ndarray:
    """A permutation of range(n) that is a function of (seed, epoch) alone."""
    return np.random.default_rng([seed, epoch]).permutation(n)


def batches(order: np.ndarray, batch_size: int):
    for i in range(0, len(order), batch_size):
        yield order[i:i + batch_size]
