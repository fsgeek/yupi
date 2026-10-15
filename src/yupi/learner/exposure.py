"""Exposure quantities for one window (docs/exposure-prereg-v0.1.md §1).

Given the exact next-KIND law P* of a window's class and the model's logit row at the
window's boundary, return the world's share H* = H(P*), the telemetry H_Q = H(Q), the
shortfall KL = KL(P* || Q), CE_direct = −Σ P* log2 Q, and g = H_Q − CE, so that
H_Q = H* + KL + g exactly.

Q is the model's KIND distribution renormalised over the KINDS. The evaluator's
kind_kl_bits renormalises over non-PAD only (evaluate.kind_output), leaving off-kind
mass; that KL is returned as kl_eval and equals kl − log2(1 − off_kind_mass).
Additive: nothing in evaluate.py changes.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict

import numpy as np

from yupi.learner.evaluate import kind_belief, kind_output, kl_bits_vec
from yupi.records import Record


def _h_bits(p: np.ndarray) -> float:
    m = p > 0
    return float(-(p[m] * np.log2(p[m])).sum())


def kind_exposure(star: Dict[Record, Fraction], lp_row: np.ndarray) -> dict:
    b = kind_belief(star)
    q_eval, off = kind_output(lp_row)
    q = q_eval / q_eval.sum()
    h_star, h_q, kl = _h_bits(b), _h_bits(q), kl_bits_vec(b, q)
    m = b > 0
    ce_direct = float(-(b[m] * np.log2(np.maximum(q[m], 1e-300))).sum())
    return dict(h_star=h_star, h_q=h_q, kl=kl, ce_direct=ce_direct, g=h_q - ce_direct,
                identity_err=abs(h_star + kl - ce_direct), kl_eval=kl_bits_vec(b, q_eval),
                off_kind_mass=off)
