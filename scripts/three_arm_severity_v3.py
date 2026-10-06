"""Power and severity of the v2.1 scorer's readings (scripts/three_arm_score_v2.py, SCORER_VERSION 2.1), simulated at
the SEED level with the frozen score_seeds() at its FROZEN settings (N_BOOT = 10,000, RNG_SEED, 95 % CI, 20 % trim).
Computed before stamping. No pilot means are used; only the pilot's sds (docs/three-arm-pilot-sd-2026-10-05.json) and
the 10-02 templates' sd. Does not modify severity v2 or its raw.

  uv run --extra learner python scripts/three_arm_severity_v3.py --raw docs/three-arm-severity-v3-2026-10-05.json \\
      [--sims 500] [--procs 64]

GENERATIVE MODEL (per seed s, n = 12; explicit shared r1 noise, a field × class interaction δ shared by every
field-bearing rung):
  K_R  = μ_R + δ_R + u_R − e_R          KS_R = δ_R + u_R − e_SR         K'_R = μ_R − e_R + e_SR
  K_D  = μ_D + δ_D + u_D − e_D          KS_D = δ_D + u_D − e_SD         K'_D = μ_D − e_D + e_SD
  μ_D = ρ' · μ_R · mD / mR  (ρ' is the true ratio of SC-controlled per-bit contrasts);  F ~ N(0, sd_F)
  u_R, u_D: the r1 model's noise on each arm's sets, corr 0.5; e_SR, e_SD: the self-copy model's noise on each arm's
  sets, corr 0.5 (same model, overlapping sets: an assumption); e_R, e_D independent.
Variance split. Per arm, with targets sd(K) and sd(K'): σ_e² = SHARE · min(sd(K)², sd(K')²), σ_u² = sd(K)² − σ_e²,
σ_eS² = sd(K')² − σ_e². Every SHARE in [0, 1] attains all four targets exactly, so the targets are jointly
attainable; SHARE = 0.5 is the one simulated (the free parameter only moves the K–K' correlation within an arm).
OFF-PHASE MIXTURE (the attack of the Codex pre-stamp review): each seed independently with prob 0.1 has its decoy's
(or relay's) SC-controlled per-bit contrast replaced by v × the relay's planted per-bit μ_R / mR, v ∈ {−1.85, +2.5};
the arm's K moves by the same amount (the arm model is what fails to converge), KS is unchanged.
sd sets: "point" = the pilot sds (K_R 0.0025 at df 4; K'_R 0.0042, K_D 0.0017, K'_D 0.0006, F 0.0011 at df 2);
"upper80" = each × its 80 % upper factor (×1.94 at df 4, ×3.08 at df 2).
"""
import argparse
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import three_arm_score_v2 as S  # noqa: E402

MR, MD = 0.340, 0.383
N_SEEDS = len(S.SEEDS)
SHARE = 0.5
CORR_U = 0.5
CORR_ES = 0.5
P_OFF = 0.1
UP_DF4, UP_DF2 = 1.94, 3.08
SDS = {"point": dict(K_R=0.0025, Kp_R=0.0042, K_D=0.0017, Kp_D=0.0006, F=0.0011)}
SDS["upper80"] = dict(K_R=0.0025 * UP_DF4, Kp_R=0.0042 * UP_DF2, K_D=0.0017 * UP_DF2, Kp_D=0.0006 * UP_DF2,
                      F=0.0011 * UP_DF2)
MU_R = (0.004, 0.006)
RHO = (1.0, 0.6, 0.4, 0.0)
DELTAS = [("none", 0.0)] + [(arm, d) for arm in ("R", "D") for d in (0.0015, -0.0015, 0.004)]
OFFPHASE = [("none", None)] + [(arm, v) for arm in ("D", "R") for v in (-1.85, 2.5)]
SEED = 20261005


def split(sdK, sdKp, share=SHARE):
    e2 = share * min(sdK, sdKp) ** 2
    return dict(u=float(np.sqrt(sdK ** 2 - e2)), e=float(np.sqrt(e2)), eS=float(np.sqrt(sdKp ** 2 - e2)))


def noise_params(sd):
    return dict(R=split(sd["K_R"], sd["Kp_R"]), D=split(sd["K_D"], sd["Kp_D"]), F=sd["F"])


