"""The three-arm v0.3 frozen scorer (scripts/three_arm_score_v3.py, SCORER_VERSION 3.0; prereg v0.3 §2–§3).
Synthetic only: planted per-seed contrasts for the claims, known t quantiles, and fake census raws / run dirs /
manifests / ceiling tables / train splits in tmp_path for the CLI's provenance gates. No real census is read here."""
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import three_arm_score_v3 as S  # noqa: E402
from relay_paired import Gate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MARGINS = {"field_interaction": 0.002, "field": 0.001}
N = 12
MR, MD = 0.20, 0.15          # mean |Δι| on each arm's moved set
KR_BIT = 0.03                # planted relay per-bit effect: K_R ≈ 0.006


def _seeds(rho, n=N, sd=0.0004, rng_seed=1, ks_shift=(0.0, 0.0), f_mean=0.0):
    rng = np.random.default_rng(rng_seed)
    K_R = MR * KR_BIT + ks_shift[0] + rng.normal(0, sd, n)          # δ_A (field × class) enters K_A and KS_A
    K_D = MD * KR_BIT * rho + ks_shift[1] + rng.normal(0, sd, n)
    KS_R = ks_shift[0] + rng.normal(0, 0.0003, n)
    KS_D = ks_shift[1] + rng.normal(0, 0.0003, n)
    F = f_mean + rng.normal(0, 0.0003, n)
    return K_R, K_D, KS_R, KS_D, F


def _score(K_R, K_D, KS_R, KS_D, F, n_boot=4000):
    return S.score_seeds(K_R, K_D, KS_R, KS_D, MR, MD, F, MARGINS, n_boot=n_boot, rng_seed=5)


def _noise(rng_seed, sd=0.0004, n=N):
    x = np.random.default_rng(rng_seed).normal(0, sd, n)
    return x - x.mean()                                              # mean exactly 0: t exactly 0


# ---- t distribution -------------------------------------------------------------------

@pytest.mark.parametrize("p,df,q", [(0.95, 11, 1.7959), (0.975, 11, 2.2010), (0.95, 2, 2.9200),
                                    (0.975, 7, 2.3646), (0.95, 30, 1.6973)])
def test_t_quantiles_known_values(p, df, q):
    assert S.t_ppf(p, df) == pytest.approx(q, abs=5e-4)
    assert S.t_cdf(q, df) == pytest.approx(p, abs=1e-4)


def test_t_cdf_closed_forms():
    assert S.t_cdf(1.0, 1) == pytest.approx(0.75, abs=1e-10)                  # Cauchy
    assert S.t_cdf(0.0, 5) == pytest.approx(0.5, abs=1e-12)
    for t in (-3.0, -0.4, 0.7, 2.5):                                           # df = 2 closed form
        assert S.t_cdf(t, 2) == pytest.approx(0.5 + t / (2 * math.sqrt(2 + t * t)), abs=1e-10)
    assert S.t_cdf(-1.3, 9) == pytest.approx(1 - S.t_cdf(1.3, 9), abs=1e-12)
    assert S.t_ppf(0.05, 11) == pytest.approx(-S.t_ppf(0.95, 11), abs=1e-9)


def test_frozen_settings():
    assert S.SCORER_VERSION == "3.0"
    assert S.SEEDS == tuple(range(1, 13))
    assert S.TAU == 0.1 and S.N_BOOT == 10000 and S.CI_LEVEL == 0.95 and S.TRIM == 0.2
    assert S.CLAIM_T == 3.0
    assert S.CLAIMS == ("C1", "C2", "C3")
    assert S.MARGINS == {"field_interaction": 0.002, "field": 0.001} == MARGINS


def test_one_sided_false_positive_rate_at_t3_df11():
    """prereg v0.3 §2: about 0.006 per claim under a Gaussian null."""
    assert 1 - S.t_cdf(3.0, 11) == pytest.approx(0.006, abs=0.001)


# ---- confirmatory claims (v0.3 §2) ------------------------------------------------------

