"""The evaluator and census on the relay rung r1ʀ ("r1R", relay design v0.1 §2;
relay pre-registration v0.1 "Frozen analysis").

  1. surface_records: with the rung given, a KIND token in the OBJECT slot is an
     `interfaces.Lit` at r1R and an error at any other rung; with no rung (the frozen
     bintest's call) it is read as a Lit, which is the only reading a KIND token in
     that slot has in any corpus.
  2. evaluate() takes the rung from the corpus manifest; a caller's rung that
     disagrees with it is refused.
  3. On a paired r1 / r1R corpus (same manifest but the rung) at (8, 4, 2): a model
     that ignores the relay slot has a KIND excess on every r1R window identical to its
     KIND excess on the paired r1 window (the ceiling is identical per class), and a
     relay field reported as its own field "relay" (not "obj", never in "kind").
     The exact-ceiling model has zero excess in every field at r1R. Values pinned.
"""
import math
import zlib
from fractions import Fraction

import numpy as np
import pytest

pytest.importorskip("torch")

from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.vocab import KINDS, MASKED, PAD, RESET, TOKEN_ID, VOCAB
from yupi.corpus.writer import generate, read_split
from yupi.interfaces import Lit, drop_relay
from yupi.learner.census import summarize
from yupi.learner.evaluate import DRAWABLE, evaluate, surface_records
from yupi.naming import pattern_all
from yupi.pattern_ceiling import ceiling_table
from yupi.pattern_filter import pattern_end_probability
from yupi.records import Record

K_LIST = (1, 2, 3)
SEQ = 22
KEY = bytes(range(32))
REC_FIELDS = ("kind", "actor", "obj", "related", "lineage")
KIND_TOKEN_IDS = {TOKEN_ID[k] for k in KINDS}


@pytest.fixture(scope="module")
def pair(tmp_path_factory):
    root = tmp_path_factory.mktemp("relay-eval")
    out = {}
    for rung in ("r1", "r1R"):
        m = Manifest.new(programs="c1prime-loop", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung=rung, run_key=KEY,
                         splits=(Split("train", 0, 16), Split("test", 2_000_000, 2_000_200)), git_commit="t")
        out[rung], _ = generate(m, root, workers=1)
    cfg, progs = m.world()
    law = m.law()
    tabs = {k: ceiling_table(cfg, progs, law, ("r1", "r1R"), prefix_len=k) for k in K_LIST}
    tables = {rung: {k: tabs[k][rung] for k in K_LIST} for rung in ("r1", "r1R")}
    return out, tables, law


def _decode(row):
    toks = []
    for t in row[1:]:
        if t == TOKEN_ID[PAD]:
            break
        toks.append(VOCAB[t])
    return tuple(toks)


def relay_blind(x):
    """A causal pseudo-model whose row at position p is a fixed function of the input
    prefix x[:p+1] with every OBJECT-slot token (r1: MASKED; r1R: the relay) replaced by MASKED:
    on paired r1 / r1R inputs it produces identical rows at every position."""
    N, T = x.shape
    out = np.empty((N, T, len(VOCAB)))
    for i in range(N):
        xm = x[i].copy()
        off = 2 if x[i, 1] == TOKEN_ID[RESET] else 1                 # BOS [RESET] records...
        for p in range(off + 2, T, 5):
            if xm[p] != TOKEN_ID[PAD]:                               # r1: MASKED; r1R: a KIND or NONE
                xm[p] = TOKEN_ID[MASKED]
        for p in range(T):
            rng = np.random.default_rng(zlib.crc32(xm[:p + 1].astype("<u2").tobytes()))
            z = rng.normal(size=len(VOCAB)) * 1.5
            z -= z.max()
            out[i, p] = z - np.log(np.exp(z).sum())
    return out


