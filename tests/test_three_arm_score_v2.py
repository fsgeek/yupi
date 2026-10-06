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
N = 8
MR, MD = 0.20, 0.15          # mean |Δι| on each arm's moved set
KR_BIT = 0.03                # planted relay per-bit effect: K_R ≈ 0.006


def _seeds(rho, n=N, sd=0.0004, rng_seed=1, ks_shift=(0.0, 0.0), f_mean=0.0):
    rng = np.random.default_rng(rng_seed)
    K_R = MR * KR_BIT + rng.normal(0, sd, n)
    K_D = MD * KR_BIT * rho + rng.normal(0, sd, n)
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


# ---- reading rules ---------------------------------------------------------------------

def test_planted_move():
    r = _score(*_seeds(1.0))
    assert r["P_V"]["pass"] and r["field_interaction"]["pass"]
    lo, hi = r["rho"]["ci90"]
    assert 0.5 < lo < 1 < hi
    assert r["reading"] == "move-dominant"


def test_planted_bind():
    r = _score(*_seeds(0.0))
    lo, hi = r["rho"]["ci90"]
    assert hi < 0.5
    assert r["reading"] == "binding-dominant"


def test_rho_near_the_split_is_unresolved():
    r = _score(*_seeds(0.5))
    lo, hi = r["rho"]["ci90"]
    assert lo < 0.5 < hi
    assert r["reading"] == "unresolved"


def test_rho_0_4_resolved_is_binding_dominant():
    r = _score(*_seeds(0.4))
    lo, hi = r["rho"]["ci90"]
    assert hi < 0.5 and r["reading"] == "binding-dominant"     # a precise 0.4 is below the split


def test_strongly_negative_decoy_is_binding_dominant():
    """A decoy that HURTS where it moves information reproduces none of the relay's gain: below the split."""
    r = _score(*_seeds(-1.0))
    lo, hi = r["rho"]["ci90"]
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


def test_replication_fail_precedes_field_interaction():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0, ks_shift=(0.01, 0.0))
    r = _score(np.random.default_rng(3).normal(0, 0.002, N), K_D, KS_R, KS_D, F)
    assert r["reading"] == "no replication"


@pytest.mark.parametrize("shift", [(0.006, 0.0), (0.0, -0.006)])
def test_field_interaction_withholds_the_mechanism(shift):
    r = _score(*_seeds(1.0, ks_shift=shift))
    assert r["P_V"]["pass"] and not r["field_interaction"]["pass"]
    assert r["reading"] == "mechanism withheld: field × class interaction"


def test_noisy_self_copy_is_reported_not_gating():
    """A self-copy contrast centred on 0 but too noisy for its TOST is reported as not equivalent, and does not
    withhold the reading: only EVIDENCE of an interaction (|t| >= 3) withholds (severity v2)."""
    K_R, K_D, _, _, F = _seeds(1.0)
    rng = np.random.default_rng(11)
    KS = rng.normal(0, 0.01, N)
    KS -= KS.mean()
    r = _score(K_R, K_D, KS, KS, F)
    assert not r["field_interaction"]["KS_R"]["equivalent"] and not r["field_interaction"]["equivalent_both"]
    assert r["field_interaction"]["pass"]
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
    assert r["per_seed"]["k_D"] == pytest.approx(list(K_D / MD))
    assert r["summary"]["k_R"]["mean"] == pytest.approx(float(np.mean(K_R / MR)))
    assert r["summary"]["K_R"]["sd"] == pytest.approx(float(np.std(K_R, ddof=1)))
    assert r["rho"]["point"] == pytest.approx(float(np.mean(K_D / MD) / np.mean(K_R / MR)))


def test_bootstrap_is_deterministic_and_resamples_jointly():
    K_R, K_D, KS_R, KS_D, F = _seeds(1.0)
    a, b = _score(K_R, K_D, KS_R, KS_D, F), _score(K_R, K_D, KS_R, KS_D, F)
    assert a["rho"] == b["rho"]
    # perfectly proportional seeds: every joint resample has ρ exactly 0.5, so the CI collapses there
    kR = np.array([0.01, 0.03, 0.05, 0.02])
    res = S.bootstrap_rho(kR, 0.5 * kR, n_boot=2000, rng_seed=0)
    assert res["ci90"][0] == pytest.approx(0.5) and res["ci90"][1] == pytest.approx(0.5)


def test_tiny_or_nonpositive_denominator_draws_widen_to_infinity():
    kR = np.array([0.02, -0.03, 0.001])          # many resamples have mean(k_R) <= 0
    kD = np.array([0.01, 0.01, 0.01])
    res = S.bootstrap_rho(kR, kD, n_boot=5000, rng_seed=0)
    assert res["n_nonpositive_denominator"] > 0.05 * 5000
    assert res["ci90"][0] == -math.inf and res["ci90"][1] == math.inf
    few = S.bootstrap_rho(np.array([0.03] * 7 + [-0.04]), np.full(8, 0.01),     # ≤ 0 only if ≥ 4 of 8 draws hit −0.04
                          n_boot=5000, rng_seed=0)
    assert 0 < few["n_nonpositive_denominator"] < 0.05 * 5000 and math.isfinite(few["ci90"][1])


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


def _make_run(tmp, cd, rung, s, corpus, epochs=15, run_seed=None, ids=range(N_WIN), pw=None):
    run = tmp / "runs" / f"{rung}-s{s}"
    run.mkdir(parents=True, exist_ok=True)
    (run / "run.json").write_text(json.dumps(dict(
        corpus_dir=str(corpus), seed=s if run_seed is None else run_seed, epochs=epochs, lr=0.001,
        model=dict(d_model=128), corpus_manifest_sha256=_sha(corpus / "manifest.json"),
        steps_total=S.FINAL_STEP)))
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
    shutil.copy(cd / "r1-s1.json", cd / "r1-s9.json")   # a seed not in --seeds: no silent seed selection
    with pytest.raises(Gate, match="not in --seeds"):
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
        S.main(["--census-dir", str(cd), "--seeds", "1", "2", "--raw", str(raw)])


def test_margins_are_the_preregistered_ones():
    assert S.MARGINS == {"field_interaction": 0.002, "field": 0.001}
    assert MARGINS == S.MARGINS