def test_claims_statistics_are_K_R_Kp_R_Kp_D():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    c = S.score_claims(K_R, K_D, KS_R, KS_D)
    for name, x in (("C1", K_R), ("C2", K_R - KS_R), ("C3", K_D - KS_D)):
        s = c[name]
        assert s["mean"] == pytest.approx(float(np.mean(x)))
        assert s["sd"] == pytest.approx(float(np.std(x, ddof=1)))
        assert s["se"] == pytest.approx(float(np.std(x, ddof=1)) / math.sqrt(N))
        assert s["t"] == pytest.approx(s["mean"] / s["se"])
        assert s["df"] == N - 1 and s["threshold"] == 3.0
        assert s["p_one_sided"] == pytest.approx(1 - S.t_cdf(s["t"], N - 1))
        assert s["pass"] is True
    assert c["C1"]["statistic"] == "K_R" and c["C2"]["statistic"] == "K'_R" and c["C3"]["statistic"] == "K'_D"


def test_claim_threshold_is_inclusive_t_ge_3():
    x = np.array([1.0, -1.0] * 6)
    x = x - x.mean()
    se = np.std(x, ddof=1) / math.sqrt(N)
    c = S.score_claims(x + 3.0 * se, x + 2.999 * se, np.zeros(N), np.zeros(N))
    assert c["C1"]["t"] == pytest.approx(3.0) and c["C1"]["pass"] is True
    assert c["C3"]["pass"] is False


def test_c3_passes_when_c1_and_c2_fail():
    """No gating chain: the decoy claim is scored even when the relay neither replicates nor beats the self-copy."""
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    K_R = _noise(3)                     # t(K_R) = 0
    KS_R = K_R.copy()                   # K'_R = 0
    c = S.score_claims(K_R, K_D, KS_R, KS_D)
    assert not c["C1"]["pass"] and not c["C2"]["pass"] and c["C3"]["pass"]
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["claims"]["C3"]["pass"] is True


def test_c2_passes_when_c3_fails():
    K_R, K_D, KS_R, KS_D, F = _seeds(0.0)
    K_D = KS_D + _noise(4)              # K'_D mean exactly 0
    c = S.score_claims(K_R, K_D, KS_R, KS_D)
    assert c["C1"]["pass"] and c["C2"]["pass"] and not c["C3"]["pass"]


def test_c2_passes_when_c1_fails():
    """C1 is K_R against r1; C2 is K'_R against the self-copy. A field cost shared by every field-bearing rung (δ < 0
    in K and KS alike) can sink K_R while K'_R stands."""
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0, ks_shift=(-0.006, 0.0))
    c = S.score_claims(K_R, K_D, KS_R, KS_D)
    assert not c["C1"]["pass"] and c["C2"]["pass"]


def test_c1_passes_c2_fails_note():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    KS_R = K_R + _noise(21)             # the self-copy matches the relay
    c = S.score_claims(K_R, K_D, KS_R, KS_D)
    assert c["C1"]["pass"] and not c["C2"]["pass"]
    assert c["note"] == S.NOTE_C1_NOT_C2
    assert "not distinguishable from carrying any field" in S.NOTE_C1_NOT_C2
    c2 = S.score_claims(*_seeds(1.0)[:4])
    assert c2["note"] is None


def test_interpretation_strings_are_fixed():
    assert set(S.INTERPRETATION) == {"C1", "C2", "C3"}
    for k in S.CLAIMS:
        assert set(S.INTERPRETATION[k]) == {True, False}
    c3_fail = S.INTERPRETATION["C3"][False]
    assert c3_fail.startswith("no claim")
    assert "not evidence for H_bind" in c3_fail
    assert "H_bind" not in c3_fail.replace("not evidence for H_bind", "").replace("a pure H_bind is not confirmable", "")
    assert "H_move holds at least in part" in S.INTERPRETATION["C3"][True]
    K_R, K_D, KS_R, KS_D, F = _seeds(0.0)
    K_D = KS_D + _noise(4)
    c = S.score_claims(K_R, K_D, KS_R, KS_D)
    assert c["C3"]["interpretation"] == c3_fail
    assert c["C1"]["interpretation"] == S.INTERPRETATION["C1"][True]
    neg = S.score_claims(*_seeds(-1.0)[:4])                          # a decoy that hurts: still "no claim"
    assert neg["C3"]["t"] < -3 and neg["C3"]["interpretation"] == c3_fail


