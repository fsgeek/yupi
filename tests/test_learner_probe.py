"""Probe v0.1 (docs/superpowers/specs/2026-09-23-probe-lock-owner-design.md):
the exact owner label from a joint belief over (state, binding), and the
linear probe with its OIR gates."""
import dataclasses
import math
from fractions import Fraction

import numpy as np
import pytest

pytest.importorskip("torch")

from yupi.state import WorldConfig, initial_state
from yupi.learner.probe import CLASSES, fit_probe, oir, owner_posterior, probe_ce


def _cfg():
    return WorldConfig.c1(p=Fraction(1, 2), queue_depth=2, epsilon=Fraction(1))


def test_owner_posterior_maps_kernel_owner_through_the_binding():
    cfg = _cfg()
    s0 = initial_state(cfg)
    s_t2 = dataclasses.replace(s0, lock_owner=(None, 2))      # kernel lock 1 owned by kernel thread 2
    s_t3 = dataclasses.replace(s0, lock_owner=(None, 3))      # ... by kernel thread 3 (not in the binding)
    beta = ((2, 0), (1,), (), ())                             # pattern t0 = kernel 2, t1 = kernel 0; pattern lock 0 = kernel lock 1
    belief = {(s_t2, beta): Fraction(1, 2), (s_t3, beta): Fraction(1, 4), (s0, beta): Fraction(1, 4)}
    d = owner_posterior(belief, 0)
    assert d == {"t0": Fraction(1, 2), "unseen": Fraction(1, 4), "none": Fraction(1, 4)}
    assert sum(d.values()) == 1
    assert owner_posterior(belief, 1) == {"invisible": Fraction(1)}
    assert set(CLASSES) >= set(d)


def _synthetic(n, d, seed, encode: bool):
    """Posteriors over 6 classes from a random logit model; activations that
    either carry those logits linearly (plus noise dims) or are independent."""
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(n, d))
    W = rng.normal(size=(d, len(CLASSES)))
    logits = Z @ W
    P = np.exp(logits - logits.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
    A = np.concatenate([Z, rng.normal(size=(n, 4))], 1) if encode else rng.normal(size=(n, d + 4))
    return A, P


def test_probe_recovers_a_linearly_encoded_posterior_and_not_an_independent_one():
    A, P = _synthetic(4000, 8, 1, encode=True)
    At, Pt = _synthetic(2000, 8, 2, encode=True)
    # the same W must generate both: regenerate with a shared rng draw
    rng = np.random.default_rng(7)
    Z, Zt = rng.normal(size=(4000, 8)), rng.normal(size=(2000, 8))
    W = rng.normal(size=(8, len(CLASSES)))
    def post(Zs):
        L = Zs @ W; Pp = np.exp(L - L.max(1, keepdims=True)); return Pp / Pp.sum(1, keepdims=True)
    P, Pt = post(Z), post(Zt)
    A = np.concatenate([Z, rng.normal(size=(4000, 4))], 1); At = np.concatenate([Zt, rng.normal(size=(2000, 4))], 1)
    probe = fit_probe(A, P, l2=1e-4)
    ce = probe_ce(probe, At, Pt)
    h_z = -float(np.sum(Pt.mean(0) * np.log2(Pt.mean(0) + 1e-300)))
    h_z_h = float(np.mean(-np.sum(Pt * np.log2(Pt + 1e-300), 1)))
    r = oir(ce, h_z, h_z_h)
    assert h_z - h_z_h > 0.3                                    # there is information to recover
    assert r > 0.95, (ce, h_z, h_z_h, r)
    A_ind = rng.normal(size=(4000, 12)); At_ind = rng.normal(size=(2000, 12))
    probe0 = fit_probe(A_ind, P, l2=1e-2)
    r0 = oir(probe_ce(probe0, At_ind, Pt), h_z, h_z_h)
    assert r0 < 0.05, r0
    assert probe_ce(probe0, At_ind, Pt) >= h_z - 0.01              # no better than the constant probe


def test_oir_edges():
    assert oir(ce=1.0, h_z=1.0, h_z_given_h=0.0) == 0.0
    assert oir(ce=0.2, h_z=1.0, h_z_given_h=0.2) == pytest.approx(1.0)
    assert oir(ce=0.5, h_z=1.0, h_z_given_h=1.0) is None           # undefined: the trace carries nothing


@pytest.fixture(scope="module")
def tiny_r2():
    import json, tempfile
    from yupi.corpus.manifest import Manifest, Split
    from yupi.corpus.writer import generate
    root = tempfile.mkdtemp(prefix="yupi-probe-")
    m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r2", run_key=b"\x05" * 32,
                     splits=(Split("train", 0, 16), Split("val", 1_000_000, 1_000_016), Split("test", 2_000_000, 2_000_200)),
                     git_commit="test")
    d, _ = generate(m, root, workers=2)
    return m, d


