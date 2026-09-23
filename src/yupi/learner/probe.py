"""Probe v0.1 — lock ownership in the residual stream (sub-project 3; design
docs/superpowers/specs/2026-09-23-probe-lock-owner-design.md; proposal §8.3).

  owner_posterior(joint_belief, l)  exact P*(Z | prefix) for pattern lock l from the
                                    filter's joint belief over (state, binding)
  fit_probe(A, P, l2)               affine A -> logits over CLASSES, minimizing the
                                    expected cross-entropy against soft labels P
                                    (+ L2), full-batch L-BFGS
  probe_ce(probe, A, P)             mean cross-entropy in bits on held-out (A, P)
  oir(ce, h_z, h_z_given_h)         (H(Z) − CE) / (H(Z) − H(Z | h)); None if undefined

Imports the exact side only through the belief structures it is handed.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, Optional

import numpy as np

CLASSES = ("none", "t0", "t1", "t2", "t3", "unseen", "invisible")
CLASS_ID = {c: i for i, c in enumerate(CLASSES)}
LOG2 = math.log(2.0)


def owner_posterior(joint_belief, l: int) -> Dict[str, Fraction]:
    """P*(owner of pattern lock l) from {(state, binding): mass}: binding[1][l] is
    the kernel lock, state.lock_owner[·] its kernel owner, binding[0] the pattern
    thread order; an owner outside binding[0] is "unseen", a lock index beyond
    the binding is "invisible"."""
    out: Dict[str, Fraction] = {}
    for (s, beta), m in joint_belief.items():
        if l >= len(beta[1]):
            z = "invisible"
        else:
            o = s.lock_owner[beta[1][l]]
            z = "none" if o is None else (f"t{beta[0].index(o)}" if o in beta[0] else "unseen")
        out[z] = out.get(z, Fraction(0)) + m
    return out


def fit_probe(A: np.ndarray, P: np.ndarray, l2: float = 1e-3, max_iter: int = 500) -> dict:
    """Multinomial logistic regression on soft labels: minimize mean_i −Σ_z P_iz log q_iz + l2·‖W‖²."""
    import torch
    X = torch.from_numpy(np.asarray(A, dtype=np.float64))
    Y = torch.from_numpy(np.asarray(P, dtype=np.float64))
    mu, sd = X.mean(0), X.std(0) + 1e-8
    Xn = (X - mu) / sd
    W = torch.zeros(X.shape[1], Y.shape[1], dtype=torch.float64, requires_grad=True)
    b = torch.zeros(Y.shape[1], dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], max_iter=max_iter, tolerance_grad=1e-9, tolerance_change=1e-12,
                            history_size=50, line_search_fn="strong_wolfe")
    def closure():
        opt.zero_grad()
        logq = torch.log_softmax(Xn @ W + b, dim=1)
        loss = -(Y * logq).sum(1).mean() + l2 * (W * W).sum()
        loss.backward()
        return loss
    opt.step(closure)
    return dict(W=W.detach().numpy(), b=b.detach().numpy(), mu=mu.numpy(), sd=sd.numpy(), l2=l2)


def probe_logq(probe: dict, A: np.ndarray) -> np.ndarray:
    Xn = (np.asarray(A, dtype=np.float64) - probe["mu"]) / probe["sd"]
    L = Xn @ probe["W"] + probe["b"]
    L = L - L.max(1, keepdims=True)
    return L - np.log(np.exp(L).sum(1, keepdims=True))


def probe_ce(probe: dict, A: np.ndarray, P: np.ndarray) -> float:
    """Mean over examples of −Σ_z P_z log2 q_z."""
    logq = probe_logq(probe, A)
    return float(-(np.asarray(P, dtype=np.float64) * logq).sum(1).mean() / LOG2)


def oir(ce: float, h_z: float, h_z_given_h: float) -> Optional[float]:
    denom = h_z - h_z_given_h
    if denom <= 1e-12:
        return None
    return (h_z - ce) / denom


def label_window(cfg, programs, law, rung: str, reset: bool, pw, beta) -> Dict[int, Dict[str, Fraction]]:
    """Exact owner posteriors for every lock visible in the pattern prefix `pw`
    (with binding `beta`), from the pattern filter run as a prefix."""
    from yupi.pattern_filter import filter_pattern_window
    post, _ = filter_pattern_window(cfg, programs, law, list(pw), rung, reset, prefix=True)
    joint = post.joint_marginal()
    return {l: owner_posterior(joint, l) for l in range(len(beta[1]))}


# ---- v0.2: readout in the model's coordinates (spec amendment 2026-09-23) --------------

NONE, UNSEEN = None, "unseen"


def _pack(A, cands, E):
    """Tensors for the bilinear readout: standardized activations, candidate
    embeddings [n, C, d] (zeros for non-token candidates), a mask [n, C], and
    indicator columns for the none / unseen candidates."""
    import torch
    n = len(cands)
    C = max(len(c) for c in cands)
    d = E.shape[1]
    emb = np.zeros((n, C, d)); mask = np.zeros((n, C), dtype=bool)
    is_none = np.zeros((n, C)); is_unseen = np.zeros((n, C)); is_tok = np.zeros((n, C))
    for i, c in enumerate(cands):
        for j, z in enumerate(c):
            mask[i, j] = True
            if z is NONE:
                is_none[i, j] = 1
            elif z == UNSEEN:
                is_unseen[i, j] = 1
            else:
                emb[i, j] = E[int(z)]; is_tok[i, j] = 1
    t = lambda x: torch.from_numpy(np.asarray(x, dtype=np.float64))
    return t(A), t(emb), torch.from_numpy(mask), t(is_none), t(is_unseen), t(is_tok)


def _bilinear_logq(W, V, b, X, emb, mask, is_none, is_unseen, is_tok):
    """Token candidates: (X W)·E_τ + b_tok; none / unseen: X·v + b, one learned direction each."""
    import torch
    h = X @ W                                                   # [n, d_E]
    nu = X @ V                                                  # [n, 2]
    logits = (torch.einsum("nd,ncd->nc", h, emb) + b[0] * is_tok
              + (nu[:, :1] + b[1]) * is_none + (nu[:, 1:] + b[2]) * is_unseen)
    logits = logits.masked_fill(~mask, -1e30)
    return torch.log_softmax(logits, dim=1)


def fit_bilinear(A, cands, P, E, l2: float = 1e-3, max_iter: int = 500) -> dict:
    """Minimize mean_i −Σ_j P_ij log q_ij + l2·‖W‖² over W [d, d_E] and b = (b_tok, b_none, b_unseen)."""
    import torch
    X, emb, mask, is_none, is_unseen, is_tok = _pack(A, cands, E)
    mu, sd = X.mean(0), X.std(0) + 1e-8
    Xn = (X - mu) / sd
    Y = torch.zeros(mask.shape, dtype=torch.float64)
    for i, p in enumerate(P):
        Y[i, :len(p)] = torch.from_numpy(np.asarray(p, dtype=np.float64))
    W = torch.zeros(X.shape[1], E.shape[1], dtype=torch.float64, requires_grad=True)
    V = torch.zeros(X.shape[1], 2, dtype=torch.float64, requires_grad=True)
    b = torch.zeros(3, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([W, V, b], max_iter=max_iter, tolerance_grad=1e-9, tolerance_change=1e-12,
                            history_size=50, line_search_fn="strong_wolfe")
    def closure():
        opt.zero_grad()
        logq = _bilinear_logq(W, V, b, Xn, emb, mask, is_none, is_unseen, is_tok)
        loss = -(Y * logq).sum(1).mean() + l2 * ((W * W).sum() + (V * V).sum())
        loss.backward()
        return loss
    opt.step(closure)
    return dict(W=W.detach().numpy(), V=V.detach().numpy(), b=b.detach().numpy(), mu=mu.numpy(), sd=sd.numpy(),
                l2=l2, readout="bilinear")


def bilinear_logq(probe: dict, A, cands, E) -> np.ndarray:
    import torch
    X, emb, mask, is_none, is_unseen, is_tok = _pack(A, cands, E)
    Xn = (X - torch.from_numpy(probe["mu"])) / torch.from_numpy(probe["sd"])
    with torch.no_grad():
        lq = _bilinear_logq(torch.from_numpy(probe["W"]), torch.from_numpy(probe["V"]), torch.from_numpy(probe["b"]),
                            Xn, emb, mask, is_none, is_unseen, is_tok)
    return lq.numpy()


def bilinear_ce(probe: dict, A, cands, P, E) -> float:
    lq = bilinear_logq(probe, A, cands, E)
    tot = 0.0
    for i, p in enumerate(P):
        p = np.asarray(p, dtype=np.float64)
        tot += -(p * lq[i, :len(p)]).sum()
    return float(tot / len(P) / LOG2)


# ---- v0.3: coordinate-free targets at the record boundary (2026-09-23) ------------------
#
# At the record-boundary position the residual stream does not carry entity
# identities in embedding coordinates (the actor token three positions back is
# unrecoverable there, though perfectly recoverable at its own position), so
# an entity-valued target cannot be read from a single position. These targets
# fold the owner posterior into facts that need no entity coordinates.

TARGETS = {
    "owner": CLASSES,
    "held": ("none", "held"),
    "owner-is-actor": ("none", "actor", "other"),
}


def collapse(p: np.ndarray, target: str, actor_index: int) -> np.ndarray:
    """Fold a posterior over CLASSES into the target's classes. `actor_index` is
    the pattern index of the record-k actor (for 'owner-is-actor')."""
    p = np.asarray(p, dtype=np.float64)
    if target == "owner":
        return p
    none = p[CLASS_ID["none"]]
    thr = {i: p[CLASS_ID[f"t{i}"]] for i in range(4)}
    unseen = p[CLASS_ID["unseen"]]
    if target == "held":
        return np.array([none, sum(thr.values()) + unseen])
    if target == "owner-is-actor":
        actor = thr.get(actor_index, 0.0)
        return np.array([none, actor, sum(thr.values()) - actor + unseen])
    raise ValueError(target)
