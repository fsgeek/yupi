"""v0.2.9 Clause 4 keyed rendering; Part I D3 pools; design v0.1 §3."""
import itertools
from collections import Counter

import pytest

from yupi.config import WorldConfig
from yupi.corpus import rendering as R
from yupi.corpus import vocab as V
from yupi.interfaces import project
from yupi.records import Record

KEY = bytes(range(32))


def test_injection_is_deterministic_in_key_and_episode():
    a = R.injection(KEY, 7, "thread", 4)
    assert a == R.injection(KEY, 7, "thread", 4)
    assert a != R.injection(bytes(32), 7, "thread", 4) or a != R.injection(KEY, 8, "thread", 4)
    assert len(a) == 4 and len(set(a)) == 4                    # an injection


def test_reserved_slice_is_never_drawn():
    reserved = set(V.pool_tokens("thread")[-V.RESERVED["thread"]:])
    for ep in range(2000):
        assert not reserved & set(R.injection(KEY, ep, "thread", 4))
    reserved_l = set(V.pool_tokens("lock")[-V.RESERVED["lock"]:])
    for ep in range(2000):
        assert not reserved_l & set(R.injection(KEY, ep, "lock", 2))


def test_d3_refusals_name_the_statute():
    with pytest.raises(R.RenderingRefused, match="Part I D3"):
        R.d3_check("thread", 4, 49)                            # ≥ 50 for ≤ 4 threads
    with pytest.raises(R.RenderingRefused, match="Part I D3"):
        R.d3_check("lock", 8, 63)                              # 8× entity count
    R.d3_check("thread", 4, 56)                                # the real drawable slice
    R.d3_check("device", 1, 14)


def test_partial_fisher_yates_is_uniform_exhaustively_on_a_small_pool():
    """Design §10: every injection of n=3 into a drawable slice of m=5 (60
    injections) over 10^5 keyed draws; chi-square below the 0.999 quantile
    (df=59, 98.3). The reserved tail (one token) never appears."""
    pool = ("a", "b", "c", "d", "e", "z")
    counts = Counter()
    for ep in range(100_000):
        inj = R._keyed_injection(KEY, ep, "small", pool, drawable=5, n_entities=3)
        assert "z" not in inj
        counts[inj] += 1
    expected = 100_000 / 60
    assert set(counts) == set(itertools.permutations(pool[:5], 3))
    chi2 = sum((c - expected) ** 2 / expected for c in counts.values())
    assert chi2 < 98.3, chi2


def test_episode_table_draw_inverse_json():
    cfg = WorldConfig.c1()
    t = R.EpisodeTable.draw(KEY, 11, cfg)
    assert len(t.thread) == 4 and len(t.lock) == 2 and len(t.device) == 1 and len(t.request) == cfg.req_pool
    inv = t.inverse()
    assert inv[t.thread[2]] == ("thread", 2) and inv[t.request[3]] == ("request", 3)
    assert R.EpisodeTable.from_json(t.to_json()) == t


@pytest.mark.parametrize("rung", ["r0", "r1", "r2", "r3", "r4"])
def test_render_unrender_round_trip_every_field_form(rung):
    cfg = WorldConfig.c1()
    t = R.EpisodeTable.draw(KEY, 3, cfg)
    recs = [
        Record("DISPATCH", 1, None, None, None),
        Record("BLOCK", 0, ("LOCK", 1), 2, None),
        Record("IO_ISSUE", 3, ("DEV", 0), None, 2),
        Record("IO_COMPLETE", 3, ("DEV", 0), None, 2),
        Record("IDLE", None, None, None, None),
        Record("RELEASE", 1, ("LOCK", 0), 0, None),
    ]
    for r in recs:
        p = project(r, rung)
        toks = R.render(p, t)
        assert len(toks) == 5 and toks[0] == r.kind
        assert all(V.token_type(x) in ("kind", "special", "thread", "lock", "device", "request") for x in toks)
        assert R.unrender(toks, t) == p


def test_render_masked_and_none_are_distinct_tokens():
    cfg = WorldConfig.c1()
    t = R.EpisodeTable.draw(KEY, 3, cfg)
    idle_r4 = R.render(project(Record("IDLE", None, None, None, None), "r4"), t)
    idle_r0 = R.render(project(Record("IDLE", None, None, None, None), "r0"), t)
    assert idle_r4 == ("IDLE", V.NONE, V.NONE, V.NONE, V.NONE)
    assert idle_r0 == ("IDLE", V.MASKED, V.MASKED, V.MASKED, V.MASKED)
