"""The three-arm v0.2 frozen scorer (scripts/three_arm_score_v2.py; design v0.2 §3, §5; pilot v0.1 result: r1 is
the control for K). Synthetic only: planted per-seed contrasts for the reading rules, known t quantiles, and fake
census raws / run dirs / manifests in tmp_path for the CLI's provenance gates. No real census is read here."""
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import three_arm_score_v2 as S  # noqa: E402
from relay_paired import Gate  # noqa: E402

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


# ---- reading rules (v2.1: SC-controlled K', trimmed ratio, 95 % CI) ---------------------

def test_frozen_settings():
    assert S.SCORER_VERSION == "2.1"
    assert S.SEEDS == tuple(range(1, 13))
    assert S.TAU == 0.1 and S.N_BOOT == 10000 and S.CI_LEVEL == 0.95 and S.TRIM == 0.2
    assert S.READINGS == ("no replication", S.NO_RELAY_GAIN, "move-dominant", "binding-dominant", "unresolved")


def test_trimmed_mean_drops_floor_fifth_each_end():
    x = np.array([100.0, -100.0, 1, 2, 3, 4, 5, 6, 7, 8, 50.0, -50.0])   # n = 12: 2 dropped each side
    assert S.trimmed_mean(x) == pytest.approx(4.5)
    assert S.trimmed_mean(np.array([1.0, 2.0, 30.0])) == pytest.approx(11.0)   # n = 3: floor(0.6) = 0, plain mean
    assert S.trimmed_mean(np.array([5.0, 1.0, 2.0, 3.0, 4.0, 1000.0])) == pytest.approx(3.5)   # n = 6: 1 each


def test_planted_move():
    r = _score(*_seeds(1.0))
    assert r["P_V"]["pass"] and r["P_Rp"]["pass"]
    lo, hi = r["rho"]["ci"]
    assert r["rho"]["level"] == 0.95
    assert 0.5 < lo < 1 < hi
    assert r["reading"] == "move-dominant"


def test_planted_bind():
    r = _score(*_seeds(0.0))
    lo, hi = r["rho"]["ci"]
    assert hi < 0.5
    assert r["reading"] == "binding-dominant"


@pytest.mark.parametrize("rho,want", [(1.0, "move-dominant"), (0.0, "binding-dominant")])
def test_field_class_interaction_cancels_in_the_sc_controlled_contrast(rho, want):
    """δ_A shared by every field-bearing rung enters K_A and KS_A alike and cancels in K'_A = K_A − KS_A. A large δ
    on the relay's sets and the opposite on the decoy's would move a K-based ratio far from the planted one."""
    K_R, K_D, KS_R, KS_D, F = _seeds(rho, ks_shift=(0.006, -0.006))
    assert abs(S._summary(KS_R)["t"]) >= 3 and abs(S._summary(KS_D)["t"]) >= 3   # a real interaction
    naive = np.mean(K_D / MD) / np.mean(K_R / MR)
    assert abs(naive - rho) > 0.4                                                  # K alone is fooled
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["reading"] == want
    assert r["rho"]["point"] == pytest.approx(rho, abs=0.15)
    assert "self_copy_contrast" in r and not r["self_copy_contrast"]["KS_R"]["equivalent"]   # descriptive only


def test_rho_near_the_split_is_unresolved():
    r = _score(*_seeds(0.5))
    lo, hi = r["rho"]["ci"]
    assert lo < 0.5 < hi
    assert r["reading"] == "unresolved"


def test_strongly_negative_decoy_is_binding_dominant():
    """A decoy that HURTS where it moves information reproduces none of the relay's gain: below the split."""
    r = _score(*_seeds(-1.0))
    lo, hi = r["rho"]["ci"]
    assert hi < 0.5 and r["reading"] == "binding-dominant"


