"""Prediction checker (owed since Aug 22; D8 attribution prereg §8).

A pre-stated prediction is (selector, quantity, relation, value). The checker
flattens every committed artifact into cells and evaluates the prediction on
every matching cell. Three outcomes, never silently collapsed: PASS, FAIL,
NO_CHECK (no committed cell matches — the P4 case). Raw artifacts with a
corrected sibling are the buggy-kernel numbers (2026-08-20 erratum) and are
flagged superseded; unknown artifact families are reported, not skipped.
"""
import json
import os
import subprocess
import sys

import pytest

from yupi.predictions import (evaluate, load_artifacts, match,
                              NON_MEASUREMENT_PREFIXES)

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")


def _write(d, name, obj):
    with open(os.path.join(d, name), "w") as f:
        json.dump(obj, f)


@pytest.fixture
def docs(tmp_path):
    d = str(tmp_path)
    qc = dict(law=dict(T_ep=6, L=4, B=2), rows=[
        dict(eps="1", rung="r1", n_windows=5, mean_state_entropy_bits=0.5,
             queries={"Q1[L0]": dict(mean_bits=0.25, resolved_mass=0.7)},
             by_endpoint={"4": dict(U=0, mean_state_entropy_bits=0.0),
                          "6": dict(U=2, mean_state_entropy_bits=0.9)}),
        dict(eps="1/2", rung="r4", n_windows=5, mean_state_entropy_bits=0.0,
             queries={"Q1[L0]": dict(mean_bits=0.0, resolved_mass=1.0)},
             by_endpoint={}),
    ])
    _write(d, "c1-query-ceilings-6-4-2-raw-2026-08-15.json",
           dict(qc, rows=[dict(qc["rows"][0], mean_state_entropy_bits=0.7)]))
    _write(d, "c1-query-ceilings-6-4-2-corrected-2026-08-20.json", qc)
    _write(d, "c1-query-ceilings-6-6-2-corrected-2026-08-20.json",
           dict(law=dict(T_ep=6, L=6, B=2), rows=[
               dict(eps="1", rung="r1", n_windows=2, mean_state_entropy_bits=0.0,
                    queries={}, by_endpoint={})]))
    _write(d, "c1-q4-ceilings-6-4-2-W4-corrected-2026-08-20.json",
           dict(law=dict(T_ep=6, L=4, B=2), W=4, rows=[
               dict(eps="1", rung="r1", n_windows=5, n_states=3, total_bits=0.8,
                    irreducible_bits=0.6, gap_bits=0.2, none_mass=0.5, by_endpoint={})]))
    _write(d, "d10-lineage-search-v2-2026-08-24.json",
           dict(prereg="x", B=2, tep_star=6, horizons=[6], laws=[
               dict(T_ep=6, L=2, delta_interaction_Q3=0.1, disciplines=dict(
                   fifo=dict(Q3=dict(prevalence=0.0, delta=0.0, max_g=0.0),
                             anchored_Q3=dict(anchored_delta=0.0, I_U_given_H3=0.0),
                             two_path_windows_checked=3),
                   stochastic=dict(Q3=dict(prevalence=0.1, delta=0.05, max_g=1.0),
                                   anchored_Q3=dict(anchored_delta=0.05, I_U_given_H3=0.0),
                                   two_path_windows_checked=4)))]))
    _write(d, "d8-attribution-c0b-2026-08-25.json", dict(prereg="p", freeze="f", cells=[
        dict(world="c0b", discipline="fifo", eps="1", T_ep=6, L=6, B=3, rung="r2",
             gates=dict(all_passed=True), delta_un=0.3, delta_an=0.2, offset_term=0.1,
             chain_semantic_an=dict(kappa=0.0, WQ=0.0, DQ=0.05, REQ=0.1, rho=0.05),
             per_endpoint_an={"3": 0.0, "6": 0.4}, collapsed_an=False, prevalence=0.5,
             cost=dict(t_gate2_s=1.0), wall_s=2.0, prereg="p"),
        dict(world="c0b", discipline="fifo", eps="1", T_ep=6, L=3, B=3, rung="r2",
             gates=dict(all_passed=False, failed="two_path_shuffled: ..."))]))
    _write(d, "held-out-selection-e-draw-2026-08-21.json", dict(seed=1))
    _write(d, "mystery-family-2026-08-24.json", dict(rows=[]))
    # filename variants seen in the record: a per-endpoint raw variant, an
    # old-labels raw variant, and an untagged file with a corrected sibling
    _write(d, "c1-query-ceilings-6-4-2-raw-2026-08-16-perT.json", qc)
    _write(d, "c1-query-ceilings-6-4-2-raw-2026-08-15-v0.1-labels.json", qc)
    _write(d, "c1-support-exact-2026-08-14.json", dict(law=dict(T_ep=6, L=2, B=2), rows=[
        dict(eps="1", rung="r1", n_windows=1, mean_support_exact="3/2", mean_support=1.5, max_support=2)]))
    _write(d, "c1-support-exact-corrected-2026-08-20.json", dict(law=dict(T_ep=6, L=2, B=2), rows=[
        dict(eps="1", rung="r1", n_windows=1, mean_support_exact="5/2", mean_support=2.5, max_support=3)]))
    return d


