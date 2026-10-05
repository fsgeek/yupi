"""The canonicalize-and-count KIND baseline (docs/count-baseline-design-v0.1.md §3 gates), on the evaluator's
generated C1 (8,4,2) test corpus with its exact prefix ceiling tables.

  1. EXACTNESS: counts filled from the tables' exact law (mass × P*), read without smoothing, give KIND excess
     (by_field.kind and kind_kl_bits) exactly 0 on every scored window. This checks canonicalization, the position
     plumbing and the renormalization together.
  2. VALID ROWS: every KIND row log-sum-exps to 0 over non-PAD tokens, with all mass on KIND tokens.
  3. NAME INVARIANCE: renaming a window's entity tokens (a consistent pool permutation) leaves every predicted
     KIND row unchanged.
"""
from fractions import Fraction

import numpy as np
import pytest

from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.vocab import ENTITY_TYPES, KINDS, PAD, TOKEN_ID, VOCAB, pool_tokens, token_type
from yupi.corpus.writer import generate, read_split
from yupi.learner.count_baseline import CountKind
from yupi.learner.data import frame
from yupi.learner.evaluate import evaluate, surface_records
from yupi.pattern_ceiling import ceiling_table

K_LIST = (1, 2, 3)
SEQ = 22


@pytest.fixture(scope="module")
def corpus():
    import tempfile
    root = tempfile.mkdtemp(prefix="yupi-count-")
    m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r4", run_key=b"\x03" * 32,
                     splits=(Split("train", 0, 400), Split("val", 1_000_000, 1_000_016), Split("test", 2_000_000, 2_000_300)),
                     git_commit="test")
    d, _ = generate(m, root, workers=2)
    cfg, progs = m.world()
    tables = {k: ceiling_table(cfg, progs, m.law(), (m.rung,), prefix_len=k)[m.rung] for k in K_LIST}
    return m, d, tables


def test_exact_law_counts_give_zero_kind_excess(corpus):
    m, d, tables = corpus
    model = CountKind.from_tables(tables, rung=m.rung)
    r = evaluate(model.logprobs_fn(mode="mle"), d, m.law(), tables, K_LIST, SEQ)
    for k in K_LIST:
        pk = r["per_k"][k]
        assert pk["missing_classes"] == 0 and pk["kind_kl_bits"]["n"] > 50, (k, pk)
        assert abs(pk["kind_kl_bits"]["mean"]) < 1e-9 and pk["kind_kl_bits"]["sd"] < 1e-9, (k, pk["kind_kl_bits"])
        kb = pk["structural_by_field"]["kind"]
        assert abs(kb["mean"]) < 1e-9 and kb["sd"] < 1e-9, (k, kb)


def _windows(d, split):
    return [tuple(VOCAB[t] for t in w) for w, _ in read_split(d, split)]


@pytest.fixture(scope="module")
def trained(corpus):
    m, d, _ = corpus
    model = CountKind(rung=m.rung)
    for w in _windows(d, "train"):
        model.add_window(w)
    return model


def _kind_rows(model, windows, mode):
    x, _, _ = frame([tuple(TOKEN_ID[t] for t in w) for w in windows], SEQ)
    lp = model.logprobs_fn(mode=mode)(x)
    out = []
    for i, w in enumerate(windows):
        reset, recs = surface_records(w, model.rung)
        off = 1 if reset else 0
        out.append(np.stack([lp[i, off + 5 * k] for k in range(len(recs))]))
    return out


@pytest.mark.parametrize("mode", ["wb", "add"])
def test_kind_rows_are_valid(corpus, trained, mode):
    m, d, _ = corpus
    kind_ids = [TOKEN_ID[k] for k in KINDS]
    for rows in _kind_rows(trained, _windows(d, "test")[:100], mode):
        for row in rows:
            nonpad = np.delete(row, TOKEN_ID[PAD])
            assert abs(np.logaddexp.reduce(nonpad)) < 1e-9
            assert abs(np.logaddexp.reduce(row[kind_ids])) < 1e-9


def test_predictions_are_invariant_to_entity_names(corpus, trained):
    m, d, _ = corpus
    windows = _windows(d, "test")[:100]
    perm = {}
    for et in ENTITY_TYPES:
        pool = list(pool_tokens(et)) if et in {token_type(t) for w in windows for t in w} else []
        perm.update(dict(zip(pool, pool[::-1])))
    renamed = [tuple(perm.get(t, t) for t in w) for w in windows]
    assert renamed != windows
    for a, b in zip(_kind_rows(trained, windows, "wb"), _kind_rows(trained, renamed, "wb")):
        np.testing.assert_allclose(a, b, atol=1e-12)