def test_failed_replication_overrides_everything():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    K_R = np.random.default_rng(3).normal(0, 0.002, N)
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["P_V"]["t"] < 3 and not r["P_V"]["pass"]
    assert r["reading"] == "no replication"
    assert r["rho"] is None                       # no ratio is ever computed on a failed relay
    assert r["H_field"]["result"] in ("equivalent", "not equivalent")   # the secondary is still reported


def test_negative_relay_is_no_replication():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    r = _score(-K_R, K_D, KS_R, KS_D, F)
    assert r["P_V"]["t"] < -3 and r["reading"] == "no replication" and r["rho"] is None


def test_no_relay_specific_gain():
    """The relay beats r1 (P_V) but only because every field-bearing rung does on its sets: the self-copy matches
    it, so K'_R ≈ 0 and the reading stops before any ratio."""
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    rng = np.random.default_rng(21)
    KS_R = K_R + rng.normal(0, 0.0004, N)
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["P_V"]["pass"] and not r["P_Rp"]["pass"]
    assert r["reading"] == S.NO_RELAY_GAIN and r["rho"] is None
    assert "self-copy" in S.NO_RELAY_GAIN


def test_replication_fail_precedes_no_relay_gain():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    K_R = np.random.default_rng(3).normal(0, 0.002, N)
    r = _score(K_R, K_D, K_R.copy(), KS_D, F)
    assert r["reading"] == "no replication"


def _outlier_seeds(rho, v, n_out=2):
    """Planted ρ' with n_out seeds whose decoy per-bit SC-controlled contrast is v × the relay's planted per-bit."""
    K_R, K_D, KS_R, KS_D, F = _seeds(rho, sd=0.0002)
    Kp_D = K_D - KS_D
    Kp_D[:n_out] = v * KR_BIT * MD
    return K_R, Kp_D + KS_D, KS_R, KS_D, F


@pytest.mark.parametrize("rho,v,wrong", [(1.0, -3.0, "binding-dominant"), (0.0, 3.5, "move-dominant")])
def test_trimmed_ratio_two_outliers_do_not_flip(rho, v, wrong):
    """Two off-phase seeds move the ratio of plain means across the split; the 20 %-trimmed ratio stays at the
    planted value and the reading never comes out in the wrong direction."""
    K_R, K_D, KS_R, KS_D, F = _outlier_seeds(rho, v)
    kp_R, kp_D = (K_R - KS_R) / MR, (K_D - KS_D) / MD
    plain = kp_D.mean() / kp_R.mean()
    assert (plain < 0.5) if rho > 0.5 else (plain > 0.5)            # the untrimmed ratio would flip
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["rho"]["point"] == pytest.approx(rho, abs=0.1)
    assert r["reading"] != wrong


def test_noisy_self_copy_is_descriptive():
    """A self-copy contrast centred on 0 but noisy is reported (t, TOST ±0.002) and gates nothing."""
    K_R, K_D, _, _, F = _seeds(1.0)
    rng = np.random.default_rng(11)
    KS = rng.normal(0, 0.0004, N)
    KS -= KS.mean()
    r = _score(K_R, K_D, KS, KS, F)
    sc = r["self_copy_contrast"]
    assert set(sc) >= {"KS_R", "KS_D"} and "t" in sc["KS_R"] and sc["KS_R"]["margin"] == 0.002
    assert r["reading"] == "move-dominant"


def test_h_field_secondary():
    r0 = _score(*_seeds(1.0, f_mean=0.0))
    assert r0["H_field"]["result"] == "equivalent"
    r1 = _score(*_seeds(1.0, f_mean=0.004))
    assert r1["H_field"]["result"] == "not equivalent"
    assert r1["reading"] == "move-dominant"       # independent of the reading
    lo, hi = r1["H_field"]["ci90"]
    assert lo < r1["H_field"]["mean"] < hi