def _pair(rng, s1, s2, c, n):
    z1, z2 = rng.normal(size=(2, n))
    return s1 * z1, s2 * (c * z1 + np.sqrt(1 - c * c) * z2)


def draw(rng, sd, muR, rho, delta, off, n=N_SEEDS):
    """One simulated confirmatory run: per-seed K_R, K_D, KS_R, KS_D, F."""
    p = noise_params(sd)
    uR, uD = _pair(rng, p["R"]["u"], p["D"]["u"], CORR_U, n)
    eSR, eSD = _pair(rng, p["R"]["eS"], p["D"]["eS"], CORR_ES, n)
    eR, eD = rng.normal(0, p["R"]["e"], n), rng.normal(0, p["D"]["e"], n)
    dR = delta[1] if delta[0] == "R" else 0.0
    dD = delta[1] if delta[0] == "D" else 0.0
    muD = rho * muR * MD / MR
    K_R, KS_R = muR + dR + uR - eR, dR + uR - eSR
    K_D, KS_D = muD + dD + uD - eD, dD + uD - eSD
    if off[0] != "none":
        hit = rng.random(n) < P_OFF
        if off[0] == "D":
            K_D = np.where(hit, KS_D + off[1] * muR / MR * MD, K_D)       # K'_D := v · μ_R/mR · mD on hit seeds
        else:
            K_R = np.where(hit, KS_R + off[1] * muR, K_R)                 # K'_R := v · μ_R on hit seeds
    F = rng.normal(0, p["F"], n)
    return K_R, K_D, KS_R, KS_D, F


def correct_reading(rho):
    return "move-dominant" if rho > S.RHO_SPLIT else "binding-dominant"


def wrong_reading(rho):
    return "binding-dominant" if rho > S.RHO_SPLIT else "move-dominant"


def run_scenario(args):
    idx, sdname, muR, rho, delta, off, sims, ss = args
    rng = np.random.default_rng(ss)
    sd = SDS[sdname]
    counts = {r: 0 for r in S.READINGS}
    n_ci = covered = 0
    for _ in range(sims):
        K_R, K_D, KS_R, KS_D, F = draw(rng, sd, muR, rho, delta, off)
        r = S.score_seeds(K_R, K_D, KS_R, KS_D, MR, MD, F, S.MARGINS)       # FROZEN n_boot, rng_seed, level, trim
        counts[r["reading"]] += 1
        if r["rho"] is not None:
            n_ci += 1
            lo, hi = r["rho"]["ci"]
            covered += int(lo <= rho <= hi)
    rates = {k: v / sims for k, v in counts.items()}
    return dict(i=idx, sd=sdname, mu_R=muR, rho=rho, delta_arm=delta[0], delta=delta[1], offphase_arm=off[0],
                offphase_v=off[1], sims=sims, readings=rates, correct=rates[correct_reading(rho)],
                wrong_direction=rates[wrong_reading(rho)], n_ratio_computed=n_ci,
                ci_coverage=(covered / n_ci) if n_ci else None)


def family(row):
    if row["offphase_arm"] != "none":
        return f"off-phase {row['offphase_arm']} v={row['offphase_v']:+g}"
    if row["delta_arm"] != "none":
        return "field x class interaction"
    return "clean"


def check_sds(n=200000, seed=1):
    """Empirical sds of the generated contrasts, against the targets (no δ, no off-phase)."""
    rng = np.random.default_rng(seed)
    out = {}
    for name, sd in SDS.items():
        K_R, K_D, KS_R, KS_D, F = draw(rng, sd, 0.0, 0.0, ("none", 0.0), ("none", None), n)
        got = dict(K_R=K_R.std(), Kp_R=(K_R - KS_R).std(), K_D=K_D.std(), Kp_D=(K_D - KS_D).std(), F=F.std(),
                   KS_R=KS_R.std(), KS_D=KS_D.std(), corr_Kp_R_Kp_D=np.corrcoef(K_R - KS_R, K_D - KS_D)[0, 1])
        out[name] = dict(target=sd, generated={k: float(v) for k, v in got.items()}, split=noise_params(sd))
    return out