def test_c3_carries_its_rival_assumption():
    c = S.score_claims(*_seeds(1.0)[:4])
    assert "δ_D" in c["C3"]["assumption"]


def test_claims_input_validation():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    with pytest.raises(ValueError):
        S.score_claims(K_R, K_D[:-1], KS_R, KS_D)
    with pytest.raises(ValueError):
        S.score_claims(K_R[:1], K_D[:1], KS_R[:1], KS_D[:1])
    bad = K_R.copy()
    bad[0] = np.nan
    with pytest.raises(ValueError):
        S.score_claims(bad, K_D, KS_R, KS_D)


# ---- descriptive block (v0.3 §3): never a verdict ---------------------------------------

def test_result_has_claims_and_a_labelled_descriptive_block():
    r = _score(*_seeds(1.0))
    assert set(r["claims"]) >= {"C1", "C2", "C3"}
    d = r["descriptive"]
    assert d["label"] == S.DESCRIPTIVE_LABEL and "not scored" in d["label"]
    assert d["v21_reading"]["label"] == "descriptive (not identified, prereg v0.3 §1)"
    assert set(d) >= {"rho", "v21_reading", "self_copy_contrast", "H_field", "per_seed", "summary"}
    assert "reading" not in r and "verdict" not in r              # no top-level mechanism verdict


def test_rho_descriptive_when_denominator_positive():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    r = _score(K_R, K_D, KS_R, KS_D, F)
    rho = r["descriptive"]["rho"]
    assert rho["point"] == pytest.approx(S.trimmed_mean((K_D - KS_D) / MD) / S.trimmed_mean((K_R - KS_R) / MR))
    assert rho["level"] == 0.95 and rho["ci"][0] < 1 < rho["ci"][1]
    assert r["descriptive"]["rho_null_reason"] is None
    assert r["descriptive"]["v21_reading"]["reading"] == "move-dominant"


def test_rho_null_when_trimmed_denominator_nonpositive():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    KS_R = K_R + 0.001 + _noise(8)                                  # K'_R ≈ −0.001 every seed
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["descriptive"]["rho"] is None
    assert "T(k'_R) <= 0" in r["descriptive"]["rho_null_reason"]
    assert r["claims"]["C3"]["pass"]                                 # claims unaffected


def test_rho_reported_even_when_c1_fails():
    """Descriptive: the ratio does not wait on any claim, only on a positive trimmed denominator."""
    _, K_D, _, KS_D, F = _seeds(1.0)
    K_R = _noise(9, 0.002)                                           # mean exactly 0: C1 fails
    Kp_R = MR * KR_BIT + _noise(10, 0.0002)                          # K'_R ≈ 0.006 every seed
    KS_R = K_R - Kp_R
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert not r["claims"]["C1"]["pass"] and r["claims"]["C2"]["pass"]
    assert r["descriptive"]["rho"] is not None
    assert r["descriptive"]["v21_reading"]["reading"] == "no replication"


@pytest.mark.parametrize("rho,want", [(1.0, "move-dominant"), (0.0, "binding-dominant"), (0.5, "unresolved")])
def test_v21_reading_reproduced_descriptively(rho, want):
    r = _score(*_seeds(rho))
    assert r["descriptive"]["v21_reading"]["reading"] == want
    assert r["claims"]["C1"]["pass"] and r["claims"]["C2"]["pass"]


def test_v21_reading_no_relay_gain():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    KS_R = K_R + _noise(21)
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["descriptive"]["v21_reading"]["reading"] == S.NO_RELAY_GAIN


def test_field_class_interaction_cancels_in_the_sc_controlled_contrast():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0, ks_shift=(0.006, -0.006))
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["descriptive"]["rho"]["point"] == pytest.approx(1.0, abs=0.15)
    assert r["claims"]["C3"]["pass"] and r["claims"]["C2"]["pass"]
    assert not r["descriptive"]["self_copy_contrast"]["KS_R"]["equivalent"]