def test_per_seed_values_and_per_bit_are_reported():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    r = _score(K_R, K_D, KS_R, KS_D, F)
    assert r["per_seed"]["K_R"] == pytest.approx(list(K_R))
    assert r["per_seed"]["Kp_R"] == pytest.approx(list(K_R - KS_R))
    assert r["per_seed"]["kp_D"] == pytest.approx(list((K_D - KS_D) / MD))
    assert r["summary"]["kp_R"]["mean"] == pytest.approx(float(np.mean((K_R - KS_R) / MR)))
    assert r["summary"]["K_R"]["sd"] == pytest.approx(float(np.std(K_R, ddof=1)))
    assert r["rho"]["point"] == pytest.approx(S.trimmed_mean((K_D - KS_D) / MD) / S.trimmed_mean((K_R - KS_R) / MR))


def test_bootstrap_is_deterministic_and_resamples_jointly():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    a, b = _score(K_R, K_D, KS_R, KS_D, F), _score(K_R, K_D, KS_R, KS_D, F)
    assert a["rho"] == b["rho"]
    # perfectly proportional seeds: every joint resample has ρ exactly 0.5, so the CI collapses there
    kR = np.array([0.01, 0.03, 0.05, 0.02, 0.04, 0.06])
    res = S.bootstrap_rho(kR, 0.5 * kR, n_boot=2000, rng_seed=0)
    assert res["ci"][0] == pytest.approx(0.5) and res["ci"][1] == pytest.approx(0.5)


def test_tiny_or_nonpositive_denominator_draws_widen_to_infinity():
    kR = np.array([0.02, -0.03, 0.001])          # many resamples have T(k_R) <= 0
    kD = np.array([0.01, 0.01, 0.01])
    res = S.bootstrap_rho(kR, kD, n_boot=5000, rng_seed=0)
    assert res["n_nonpositive_denominator"] > 0.05 * 5000
    assert res["ci"][0] == -math.inf and res["ci"][1] == math.inf


def test_input_validation():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    with pytest.raises(ValueError):
        S.score_seeds(K_R, K_D[:-1], KS_R, KS_D, MR, MD, F, MARGINS)
    with pytest.raises(ValueError):
        S.score_seeds(K_R, K_D, KS_R, KS_D, 0.0, MD, F, MARGINS)
    with pytest.raises(ValueError):
        S.score_seeds(K_R, K_D, KS_R, KS_D, MR, MD, F, {"field": 0.001})
    with pytest.raises(ValueError):
        S.score_seeds(K_R[:1], K_D[:1], KS_R[:1], KS_D[:1], MR, MD, F[:1], MARGINS)


# ---- per-seed arrays from per-window excess (pure) ------------------------------------

def test_seed_arrays_by_hand():
    # 6 windows; relay: moved {0,1}, zero {4,5}; decoy: moved {2}, zero {3,4}
    xR, zR = np.array([0.3, 0.5, 0.0, 0.05, 0.0, 0.0]), np.array([0, 0, 0, 0, 1, 1], bool)
    xD, zD = np.array([0.0, 0.08, 0.2, 0.0, 0.0, 0.01]), np.array([0, 0, 0, 1, 1, 0], bool)
    y1 = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    yR = np.array([0.8, 0.6, 1.0, 1.0, 1.0, 1.0])
    yD = np.array([1.0, 1.0, 0.9, 1.0, 1.0, 1.0])
    yS = np.array([1.0, 1.0, 1.0, 1.0, 0.98, 0.98])
    y = {("r1", 7): y1, ("r1R", 7): yR, ("r1D", 7): yD, ("r1S", 7): yS}
    out = S.seed_arrays(y, {"r1R": (xR, zR), "r1D": (xD, zD)}, [7], tau=0.1)
    assert out["K_R"][0] == pytest.approx(0.3)            # (0.2 + 0.4) / 2 − 0
    assert out["K_D"][0] == pytest.approx(0.1)            # 0.1 − 0
    assert out["KS_R"][0] == pytest.approx(0.0 - 0.02)    # moved 0, zero (0.02 + 0.02)/2
    assert out["KS_D"][0] == pytest.approx(0.0 - 0.01)    # moved 0, zero (0 + 0.02)/2
    assert out["mR"] == pytest.approx(0.4) and out["mD"] == pytest.approx(0.2)
    assert out["F"][0] == pytest.approx(0.04 / 6)
    assert out["sets"]["r1R"] == {"moved": 2, "zero": 2} and out["sets"]["r1D"] == {"moved": 1, "zero": 2}


