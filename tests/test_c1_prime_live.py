"""Pins for `docs/c1-prime-live-census-v0.1.md` (artifact-based; the C1′
(48,4,2) recursion itself is minutes and its filter sample tens of minutes,
so the numbers are pinned from the committed raws)."""
import json
import pathlib

import pytest

DOCS = pathlib.Path(__file__).parent.parent / "docs"
DELTA = 0.01


def _ladder(path):
    d = json.load(open(DOCS / path))
    return d, {(r["eps"], r["rung"]): r for r in d["rows"]}


def test_live_world_every_pair_far_above_delta():
    d, rows = _ladder("c1prime-r0-ladder-census-48-4-2-2026-09-03.json")
    assert d["programs"] == "c1prime" and d["aggregation"] == "window"
    for eps, (g12, g23, g34) in (("1", (0.127, 0.293, 0.042)), ("1/2", (0.121, 0.216, 0.036))):
        q = lambda r, n: rows[(eps, r)]["facts"][n]
        assert round(q("r1", "Q1[L0]") - q("r2", "Q1[L0]"), 3) == g12
        assert round(q("r2", "Q1[L0]") - q("r3", "Q1[L0]"), 3) == g23
        assert round(q("r3", "Q3[D0]") - q("r4", "Q3[D0]"), 3) == g34
        assert min(g12, g23, g34) > 3 * DELTA


def test_exposure_share_same_live_as_half_dead_double_from_reset():
    gaps = {}
    for lab, path in (("live", "c1prime-r0-ladder-census-48-4-2-2026-09-03.json"),
                      ("half", "r0-ladder-census-32-4-2-2026-09-03.json"),
                      ("reset", "r0-ladder-census-14-4-2-2026-09-03.json")):
        _, rows = _ladder(path)
        g = lambda r: rows[("1", r)]["predictive"]["kinds2"]["gap"]
        gaps[lab] = g("r1") - g("r4")
    assert round(gaps["live"], 3) == 0.141 and round(gaps["half"], 3) == 0.139 and round(gaps["reset"], 3) == 0.076
    assert abs(gaps["live"] - gaps["half"]) < 0.005 and gaps["live"] > 1.8 * gaps["reset"]


def test_live_world_mass_and_identity_step():
    _, rows = _ladder("c1prime-r0-ladder-census-48-4-2-2026-09-03.json")
    H = lambda r: rows[("1", r)]["mean_state_entropy_bits"]
    assert round(H("r1"), 3) == 4.235 and round(H("r0") - H("r1"), 2) == 3.32
    assert H("r0") > H("r1") > H("r2") > H("r3") > H("r4")


def test_filter_sample_exact_on_largest_supports():
    d, rows = _ladder("c1prime-r0-ladder-census-48-4-2-2026-09-03.json")
    for b in d["r0"]:
        assert b["filter_sample"]["mismatches"] == 0 and b["filter_sample"]["n"] == 20
    assert rows[("1/2", "r0")]["max_support"] == 30234 and rows[("1", "r1")]["max_support"] == 7337


@pytest.mark.parametrize("path,amb,unreach_pct", [
    ("c1prime-residual-ambiguity-census-48-4-2-2026-09-03.json", 0.917, 25),
    ("c1prime-residual-ambiguity-census-64-4-2-2026-09-03.json", 0.937, 24)])
def test_residual_live_world(path, amb, unreach_pct):
    d = json.load(open(DOCS / path))
    assert d["programs"] == "c1prime"
    r = next(x for x in d["rows"] if x["eps"] == "1")
    reach = sum(s["split_mass"]["r4"] for s in r["signatures"])
    assert round(r["ambiguous_mass"], 3) == amb
    assert round((r["ambiguous_mass"] - reach) / r["ambiguous_mass"] * 100) == unreach_pct


def test_pricing_says_context_4_is_the_ceiling_unrolled():
    p = {}
    for law in ("32-4", "48-4", "48-6"):
        d = json.load(open(DOCS / f"window-process-pricing-c1prime-{law}-2-r1-2026-09-03.json"))
        assert d["programs"] == "c1prime"
        p[law] = d["rows"][0]
    assert p["32-4"]["max_pairs"] == 102950 and p["48-4"]["max_pairs"] == 332119 and p["48-6"]["max_pairs"] == 1650623
    assert p["48-6"]["peak_rss_kb"] > 8e6                      # over the proposed 8 GB line
    assert p["48-4"]["peak_rss_kb"] < 8e6 and p["48-4"]["max_pairs"] < 2e6
