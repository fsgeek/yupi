"""The evaluator and census on the decoy rung r1ᴅ ("r1D", three-arm design v0.1 §3),
mirroring tests/test_learner_evaluate_relay.py: the OBJECT slot is read as a KIND
literal (or NONE) at every registered window-level rung and reported under the
rung's own field name ("decoy" at r1D); a model blind to the slot has the paired
r1 KIND excess bit for bit; the exact-ceiling model has zero excess.
"""
import sys
from fractions import Fraction
from pathlib import Path

import pytest

pytest.importorskip("torch")

from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.writer import generate
from yupi.interfaces import WINDOW_RUNGS, Lit, drop_relay
from yupi.learner.census import summarize
from yupi.learner.evaluate import FIELDS, RELAY_FIELDS, evaluate, field_names, surface_records
from yupi.pattern_ceiling import ceiling_table

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_learner_evaluate_relay import K_LIST, SEQ, RelayBayes, relay_blind  # noqa: E402

KEY = bytes(range(32))


@pytest.fixture(scope="module")
def pair(tmp_path_factory):
    root = tmp_path_factory.mktemp("decoy-eval")
    out = {}
    for rung in ("r1", "r1D"):
        m = Manifest.new(programs="c1prime-loop", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung=rung, run_key=KEY,
                         splits=(Split("train", 0, 16), Split("test", 2_000_000, 2_000_200)), git_commit="t")
        out[rung], _ = generate(m, root, workers=1)
    cfg, progs = m.world()
    law = m.law()
    tabs = {k: ceiling_table(cfg, progs, law, ("r1", "r1D"), prefix_len=k) for k in K_LIST}
    tables = {rung: {k: tabs[k][rung] for k in K_LIST} for rung in ("r1", "r1D")}
    return out, tables, law


def test_field_names_per_window_rung():
    assert field_names("r1R") == RELAY_FIELDS == ("kind", "actor", "relay", "related", "lineage")
    assert field_names("r1D") == ("kind", "actor", "decoy", "related", "lineage")
    assert field_names("r1S") == ("kind", "actor", "self", "related", "lineage")
    assert field_names("r1") == field_names(None) == FIELDS
    assert all(field_names(r) != FIELDS for r in WINDOW_RUNGS)


@pytest.mark.parametrize("rung", ["r1D", "r1S"])
def test_surface_records_reads_the_slot_as_a_literal(rung):
    from yupi.corpus.vocab import VOCAB, token_type
    a = next(t for t in VOCAB if token_type(t) == "thread")
    lock = next(t for t in VOCAB if token_type(t) == "lock")
    toks = ("STEP", a, "NONE", "MASKED", "MASKED", "BLOCK", a, "STEP", "MASKED", "MASKED")
    reset, recs = surface_records(toks, rung)
    assert not reset and recs[0].obj is None and recs[1].obj == Lit("STEP")
    with pytest.raises(ValueError):
        surface_records(toks[:7] + (lock,) + toks[8:], rung)        # an entity in the slot


def _per_window(fn, d, law, tables):
    rows = {}
    r = evaluate(fn, d, law, tables, K_LIST, SEQ, on_window=lambda i, k, key, ex: rows.__setitem__((i, k), (key, ex)))
    return r, rows


def test_evaluate_refuses_a_rung_that_disagrees_with_the_manifest(pair):
    dirs, tables, law = pair
    with pytest.raises(ValueError):
        evaluate(relay_blind, dirs["r1D"], law, tables["r1D"], (1,), SEQ, n=5, rung="r1R")


def test_blind_model_has_the_paired_kind_excess(pair):
    dirs, tables, law = pair
    r1, w1 = _per_window(relay_blind, dirs["r1"], law, tables["r1"])
    rd, wd = _per_window(relay_blind, dirs["r1D"], law, tables["r1D"])
    assert set(w1) == set(wd) and len(w1) > 300
    for (i, k), (key_d, ex_d) in wd.items():
        key_1, ex_1 = w1[(i, k)]
        assert key_1 == (key_d[0], drop_relay(key_d[1]))
        assert list(ex_d["structural_by_field"]) == ["kind", "actor", "decoy", "related", "lineage"]
        assert ex_d["structural_by_field"]["kind"] == ex_1["structural_by_field"]["kind"]    # bit for bit
        assert ex_d["structural_by_field"]["actor"] == ex_1["structural_by_field"]["actor"]
        assert ex_d["kind_kl_bits"] == ex_1["kind_kl_bits"]
        assert ex_d["naming_bits"] == ex_1["naming_bits"]
    for k in K_LIST:
        a, b = r1["per_k"][k], rd["per_k"][k]
        assert a["missing_classes"] == b["missing_classes"] == 0
        assert a["structural_bits"]["n"] == b["structural_bits"]["n"]
        assert a["structural_by_field"]["kind"] == b["structural_by_field"]["kind"]
        assert set(b["structural_by_field"]) == {"kind", "actor", "decoy", "related", "lineage"}
        assert b["identity_max_abs"] < 1e-9
    rows = [dict(key=key, structural=sum(ex["structural_by_field"].values()), by_field=ex["structural_by_field"])
            for (i, k), (key, ex) in wd.items() if k == 3]
    assert set(summarize(rows)["classes"][0]["by_field"]) == {"kind", "actor", "decoy", "related", "lineage"}


def test_exact_ceiling_model_has_zero_excess_at_r1D(pair):
    dirs, tables, law = pair
    r = evaluate(RelayBayes(tables["r1D"], law), dirs["r1D"], law, tables["r1D"], K_LIST, SEQ)
    for k in K_LIST:
        pk = r["per_k"][k]
        assert pk["missing_classes"] == 0 and pk["structural_bits"]["n"] > 100
        for key in ("structural_bits", "naming_bits", "token_bits", "kind_kl_bits", "end_bits"):
            assert abs(pk[key]["mean"]) < 1e-9 and pk[key]["sd"] < 1e-9, (k, key, pk[key])
        for f in ("kind", "actor", "decoy", "related", "lineage"):
            assert abs(pk["structural_by_field"][f]["mean"]) < 1e-9 and pk["structural_by_field"][f]["sd"] < 1e-9