def test_seed_arrays_refuse_empty_or_inconsistent_sets():
    x, z = np.array([0.0, 0.0]), np.array([1, 1], bool)
    y = {(r, 1): np.zeros(2) for r in S.RUNGS}
    with pytest.raises(Gate):                              # empty moved set
        S.seed_arrays(y, {"r1R": (x, z), "r1D": (np.array([0.5, 0.0]), z)}, [1], tau=0.1)
    with pytest.raises(Gate):                              # a window flagged exact-zero with |Δι| > τ
        S.seed_arrays(y, {"r1R": (np.array([0.5, 0.0]), np.array([1, 1], bool)),
                          "r1D": (np.array([0.5, 0.0]), np.array([0, 1], bool))}, [1], tau=0.1)


# ---- CLI provenance gates on fake censuses ----------------------------------------------

RUN_KEY_HEX = "5631e4d23aa08338a656740e41ef6e8d873ec6c75696cd5adb9211fff077e00f"   # sha256[:16] = 0582ffbeb4693d27
SEEDS = (1, 2)
N_WIN = 10


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _make_world(tmp, seeds=SEEDS):
    assert hashlib.sha256(bytes.fromhex(RUN_KEY_HEX)).hexdigest()[:16] == S.FRESH_RUN
    cd = tmp / "census"
    cd.mkdir()
    for rung in S.RUNGS:
        corpus = tmp / "corpus" / f"c1prime-loop-40-8-2-{rung}-eps1" / S.FRESH_RUN
        corpus.mkdir(parents=True)
        (corpus / "manifest.json").write_text(json.dumps(dict(rung=rung, epsilon="1", run_key_hex=RUN_KEY_HEX)))
        for s in seeds:
            _make_run(tmp, cd, rung, s, corpus)
    return cd


def _recipe_json():
    """A run.json carrying exactly the frozen recipe (dotted names nest under their prefix)."""
    rj = {}
    for k, v in S.RECIPE.items():
        if "." in k:
            a, b = k.split(".")
            rj.setdefault(a, {})[b] = v
        else:
            rj[k] = v
    return rj


def _make_run(tmp, cd, rung, s, corpus, epochs=15, run_seed=None, ids=range(N_WIN), pw=None):
    run = tmp / "runs" / f"{rung}-s{s}"
    run.mkdir(parents=True, exist_ok=True)
    rj = _recipe_json()
    rj.update(corpus_dir=str(corpus), seed=s if run_seed is None else run_seed, epochs=epochs,
              corpus_manifest_sha256=_sha(corpus / "manifest.json"))
    (run / "run.json").write_text(json.dumps(rj))
    (run / "log.jsonl").write_text("".join(json.dumps(dict(step=st, epoch=0)) + "\n" for st in (1000, S.FINAL_STEP)))
    (run / "ckpt.pt").write_bytes(f"{rung}{s}".encode())
    if pw is None:
        pw = cd / f"{rung}-s{s}.jsonl"
        kind = S.RUNGS.index(rung) * 0.1 + s * 0.01             # distinct content per census (else "duplicate")
        pw.write_text("".join(json.dumps(dict(i=i, key=0, by_field=dict(kind=kind + i * 1e-4))) + "\n" for i in ids))
    c = dict(run=str(run), step=S.FINAL_STEP, seed=s, corpus=str(corpus), rung=rung, eps="1", k=7, split="test",
             n=None, checkpoint_sha256=_sha(run / "ckpt.pt"), per_window_file=str(pw), per_window_sha256=_sha(pw))
    (cd / f"{rung}-s{s}.json").write_text(json.dumps(c))
    return c


