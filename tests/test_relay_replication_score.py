"""The relay replication frozen scorer (scripts/relay_replication_score.py, SCORER_VERSION 1.0; design
docs/relay-replication-design-v0.1.md §2–§4). Synthetic only: planted per-seed L values for the sign test, hand-built
per-window arrays for the contrasts, and fake census raws / run dirs / manifests / ceiling tables / train splits in
tmp_path for the provenance gates. No real census is read here."""
import hashlib
import json
import math
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import relay_replication_score as S  # noqa: E402
from relay_paired import Gate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _L(n_pos, n=12, n_tie=0):
    """n_pos strictly positive values, n_tie exact zeros, the rest strictly negative."""
    pos = [0.001 * (j + 1) for j in range(n_pos)]
    tie = [0.0] * n_tie
    neg = [-0.0005 * (j + 1) for j in range(n - n_pos - n_tie)]
    return np.array(pos + tie + neg)


# ---- frozen constants ------------------------------------------------------------------

def test_frozen_constants():
    assert S.SCORER_VERSION == "1.0"
    assert S.RUNGS == ("r1", "r1R", "r1S")
    assert S.SEEDS == tuple(range(1, 13))
    assert S.PASS_K == 10 and S.BACK == -0.05 and S.FWD == 0.05
    assert S.FINAL_STEP == 117195 and S.RECIPE["epochs"] == 15
    assert S.FRESH_RUN == "0582ffbeb4693d27"
    assert S.N_WINDOWS == 84867
    assert set(S.TABLE_SHA256) == set(S.RUNGS) and set(S.TRAIN_SPLIT_SHA256) == set(S.RUNGS)
    assert S.EXACT_R == "docs/relay-exact-side-2026-09-30.json"
    assert len(S.EXACT_R_SHA256) == 64 and len(S.DIOTA_R_SHA256) == 64


def test_frozen_hashes_match_three_arm_v3():
    import three_arm_score_v3 as V3
    for r in S.RUNGS:
        assert S.TABLE_SHA256[r] == V3.TABLE_SHA256[r]
        assert S.TRAIN_SPLIT_SHA256[r] == V3.TRAIN_SPLIT_SHA256[r]
    assert S.RECIPE == V3.RECIPE


def test_frozen_relay_exact_side_sha_is_the_file_on_disk():
    assert hashlib.sha256((ROOT / S.EXACT_R).read_bytes()).hexdigest() == S.EXACT_R_SHA256
    es = json.loads((ROOT / S.EXACT_R).read_text())
    assert next(d for d in es["d_iota_kind_4"] if d["eps"] == S.EPS)["per_class_sha256"] == S.DIOTA_R_SHA256


# ---- binomial tail ---------------------------------------------------------------------

def test_binomial_tail_exact_values():
    assert S.binom_tail(10, 12) == Fraction(79, 4096)
    assert float(S.binom_tail(10, 12)) == pytest.approx(0.019287109375, abs=0)
    assert S.binom_tail(12, 12) == Fraction(1, 4096)
    assert S.binom_tail(11, 12) == Fraction(13, 4096)
    assert S.binom_tail(0, 12) == 1
    assert S.binom_tail(9, 12) == Fraction(299, 4096)


# ---- confirmatory sign test (pure) ------------------------------------------------------

@pytest.mark.parametrize("k", [10, 11, 12])
def test_planted_pass(k):
    c = S.score_confirmatory(_L(k))
    assert c["k"] == k and c["n"] == 12 and c["pass"] is True
    assert c["p_one_sided"] == pytest.approx(float(S.binom_tail(k, 12)), abs=0)
    assert c["p_exact"] == str(S.binom_tail(k, 12))
    assert c["interpretation"] == S.CLAIM_PASS
    assert c["locality_note"] is None


def test_planted_pass_p_values():
    assert S.score_confirmatory(_L(10))["p_one_sided"] == pytest.approx(0.019287109375, abs=1e-15)
    assert S.score_confirmatory(_L(12))["p_one_sided"] == 1 / 4096


def test_pass_text_is_the_design_claim():
    design = (ROOT / "docs/relay-replication-design-v0.1.md").read_text()
    quoted = " ".join(l[1:].strip() for l in design.splitlines() if l.startswith(">"))
    assert S.CLAIM_PASS.startswith("On the windows where an exact, ceiling-identical relay pushes")
    assert S.CLAIM_PASS in " ".join(quoted.split())


