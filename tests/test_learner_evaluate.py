"""The evaluator (contract v0.1.2; plan Task 6) on a generated C1 (8,4,2)
corpus with its exact prefix ceiling tables.

  1. A SYNTHETIC BAYES model — whose softmax at every field position is the
     exact field conditional P*(· | Π-prefix, realized earlier fields) spread
     uniformly over the consistent tokens, with the end-of-window term from
     pattern_end_probability — has structural, naming, kind-KL and end
     excess exactly 0 (to 1e-9) at every k on every test window.
  2. A UNIFORM model's token excess equals log2(155) + 4·log2(156) minus the
     mean ceiling token cost (the KIND field is scored given continuation).
  3. On any model, structural + naming == token per window (algebraic identity)
     and the kind KL is non-negative.
  4. Every test window's class is present in the table (no missing classes).
"""
import math
from fractions import Fraction

import numpy as np
import pytest

pytest.importorskip("torch")

from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.vocab import ENTITY_TYPES, KINDS, PAD, RESET, TOKEN_ID, VOCAB, token_type
from yupi.corpus.writer import generate, read_split
from yupi.learner.data import BOS
from yupi.learner.evaluate import DRAWABLE, evaluate, surface_records
from yupi.naming import pattern_all
from yupi.pattern_ceiling import ceiling_table
from yupi.pattern_filter import pattern_end_probability
from yupi.records import Record

K_LIST = (1, 2, 3)
SEQ = 22


@pytest.fixture(scope="module")
def corpus():
    import tempfile
    root = tempfile.mkdtemp(prefix="yupi-eval-")
    m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r4", run_key=b"\x02" * 32,
                     splits=(Split("train", 0, 64), Split("val", 1_000_000, 1_000_016), Split("test", 2_000_000, 2_000_300)),
                     git_commit="test")
    d, _ = generate(m, root, workers=2)
    cfg, progs = m.world()
    tables = {k: ceiling_table(cfg, progs, m.law(), (m.rung,), prefix_len=k)[m.rung] for k in K_LIST}
    return m, d, tables


def _decode(row):
    toks = []
    for t in row[1:]:
        if t == TOKEN_ID[PAD]:
            break
        toks.append(VOCAB[t])
    return tuple(toks)


class SyntheticBayes:
    """log-softmax rows that ARE the exact field conditionals, token-spread."""

    def __init__(self, tables, law):
        self.tables, self.law = tables, law

    def _field_dist(self, star, recs_k, partial, rho, j):
        """{token: prob} for field j given the realized earlier fields of the
        record: candidates filtered by the realized PATTERN values (rho), the
        token mapping from the binding extended by the realized tokens (partial)."""
        f = ("kind", "actor", "obj", "related", "lineage")[j]
        cands = list(star.items())
        for g in ("kind", "actor", "obj", "related", "lineage")[:j]:
            v = getattr(rho, g)
            cands = [(r, m) for r, m in cands if getattr(r, g) == v]
        den = sum((m for _, m in cands), Fraction(0))
        _, ext = pattern_all(recs_k + (partial,))                  # binding extended by the realized earlier fields
        by_value = {}
        for r, m in cands:
            v = getattr(r, f)
            by_value[v] = by_value.get(v, Fraction(0)) + m / den
        out = {}
        for v, p in by_value.items():
            if v is None:
                out["NONE"] = out.get("NONE", 0.0) + float(p)
            elif v == "MASKED":
                out["MASKED"] = out.get("MASKED", 0.0) + float(p)
            elif f == "kind":
                out[v] = out.get(v, 0.0) + float(p)
            else:
                if f == "obj":
                    tag, idx = v
                    et = "lock" if tag == "LOCK" else "device"
                else:
                    idx = v
                    et = "thread" if f in ("actor", "related") else "request"
                order = ext[("thread", "lock", "device", "request").index(et)]
                if idx < len(order):
                    tok = order[idx]
                    out[tok] = out.get(tok, 0.0) + float(p)
                else:                                                # fresh: uniform over drawable unused
                    unused = sorted(DRAWABLE[et] - set(order))
                    for tok in unused:
                        out[tok] = out.get(tok, 0.0) + float(p) / len(unused)
        return out

    def __call__(self, x):
        N, T = x.shape
        lp = np.full((N, T, len(VOCAB)), -math.log(len(VOCAB)))   # uniform where nothing is defined (position 0)
        for i in range(N):
            toks = _decode(x[i])
            reset, recs = surface_records(toks)
            off = 1 if reset else 0
            for k in range(1, len(recs)):                            # positions predicting record k (k records seen)
                pw, _ = pattern_all(recs[:k])
                if (reset, pw) not in self.tables.get(k, {}):
                    continue
                _, star = self.tables[k][(reset, pw)]
                p_end = float(pattern_end_probability(self.law, k, reset))
                real = recs[k]
                rho = pattern_all(recs[:k + 1])[0][-1]
                for j in range(5):
                    fields = [getattr(real, g) for g in ("kind", "actor", "obj", "related", "lineage")]
                    partial = Record(*(fields[:j] + [None] * (5 - j)))
                    dist = self._field_dist(star, recs[:k], partial, rho, j)
                    row = np.full(len(VOCAB), 1e-300)
                    scale = (1.0 - p_end) if j == 0 else 1.0
                    for tok, p in dist.items():
                        row[TOKEN_ID[tok]] = p * scale
                    if j == 0:
                        row[TOKEN_ID[PAD]] = p_end
                    lp[i, off + 5 * k + j] = np.log(np.maximum(row, 1e-300))
            # the final boundary: end with the exact probability
            n_rec = len(recs)
            p_end = float(pattern_end_probability(self.law, n_rec, reset))
            row = np.full(len(VOCAB), (1.0 - p_end) / (len(VOCAB) - 1) if p_end < 1 else 1e-300)
            row[TOKEN_ID[PAD]] = max(p_end, 1e-300)
            lp[i, off + 5 * n_rec] = np.log(row)
        return lp