def summarize(rows):
    fams = {}
    for r in rows:
        fams.setdefault((family(r), r["sd"]), []).append(r)
    by_family = {}
    for (f, sd), rs in sorted(fams.items()):
        w = max(rs, key=lambda r: r["wrong_direction"])
        by_family[f"{f} | {sd}"] = dict(max_wrong_direction=w["wrong_direction"],
                                        at=dict(mu_R=w["mu_R"], rho=w["rho"], delta_arm=w["delta_arm"],
                                                delta=w["delta"]),
                                        scenarios=len(rs))
    power = {}
    for r in rows:
        if r["sd"] == "point" and family(r) == "clean":
            power[f"mu_R={r['mu_R']} rho'={r['rho']}"] = dict(correct=r["correct"], readings=r["readings"])
    power_range_with_delta = {}
    for r in rows:
        if r["sd"] == "point" and r["offphase_arm"] == "none":
            k = f"mu_R={r['mu_R']} rho'={r['rho']}"
            lo, hi = power_range_with_delta.get(k, (1.0, 0.0))
            power_range_with_delta[k] = (min(lo, r["correct"]), max(hi, r["correct"]))
    cov = {}
    for sd in SDS:
        for fam_clean in (True, False):
            rs = [r for r in rows if r["sd"] == sd and (r["offphase_arm"] == "none") == fam_clean and r["n_ratio_computed"] >= 50]
            if not rs:
                continue
            tot = sum(r["n_ratio_computed"] for r in rs)
            cov[f"{sd} | {'no off-phase' if fam_clean else 'off-phase mixture'}"] = dict(
                pooled=sum(r["ci_coverage"] * r["n_ratio_computed"] for r in rs) / tot,
                min=min(r["ci_coverage"] for r in rs), n_scenarios=len(rs),
                note="conditional on a ratio being computed (P_V and P_R' pass); scenarios with >= 50 such sims")
    return dict(max_wrong_direction_overall=max(r["wrong_direction"] for r in rows),
                max_wrong_direction_by_family=by_family, power_point_clean=power,
                power_point_range_over_delta=power_range_with_delta, ci_coverage_of_rho=cov)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--sims", type=int, default=500)
    ap.add_argument("--procs", type=int, default=64)
    a = ap.parse_args()
    raw = Path(a.raw)
    log = raw.with_suffix(".log")
    if raw.exists() or log.exists():
        raise SystemExit(f"refusing to overwrite {raw} or {log}")
    if a.sims < 300:
        raise SystemExit("at least 300 simulations per scenario")
    grid = list(itertools.product(SDS, MU_R, RHO, DELTAS, OFFPHASE))
    seeds = np.random.SeedSequence(SEED).spawn(len(grid))
    jobs = [(i, sd, mu, rho, d, o, a.sims, seeds[i]) for i, (sd, mu, rho, d, o) in enumerate(grid)]
    t0 = time.time()
    lines = []

    def emit(s):
        print(s, flush=True)
        lines.append(s)

    sdcheck = check_sds()
    emit(json.dumps(dict(sd_check=sdcheck)))
    rows = []
    with Pool(a.procs) as pool:
        for row in pool.imap_unordered(run_scenario, jobs):
            rows.append(row)
            emit(json.dumps(row))
    rows.sort(key=lambda r: r["i"])
    summ = summarize(rows)
    emit(json.dumps(dict(summary=summ), indent=1))
    emit(f"wall {time.time() - t0:.0f} s, {len(rows)} scenarios x {a.sims} sims")
    out = dict(prereg="docs/three-arm-prereg-v0.2.md (v2.1 scorer)", scorer_version=S.SCORER_VERSION,
               scorer_sha256=S._sha(Path(S.__file__).resolve()), sims=a.sims, n_seeds=N_SEEDS,
               frozen=dict(n_boot=S.N_BOOT, rng_seed=S.RNG_SEED, ci_level=S.CI_LEVEL, trim=S.TRIM, tau=S.TAU),
               model=dict(share=SHARE, corr_u=CORR_U, corr_eS=CORR_ES, p_offphase=P_OFF, mR=MR, mD=MD,
                          upper80_factors=dict(df4=UP_DF4, df2=UP_DF2)),
               sds=SDS, sd_check=sdcheck, grid=dict(mu_R=MU_R, rho=RHO, deltas=DELTAS, offphase=OFFPHASE),
               summary=summ, rows=rows)
    raw.write_text(json.dumps(out, indent=1) + "\n")
    log.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