def test_planted_fail_nine():
    c = S.score_confirmatory(_L(9))
    assert c["k"] == 9 and c["pass"] is False
    assert c["interpretation"] == S.FAIL_TEXT == ("not replicated at the model level (non-answer; not evidence for "
                                                  "locality unless k ≤ 2)")
    assert c["locality_note"] is None
    assert c["p_one_sided"] == pytest.approx(299 / 4096, abs=0)


def test_ties_count_as_not_positive():
    c = S.score_confirmatory(_L(9, n_tie=3))          # 9 positive, 3 exactly zero: k = 9, fail
    assert c["k"] == 9 and c["n_ties"] == 3 and c["pass"] is False
    c = S.score_confirmatory(_L(10, n_tie=2))
    assert c["k"] == 10 and c["n_ties"] == 2 and c["pass"] is True
    c = S.score_confirmatory(np.zeros(12))
    assert c["k"] == 0 and c["n_ties"] == 12 and c["pass"] is False


@pytest.mark.parametrize("k", [0, 1, 2])
def test_locality_note_when_k_at_most_two(k):
    c = S.score_confirmatory(_L(k))
    assert c["pass"] is False and c["interpretation"] == S.FAIL_TEXT
    assert c["locality_note"] == S.LOCALITY_NOTE == ("locality direction: typical model is worse where information is "
                                                     "pushed back")


def test_no_locality_note_at_three():
    assert S.score_confirmatory(_L(3))["locality_note"] is None


def test_confirmatory_refuses_nonfinite():
    with pytest.raises(ValueError):
        S.score_confirmatory(np.array([0.1] * 11 + [np.nan]))


# ---- per-seed contrasts from per-window excess (pure) -----------------------------------

def test_seed_arrays_by_hand():
    #              back   back   fwd   fwd   zero  zero  small(not in any set)
    x = np.array([-0.3, -0.1, 0.2, 0.06, 0.0, 0.0, 0.01])
    z = np.array([0, 0, 0, 0, 1, 1, 0], bool)
    y1 = np.ones(7)
    yR = np.array([0.8, 0.9, 0.7, 0.9, 1.0, 0.98, 0.0])
    yS = np.array([0.95, 0.95, 1.0, 1.0, 1.0, 1.0, 0.0])
    y = {("r1", 4): y1, ("r1R", 4): yR, ("r1S", 4): yS}
    out = S.seed_arrays(y, x, z, [4])
    # D = y1 - yR: back 0.2, 0.1 (mean 0.15); fwd 0.3, 0.1 (0.2); zero 0, 0.02 (0.01)
    assert out["L"][0] == pytest.approx(0.14)
    assert out["R"][0] == pytest.approx(0.19)
    # DS = y1 - yS: back 0.05, 0.05; zero 0, 0
    assert out["LS"][0] == pytest.approx(0.05)
    assert out["sets"] == dict(back=2, forward=2, zero=2, n_windows=7)


def test_seed_arrays_boundaries_are_strict():
    x = np.array([-0.05, 0.05, -0.0500001, 0.0500001, 0.0])
    z = np.array([0, 0, 0, 0, 1], bool)
    y = {(r, 1): np.zeros(5) for r in S.RUNGS}
    out = S.seed_arrays(y, x, z, [1])
    assert out["sets"]["back"] == 1 and out["sets"]["forward"] == 1


def test_seed_arrays_zero_set_is_the_exact_flag_not_float_zero():
    x = np.array([-0.2, 0.3, 0.0, 0.0])
    z = np.array([0, 0, 0, 1], bool)                  # window 2 is float 0 but not flagged exact: in no set
    y = {("r1", 1): np.array([1.0, 0.0, 5.0, 0.0]), ("r1R", 1): np.zeros(4), ("r1S", 1): np.zeros(4)}
    out = S.seed_arrays(y, x, z, [1])
    assert out["L"][0] == pytest.approx(1.0) and out["sets"]["zero"] == 1


def test_seed_arrays_refuse_empty_or_inconsistent_sets():
    y = {(r, 1): np.zeros(3) for r in S.RUNGS}
    with pytest.raises(Gate, match="empty"):
        S.seed_arrays(y, np.array([0.2, 0.3, 0.0]), np.array([0, 0, 1], bool), [1])        # no back set
    with pytest.raises(Gate, match="empty"):
        S.seed_arrays(y, np.array([-0.2, 0.3, 0.0]), np.array([0, 0, 0], bool), [1])       # no zero set
    with pytest.raises(Gate, match="exact-zero"):
        S.seed_arrays(y, np.array([-0.2, 0.3, 0.0]), np.array([1, 0, 1], bool), [1])       # flagged but moved