def test_synthetic_bayes_has_zero_excess(corpus):
    m, d, tables = corpus
    r = evaluate(SyntheticBayes(tables, m.law()), d, m.law(), tables, K_LIST, SEQ)
    assert r["n_windows"] == 300
    for k in K_LIST:
        pk = r["per_k"][k]
        assert pk["missing_classes"] == 0 and pk["structural_bits"]["n"] > 50, (k, pk)
        for key in ("structural_bits", "naming_bits", "token_bits", "kind_kl_bits", "end_bits"):
            assert abs(pk[key]["mean"]) < 1e-9 and pk[key]["sd"] < 1e-9, (k, key, pk[key])
        assert pk["identity_max_abs"] < 1e-9
    assert abs(r["final_end_bits"]["mean"]) < 1e-9


def test_uniform_model_excess_is_the_entropy_gap(corpus):
    m, d, tables = corpus
    uniform = lambda x: np.full(x.shape + (len(VOCAB),), -math.log(len(VOCAB)))
    r = evaluate(uniform, d, m.law(), tables, K_LIST, SEQ)
    for k in K_LIST:
        pk = r["per_k"][k]
        expect = math.log2(155) + 4 * math.log2(156) - pk["ceiling_token_bits"]["mean"]
        assert abs(pk["token_bits"]["mean"] - expect) < 1e-9
        assert pk["identity_max_abs"] < 1e-9 and pk["kind_kl_bits"]["mean"] >= 0
        assert pk["structural_bits"]["mean"] > 0 and pk["naming_bits"]["mean"] > 0


def test_random_model_identity_and_nonnegative_kind_kl(corpus):
    m, d, tables = corpus
    rng = np.random.default_rng(0)
    def noisy(x):
        z = rng.normal(size=x.shape + (len(VOCAB),)) * 2.0
        z -= z.max(-1, keepdims=True)
        return z - np.log(np.exp(z).sum(-1, keepdims=True))
    r = evaluate(noisy, d, m.law(), tables, K_LIST, SEQ)
    for k in K_LIST:
        pk = r["per_k"][k]
        assert pk["identity_max_abs"] < 1e-9 and pk["kind_kl_bits"]["mean"] >= 0 and pk["missing_classes"] == 0


def test_surface_records_pattern_equals_structural_pattern(corpus):
    """Π on surface tokens == Π on the structural projected records (σ-invariance)."""
    from yupi.corpus.rendering import EpisodeTable
    from yupi.corpus.windows import deserialize
    m, d, tables = corpus
    for toks, tab in read_split(d, "test")[:100]:
        surf = tuple(VOCAB[t] for t in toks)
        reset_s, recs_s = surface_records(surf)
        reset_t, recs_t = deserialize(surf, EpisodeTable.from_json(tab))
        assert reset_s == reset_t and pattern_all(recs_s)[0] == pattern_all(recs_t)[0]
