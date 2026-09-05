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


def test_q4_and_predictive_targets_at_the_same_gated_law_pinned():
    """Q4 (W = 4) and the τ family at (40,8,2) r4 ε = 1, produced on the
    recursion; they carry no gate of their own and are covered by the r4
    ε = 1 sharded gate (their docstrings say so). Raws filed 2026-09-05."""
    q = json.load(open(DOCS / "c1prime-loop-q4-ceilings-40-8-2-r4-W4-2026-09-05.json"))
    assert q["aggregation"] == "window" and q["programs"] == "c1prime-loop" and q["W"] == 4
    (r,) = q["rows"]
    assert r["eps"] == "1" and r["rung"] == "r4" and r["n_windows"] == 1524612 and r["n_states"] == 1973
    assert (round(r["total_bits"], 4), round(r["irreducible_bits"], 4), round(r["gap_bits"], 4), round(r["none_mass"], 4)) == (0.9122, 0.8361, 0.0761, 0.4454)
    t = json.load(open(DOCS / "c1prime-loop-predictive-targets-40-8-2-r4-2026-09-05.json"))
    assert t["aggregation"] == "window" and t["m"] == 2 and t["W"] == 4
    (s,) = t["rows"]
    assert s["n_windows"] == 1524612 and s["n_pnext_classes"] == 37523
    assert round(s["means"]["pnext"]["gap"], 4) == 0.1026 and round(s["means"]["kinds2"]["gap"], 4) == 0.1191
    assert round(s["means"]["ttw4"]["gap"], 4) == 0.0572 and round(s["means"]["lineage4"]["gap"], 4) == 0.0226
    d = s["divergent"]
    assert d["pairs"] == 15247291009 and d["windows"] == 1196345 and round(d["mass"], 4) == 0.6698
    assert round(d["pair_prob"], 6) == 0.008817 and round(d["tv_pair_prob"], 6) == 0.004691


def test_r4_eps_half_three_artifacts_pinned():
    """The same three producers at (40,8,2) r4, ε = ½, under the r4 ε = ½
    sharded gate (raws filed 2026-09-05)."""
    q = json.load(open(DOCS / "c1prime-loop-query-ceilings-40-8-2-r4-2026-09-05-eps1_2.json"))
    (r,) = q["rows"]
    assert r["eps"] == "1/2" and r["n_windows"] == 1524612
    assert r["gate"].count("full-eps1_2-shard") == 8
    assert round(r["mean_state_entropy_bits"], 4) == 0.1658
    for k, v in (("Q1[L0]", 0.0032), ("Q1[L1]", 0.0209), ("Q2[T0]", 0.0186), ("Q3[D0]", 0.0098), ("Q5joint", 0.0243)):
        assert round(r["queries"][k]["mean_bits"], 4) == v, k
    q4 = json.load(open(DOCS / "c1prime-loop-q4-ceilings-40-8-2-r4-W4-2026-09-05-eps1_2.json"))["rows"][0]
    assert q4["eps"] == "1/2" and q4["n_states"] == 4231
    assert (round(q4["total_bits"], 4), round(q4["irreducible_bits"], 4), round(q4["gap_bits"], 4), round(q4["none_mass"], 4)) == (0.7573, 0.7205, 0.0368, 0.4144)
    t = json.load(open(DOCS / "c1prime-loop-predictive-targets-40-8-2-r4-2026-09-05-eps1_2.json"))["rows"][0]
    assert t["eps"] == "1/2" and t["n_pnext_classes"] == 87421
    assert round(t["means"]["pnext"]["gap"], 4) == 0.0561 and round(t["means"]["kinds2"]["gap"], 4) == 0.0683
    assert t["divergent"]["pairs"] == 7280573310 and t["divergent"]["windows"] == 1182875 and round(t["divergent"]["mass"], 4) == 0.7184


