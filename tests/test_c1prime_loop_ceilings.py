"""First gated live-world ceilings: (40,8,2), looping C1′, r4, ε = 1
(`docs/c1prime-loop-query-ceilings-40-8-2-r4-2026-09-04.json`, produced on
the recursion under the external sharded gate). Pins: the gate field names
the eight all-exact shard raws; the law-mass H(S) equals the pass-pricing
raw's r4 value (two independent runs of the recursion); the U = 0 part of
H(S) is exactly zero (reset-anchored r4 windows are injective in the
looping world too); the statutory query means. Exploratory until Part II
v0.2.8.1 / v0.2.7.1 are enacted; gated regardless."""
import json
import pathlib

from yupi.sync import conditional_from_by_endpoint
from yupi.window import WindowLaw

DOCS = pathlib.Path(__file__).parent.parent / "docs"


def _row():
    d = json.load(open(DOCS / "c1prime-loop-query-ceilings-40-8-2-r4-2026-09-04.json"))
    assert d["aggregation"] == "window" and d["gate"] == "external" and d["programs"] == "c1prime-loop"
    (r,) = d["rows"]
    assert r["eps"] == "1" and r["rung"] == "r4"
    return r


def test_gate_field_names_the_eight_exact_shards():
    r = _row()
    files = r["gate"].removeprefix("external:").split(",")
    assert len(files) == 8 and all(f.startswith("window-gate-c1prime-loop-40-8-2-r4-2026-09-04-full-shard") for f in files)
    for f in files:
        (g,) = json.load(open(DOCS / f))["rows"]
        assert g["mismatches"] == []


def test_state_entropy_matches_the_pass_pricing_raw_and_has_no_reset_part():
    r = _row()
    p = json.load(open(DOCS / "window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-04.json"))
    pr = next(x for x in p["rows"] if x["eps"] == "1")
    assert r["n_windows"] == 1524612 == pr["per_rung"]["r4"]["n_windows"]
    assert abs(r["mean_state_entropy_bits"] - pr["per_rung"]["r4"]["mean_state_entropy_bits"]) < 1e-9
    c = conditional_from_by_endpoint(r["by_endpoint"], WindowLaw(T_ep=40, L=8, B=2), "mean_state_entropy_bits")
    assert c["H_U0"] == 0.0 and round(c["E_H_given_U_pos"], 4) == 0.4873


def test_statutory_query_means_pinned():
    q = _row()["queries"]
    for k, v in (("Q1[L0]", 0.0170), ("Q1[L1]", 0.0402), ("Q2[T0]", 0.0502), ("Q2[T1]", 0.0228),
                 ("Q2[T2]", 0.0456), ("Q2[T3]", 0.0117), ("Q3[D0]", 0.0141), ("Q5joint", 0.0606)):
        assert round(q[k]["mean_bits"], 4) == v, k
    assert round(q["Q1[L0]"]["resolved_mass"], 3) == 0.983
