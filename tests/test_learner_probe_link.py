"""The per-window link between probe error and model excess
(scripts/learner_probe_link.py, 2026-09-24): rank correlation and the quartile
gap with its permutation null, on synthetic data with known answers, and the
join end to end on synthetic files."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import learner_probe_link as link  # noqa: E402


def test_spearman_known_values():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert link.spearman(x, x ** 3) == pytest.approx(1.0)
    assert link.spearman(x, -x) == pytest.approx(-1.0)
    # ties are averaged: [1,1,2] vs [1,2,3] has ranks [0.5,0.5,2] vs [0,1,2]
    assert link.spearman(np.array([1.0, 1.0, 2.0]), np.array([1.0, 2.0, 3.0])) == pytest.approx(0.8660254, abs=1e-6)
    assert link.pearson(np.ones(5), x) is None


def test_quartile_gap_and_null_separate_dependent_from_independent():
    rng = np.random.default_rng(0)
    ce = rng.gamma(2.0, 0.1, size=4000)
    dep = ce + rng.normal(0, 0.1, size=4000)          # excess grows with probe CE
    ind = rng.normal(0, 0.1, size=4000)               # excess independent of probe CE
    qd = link.quartiles(ce, dep, np.random.default_rng(1))
    qi = link.quartiles(ce, ind, np.random.default_rng(1))
    assert qd["means"][3] > qd["means"][0] and qd["gap"] > 5 * qd["null"]["sd"] and qd["null"]["p_ge"] == 0.0
    assert abs(qi["gap"]) < 4 * qi["null"]["sd"] and qi["null"]["p_ge"] > 0.01
    assert link.spearman(ce, dep) > 0.5 and abs(link.spearman(ce, ind)) < 0.05


def test_join_end_to_end(tmp_path, capsys):
    rng = np.random.default_rng(3)
    n = 600
    ce = rng.gamma(2.0, 0.1, size=n); h = np.where(rng.random(n) < 0.7, 0.0, 0.3)
    excess = 0.5 * ce + rng.normal(0, 0.05, size=n)
    census = tmp_path / "census.jsonl"
    with open(census, "w") as f:
        for i in range(n):
            f.write(json.dumps(dict(i=i, key=i % 7, structural=float(excess[i]), naming=0.0,
                                    by_field=dict(kind=float(excess[i] / 2), actor=0.0, obj=0.0, related=0.0, lineage=0.0))) + "\n")
    per = tmp_path / "per.jsonl"
    with open(per, "w") as f:
        for L in range(5):
            for i in range(n):
                # only layer 3 carries the dependence; other layers are noise
                c = ce[i] if L == 3 else float(rng.gamma(2.0, 0.1))
                f.write(json.dumps(dict(i=i, lock=0, layer=L, ce=c, h=float(h[i]), p=[0.5, 0.5], q=[0.5, 0.5])) + "\n")
    praw = tmp_path / "probe.json"
    praw.write_text(json.dumps(dict(run="synthetic", seed=1, target="held",
                                    results={f"l0/L{L}": dict(lock=0, layer=L, oir=(0.9 if L == 3 else 0.1)) for L in range(5)})))
    raw = tmp_path / "link.json"
    assert link.main(["--census", str(census), "--per-example", str(per), "--probe-raw", str(praw), "--raw", str(raw)]) == 0
    out = json.loads(raw.read_text())["by_lock"]["0"]
    assert out["layer"] == 3 and out["n"] == n
    assert out["spearman_struct"] > 0.5 and out["quartiles_struct"]["null"]["p_ge"] == 0.0
    assert out["determined"]["n"] == int((h == 0).sum()) and out["determined"]["spearman_struct"] > 0.5
    assert "lock 0 layer 3" in capsys.readouterr().out


def test_residualization_removes_a_shared_difficulty_confound_and_keeps_a_real_link():
    """Probe CE and excess both grow with a window 'difficulty' d but are otherwise
    independent: the pooled quartile gap is significant; after removing 50-bin means
    of d from both, the gap shrinks by more than 90 %. A true
    within-bin dependence survives residualization. Class fixed effects: with the
    confound constant within a class, residualizing by class removes it entirely."""
    rng = np.random.default_rng(5)
    n = 6000
    d = rng.gamma(2.0, 1.0, size=n)
    ce = 0.2 * d + rng.gamma(2.0, 0.05, size=n)
    ex = 0.05 * d + rng.normal(0, 0.05, size=n)
    pooled = link.quartiles(ce, ex, np.random.default_rng(1))
    assert pooled["gap"] > 3 * pooled["null"]["sd"]
    bins = np.digitize(d, np.quantile(d, np.linspace(0, 1, 51)[1:-1]))
    within = link.residualized(ce, ex, bins, np.random.default_rng(1))
    # 50 bins of a gamma covariate leave a sliver of within-bin confound in the wide tail bins;
    # the gap falls by more than 90 % and the residual rank correlation is small
    assert abs(within["gap"]) < 0.1 * pooled["gap"] and abs(within["spearman"]) < 0.06, within
    within2 = link.residualized(ce, ex + 0.3 * ce, bins, np.random.default_rng(1))
    assert within2["gap"] > 5 * within2["null"]["sd"] and within2["null"]["p_ge"] == 0.0
    # class fixed effects: the confound is a class property
    cls = rng.integers(0, 2000, size=n); dc = rng.gamma(2.0, 1.0, size=2000)[cls]
    ce_c = 0.2 * dc + rng.gamma(2.0, 0.05, size=n); ex_c = 0.05 * dc + rng.normal(0, 0.05, size=n)
    assert link.quartiles(ce_c, ex_c, np.random.default_rng(1))["null"]["p_ge"] == 0.0
    fe = link.residualized(ce_c, ex_c, cls, np.random.default_rng(1))
    assert abs(fe["spearman"]) < 0.05 and fe["null"]["p_ge"] > 0.01 and fe["n_groups"] > 1000


def test_class_level_link_sees_a_between_class_dependence_that_windows_hide():
    """Excess = class effect + large realized-record noise; probe CE = the same class
    effect + noise. Per window the rank correlation is tiny; on class means it is
    clear. Independent class effects give no between-class link."""
    rng = np.random.default_rng(11)
    n, C = 30000, 6000
    cls = rng.integers(0, C, size=n)
    eff = rng.gamma(2.0, 0.02, size=C)
    ce = eff[cls] + rng.gamma(2.0, 0.05, size=n)
    ex = eff[cls] + rng.normal(0, 0.3, size=n)
    rho_w = link.spearman(ce, ex)
    assert abs(rho_w) < 0.06
    cl = link.class_level(ce, ex, cls, np.random.default_rng(1))
    # ~5 windows per class: the class mean averages the noise down by ~sqrt(5), no more
    assert cl["n_classes"] > 1000 and cl["spearman"] > 2 * rho_w and cl["null"]["p_ge"] == 0.0
    ex_ind = rng.gamma(2.0, 0.02, size=C)[cls] + rng.normal(0, 0.3, size=n)
    cl2 = link.class_level(ce, ex_ind, cls, np.random.default_rng(1))
    assert abs(cl2["spearman"]) < 0.05 and cl2["null"]["p_ge"] > 0.01


def test_next_record_lock_uses_pattern_indices():
    """Record k+1's lock is reported in the pattern observer's lock index (first
    appearance order over the first k+1 records), None for a non-lock record."""
    from yupi.records import Record
    R = lambda kind, actor, obj=None: Record(kind=kind, actor=actor, obj=obj, related=None, lineage=None)
    recs = [R("ACQUIRE", 3, ("LOCK", 1)), R("STEP", 3), R("ACQUIRE", 0, ("LOCK", 0)), R("BLOCK", 2, ("LOCK", 1))]
    assert link.next_record_lock(recs, 0) == 0          # kernel lock 1 is pattern lock 0
    assert link.next_record_lock(recs, 1) is None       # STEP
    assert link.next_record_lock(recs, 2) == 1          # kernel lock 0 appears second
    assert link.next_record_lock(recs, 3) == 0
    assert link.next_record_lock(recs, 4) is None       # no record 5


def test_class_frequency_counts_every_long_enough_window(tiny_r2_link):
    """count_classes over a split sums to the number of windows with >= k records; every
    eval window with >= k records gets a key and short ones get None."""
    import learner_class_frequency as cf
    from yupi.corpus.vocab import VOCAB
    from yupi.corpus.writer import read_split
    from yupi.learner.evaluate import surface_records
    m, d = tiny_r2_link
    k = 3
    windows = [w for w, _ in read_split(d, "test")]
    counts = cf.count_classes(windows, k, workers=2, chunk=50)
    n_long = sum(len(surface_records(tuple(VOCAB[t] for t in w))[1]) >= k for w in windows)
    assert sum(counts.values()) == n_long and n_long > 50 and len(counts) > 1
    keys = [cf.class_key(w, k) for w in windows]
    assert sum(kk is not None for kk in keys) == n_long
    assert all(kk in counts for kk in keys if kk is not None)


@pytest.fixture(scope="module")
def tiny_r2_link():
    import tempfile
    from fractions import Fraction
    from yupi.corpus.manifest import Manifest, Split
    from yupi.corpus.writer import generate
    root = tempfile.mkdtemp(prefix="yupi-link-")
    m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r2", run_key=b"\x05" * 32,
                     splits=(Split("train", 0, 16), Split("val", 1_000_000, 1_000_016), Split("test", 2_000_000, 2_000_200)),
                     git_commit="test")
    d, _ = generate(m, root, workers=2)
    return m, d


def test_release_actor_group_stats():
    """Exposure ratio 1 − mean excess / mean H*; None when H* is 0; se from the sample."""
    import learner_release_actor as ra
    s = ra.group_stats([(0.1, 1.0, 0.0), (0.3, 1.0, 0.2)])
    assert s["n"] == 2 and s["actor_excess"] == pytest.approx(0.2) and s["h_actor"] == 1.0
    assert s["exposure_ratio"] == pytest.approx(0.8) and s["kind_excess"] == pytest.approx(0.1)
    assert ra.group_stats([(0.0, 0.0, 0.0)])["exposure_ratio"] is None and ra.group_stats([]) is None
