"""Exposure quantities (docs/exposure-prereg-v0.1.md §1): H*, H_Q, KL, CE and g = H_Q − CE
for one window's exact next-KIND law and model logit row."""
import math
from fractions import Fraction

import numpy as np
import pytest

from yupi.corpus.vocab import KINDS, TOKEN_ID, VOCAB
from yupi.learner.evaluate import PAD_ID
from yupi.records import Record

R = lambda kind, actor: Record(kind=kind, actor=actor, obj=None, related=None, lineage=None)
STAR = {R("STEP", 0): Fraction(1, 2), R("RELEASE", 1): Fraction(1, 4), R("DISPATCH", 2): Fraction(1, 4)}


def _lp_from_kind_probs(q: dict, off: float = 0.0, pad: float = 0.0) -> np.ndarray:
    p = np.full(len(VOCAB), 1e-30)
    for k, v in q.items():
        p[TOKEN_ID[k]] = v * (1 - off)
    if off:
        p[TOKEN_ID["T0"] if "T0" in TOKEN_ID else next(i for i, t in enumerate(VOCAB) if t not in KINDS and i != PAD_ID)] = off
    p[PAD_ID] = pad
    p = p / p.sum()
    return np.log(p)


def test_model_equal_to_star_has_zero_kl_and_zero_g():
    from yupi.learner.exposure import kind_exposure
    e = kind_exposure(STAR, _lp_from_kind_probs({"STEP": .5, "RELEASE": .25, "DISPATCH": .25}))
    assert e["h_star"] == pytest.approx(1.5, abs=1e-9)
    assert e["h_q"] == pytest.approx(1.5, abs=1e-9)
    assert e["kl"] == pytest.approx(0.0, abs=1e-9) and e["g"] == pytest.approx(0.0, abs=1e-9)


def test_identity_and_sign_of_g_for_an_overconfident_model():
    from yupi.learner.exposure import kind_exposure
    q = {"STEP": .9, "RELEASE": .05, "DISPATCH": .05}
    e = kind_exposure(STAR, _lp_from_kind_probs(q))
    ce_direct = -sum(p * math.log2(q[k]) for k, p in [("STEP", .5), ("RELEASE", .25), ("DISPATCH", .25)])
    assert e["ce_direct"] == pytest.approx(ce_direct, abs=1e-9)
    assert e["identity_err"] < 1e-9                       # |H* + KL − CE_direct|
    assert e["h_q"] < e["h_star"] and e["g"] < 0           # sharper than the world, and than its own loss


def test_kl_matches_the_evaluator_convention_with_pad_and_off_kind_mass():
    """Q is renormalised over non-PAD only (evaluate.kind_output); KL equals kl_bits_vec(kind_belief, Q)."""
    from yupi.learner.evaluate import kind_belief, kind_output, kl_bits_vec
    from yupi.learner.exposure import kind_exposure
    rng = np.random.default_rng(1)
    logits = rng.normal(size=len(VOCAB)); logits[PAD_ID] = 3.0
    lp = logits - np.log(np.exp(logits).sum())
    e = kind_exposure(STAR, lp)
    q, off = kind_output(lp)
    assert e["kl_eval"] == pytest.approx(kl_bits_vec(kind_belief(STAR), q), abs=1e-12)
    assert e["off_kind_mass"] == pytest.approx(off, abs=1e-12)
    # on Q renormalised to the KINDS, KL differs from the evaluator's by exactly -log2(1 - off)
    assert e["kl_eval"] - e["kl"] == pytest.approx(-math.log2(1 - off), abs=1e-12)
    # H_Q is over the kind distribution renormalised to the KINDS (the telemetry a KIND reader sees)
    qn = q / q.sum()
    assert e["h_q"] == pytest.approx(float(-(qn[qn > 0] * np.log2(qn[qn > 0])).sum()), abs=1e-12)