# ---- score_seeds (pure) -----------------------------------------------------------------

def _score(k=10, n_boot=2000):
    L = _L(k)
    R = L + 0.002
    LS = L * 0.1
    return S.score_seeds(L, R, LS, S.SEEDS, dict(back=5, forward=6, zero=7, n_windows=20), n_boot=n_boot, rng_seed=3)


def test_score_seeds_structure():
    res = _score()
    assert res["scorer_version"] == "1.0"
    assert res["confirmatory"]["pass"] is True and res["confirmatory"]["k"] == 10
    d = res["descriptive"]
    assert d["label"] == S.DESCRIPTIVE_LABEL
    L = _L(10)
    assert d["L"]["mean"] == pytest.approx(L.mean())
    assert d["L"]["sd"] == pytest.approx(L.std(ddof=1))
    assert d["L"]["t"] == pytest.approx(L.mean() / (L.std(ddof=1) / math.sqrt(12)))
    lo, hi = d["L_bootstrap"]["ci"]
    assert lo <= L.mean() <= hi
    assert d["L_bootstrap"]["n_boot"] == 2000 and d["L_bootstrap"]["level"] == 0.95
    assert d["R"]["mean"] == pytest.approx((L + 0.002).mean())
    assert d["LS"]["note"] == S.SELF_COPY_NOTE == "self-copy: zero-entropy field, descriptive only (design §4)"
    assert [r["seed"] for r in d["per_seed"]] == list(S.SEEDS)
    assert d["per_seed"][0] == dict(seed=1, L=L[0], R=L[0] + 0.002, LS=L[0] * 0.1, L_positive=True)
    assert d["sets"] == dict(back=5, forward=6, zero=7, n_windows=20)


def test_bootstrap_is_reproducible_and_frozen():
    a, b = _score(n_boot=1000), _score(n_boot=1000)
    assert a["descriptive"]["L_bootstrap"] == b["descriptive"]["L_bootstrap"]
    assert S.N_BOOT == 10000 and S.CI_LEVEL == 0.95 and isinstance(S.RNG_SEED, int)


def test_bootstrap_ci_of_a_constant_is_the_constant():
    r = S.bootstrap_mean(np.full(12, 0.004), 500, 1)
    assert r["ci"][0] == pytest.approx(0.004) and r["ci"][1] == pytest.approx(0.004)


def test_confirmatory_does_not_depend_on_descriptive():
    """The verdict reads only the signs: a huge negative outlier does not move it."""
    L = _L(10)
    L[-1] = -100.0
    res = S.score_seeds(L, L, L, S.SEEDS, dict(back=1, forward=1, zero=1, n_windows=3), n_boot=200, rng_seed=1)
    assert res["confirmatory"]["pass"] is True and res["descriptive"]["L"]["mean"] < 0


# ---- CLI provenance gates on fake censuses ----------------------------------------------

RUN_KEY_HEX = "5631e4d23aa08338a656740e41ef6e8d873ec6c75696cd5adb9211fff077e00f"   # sha256[:16] = 0582ffbeb4693d27
SEEDS = (1, 2)
N_WIN = 10


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT, check=True).stdout.strip()


def _recipe_json():
    rj = {}
    for k, v in S.RECIPE.items():
        if "." in k:
            a, b = k.split(".")
            rj.setdefault(a, {})[b] = v
        else:
            rj[k] = v
    return rj