def _edit(cd, name, **kw):
    p = cd / name
    c = json.loads(p.read_text())
    c.update(kw)
    p.write_text(json.dumps(c))


def test_gates_pass_on_a_consistent_world(tmp_path):
    cd = _make_world(tmp_path)
    cen, ids = S.gate_censuses(cd, list(SEEDS))
    assert set(cen) == {(r, s) for r in S.RUNGS for s in SEEDS} and ids == list(range(N_WIN))


def test_gate_wrong_rung(tmp_path):
    cd = _make_world(tmp_path)
    # the file says r1D, the census says r1D, but the run's corpus manifest is the self-copy's
    c = json.loads((cd / "r1D-s1.json").read_text())
    other = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1S-eps1" / S.FRESH_RUN
    run = Path(c["run"])
    rj = json.loads((run / "run.json").read_text())
    rj.update(corpus_dir=str(other), corpus_manifest_sha256=_sha(other / "manifest.json"))
    (run / "run.json").write_text(json.dumps(rj))
    _edit(cd, "r1D-s1.json", corpus=str(other))
    with pytest.raises(Gate, match="rung"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_census_rung_field_mismatch(tmp_path):
    cd = _make_world(tmp_path)
    _edit(cd, "r1R-s2.json", rung="r1D")
    with pytest.raises(Gate, match="rung"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_wrong_seed(tmp_path):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1S-s2.json").read_text())
    rj = json.loads((Path(c["run"]) / "run.json").read_text())
    rj["seed"] = 1
    (Path(c["run"]) / "run.json").write_text(json.dumps(rj))
    with pytest.raises(Gate, match="seed"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_wrong_epochs(tmp_path):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1-s1.json").read_text())
    rj = json.loads((Path(c["run"]) / "run.json").read_text())
    rj["epochs"] = 5
    (Path(c["run"]) / "run.json").write_text(json.dumps(rj))
    with pytest.raises(Gate, match="epochs"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_unfinished_training(tmp_path):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1-s2.json").read_text())
    (Path(c["run"]) / "log.jsonl").write_text(json.dumps(dict(step=50000)) + "\n")
    with pytest.raises(Gate, match="step"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_wrong_corpus_run(tmp_path):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1-s1.json").read_text())
    m = Path(c["corpus"]) / "manifest.json"
    m.write_text(json.dumps(dict(rung="r1", epsilon="1", run_key_hex="00" * 32)))
    rj = json.loads((Path(c["run"]) / "run.json").read_text())
    rj["corpus_manifest_sha256"] = _sha(m)
    (Path(c["run"]) / "run.json").write_text(json.dumps(rj))
    with pytest.raises(Gate, match="corpus run"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_checkpoint_changed_after_census(tmp_path):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1R-s1.json").read_text())
    (Path(c["run"]) / "ckpt.pt").write_bytes(b"retrained")
    with pytest.raises(Gate, match="checkpoint"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_duplicate_seed_argument(tmp_path):
    cd = _make_world(tmp_path)
    with pytest.raises(Gate, match="duplicate"):
        S.gate_censuses(cd, [1, 1])


def test_gate_duplicate_census_content(tmp_path):
    cd = _make_world(tmp_path)
    # r1D-s2's census reuses r1D-s1's per-window file: every per-file gate passes, the cross-file one refuses
    c1 = json.loads((cd / "r1D-s1.json").read_text())
    _edit(cd, "r1D-s2.json", per_window_file=c1["per_window_file"], per_window_sha256=c1["per_window_sha256"])
    with pytest.raises(Gate, match="duplicate"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_missing_census(tmp_path):
    cd = _make_world(tmp_path)
    (cd / "r1S-s1.json").unlink()
    with pytest.raises(Gate, match="missing"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_unlisted_census_in_dir(tmp_path):
    cd = _make_world(tmp_path)
    shutil.copy(cd / "r1-s1.json", cd / "r1-s9.json")   # a seed not scored: no silent seed selection
    with pytest.raises(Gate, match="outside"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_window_set_mismatch(tmp_path):
    cd = _make_world(tmp_path)
    corpus = tmp_path / "corpus" / "c1prime-loop-40-8-2-r1R-eps1" / S.FRESH_RUN
    _make_run(tmp_path, cd, "r1R", 2, corpus, ids=range(N_WIN - 1))
    with pytest.raises(Gate, match="window"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_not_full_test_census(tmp_path):
    cd = _make_world(tmp_path)
    _edit(cd, "r1-s1.json", n=500)
    with pytest.raises(Gate):
        S.gate_censuses(cd, list(SEEDS))


def test_cli_refuses_to_overwrite(tmp_path):
    cd = _make_world(tmp_path)
    raw = tmp_path / "out.json"
    raw.write_text("{}")
    with pytest.raises(SystemExit, match="overwrite"):
        S.main(["--census-dir", str(cd), "--raw", str(raw)])


@pytest.mark.parametrize("extra", [["--seeds", "1", "2"], ["--seed", "1"], ["--tau", "0.05"], ["--n-boot", "100"],
                                   ["--rng-seed", "7"], ["--level", "0.9"], ["--trim", "0"]])
def test_cli_refuses_any_setting_override(tmp_path, extra):
    raw = tmp_path / "out.json"
    with pytest.raises(SystemExit) as e:
        S.main(["--census-dir", str(tmp_path), "--raw", str(raw)] + extra)
    assert e.value.code == 2 and not raw.exists()              # argparse: unrecognized argument


def test_cli_scores_exactly_the_frozen_seeds(tmp_path):
    """The CLI has no seed argument: a directory with seeds 1, 2 only is refused because 3..12 are missing."""
    cd = _make_world(tmp_path)
    with pytest.raises(Gate, match="missing"):
        S.main(["--census-dir", str(cd), "--raw", str(tmp_path / "out.json")])


def test_margins_are_the_preregistered_ones():
    assert S.MARGINS == {"field_interaction": 0.002, "field": 0.001}
    assert MARGINS == S.MARGINS


# ---- v2.1 gates ------------------------------------------------------------------------

def test_recipe_matches_the_pilot_runs():
    assert S.RECIPE == {"batch_size": 256, "epochs": 15, "lr": 0.001, "lr_min": 0.0001, "warmup": 500,
                        "weight_decay": 0.1, "grad_clip": 1.0, "max_steps": None, "model.d_model": 128,
                        "model.n_layer": 4, "model.n_head": 4, "model.d_mlp": 512, "model.n_pos": 42,
                        "model.vocab_in": 157, "model.vocab_out": 156, "n_params": 838940, "steps_per_epoch": 7813,
                        "steps_planned": 117195, "steps_total": 117195}


@pytest.mark.parametrize("field,value", [("model.n_layer", 2), ("model.n_head", 8), ("lr_min", 0.0), ("warmup", 0),
                                         ("batch_size", 128), ("lr", 3e-4), ("steps_planned", 100000),
                                         ("model.d_model", 64), ("weight_decay", None)])
def test_gate_recipe_mismatch(tmp_path, field, value):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1D-s2.json").read_text())
    p = Path(c["run"]) / "run.json"
    rj = json.loads(p.read_text())
    if "." in field:
        a, b = field.split(".")
        rj[a][b] = value
    else:
        rj[field] = value
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="recipe"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_recipe_field_missing(tmp_path):
    cd = _make_world(tmp_path)
    c = json.loads((cd / "r1-s1.json").read_text())
    p = Path(c["run"]) / "run.json"
    rj = json.loads(p.read_text())
    del rj["model"]["n_head"]
    p.write_text(json.dumps(rj))
    with pytest.raises(Gate, match="recipe"):
        S.gate_censuses(cd, list(SEEDS))


def test_gate_census_n_must_be_none(tmp_path):
    cd = _make_world(tmp_path)
    _edit(cd, "r1S-s1.json", n=100000)
    with pytest.raises(Gate):
        S.gate_censuses(cd, list(SEEDS))


def test_window_set_is_the_full_k7_test_split():
    n_rec = {0: 8, 1: 8, 2: 5, 3: 9, 4: 7, 5: 8}            # k = 7 scores windows with ≥ 8 records
    S.check_window_set(n_rec, [0, 1, 3, 5])
    with pytest.raises(Gate, match="window count"):
        S.check_window_set(n_rec, [0, 1, 3])                # one scorable window dropped
    with pytest.raises(Gate, match="window"):
        S.check_window_set(n_rec, [0, 1, 3, 4])             # right count, wrong window (4 is too short)


def _self_copy_side(tmp, all_gates=True, flags=(True, True)):
    p = tmp / "r1S-exact.json"
    p.write_text(json.dumps(dict(rung_name="r1S", all_gates=all_gates, d_iota_kind_4=[
        dict(eps=e, self_copy_all_zero_exact=f, gate=True) for e, f in zip(("1", "1/2"), flags)])))
    return p


def test_self_copy_exact_side_gate(tmp_path):
    assert S.EXACT_S == "docs/three-arm-exact-side-r1S-2026-10-05.json"
    S.check_self_copy_exact(_self_copy_side(tmp_path))
    S.check_self_copy_exact(S.EXACT_S)                                        # the committed raw passes


@pytest.mark.parametrize("kw", [dict(all_gates=False), dict(flags=(True, False)), dict(flags=(False, True))])
def test_self_copy_exact_side_gate_refuses(tmp_path, kw):
    with pytest.raises(Gate, match="r1S"):
        S.check_self_copy_exact(_self_copy_side(tmp_path, **kw))


def test_self_copy_exact_side_gate_refuses_missing_flag(tmp_path):
    p = tmp_path / "r1S-exact.json"
    p.write_text(json.dumps(dict(rung_name="r1S", all_gates=True, d_iota_kind_4=[dict(eps="1", gate=True)])))
    with pytest.raises(Gate, match="r1S"):
        S.check_self_copy_exact(p)


# ---- cross-rung class pairing ----------------------------------------------------------

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
    for i in range(n_win):                                   # windows drawn from a small pool: classes repeat
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
    recs[arm][3] = (recs[arm][3][0], window_map(arm)(other))          # arm window 3 is the image of r1 window 5
    if recs[arm][3][1] == window_map(arm)(recs["r1"][3][1]):
        pytest.skip("windows 3 and 5 coincide")
    with pytest.raises(Gate, match="pair"):
        S.check_class_pairing(recs, rows, ids)


def test_class_pairing_refuses_a_census_that_merges_classes():
    recs, rows, ids = _pair_world()
    r = rows[("r1R", 2)]
    a, b = next((i, j) for i in ids for j in ids if r[i]["key"] != r[j]["key"])
    r[b] = dict(r[b], key=r[a]["key"])                                 # two distinct arm classes, one census id
    with pytest.raises(Gate, match="class"):
        S.check_class_pairing(recs, rows, ids)


def test_class_pairing_refuses_a_census_that_splits_a_class():
    recs, rows, ids = _pair_world(n_win=200)
    r = rows[("r1D", 1)]
    seen = {}
    a, b = next((seen[r[i]["key"]], i) for i in ids if seen.setdefault(r[i]["key"], i) != i)
    r[b] = dict(r[b], key=10 ** 6)                                     # one arm class, two census ids
    with pytest.raises(Gate, match="class"):
        S.check_class_pairing(recs, rows, ids)


def test_class_pairing_refuses_rows_without_a_class_id():
    recs, rows, ids = _pair_world()
    rows[("r1", 1)][0] = {"i": 0}
    with pytest.raises(Gate, match="class"):
        S.check_class_pairing(recs, rows, ids)