def test_adapters_flatten_known_families(docs):
    cells, unknown = load_artifacts(docs)
    fam = {c["family"] for c in cells}
    assert fam == {"c1-query-ceilings", "c1-q4-ceilings", "d10-lineage-search", "c1-support-exact",
                   "d8-attribution"}
    d8 = [c for c in cells if c["family"] == "d8-attribution"]
    assert {c["quantity"] for c in d8} >= {"delta_an", "chain_semantic_an.REQ", "per_endpoint_an",
                                           "gates.all_passed", "collapsed_an"}
    assert [c["T"] for c in d8 if c["quantity"] == "per_endpoint_an"] == [3, 6]
    assert any(c["quantity"] == "gates.all_passed" and c["value"] == 0 and c["L"] == 3 for c in d8)
    assert not any(c["quantity"] == "delta_an" and c["L"] == 3 for c in d8)   # failed cell: no numbers
    assert unknown == ["mystery-family-2026-08-24.json"]
    assert any(p in "held-out-selection-e-draw-2026-08-21.json" for p in NON_MEASUREMENT_PREFIXES)
    q = [c for c in cells if c["quantity"] == "Q1[L0].mean_bits" and c["eps"] == "1"]
    assert len(q) == 4                       # raw, corrected, raw-perT, raw-v0.1-labels
    assert [c for c in q if not c["superseded"]][0]["tag"] == "corrected"
    assert all(c["kernel"] == ("fixed" if c["tag"] == "corrected" else "buggy") for c in q)
    sup = [c for c in cells if c["family"] == "c1-support-exact"]
    assert {(c["tag"], c["superseded"]) for c in sup} == {(None, True), ("corrected", False)}
    ep = [c for c in cells if c["quantity"] == "by_endpoint.mean_state_entropy_bits"]
    assert {c["T"] for c in ep} == {4, 6}
    d10 = [c for c in cells if c["family"] == "d10-lineage-search"]
    assert {c["discipline"] for c in d10} == {"fifo", "stochastic", None}
    assert any(c["quantity"] == "Q3.delta" and c["discipline"] == "stochastic"
               and c["value"] == 0.05 for c in d10)


def test_raw_with_corrected_sibling_is_superseded(docs):
    cells, _ = load_artifacts(docs)
    raw = [c for c in cells if c["tag"] == "raw"]
    assert raw and all(c["superseded"] for c in raw)
    assert all(not c["superseded"] for c in cells if c["tag"] == "corrected")
    # default matching excludes superseded cells; opting in includes them
    sel = dict(family="c1-query-ceilings", quantity="mean_state_entropy_bits", eps="1", L=4)
    assert {c["value"] for c in match(cells, sel)} == {0.5}
    assert {c["value"] for c in match(cells, dict(sel, superseded="any"))} == {0.5, 0.7}


def test_selector_semantics(docs):
    cells, _ = load_artifacts(docs)
    base = dict(family="c1-query-ceilings", quantity="mean_state_entropy_bits")
    assert len(match(cells, dict(base, rung=["r1", "r4"]))) == 3
    assert len(match(cells, dict(base, T_ep={"le": 6}, L={"lt": 6}))) == 2
    full = match(cells, dict(base, L="T_ep"))                 # full context
    assert [c["L"] for c in full] == [6]
    assert match(cells, dict(base, eps="1/2"))[0]["rung"] == "r4"