def test_self_copy_contrast_and_h_field_descriptive():
    r0 = _score(*_seeds(1.0, f_mean=0.0))
    assert r0["descriptive"]["H_field"]["result"] == "equivalent"
    r1 = _score(*_seeds(1.0, f_mean=0.004))
    assert r1["descriptive"]["H_field"]["result"] == "not equivalent"
    assert [r1["claims"][c]["pass"] for c in S.CLAIMS] == [r0["claims"][c]["pass"] for c in S.CLAIMS]
    sc = r0["descriptive"]["self_copy_contrast"]
    assert set(sc) >= {"KS_R", "KS_D"} and "t" in sc["KS_R"] and sc["KS_R"]["margin"] == 0.002


def test_per_seed_values_are_reported():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    r = _score(K_R, K_D, KS_R, KS_D, F)
    ps = r["descriptive"]["per_seed"]
    assert ps["K_R"] == pytest.approx(list(K_R))
    assert ps["Kp_R"] == pytest.approx(list(K_R - KS_R))
    assert ps["Kp_D"] == pytest.approx(list(K_D - KS_D))
    assert ps["kp_D"] == pytest.approx(list((K_D - KS_D) / MD))
    assert ps["F"] == pytest.approx(list(F))


def test_trimmed_mean_drops_floor_fifth_each_end():
    x = np.array([100.0, -100.0, 1, 2, 3, 4, 5, 6, 7, 8, 50.0, -50.0])
    assert S.trimmed_mean(x) == pytest.approx(4.5)
    assert S.trimmed_mean(np.array([1.0, 2.0, 30.0])) == pytest.approx(11.0)


def test_bootstrap_is_deterministic_and_resamples_jointly():
    kR = np.array([0.01, 0.03, 0.05, 0.02, 0.04, 0.06])
    res = S.bootstrap_rho(kR, 0.5 * kR, n_boot=2000, rng_seed=0)
    assert res["ci"][0] == pytest.approx(0.5) and res["ci"][1] == pytest.approx(0.5)
    assert S.bootstrap_rho(kR, 0.3 * kR + 0.001, 500, 3) == S.bootstrap_rho(kR, 0.3 * kR + 0.001, 500, 3)


def test_score_seeds_input_validation():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    with pytest.raises(ValueError):
        S.score_seeds(K_R, K_D, KS_R, KS_D, 0.0, MD, F, MARGINS)
    with pytest.raises(ValueError):
        S.score_seeds(K_R, K_D, KS_R, KS_D, MR, MD, F, {"field": 0.001})
    with pytest.raises(ValueError):
        S.score_seeds(K_R, K_D, KS_R, KS_D, MR, MD, F[:-1], MARGINS)


# ---- per-seed arrays from per-window excess (pure) ------------------------------------

def test_seed_arrays_by_hand():
    xR, zR = np.array([0.3, 0.5, 0.0, 0.05, 0.0, 0.0]), np.array([0, 0, 0, 0, 1, 1], bool)
    xD, zD = np.array([0.0, 0.08, 0.2, 0.0, 0.0, 0.01]), np.array([0, 0, 0, 1, 1, 0], bool)
    y1 = np.ones(6)
    yR = np.array([0.8, 0.6, 1.0, 1.0, 1.0, 1.0])
    yD = np.array([1.0, 1.0, 0.9, 1.0, 1.0, 1.0])
    yS = np.array([1.0, 1.0, 1.0, 1.0, 0.98, 0.98])
    y = {("r1", 7): y1, ("r1R", 7): yR, ("r1D", 7): yD, ("r1S", 7): yS}
    out = S.seed_arrays(y, {"r1R": (xR, zR), "r1D": (xD, zD)}, [7], tau=0.1)
    assert out["K_R"][0] == pytest.approx(0.3)
    assert out["K_D"][0] == pytest.approx(0.1)
    assert out["KS_R"][0] == pytest.approx(-0.02)
    assert out["KS_D"][0] == pytest.approx(-0.01)
    assert out["mR"] == pytest.approx(0.4) and out["mD"] == pytest.approx(0.2)
    assert out["F"][0] == pytest.approx(0.04 / 6)


