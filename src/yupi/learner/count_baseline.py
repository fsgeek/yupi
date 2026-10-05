"""The canonicalize-and-count KIND baseline (docs/count-baseline-design-v0.1.md).

A learner with no weights. A prefix of k records is canonicalized to its pattern class (reset flag,
Π_all(records[:k])), which is exactly the ceiling tables' key, and the KIND of record k + 1 is counted under it.
It is also counted under the backoff classes "pattern of the last m records" (m = 1 .. min(k − 1, max_order))
and unconditionally. Prediction modes:

  mle  the full class's relative frequencies, with no smoothing (for the exactness gate; unseen → uniform)
  wb   Witten–Bell interpolation up the chain unigram(add-one) → m = 1 → … → full class
  add  add-α on the full class (α chosen on val by the caller), backing off to wb for unseen classes

`logprobs_fn(mode)` satisfies the evaluator contract (inputs [N, seq_len] → [N, seq_len, |VOCAB|] log-probs).
Only the KIND positions (off + 5k) carry the learner's prediction: KIND tokens hold log P(kind), PAD holds
log 1/2 (a fixed continue/end guess), other tokens hold −1e30. Every other position is uniform. **Only
by_field.kind and kind_kl_bits are meaningful for this learner.**
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, Optional

import numpy as np

from yupi.corpus.vocab import KINDS, PAD, TOKEN_ID, VOCAB
from yupi.learner.evaluate import surface_records
from yupi.naming import pattern_all

_KIND_IDS = np.array([TOKEN_ID[k] for k in KINDS])
_KIDX = {k: i for i, k in enumerate(KINDS)}
_NK = len(KINDS)
_NEG = -1e30


class CountKind:
    def __init__(self, rung: Optional[str] = None, max_order: int = 6, alpha: float = 0.5):
        self.rung = rung
        self.max_order = max_order
        self.alpha = alpha
        self.full: Dict[tuple, np.ndarray] = defaultdict(lambda: np.zeros(_NK))
        self.suffix: Dict[tuple, np.ndarray] = defaultdict(lambda: np.zeros(_NK))
        self.uni = np.zeros(_NK)

    # ---- counting -----------------------------------------------------------------------
    def add_window(self, tokens) -> None:
        reset, recs = surface_records(tokens, self.rung)
        for k in range(len(recs)):
            j = _KIDX[recs[k].kind]
            self.full[(reset, pattern_all(recs[:k])[0])][j] += 1
            for m in range(1, min(k - 1, self.max_order) + 1):
                self.suffix[(m, pattern_all(recs[k - m:k])[0])][j] += 1
            self.uni[j] += 1

    @classmethod
    def from_tables(cls, tables, rung: Optional[str] = None) -> "CountKind":
        """Counts ∝ the exact law: for each k-table class, mass × P*(kind) (the exactness gate)."""
        model = cls(rung=rung)
        for table in tables.values():
            for key, (mass, star) in table.items():
                c = model.full[key]
                for rec, p in star.items():
                    c[_KIDX[rec.kind]] += float(mass) * float(p)
        return model

    # ---- prediction ---------------------------------------------------------------------
    def kind_dist(self, reset: bool, recs, mode: str) -> np.ndarray:
        k = len(recs)
        full = self.full.get((reset, pattern_all(recs)[0]))
        if mode == "mle":
            return full / full.sum() if full is not None and full.sum() > 0 else np.full(_NK, 1.0 / _NK)
        if mode == "add" and full is not None and full.sum() > 0:
            return (full + self.alpha) / (full.sum() + self.alpha * _NK)
        p = (self.uni + 1.0) / (self.uni.sum() + _NK)
        chain = [self.suffix.get((m, pattern_all(recs[k - m:])[0])) for m in range(1, min(k - 1, self.max_order) + 1)]
        chain.append(full)
        for c in chain:
            if c is None:
                continue
            n = c.sum()
            if n <= 0:
                continue
            t = float((c > 0).sum())
            p = (c + t * p) / (n + t)
        return p

    def logprobs_fn(self, mode: str = "wb"):
        V = len(VOCAB)
        pad_id = TOKEN_ID[PAD]

        def fn(x: np.ndarray) -> np.ndarray:
            n, s = x.shape
            out = np.full((n, s, V), -math.log(V))
            for i in range(n):
                toks = []
                for t in x[i, 1:]:
                    if t == pad_id:
                        break
                    toks.append(VOCAB[t])
                reset, recs = surface_records(tuple(toks), self.rung)
                off = 1 if reset else 0
                for k in range(len(recs) + 1):
                    pos = off + 5 * k
                    if pos >= s:
                        break
                    row = np.full(V, _NEG)
                    row[_KIND_IDS] = np.log(np.maximum(self.kind_dist(reset, recs[:k], mode), 1e-300))
                    row[pad_id] = math.log(0.5)
                    out[i, pos] = row
            return out
        return fn
