"""Full-gate verdicts at the frozen law (40,8,2), looping C1′
(`docs/looping-exit-law-freeze-v0.1.md` §5 item 2): a (rung, ε) is gated
iff its eight interleaved shards report zero mismatches and their window
counts sum to the recursion's total. Each gated pair is pinned here as it
lands; a pair absent from GATED has NOT been gated and no ceiling on it is
statutory."""
import json
import pathlib

import pytest

DOCS = pathlib.Path(__file__).parent.parent / "docs"

# (rung, eps) → (n_windows_total, date the raws carry)
GATED = {
    ("r4", "1"): (1524612, "2026-09-04"),
}


@pytest.mark.parametrize("rung,eps", sorted(GATED))
def test_gated_pair_partitions_every_window_with_zero_mismatches(rung, eps):
    total, date = GATED[(rung, eps)]
    tag = "" if eps == "1" else "-eps" + eps.replace("/", "_")
    rows = []
    for i in range(8):
        d = json.load(open(DOCS / f"window-gate-c1prime-loop-40-8-2-{rung}-{date}-full{tag}-shard{i}.json"))
        assert d["programs"] == "c1prime-loop" and d["rung"] == rung and d["shard"] == [i, 8]
        assert d["law"] == dict(T_ep=40, L=8, B=2)
        (r,) = d["rows"]
        assert r["eps"] == eps and r["n_windows_total"] == total and r["mismatches"] == []
        rows.append(r)
    assert sum(r["n"] for r in rows) == total
    assert max(r["n"] for r in rows) - min(r["n"] for r in rows) <= 1


def test_r4_eps1_cost_pinned():
    r = json.load(open(DOCS / "window-gate-c1prime-loop-40-8-2-r4-2026-09-04-full-shard0.json"))["rows"][0]
    assert r["n"] == 190577 and round(r["mean_seconds_per_window"], 3) == 0.087
    assert r["max_support"] == 101 and r["peak_rss_kb"] < 8e6