def _make_run(tmp, cd, rung, s, corpus, ids=range(N_WIN), pw=None, lines=None, rev=None):
    run = tmp / "runs" / f"{rung}-s{s}"
    run.mkdir(parents=True, exist_ok=True)
    rj = _recipe_json()
    rj.update(corpus_dir=str(corpus), seed=s, corpus_manifest_sha256=_sha(corpus / "manifest.json"),
              git_revision=rev or _git("rev-parse", "HEAD"), git_dirty=False)
    (run / "run.json").write_text(json.dumps(rj))
    (run / "log.jsonl").write_text("".join(json.dumps(dict(step=st, epoch=0)) + "\n" for st in (1000, S.FINAL_STEP)))
    (run / "ckpt.pt").write_bytes(f"{rung}{s}".encode())
    if pw is None:
        pw = cd / f"{rung}-s{s}.jsonl"
        kind = S.RUNGS.index(rung) * 0.1 + s * 0.01
        if lines is None:
            lines = [dict(i=i, key=0, by_field=dict(kind=kind + i * 1e-4)) for i in ids]
        pw.write_text("".join(json.dumps(r) + "\n" for r in lines))
    c = dict(run=str(run), step=S.FINAL_STEP, seed=s, corpus=str(corpus), rung=rung, eps="1", k=7, split="test",
             n=None, programs=S.PROGRAMS, law=dict(S.LAW), git="0" * 40,
             table_sha256=_sha(S.TABLES_DIR / S.table_name(rung)),
             checkpoint_sha256=_sha(run / "ckpt.pt"), per_window_file=str(pw), per_window_sha256=_sha(pw))
    (cd / f"{rung}-s{s}.json").write_text(json.dumps(c))
    return c


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A consistent fake world: 3 rungs × SEEDS censuses, runs (clean, one HEAD revision), corpora with train splits,
    ceiling tables. The frozen table / train-split sha256 constants and the window count are pointed at the fakes."""
    assert hashlib.sha256(bytes.fromhex(RUN_KEY_HEX)).hexdigest()[:16] == S.FRESH_RUN
    tables = tmp_path / "ceilings"
    tables.mkdir()
    tsha, ssha = {}, {}
    cd = tmp_path / "census"
    cd.mkdir()
    for rung in S.RUNGS:
        tp = tables / S.table_name(rung)
        tp.write_text(json.dumps(dict(table=rung)) + "\n")
        tsha[rung] = _sha(tp)
        corpus = tmp_path / "corpus" / f"c1prime-loop-40-8-2-{rung}-eps1" / S.FRESH_RUN
        corpus.mkdir(parents=True)
        (corpus / "manifest.json").write_text(json.dumps(dict(rung=rung, epsilon="1", run_key_hex=RUN_KEY_HEX)))
        for f in S.TRAIN_FILES:
            (corpus / f).write_bytes(f"{rung}:{f}".encode())
        ssha[rung] = {f: _sha(corpus / f) for f in S.TRAIN_FILES}
    monkeypatch.setattr(S, "TABLES_DIR", tables)
    monkeypatch.setattr(S, "TABLE_SHA256", tsha)
    monkeypatch.setattr(S, "TRAIN_SPLIT_SHA256", ssha)
    monkeypatch.setattr(S, "N_WINDOWS", N_WIN)
    for rung in S.RUNGS:
        corpus = tmp_path / "corpus" / f"c1prime-loop-40-8-2-{rung}-eps1" / S.FRESH_RUN
        for s in SEEDS:
            _make_run(tmp_path, cd, rung, s, corpus)
    return cd


def _edit(cd, name, **kw):
    p = cd / name
    c = json.loads(p.read_text())
    c.update(kw)
    p.write_text(json.dumps(c))


def _run_json(cd, name):
    c = json.loads((cd / name).read_text())
    p = Path(c["run"]) / "run.json"
    return p, json.loads(p.read_text())


def _set_run_json(cd, name, **kw):
    p, rj = _run_json(cd, name)
    for k, v in kw.items():
        if v is _DEL:
            rj.pop(k, None)
        else:
            rj[k] = v
    p.write_text(json.dumps(rj))


_DEL = object()


def _set_all_run_json(cd, **kw):
    for r in S.RUNGS:
        for s in SEEDS:
            _set_run_json(cd, f"{r}-s{s}.json", **kw)


def test_gates_pass_on_a_consistent_world(world):
    cen, ids, prov = S.gate_censuses(world, list(SEEDS))
    assert set(cen) == {(r, s) for r in S.RUNGS for s in SEEDS} and ids == list(range(N_WIN))
    assert prov["trainer_git"] == dict(field="git_revision", revision=_git("rev-parse", "HEAD"), git_dirty=False,
                                       ancestor_of_head=True, n_runs=len(S.RUNGS) * len(SEEDS))
    assert set(prov["train_split_sha256"]) == set(S.RUNGS)
    assert set(prov["table_sha256"]) == set(S.RUNGS)


# -- trainer revision (new in 1.0: mandatory) --

def test_revision_older_ancestor_passes(world):
    old = _git("rev-parse", "HEAD~1")
    _set_all_run_json(world, git_revision=old)
    _, _, prov = S.gate_censuses(world, list(SEEDS))
    assert prov["trainer_git"]["revision"] == old


def test_revision_missing_refused(world):
    _set_run_json(world, "r1S-s2.json", git_revision=_DEL)
    with pytest.raises(Gate, match="git_revision"):
        S.gate_censuses(world, list(SEEDS))


def test_revision_null_refused(world):
    _set_all_run_json(world, git_revision=None, git_dirty=None)
    with pytest.raises(Gate, match="git_revision"):
        S.gate_censuses(world, list(SEEDS))


def test_dirty_revision_refused(world):
    _set_run_json(world, "r1R-s1.json", git_dirty=True)
    with pytest.raises(Gate, match="dirty"):
        S.gate_censuses(world, list(SEEDS))


@pytest.mark.parametrize("val", [None, 0, "false", _DEL])
def test_dirty_flag_must_be_literal_false(world, val):
    _set_run_json(world, "r1-s2.json", git_dirty=val)
    with pytest.raises(Gate, match="dirty"):
        S.gate_censuses(world, list(SEEDS))


def test_mixed_revisions_refused(world):
    _set_run_json(world, "r1R-s2.json", git_revision=_git("rev-parse", "HEAD~1"))
    with pytest.raises(Gate, match="revisions"):
        S.gate_censuses(world, list(SEEDS))


def test_non_ancestor_revision_refused(world):
    _set_all_run_json(world, git_revision="1234567" * 5 + "89ab0")
    with pytest.raises(Gate, match="ancestor"):
        S.gate_censuses(world, list(SEEDS))


def test_revision_not_a_full_hash_refused(world):
    _set_all_run_json(world, git_revision=_git("rev-parse", "--short", "HEAD"))
    with pytest.raises(Gate, match="full commit hash"):
        S.gate_censuses(world, list(SEEDS))


# -- census set: rungs, seeds, extra files --

def test_gate_missing_seed(world):
    (world / "r1S-s2.json").unlink()
    with pytest.raises(Gate, match="missing"):
        S.gate_censuses(world, list(SEEDS))


def test_cli_scores_exactly_the_frozen_seeds(world, tmp_path):
    """The world holds seeds 1, 2; the CLI wants 1..12 and finds seed 3 missing."""
    with pytest.raises(Gate, match="missing"):
        S.main(["--census-dir", str(world), "--raw", str(tmp_path / "out.json")])
    assert not (tmp_path / "out.json").exists()


def test_gate_extra_seed_file(world):
    shutil.copy(world / "r1-s1.json", world / "r1-s9.json")
    with pytest.raises(Gate, match="outside"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_extra_rung_file(world):
    """A census raw for a rung outside r1, r1R, r1S (the three-arm decoy) is refused, not ignored."""
    shutil.copy(world / "r1R-s1.json", world / "r1D-s1.json")
    with pytest.raises(Gate, match="outside"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_wrong_rung_corpus(world, tmp_path):
    c = json.loads((world / "r1R-s1.json").read_text())
    other = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1S-eps1" / S.FRESH_RUN
    _set_run_json(world, "r1R-s1.json", corpus_dir=str(other), corpus_manifest_sha256=_sha(other / "manifest.json"))
    _edit(world, "r1R-s1.json", corpus=str(other))
    with pytest.raises(Gate, match="rung"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_census_rung_field_mismatch(world):
    _edit(world, "r1R-s2.json", rung="r1S")
    with pytest.raises(Gate, match="rung"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_wrong_seed_in_run_json(world):
    _set_run_json(world, "r1S-s2.json", seed=1)
    with pytest.raises(Gate, match="seed"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_duplicate_seed_argument(world):
    with pytest.raises(Gate, match="duplicate"):
        S.gate_censuses(world, [1, 1])


# -- windows --

def test_gate_wrong_window_count(world, monkeypatch):
    monkeypatch.setattr(S, "N_WINDOWS", N_WIN + 1)
    with pytest.raises(Gate, match="window count"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_duplicate_window_id(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1R-eps1" / S.FRESH_RUN
    lines = [dict(i=i, key=0, by_field=dict(kind=0.3)) for i in range(N_WIN)] + [dict(i=4, key=0,
                                                                                       by_field=dict(kind=9.0))]
    _make_run(tmp_path, world, "r1R", 2, corpus, lines=lines)
    with pytest.raises(Gate, match="duplicate window id"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_window_set_mismatch(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1S-eps1" / S.FRESH_RUN
    _make_run(tmp_path, world, "r1S", 2, corpus, ids=[i for i in range(N_WIN + 1) if i != 3])
    with pytest.raises(Gate, match="window"):
        S.gate_censuses(world, list(SEEDS))


def test_window_set_is_the_full_k7_test_split(monkeypatch):
    monkeypatch.setattr(S, "N_WINDOWS", 4)
    n_rec = {0: 8, 1: 8, 2: 5, 3: 9, 4: 7, 5: 8}
    S.check_window_set(n_rec, [0, 1, 3, 5])
    with pytest.raises(Gate, match="window count"):
        S.check_window_set(n_rec, [0, 1, 3])
    with pytest.raises(Gate, match="window"):
        S.check_window_set(n_rec, [0, 1, 3, 4])
    monkeypatch.setattr(S, "N_WINDOWS", 5)
    with pytest.raises(Gate, match="window count"):
        S.check_window_set(n_rec, [0, 1, 3, 5])


@pytest.mark.parametrize("kw", [dict(n=500), dict(k=5), dict(split="val")])
def test_gate_not_full_k7_test_census(world, kw):
    _edit(world, "r1-s1.json", **kw)
    with pytest.raises(Gate):
        S.gate_censuses(world, list(SEEDS))


# -- recipe, training, corpus, tables, splits (carried from v3) --

@pytest.mark.parametrize("field,value", [("model.n_layer", 2), ("epochs", 5), ("lr", 0.002), ("steps_total", 100000),
                                         ("model.d_model", 64)])
def test_gate_recipe_mismatch(world, field, value):
    p, rj = _run_json(world, "r1R-s2.json")
    if "." in field:
        a, b = field.split(".")
        rj[a][b] = value
    else:
        rj[field] = value
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="recipe"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_recipe_field_missing(world):
    p, rj = _run_json(world, "r1-s1.json")
    del rj["model"]["n_head"]
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="recipe"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_unfinished_training(world):
    c = json.loads((world / "r1-s2.json").read_text())
    (Path(c["run"]) / "log.jsonl").write_text(json.dumps(dict(step=50000)) + "\n")
    with pytest.raises(Gate, match="step"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_census_not_at_final_step(world):
    _edit(world, "r1-s2.json", step=100000)
    with pytest.raises(Gate, match="step"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_wrong_corpus_run(world):
    c = json.loads((world / "r1-s1.json").read_text())
    m = Path(c["corpus"]) / "manifest.json"
    m.write_text(json.dumps(dict(rung="r1", epsilon="1", run_key_hex="00" * 32)))
    for s in SEEDS:
        _set_run_json(world, f"r1-s{s}.json", corpus_manifest_sha256=_sha(m))
    with pytest.raises(Gate, match="corpus run"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_checkpoint_changed_after_census(world):
    c = json.loads((world / "r1R-s1.json").read_text())
    (Path(c["run"]) / "ckpt.pt").write_bytes(b"retrained")
    with pytest.raises(Gate, match="checkpoint"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_duplicate_census_content(world):
    c1 = json.loads((world / "r1S-s1.json").read_text())
    _edit(world, "r1S-s2.json", per_window_file=c1["per_window_file"], per_window_sha256=c1["per_window_sha256"])
    with pytest.raises(Gate, match="duplicate"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_table_changed_on_disk(world):
    (S.TABLES_DIR / S.table_name("r1R")).write_text("{\"table\": \"edited\"}\n")
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_table_not_the_frozen_one(world, monkeypatch):
    monkeypatch.setitem(S.TABLE_SHA256, "r1S", "cd" * 32)
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_train_split_changed(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1R-eps1" / S.FRESH_RUN
    (corpus / "train.tokens").write_bytes(b"regenerated")
    with pytest.raises(Gate, match="train split"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_seeds_of_a_rung_on_different_corpora(world, tmp_path):
    src = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    dst = tmp_path / "corpus2" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    shutil.copytree(src, dst)
    _make_run(tmp_path, world, "r1", 2, dst)
    with pytest.raises(Gate, match="different corpora"):
        S.gate_censuses(world, list(SEEDS))


# -- relay exact side --

def test_relay_exact_side_gate_passes_on_the_frozen_file():
    prov = S.check_relay_exact(S.EXACT_R)
    assert prov["exact_side_sha256"] == S.EXACT_R_SHA256


def test_relay_exact_side_gate_refuses_other_bytes(tmp_path):
    p = tmp_path / "es.json"
    p.write_text((ROOT / S.EXACT_R).read_text() + "\n")
    with pytest.raises(Gate, match="sha256"):
        S.check_relay_exact(p)


def test_relay_exact_side_gate_refuses_other_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "DIOTA_R_SHA256", "ab" * 32)
    with pytest.raises(Gate, match="cache"):
        S.check_relay_exact(S.EXACT_R)


# -- CLI --

def test_cli_refuses_to_overwrite(world, tmp_path):
    raw = tmp_path / "out.json"
    raw.write_text("{}")
    with pytest.raises(SystemExit, match="overwrite"):
        S.main(["--census-dir", str(world), "--raw", str(raw)])


@pytest.mark.parametrize("extra", [["--seeds", "1", "2"], ["--seed", "1"], ["--n-boot", "100"], ["--rng-seed", "7"],
                                   ["--pass-k", "9"], ["--back", "-0.1"], ["--level", "0.9"]])
def test_cli_refuses_any_setting_override(tmp_path, extra):
    raw = tmp_path / "out.json"
    with pytest.raises(SystemExit) as e:
        S.main(["--census-dir", str(tmp_path), "--raw", str(raw)] + extra)
    assert e.value.code == 2 and not raw.exists()


def test_frozen_settings_flag():
    assert S.frozen_settings(S.SEEDS, S.N_BOOT, S.RNG_SEED) is True
    assert S.frozen_settings((1, 2), S.N_BOOT, S.RNG_SEED) is False
    assert S.frozen_settings(S.SEEDS, 100, S.RNG_SEED) is False
    assert S.frozen_settings(S.SEEDS, S.N_BOOT, 7) is False


# ---- cross-rung class pairing (three rungs) ---------------------------------------------

from yupi.interfaces import MASKED, window_map  # noqa: E402
from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import serial_key  # noqa: E402
from yupi.records import Record  # noqa: E402


def _pair_world(n_win=40, seeds=(1, 2), rng_seed=0):
    rng = np.random.default_rng(rng_seed)
    kinds, threads = ("DISPATCH", "STEP", "ACQUIRE"), ("T7", "T19")
    pool = [(bool(rng.integers(2)), tuple(Record(kinds[rng.integers(3)], threads[rng.integers(2)], MASKED, MASKED,
                                                 MASKED) for _ in range(8))) for _ in range(12)]
    recs = {r: {} for r in S.RUNGS}
    for i in range(n_win):
        reset, r1 = pool[rng.integers(len(pool))]
        recs["r1"][i] = (reset, r1)
        for arm in S.ARMS:
            recs[arm][i] = (reset, window_map(arm)(r1))
    rows = {}
    for rung in S.RUNGS:
        cid = {}
        for s in seeds:
            rows[(rung, s)] = {i: dict(i=i, key=cid.setdefault(serial_key((recs[rung][i][0],
                                                                            pattern_all(recs[rung][i][1][:7])[0])),
                                                               len(cid)))
                               for i in range(n_win)}
    return recs, rows, list(range(n_win))


def test_class_pairing_passes_and_returns_r1_keys():
    recs, rows, ids = _pair_world()
    keys = S.check_class_pairing(recs, rows, ids)
    assert keys == [serial_key((recs["r1"][i][0], pattern_all(recs["r1"][i][1][:7])[0])) for i in ids]


@pytest.mark.parametrize("arm", ["r1R", "r1S"])
def test_class_pairing_refuses_an_unpaired_arm_window(arm):
    recs, rows, ids = _pair_world()
    other = recs["r1"][5][1]
    recs[arm][3] = (recs[arm][3][0], window_map(arm)(other))
    if recs[arm][3][1] == window_map(arm)(recs["r1"][3][1]):
        pytest.skip("windows 3 and 5 coincide")
    with pytest.raises(Gate, match="pair"):
        S.check_class_pairing(recs, rows, ids)


def test_class_pairing_refuses_a_census_that_merges_classes():
    recs, rows, ids = _pair_world()
    r = rows[("r1R", 2)]
    a, b = next((i, j) for i in ids for j in ids if r[i]["key"] != r[j]["key"])
    r[b] = dict(r[b], key=r[a]["key"])
    with pytest.raises(Gate, match="class"):
        S.check_class_pairing(recs, rows, ids)