def test_evaluate_three_outcomes(docs):
    cells, _ = load_artifacts(docs)
    full_zero = dict(id="theorem", select=dict(family="c1-query-ceilings",
                     quantity="mean_state_entropy_bits", L="T_ep"), relation="==", value=0)
    r = evaluate(full_zero, cells)
    assert r["status"] == "PASS" and r["n_matched"] == 1 and r["n_fail"] == 0
    wrong = dict(full_zero, id="wrong", select=dict(full_zero["select"], L=4), relation="==", value=0)
    r = evaluate(wrong, cells)
    assert r["status"] == "FAIL" and r["n_fail"] == 1 and r["failures"][0]["value"] == 0.5
    nothing = dict(full_zero, id="p4", select=dict(full_zero["select"], T_ep=4))
    assert evaluate(nothing, cells)["status"] == "NO_CHECK"
    tol = dict(full_zero, id="tol", select=dict(family="c1-q4-ceilings", quantity="gap_bits"),
               relation="==", value=0.2000000001, tol=1e-6)
    assert evaluate(tol, cells)["status"] == "PASS"
    gt = dict(id="gt", select=dict(family="d10-lineage-search", quantity="Q3.delta",
              discipline="stochastic"), relation=">", value=0)
    assert evaluate(gt, cells)["status"] == "PASS"


def test_existence_quantifier(docs):
    """An existence prediction ("informative somewhere") is 'any'; the
    default 'all' would fail it on the null cells — which is what happened
    when the checker was first run against the D10 record."""
    cells, _ = load_artifacts(docs)
    sel = dict(family="d10-lineage-search", quantity="Q3.delta")   # fifo 0.0, stochastic 0.05
    assert evaluate(dict(id="u", select=sel, relation=">", value=0), cells)["status"] == "FAIL"
    r = evaluate(dict(id="e", select=sel, relation=">", value=0, quantifier="any"), cells)
    assert r["status"] == "PASS" and r["n_matched"] == 2 and r["n_fail"] == 0
    r = evaluate(dict(id="e0", select=sel, relation=">", value=1, quantifier="any"), cells)
    assert r["status"] == "FAIL" and r["n_fail"] == 2
    with pytest.raises(ValueError):
        evaluate(dict(id="q", select=sel, relation=">", value=0, quantifier="some"), cells)


def test_cli_exit_codes(docs, tmp_path):
    preds = [dict(id="ok", select=dict(family="c1-query-ceilings",
                  quantity="mean_state_entropy_bits", L="T_ep"), relation="==", value=0)]
    pf = os.path.join(str(tmp_path), "p.json")
    script = os.path.join(os.path.dirname(__file__), "..", "scripts", "check_predictions.py")
    def run(ps):
        json.dump(ps, open(pf, "w"))
        return subprocess.run([sys.executable, script, pf, "--docs", docs],
                              capture_output=True, text=True)
    r = run(preds); assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout and "unknown" in r.stdout.lower()
    r = run(preds + [dict(preds[0], id="nochk", select=dict(preds[0]["select"], T_ep=4))])
    assert r.returncode == 2 and "NO_CHECK" in r.stdout
    r = run(preds + [dict(preds[0], id="bad", select=dict(preds[0]["select"], L=4))])
    assert r.returncode == 1 and "FAIL" in r.stdout


def test_real_docs_full_context_state_entropy_is_zero():
    """A known theorem against the real record: at L = T_ep every rung is
    lossless (full-context injectivity), so mean state entropy is exactly 0
    in every committed c1-query-ceilings artifact at full context."""
    cells, unknown = load_artifacts(DOCS)
    r = evaluate(dict(id="inj", select=dict(family="c1-query-ceilings",
                 quantity="mean_state_entropy_bits", L="T_ep"), relation="==", value=0), cells)
    assert r["status"] == "PASS" and r["n_matched"] >= 2, r
    assert unknown == [], unknown   # every committed family has an adapter or is listed non-measurement