def test_seed_arrays_refuse_empty_or_inconsistent_sets():
    x, z = np.array([0.0, 0.0]), np.array([1, 1], bool)
    y = {(r, 1): np.zeros(2) for r in S.RUNGS}
    with pytest.raises(Gate):
        S.seed_arrays(y, {"r1R": (x, z), "r1D": (np.array([0.5, 0.0]), z)}, [1], tau=0.1)
    with pytest.raises(Gate):
        S.seed_arrays(y, {"r1R": (np.array([0.5, 0.0]), np.array([1, 1], bool)),
                          "r1D": (np.array([0.5, 0.0]), np.array([0, 1], bool))}, [1], tau=0.1)


# ---- CLI provenance gates on fake censuses ----------------------------------------------

RUN_KEY_HEX = "5631e4d23aa08338a656740e41ef6e8d873ec6c75696cd5adb9211fff077e00f"   # sha256[:16] = 0582ffbeb4693d27
SEEDS = (1, 2)
N_WIN = 10


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT, check=True).stdout.strip()


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A consistent fake world: 4 rungs × SEEDS censuses, runs, corpora with train splits, ceiling tables. The frozen
    table and train-split sha256 constants are pointed at the fake files."""
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
    for rung in S.RUNGS:
        corpus = tmp_path / "corpus" / f"c1prime-loop-40-8-2-{rung}-eps1" / S.FRESH_RUN
        for s in SEEDS:
            _make_run(tmp_path, cd, rung, s, corpus)
    return cd


def _recipe_json():
    rj = {}
    for k, v in S.RECIPE.items():
        if "." in k:
            a, b = k.split(".")
            rj.setdefault(a, {})[b] = v
        else:
            rj[k] = v
    return rj


def _make_run(tmp, cd, rung, s, corpus, ids=range(N_WIN), pw=None, lines=None):
    run = tmp / "runs" / f"{rung}-s{s}"
    run.mkdir(parents=True, exist_ok=True)
    rj = _recipe_json()
    rj.update(corpus_dir=str(corpus), seed=s, corpus_manifest_sha256=_sha(corpus / "manifest.json"))
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


def _edit(cd, name, **kw):
    p = cd / name
    c = json.loads(p.read_text())
    c.update(kw)
    p.write_text(json.dumps(c))


def _run_json(cd, name):
    c = json.loads((cd / name).read_text())
    p = Path(c["run"]) / "run.json"
    return p, json.loads(p.read_text())


def _set_all_run_json(cd, **kw):
    for r in S.RUNGS:
        for s in SEEDS:
            p, rj = _run_json(cd, f"{r}-s{s}.json")
            rj.update(kw)
            p.write_text(json.dumps(rj))


def test_gates_pass_on_a_consistent_world(world):
    cen, ids, prov = S.gate_censuses(world, list(SEEDS))
    assert set(cen) == {(r, s) for r in S.RUNGS for s in SEEDS} and ids == list(range(N_WIN))
    assert prov["trainer_git"]["recorded"] is False
    assert set(prov["train_split_sha256"]) == set(S.RUNGS)
    assert set(prov["table_sha256"]) == set(S.RUNGS)


# -- new in 3.0: duplicate window ids (Codex round 3) --

def test_gate_duplicate_window_id_refused(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1D-eps1" / S.FRESH_RUN
    lines = [dict(i=i, key=0, by_field=dict(kind=0.3 + i * 1e-4)) for i in range(N_WIN)]
    lines.append(dict(i=4, key=0, by_field=dict(kind=9.0)))       # a second row for window 4: dict overwrite hides it
    _make_run(tmp_path, world, "r1D", 2, corpus, lines=lines)
    with pytest.raises(Gate, match="duplicate window id"):
        S.gate_censuses(world, list(SEEDS))


def test_load_census_refuses_duplicate_ids_directly(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    lines = [dict(i=0, key=0, by_field=dict(kind=0.1)), dict(i=0, key=0, by_field=dict(kind=0.1))]
    _make_run(tmp_path, world, "r1", 1, corpus, lines=lines)
    with pytest.raises(Gate, match="duplicate window id"):
        S.load_census(world / "r1-s1.json")


def test_load_census_refuses_row_without_id(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    _make_run(tmp_path, world, "r1", 1, corpus, lines=[dict(key=0, by_field=dict(kind=0.1))])
    with pytest.raises(Gate, match="window id"):
        S.load_census(world / "r1-s1.json")


def test_load_census_refuses_per_window_sha_mismatch(world):
    c = json.loads((world / "r1-s1.json").read_text())
    Path(c["per_window_file"]).write_text(Path(c["per_window_file"]).read_text() + "\n")
    with pytest.raises(Gate, match="sha256"):
        S.load_census(world / "r1-s1.json")


# -- new in 3.0: ceiling table sha256 --

def test_gate_table_changed_on_disk(world):
    (S.TABLES_DIR / S.table_name("r1R")).write_text("{\"table\": \"edited\"}\n")
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_census_records_other_table_sha(world):
    _edit(world, "r1D-s1.json", table_sha256="ab" * 32)
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_table_not_the_frozen_one(world, monkeypatch):
    """The census and the disk agree, but on a table that is not the frozen one."""
    monkeypatch.setitem(S.TABLE_SHA256, "r1S", "cd" * 32)
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_table_missing(world):
    (S.TABLES_DIR / S.table_name("r1")).unlink()
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


@pytest.mark.parametrize("kw", [dict(programs="c1-loop"), dict(law=dict(T_ep=40, L=8, B=3)), dict(table_sha256=None)])
def test_gate_census_table_identity_fields(world, kw):
    _edit(world, "r1-s2.json", **kw)
    with pytest.raises(Gate, match="table"):
        S.gate_censuses(world, list(SEEDS))


def test_table_name_and_frozen_hashes():
    assert S.table_name("r1D") == "c1prime-loop-40-8-2-r1D-eps1-k7.jsonl"
    assert set(S.TABLE_SHA256) == set(S.RUNGS) and all(len(v) == 64 for v in S.TABLE_SHA256.values())
    assert set(S.TRAIN_SPLIT_SHA256) == set(S.RUNGS)
    assert S.TRAIN_FILES == ("train.tokens", "train.index", "train.table.jsonl")
    assert all(set(v) == set(S.TRAIN_FILES) for v in S.TRAIN_SPLIT_SHA256.values())


# -- new in 3.0: trainer git revision --

def test_trainer_revision_consistent_and_ancestor_passes(world):
    head = _git("rev-parse", "HEAD~1")
    _set_all_run_json(world, git_commit=head)
    _, _, prov = S.gate_censuses(world, list(SEEDS))
    assert prov["trainer_git"] == dict(recorded=True, field="git_commit", revision=head, ancestor_of_head=True)


def test_trainer_revision_mismatch_refused(world):
    _set_all_run_json(world, git_commit=_git("rev-parse", "HEAD"))
    p, rj = _run_json(world, "r1R-s2.json")
    rj["git_commit"] = _git("rev-parse", "HEAD~1")
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="trainer"):
        S.gate_censuses(world, list(SEEDS))


def test_trainer_revision_partial_refused(world):
    _set_all_run_json(world, git_commit=_git("rev-parse", "HEAD"))
    p, rj = _run_json(world, "r1S-s1.json")
    del rj["git_commit"]
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="trainer"):
        S.gate_censuses(world, list(SEEDS))


def test_trainer_revision_not_ancestor_refused(world):
    _set_all_run_json(world, git_commit="1234567" * 5 + "89ab0")
    with pytest.raises(Gate, match="ancestor"):
        S.gate_censuses(world, list(SEEDS))


@pytest.mark.parametrize("suffix", ["+dirty"])
def test_trainer_revision_dirty_refused(world, suffix):
    _set_all_run_json(world, git_commit=_git("rev-parse", "HEAD") + suffix)
    with pytest.raises(Gate, match="trainer"):
        S.gate_censuses(world, list(SEEDS))


def test_trainer_revision_two_field_names_refused(world):
    _set_all_run_json(world, git_commit=_git("rev-parse", "HEAD"), git=_git("rev-parse", "HEAD~1"))
    with pytest.raises(Gate, match="trainer"):
        S.gate_censuses(world, list(SEEDS))


# -- new in 3.0: train split bytes --

def test_gate_train_split_changed(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1D-eps1" / S.FRESH_RUN
    (corpus / "train.tokens").write_bytes(b"regenerated")
    with pytest.raises(Gate, match="train split"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_train_split_missing(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    (corpus / "train.index").unlink()
    with pytest.raises(Gate, match="train split"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_train_split_not_the_frozen_one(world, monkeypatch):
    monkeypatch.setitem(S.TRAIN_SPLIT_SHA256, "r1R", dict(S.TRAIN_SPLIT_SHA256["r1R"], **{"train.index": "ef" * 32}))
    with pytest.raises(Gate, match="train split"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_seeds_of_a_rung_on_different_corpora(world, tmp_path):
    """All seeds of a rung must point at the same train files: a byte-identical copy elsewhere is still refused."""
    src = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    dst = tmp_path / "corpus2" / "c1prime-loop-40-8-2-r1-eps1" / S.FRESH_RUN
    shutil.copytree(src, dst)
    _make_run(tmp_path, world, "r1", 2, dst)
    with pytest.raises(Gate, match="different corpora"):
        S.gate_censuses(world, list(SEEDS))


# -- carried over from 2.1 --

def test_gate_wrong_rung(world, tmp_path):
    c = json.loads((world / "r1D-s1.json").read_text())
    other = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1S-eps1" / S.FRESH_RUN
    run = Path(c["run"])
    rj = json.loads((run / "run.json").read_text())
    rj.update(corpus_dir=str(other), corpus_manifest_sha256=_sha(other / "manifest.json"))
    (run / "run.json").write_text(json.dumps(rj))
    _edit(world, "r1D-s1.json", corpus=str(other))
    with pytest.raises(Gate, match="rung"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_census_rung_field_mismatch(world):
    _edit(world, "r1R-s2.json", rung="r1D")
    with pytest.raises(Gate, match="rung"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_wrong_seed(world):
    p, rj = _run_json(world, "r1S-s2.json")
    rj["seed"] = 1
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="seed"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_unfinished_training(world):
    c = json.loads((world / "r1-s2.json").read_text())
    (Path(c["run"]) / "log.jsonl").write_text(json.dumps(dict(step=50000)) + "\n")
    with pytest.raises(Gate, match="step"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_wrong_corpus_run(world):
    c = json.loads((world / "r1-s1.json").read_text())
    m = Path(c["corpus"]) / "manifest.json"
    m.write_text(json.dumps(dict(rung="r1", epsilon="1", run_key_hex="00" * 32)))
    for s in SEEDS:
        p, rj = _run_json(world, f"r1-s{s}.json")
        rj["corpus_manifest_sha256"] = _sha(m)
        p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="corpus run"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_checkpoint_changed_after_census(world):
    c = json.loads((world / "r1R-s1.json").read_text())
    (Path(c["run"]) / "ckpt.pt").write_bytes(b"retrained")
    with pytest.raises(Gate, match="checkpoint"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_duplicate_seed_argument(world):
    with pytest.raises(Gate, match="duplicate"):
        S.gate_censuses(world, [1, 1])


def test_gate_duplicate_census_content(world):
    c1 = json.loads((world / "r1D-s1.json").read_text())
    _edit(world, "r1D-s2.json", per_window_file=c1["per_window_file"], per_window_sha256=c1["per_window_sha256"])
    with pytest.raises(Gate, match="duplicate"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_missing_census(world):
    (world / "r1S-s1.json").unlink()
    with pytest.raises(Gate, match="missing"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_unlisted_census_in_dir(world):
    shutil.copy(world / "r1-s1.json", world / "r1-s9.json")
    with pytest.raises(Gate, match="outside"):
        S.gate_censuses(world, list(SEEDS))


def test_gate_window_set_mismatch(world, tmp_path):
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1R-eps1" / S.FRESH_RUN
    _make_run(tmp_path, world, "r1R", 2, corpus, ids=range(N_WIN - 1))
    with pytest.raises(Gate, match="window"):
        S.gate_censuses(world, list(SEEDS))


@pytest.mark.parametrize("kw", [dict(n=500), dict(k=5), dict(split="val")])
def test_gate_not_full_k7_test_census(world, kw):
    _edit(world, "r1-s1.json", **kw)
    with pytest.raises(Gate):
        S.gate_censuses(world, list(SEEDS))


@pytest.mark.parametrize("field,value", [("model.n_layer", 2), ("lr_min", 0.0), ("warmup", 0), ("epochs", 5),
                                         ("batch_size", 128), ("steps_planned", 100000), ("weight_decay", None)])
def test_gate_recipe_mismatch(world, field, value):
    p, rj = _run_json(world, "r1D-s2.json")
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


def test_recipe_matches_the_pilot_runs():
    assert S.RECIPE == {"batch_size": 256, "epochs": 15, "lr": 0.001, "lr_min": 0.0001, "warmup": 500,
                        "weight_decay": 0.1, "grad_clip": 1.0, "max_steps": None, "model.d_model": 128,
                        "model.n_layer": 4, "model.n_head": 4, "model.d_mlp": 512, "model.n_pos": 42,
                        "model.vocab_in": 157, "model.vocab_out": 156, "n_params": 838940, "steps_per_epoch": 7813,
                        "steps_planned": 117195, "steps_total": 117195}


def test_cli_refuses_to_overwrite(world, tmp_path):
    raw = tmp_path / "out.json"
    raw.write_text("{}")
    with pytest.raises(SystemExit, match="overwrite"):
        S.main(["--census-dir", str(world), "--raw", str(raw)])


@pytest.mark.parametrize("extra", [["--seeds", "1", "2"], ["--seed", "1"], ["--tau", "0.05"], ["--n-boot", "100"],
                                   ["--rng-seed", "7"], ["--level", "0.9"], ["--trim", "0"], ["--claim-t", "2"]])
def test_cli_refuses_any_setting_override(tmp_path, extra):
    raw = tmp_path / "out.json"
    with pytest.raises(SystemExit) as e:
        S.main(["--census-dir", str(tmp_path), "--raw", str(raw)] + extra)
    assert e.value.code == 2 and not raw.exists()


def test_cli_scores_exactly_the_frozen_seeds(world, tmp_path):
    with pytest.raises(Gate, match="missing"):
        S.main(["--census-dir", str(world), "--raw", str(tmp_path / "out.json")])


def test_window_set_is_the_full_k7_test_split():
    n_rec = {0: 8, 1: 8, 2: 5, 3: 9, 4: 7, 5: 8}
    S.check_window_set(n_rec, [0, 1, 3, 5])
    with pytest.raises(Gate, match="window count"):
        S.check_window_set(n_rec, [0, 1, 3])
    with pytest.raises(Gate, match="window"):
        S.check_window_set(n_rec, [0, 1, 3, 4])


def _self_copy_side(tmp, all_gates=True, flags=(True, True)):
    p = tmp / "r1S-exact.json"
    p.write_text(json.dumps(dict(rung_name="r1S", all_gates=all_gates, d_iota_kind_4=[
        dict(eps=e, self_copy_all_zero_exact=f, gate=True) for e, f in zip(("1", "1/2"), flags)])))
    return p


def test_self_copy_exact_side_gate(tmp_path):
    assert S.EXACT_S == "docs/three-arm-exact-side-r1S-2026-10-05.json"
    S.check_self_copy_exact(_self_copy_side(tmp_path))
    S.check_self_copy_exact(S.EXACT_S)


@pytest.mark.parametrize("kw", [dict(all_gates=False), dict(flags=(True, False)), dict(flags=(False, True))])
def test_self_copy_exact_side_gate_refuses(tmp_path, kw):
    with pytest.raises(Gate, match="r1S"):
        S.check_self_copy_exact(_self_copy_side(tmp_path, **kw))


# ---- cross-rung class pairing (carried over) --------------------------------------------

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
        for arm in ("r1R", "r1D", "r1S"):
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


@pytest.mark.parametrize("arm", ["r1R", "r1D", "r1S"])
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


def test_class_pairing_refuses_rows_without_a_class_id():
    recs, rows, ids = _pair_world()
    rows[("r1", 1)][0] = {"i": 0}
    with pytest.raises(Gate, match="class"):
        S.check_class_pairing(recs, rows, ids)