class RelayBayes:
    """log-softmax rows that ARE the exact field conditionals at r1R (the relay
    field's value is a Lit, rendered as its KIND token)."""

    def __init__(self, tables, law):
        self.tables, self.law = tables, law

    def _field_dist(self, star, recs_k, partial, rho, j):
        f = REC_FIELDS[j]
        cands = list(star.items())
        for g in REC_FIELDS[:j]:
            v = getattr(rho, g)
            cands = [(r, m) for r, m in cands if getattr(r, g) == v]
        den = sum((m for _, m in cands), Fraction(0))
        _, ext = pattern_all(recs_k + (partial,))
        by_value = {}
        for r, m in cands:
            v = getattr(r, f)
            by_value[v] = by_value.get(v, Fraction(0)) + m / den
        out = {}
        for v, p in by_value.items():
            if v is None:
                tok = "NONE"
            elif v == "MASKED":
                tok = "MASKED"
            elif isinstance(v, Lit):
                tok = v.kind
            elif f == "kind":
                tok = v
            else:
                assert f == "actor", (f, v)
                order = ext[0]
                if v < len(order):
                    tok = order[v]
                else:
                    unused = sorted(DRAWABLE["thread"] - set(order))
                    for t in unused:
                        out[t] = out.get(t, 0.0) + float(p) / len(unused)
                    continue
            out[tok] = out.get(tok, 0.0) + float(p)
        return out

    def __call__(self, x):
        N, T = x.shape
        lp = np.full((N, T, len(VOCAB)), -math.log(len(VOCAB)))
        for i in range(N):
            toks = _decode(x[i])
            reset, recs = surface_records(toks, "r1R")
            off = 1 if reset else 0
            for k in range(1, len(recs)):
                pw, _ = pattern_all(recs[:k])
                if (reset, pw) not in self.tables.get(k, {}):
                    continue
                _, star = self.tables[k][(reset, pw)]
                p_end = float(pattern_end_probability(self.law, k, reset))
                real = recs[k]
                rho = pattern_all(recs[:k + 1])[0][-1]
                for j in range(5):
                    fields = [getattr(real, g) for g in REC_FIELDS]
                    partial = Record(*(fields[:j] + [None] * (5 - j)))
                    dist = self._field_dist(star, recs[:k], partial, rho, j)
                    row = np.full(len(VOCAB), 1e-300)
                    scale = (1.0 - p_end) if j == 0 else 1.0
                    for tok, p in dist.items():
                        row[TOKEN_ID[tok]] = p * scale
                    if j == 0:
                        row[TOKEN_ID[PAD]] = p_end
                    lp[i, off + 5 * k + j] = np.log(np.maximum(row, 1e-300))
            n_rec = len(recs)
            p_end = float(pattern_end_probability(self.law, n_rec, reset))
            row = np.full(len(VOCAB), (1.0 - p_end) / (len(VOCAB) - 1) if p_end < 1 else 1e-300)
            row[TOKEN_ID[PAD]] = max(p_end, 1e-300)
            lp[i, off + 5 * n_rec] = np.log(row)
        return lp


# ---- 1. surface_records -------------------------------------------------------------

R1R_TOKS = ("STEP", "T3", "NONE", "MASKED", "MASKED", "BLOCK", "T3", "STEP", "MASKED", "MASKED")


def _thread_tokens(n):
    from yupi.corpus.vocab import token_type
    return [t for t in VOCAB if token_type(t) == "thread"][:n]


def test_surface_records_reads_the_relay_as_a_literal_only_at_the_relay_rung():
    a = _thread_tokens(1)[0]
    toks = tuple(a if t == "T3" else t for t in R1R_TOKS)
    reset, recs = surface_records(toks, "r1R")
    assert not reset and recs[0].obj is None and recs[1].obj == Lit("STEP")
    assert surface_records(toks) == (reset, recs)                 # the frozen bintest's call (no rung)
    with pytest.raises(ValueError):
        surface_records(toks, "r1")
    with pytest.raises(ValueError):
        surface_records(toks, "r4")
    from yupi.corpus.vocab import token_type
    lock = next(t for t in VOCAB if token_type(t) == "lock")
    bad = toks[:7] + (lock,) + toks[8:]
    with pytest.raises(ValueError):
        surface_records(bad, "r1R")                               # an entity in the relay slot
    # non-relay rungs: unchanged reading
    r4 = ("ACQUIRE", a, lock, "NONE", "NONE")
    assert surface_records(r4, "r4") == surface_records(r4)
    assert surface_records(r4)[1][0].obj == ("LOCK", lock)


# ---- 2. the manifest decides --------------------------------------------------------

def test_evaluate_refuses_a_rung_that_disagrees_with_the_manifest(pair):
    dirs, tables, law = pair
    with pytest.raises(ValueError):
        evaluate(relay_blind, dirs["r1R"], law, tables["r1R"], (1,), SEQ, n=5, rung="r1")
    with pytest.raises(ValueError):
        evaluate(relay_blind, dirs["r1"], law, tables["r1"], (1,), SEQ, n=5, rung="r1R")


# ---- 3. paired evaluation -----------------------------------------------------------

def _per_window(fn, d, law, tables):
    rows = {}
    r = evaluate(fn, d, law, tables, K_LIST, SEQ, on_window=lambda i, k, key, ex: rows.__setitem__((i, k), (key, ex)))
    return r, rows