def test_r1_eps1_three_artifacts_pinned_and_r1_to_r4_gap_is_above_delta():
    """r1 at (40,8,2) ε = 1 under the r1 ε = 1 sharded gate (raws 2026-09-05),
    and the first statutory-query rung gap in a live world at context 8:
    r1 → r4 on Q1[L0] is 0.1439 bits, fourteen times δ = 0.01 (exploratory
    until enactment; adjacent pairs await the r2 and r3 gates)."""
    q1 = json.load(open(DOCS / "c1prime-loop-query-ceilings-40-8-2-r1-2026-09-05.json"))
    (r,) = q1["rows"]
    assert r["eps"] == "1" and r["rung"] == "r1" and r["n_windows"] == 819073 and r["gate"].count("-r1-2026-09-05-full-shard") == 8
    assert round(r["mean_state_entropy_bits"], 4) == 0.6008
    for k, v in (("Q1[L0]", 0.1609), ("Q1[L1]", 0.1021), ("Q2[T0]", 0.0996), ("Q3[D0]", 0.0313), ("Q5joint", 0.1177)):
        assert round(r["queries"][k]["mean_bits"], 4) == v, k
    r4 = _row()
    gap = r["queries"]["Q1[L0]"]["mean_bits"] - r4["queries"]["Q1[L0]"]["mean_bits"]
    assert round(gap, 4) == 0.1439 and gap > 10 * 0.01
    assert all(r["queries"][k]["mean_bits"] >= r4["queries"][k]["mean_bits"] - 1e-12 for k in r["queries"])   # refinement
    q4 = json.load(open(DOCS / "c1prime-loop-q4-ceilings-40-8-2-r1-W4-2026-09-05.json"))["rows"][0]
    assert q4["rung"] == "r1" and (round(q4["total_bits"], 4), round(q4["irreducible_bits"], 4), round(q4["gap_bits"], 4)) == (0.9642, 0.8361, 0.1281)
    t = json.load(open(DOCS / "c1prime-loop-predictive-targets-40-8-2-r1-2026-09-05.json"))["rows"][0]
    assert t["rung"] == "r1" and t["n_pnext_classes"] == 37879 and round(t["means"]["kinds2"]["gap"], 4) == 0.1858
    assert t["divergent"]["windows"] == 630007 and round(t["divergent"]["mass"], 4) == 0.6085


def test_r1_eps_half_three_artifacts_pinned_and_gap_to_r4():
    """r1 at (40,8,2) ε = ½ under the r1 ε = ½ gate (raws 2026-09-05): the
    r1 → r4 gap on Q1[L0] is 0.0764 bits, seven times δ."""
    q1 = json.load(open(DOCS / "c1prime-loop-query-ceilings-40-8-2-r1-2026-09-05-eps1_2.json"))
    (r,) = q1["rows"]
    assert r["eps"] == "1/2" and r["rung"] == "r1" and r["n_windows"] == 819073 and r["gate"].count("eps1_2-shard") == 8
    assert round(r["mean_state_entropy_bits"], 4) == 0.2963
    for k, v in (("Q1[L0]", 0.0796), ("Q1[L1]", 0.0682), ("Q2[T0]", 0.0453), ("Q3[D0]", 0.0247), ("Q5joint", 0.0576)):
        assert round(r["queries"][k]["mean_bits"], 4) == v, k
    r4 = json.load(open(DOCS / "c1prime-loop-query-ceilings-40-8-2-r4-2026-09-05-eps1_2.json"))["rows"][0]
    assert round(r["queries"]["Q1[L0]"]["mean_bits"] - r4["queries"]["Q1[L0]"]["mean_bits"], 4) == 0.0764
    assert all(r["queries"][k]["mean_bits"] >= r4["queries"][k]["mean_bits"] - 1e-12 for k in r["queries"])
    q4 = json.load(open(DOCS / "c1prime-loop-q4-ceilings-40-8-2-r1-W4-2026-09-05-eps1_2.json"))["rows"][0]
    assert (round(q4["total_bits"], 4), round(q4["irreducible_bits"], 4), round(q4["gap_bits"], 4)) == (0.7908, 0.7205, 0.0703)
    t = json.load(open(DOCS / "c1prime-loop-predictive-targets-40-8-2-r1-2026-09-05-eps1_2.json"))["rows"][0]
    assert t["n_pnext_classes"] == 78472 and round(t["means"]["kinds2"]["gap"], 4) == 0.1154
    assert t["divergent"]["windows"] == 619385 and round(t["divergent"]["mass"], 4) == 0.6598