def test_label_window_gates(tiny_r2):
    """Per visible lock the masses sum to 1; a prefix holding ACQUIRE(t, l) with no
    later RELEASE(·, l) or BLOCK(·, l) by another owner leaves P*(owner = t) = 1;
    a lock that has not appeared is not labeled."""
    from yupi.corpus.vocab import VOCAB
    from yupi.corpus.writer import read_split
    from yupi.learner.evaluate import surface_records
    from yupi.learner.probe import label_window
    from yupi.naming import pattern_all
    m, d = tiny_r2
    cfg, progs = m.world(); law = m.law()
    n_checked = n_acq = 0
    for w, _ in read_split(d, "test")[:120]:
        reset, recs = surface_records(tuple(VOCAB[t] for t in w))
        for k in (1, 2, 3):
            if k > len(recs):
                continue
            pw, beta = pattern_all(recs[:k])
            labels = label_window(cfg, progs, law, m.rung, reset, pw, beta)
            assert set(labels) == set(range(len(beta[1])))
            for l, post in labels.items():
                assert sum(post.values()) == 1 and "invisible" not in post
                n_checked += 1
                # last lock event on l in the prefix
                last = [r for r in pw if r.obj == ("LOCK", l)]
                if last and last[-1].kind == "ACQUIRE":
                    assert post == {f"t{last[-1].actor}": Fraction(1)}, (pw, l, post)
                    n_acq += 1
    assert n_checked > 20 and n_acq > 3


def test_bilinear_readout_recovers_a_token_coded_posterior():
    """fit_bilinear(A, cands, P, E): logit(τ) = A W E_τ + b_tok, plus scalars for the
    two non-token classes; softmax restricted to each example's candidate set. On
    synthetic data where A = E_owner + noise (the owner's embedding is in the
    activation), OIR → 1; on independent A, OIR → 0."""
    from yupi.learner.probe import fit_bilinear, bilinear_ce
    rng = np.random.default_rng(3)
    d, n_tok = 16, 20
    E = rng.normal(size=(n_tok, d))
    def make(n, encode):
        cands, P, A = [], [], []
        for _ in range(n):
            toks = list(rng.choice(n_tok, size=4, replace=False))
            c = [None, "unseen"] + toks               # candidate set: none, unseen, then tokens
            p = np.zeros(len(c)); j = rng.integers(len(c)); p[j] = 1.0   # hard label: the owner
            owner = c[j]
            vec = (E[owner] if isinstance(owner, (int, np.integer)) else (np.ones(d) if owner == "unseen" else -np.ones(d)))
            A.append(vec + 0.3 * rng.normal(size=d) if encode else rng.normal(size=d))
            cands.append(c); P.append(p)
        return np.array(A), cands, P
    A, C, P = make(3000, True); At, Ct, Pt = make(1500, True)
    pr = fit_bilinear(A, C, P, E, l2=1e-4)
    ce = bilinear_ce(pr, At, Ct, Pt, E)
    # H(Z): marginal over the candidate *positions* is not meaningful across sets; use per-example uniform baseline
    base = float(np.mean([math.log2(len(c)) for c in Ct]))
    h_given = float(np.mean([-(p[p > 0] * np.log2(p[p > 0])).sum() for p in Pt]))
    assert h_given == 0.0 and ce < 0.3, (ce, base)                   # the owner's embedding is read out
    A0, C0, P0 = make(3000, False); At0, Ct0, Pt0 = make(1500, False)
    pr0 = fit_bilinear(A0, C0, P0, E, l2=1e-2)
    assert bilinear_ce(pr0, At0, Ct0, Pt0, E) > base - 0.1