def test_relay_blind_model_has_the_paired_kind_excess(pair):
    dirs, tables, law = pair
    r1, w1 = _per_window(relay_blind, dirs["r1"], law, tables["r1"])
    rr, wr = _per_window(relay_blind, dirs["r1R"], law, tables["r1R"])
    assert set(w1) == set(wr) and len(w1) > 300
    for (i, k), (key_r, ex_r) in wr.items():
        key_1, ex_1 = w1[(i, k)]
        assert key_1 == (key_r[0], drop_relay(key_r[1]))           # the pair's classes correspond
        assert list(ex_1["structural_by_field"]) == ["kind", "actor", "obj", "related", "lineage"]
        assert list(ex_r["structural_by_field"]) == ["kind", "actor", "relay", "related", "lineage"]
        assert ex_r["structural_by_field"]["kind"] == ex_1["structural_by_field"]["kind"]    # bit for bit
        assert ex_r["structural_by_field"]["actor"] == ex_1["structural_by_field"]["actor"]
        assert ex_r["kind_kl_bits"] == ex_1["kind_kl_bits"]
        assert ex_r["naming_bits"] == ex_1["naming_bits"]
    for k in K_LIST:
        a, b = r1["per_k"][k], rr["per_k"][k]
        assert a["missing_classes"] == b["missing_classes"] == 0
        assert a["structural_by_field"]["kind"] == b["structural_by_field"]["kind"]
        assert set(b["structural_by_field"]) == {"kind", "actor", "relay", "related", "lineage"}
        assert set(a["structural_by_field"]) == {"kind", "actor", "obj", "related", "lineage"}
        assert b["identity_max_abs"] < 1e-9
    # pinned (k = 3): n, the KIND excess mean (both rungs) and the relay field's mean
    b3 = rr["per_k"][3]
    assert b3["structural_bits"]["n"] == PIN_N3
    assert b3["structural_by_field"]["kind"]["mean"] == pytest.approx(PIN_KIND3, abs=1e-12)
    assert b3["structural_by_field"]["relay"]["mean"] == pytest.approx(PIN_RELAY3, abs=1e-12)
    assert r1["per_k"][3]["structural_by_field"]["obj"]["mean"] == pytest.approx(PIN_OBJ3_R1, abs=1e-12)


def test_exact_ceiling_model_has_zero_excess_at_r1R(pair):
    dirs, tables, law = pair
    r = evaluate(RelayBayes(tables["r1R"], law), dirs["r1R"], law, tables["r1R"], K_LIST, SEQ)
    for k in K_LIST:
        pk = r["per_k"][k]
        assert pk["missing_classes"] == 0 and pk["structural_bits"]["n"] > 100
        for key in ("structural_bits", "naming_bits", "token_bits", "kind_kl_bits", "end_bits"):
            assert abs(pk[key]["mean"]) < 1e-9 and pk[key]["sd"] < 1e-9, (k, key, pk[key])
        for f in ("kind", "actor", "relay", "related", "lineage"):
            assert abs(pk["structural_by_field"][f]["mean"]) < 1e-9 and pk["structural_by_field"][f]["sd"] < 1e-9


def test_relay_windows_have_kind_relays(pair):
    """The fixture's r1R corpus really carries relays (otherwise the pairing test is vacuous)."""
    dirs, _, _ = pair
    n = sum(any(isinstance(r.obj, Lit) for r in surface_records(tuple(VOCAB[t] for t in toks), "r1R")[1])
            for toks, _ in read_split(dirs["r1R"], "test"))
    assert n == PIN_N_RELAYED


def test_census_summarize_carries_the_relay_field():
    rows = [dict(i=i, key=i % 2, structural=0.3, naming=0.0,
                 by_field=dict(kind=0.1, actor=0.1, relay=0.1, related=0.0, lineage=0.0)) for i in range(6)]
    s = summarize(rows, top=2)
    assert list(s["classes"][0]["by_field"]) == ["kind", "actor", "relay", "related", "lineage"]
    assert s["classes"][0]["by_field"]["relay"] == pytest.approx(0.1)


# pinned 2026-09-30 from the fixture above (run key bytes(range(32)), test windows 2,000,000..2,000,199)
PIN_N3 = 153
PIN_KIND3 = 8.672656239877265
PIN_RELAY3 = 9.206857224924251
PIN_OBJ3_R1 = 8.881259145334127
PIN_N_RELAYED = 135
