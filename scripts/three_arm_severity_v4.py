"""Severity and power of the prereg v0.3 confirmatory claims C1–C3 (scripts/three_arm_score_v3.py, SCORER_VERSION 3.0),
simulated at the SEED level and scored with the frozen v3 claim function score_claims() (t ≥ 3, one-sided, df 11).
The bootstrap is descriptive in v0.3 and is not simulated. Computed before stamping. No pilot means are used; only
the pilot's sds (docs/three-arm-pilot-sd-2026-10-05.json, via severity v3's SDS). Does not modify severity v3.

  uv run --extra learner python scripts/three_arm_severity_v4.py --raw docs/three-arm-severity-v4-2026-10-05.json \\
      [--sims 4000] [--procs 64]

GENERATIVE MODEL: severity v3's (scripts/three_arm_severity_v3.py), reused: per seed, shared r1 noise u (corr 0.5
across the arms' sets), self-copy noise e_S (corr 0.5), independent arm noise e, variance split SHARE = 0.5, sd sets
"point" (pilot sds) and "upper80". Extended with:
  K_R = μ_R + δsh_R + δas_R + u_R − e_R        KS_R = δsh_R + u_R − e_SR
  K_D = μ_D + δsh_D + δas_D + u_D − e_D        KS_D = δsh_D + u_D − e_SD          μ_D = ρ' μ_R mD / mR
  δsh_A: a field × class interaction SHARED by every field-bearing rung (enters K_A and KS_A; cancels in K'_A).
  δas_A: an ARM-SPECIFIC effect of carrying a variable field (enters K_A only; lands in K'_A) — round 3's confound.
  off-phase (v3 semantics): each seed independently with prob p has its arm's K'_A REPLACED by v · μ_ref (relay) or
    v · μ_ref · mD / mR (decoy); the arm's K moves with it, KS does not. Target R, D, or RD (the same seeds hit on
    both arms: off-phase correlated across arms within a seed, as a failed self-copy model would produce).
  two-phase mixture: each seed with prob p is in phase A; K'_A shifts by a (1 − p) in phase A and by −a p otherwise,
    a = v · μ_ref (· mD/mR for the decoy), so the population mean is unchanged (a bimodal, mean-preserving null).
  heteroskedastic: per-seed noise multiplier, "few-wide" (2 random seeds × 3) or "lognormal" (exp N(0, 0.75²)).

NULLS. C1: E[K_R] = 0 (μ_R = 0, no δ on the relay). C2: E[K'_R] = 0 (μ_R = 0; base B2 adds a shared δ_R = +0.006
so that K_R > 0 while K'_R = 0, the "C1 passes, C2 fails" world). C3: E[K'_D] = 0 (ρ' = 0, at μ_R = 0 or 0.006).
A positive arm-specific δ on a claim's own arm (δas_D > 0 for C3, δas_R > 0 for C2) makes the claim's population
mean positive without information moved: it is that claim's DIRECT RIVAL, reported separately (with a sweep) and not
counted toward the false-positive bar; prereg v0.3 must state the assumption. Every other perturbation of a null
base, including non-centred off-phase, counts.
"""
import argparse
import itertools
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import three_arm_score_v3 as S  # noqa: E402
import three_arm_severity_v3 as V3  # noqa: E402  (the generative model: sds, variance split, correlations)

MR, MD = V3.MR, V3.MD
SDS = V3.SDS
N_SEEDS = len(S.SEEDS)
SEED = 20261006
MIN_SIMS = 2000
BAR = 0.05
MU_POWER = (0.004, 0.006)
AS_DELTAS = (0.0015, -0.0015, 0.004, -0.004)
OFF_P = (0.1, 0.2)
OFF_V = (2.5, -1.85)
MU_REF = (0.004, 0.006)
TWO_P = (0.1, 0.2, 0.5)
TWO_V = (2.5, -2.5)
HETERO = ("few-wide", "lognormal")
SWEEP_D = (0.0002, 0.0004, 0.0006, 0.0008, 0.001, 0.0015, 0.004)
SWEEP_R = (0.0005, 0.001, 0.0015, 0.002, 0.003, 0.004)
BASES = {"B0": dict(muR=0.0, rho=0.0, sh=("none", 0.0)),          # every claim null
         "B1": dict(muR=0.006, rho=0.0, sh=("none", 0.0)),        # C3 null; the relay real
         "B2": dict(muR=0.0, rho=0.0, sh=("R", 0.006))}           # C2, C3 null; K_R > 0 from a shared field effect


def _mult(rng, hetero, n):
    if hetero is None:
        return np.ones(n)
    if hetero == "few-wide":
        m = np.ones(n)
        m[rng.choice(n, 2, replace=False)] = 3.0
        return m
    if hetero == "lognormal":
        return np.exp(rng.normal(0, 0.75, n))
    raise ValueError(hetero)


def draw(rng, sd, muR, rho, sh=("none", 0.0), as_=("none", 0.0), off=None, two=None, hetero=None, n=N_SEEDS):
    """One simulated confirmatory run: per-seed K_R, K_D, KS_R, KS_D (module docstring)."""
    p = V3.noise_params(sd)
    m = _mult(rng, hetero, n)
    uR, uD = V3._pair(rng, p["R"]["u"], p["D"]["u"], V3.CORR_U, n)
    eSR, eSD = V3._pair(rng, p["R"]["eS"], p["D"]["eS"], V3.CORR_ES, n)
    eR, eD = rng.normal(0, p["R"]["e"], n), rng.normal(0, p["D"]["e"], n)
    uR, uD, eSR, eSD, eR, eD = (x * m for x in (uR, uD, eSR, eSD, eR, eD))
    d = {a: (sh[1] if sh[0] == a else 0.0, as_[1] if as_[0] == a else 0.0) for a in ("R", "D")}
    muD = rho * muR * MD / MR
    K_R, KS_R = muR + d["R"][0] + d["R"][1] + uR - eR, d["R"][0] + uR - eSR
    K_D, KS_D = muD + d["D"][0] + d["D"][1] + uD - eD, d["D"][0] + uD - eSD
    scale = {"R": 1.0, "D": MD / MR}
    if off is not None:
        hit = rng.random(n) < off["p"]
        if "R" in off["target"]:
            K_R = np.where(hit, KS_R + off["v"] * off["mu_ref"] * scale["R"], K_R)
        if "D" in off["target"]:
            K_D = np.where(hit, KS_D + off["v"] * off["mu_ref"] * scale["D"], K_D)
    if two is not None:
        hit = rng.random(n) < two["p"]
        shift = np.where(hit, 1.0 - two["p"], -two["p"]) * two["v"] * two["mu_ref"]
        if "R" in two["target"]:
            K_R = K_R + shift * scale["R"]
        if "D" in two["target"]:
            K_D = K_D + shift * scale["D"]
    return K_R, K_D, KS_R, KS_D


def wilson_upper(k, n, z=1.959964):
    if n == 0:
        return None
    p = k / n
    return float((p + z * z / (2 * n) + z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n))


# ---- the scenario grid -----------------------------------------------------------------

def _scen(kind, sd, base, **kw):
    b = BASES[base] if base else {}
    s = dict(kind=kind, sd=sd, base=base, muR=b.get("muR", 0.0), rho=b.get("rho", 0.0), sh=b.get("sh", ("none", 0.0)),
             as_=("none", 0.0), off=None, two=None, hetero=None, family=None)
    s.update(kw)
    return s


def grid():
    out = []
    for sd, base in itertools.product(SDS, BASES):
        out.append(_scen("null", sd, base, family="clean"))
        for arm, dl in itertools.product(("R", "D"), AS_DELTAS):
            out.append(_scen("null", sd, base, as_=(arm, dl), family="arm-specific delta"))
        for tgt, p, v, mu in itertools.product(("R", "D", "RD"), OFF_P, OFF_V, MU_REF):
            out.append(_scen("null", sd, base, off=dict(target=tgt, p=p, v=v, mu_ref=mu),
                             family="off-phase (correlated across arms)" if tgt == "RD" else "off-phase (one arm)"))
        for tgt, p, v in itertools.product(("R", "D", "RD"), TWO_P, TWO_V):
            out.append(_scen("null", sd, base, two=dict(target=tgt, p=p, v=v, mu_ref=0.006),
                             family="two-phase mixture (mean-preserving)"))
        for h in HETERO:
            out.append(_scen("null", sd, base, hetero=h, family="heteroskedastic"))
        off = dict(target="RD", p=0.2, v=2.5, mu_ref=0.006)
        out += [_scen("null", sd, base, off=off, hetero="few-wide", family="combined"),
                _scen("null", sd, base, off=off, as_=("D", -0.0015), family="combined"),
                _scen("null", sd, base, off=off, as_=("R", -0.0015), family="combined"),
                _scen("null", sd, base, two=dict(target="RD", p=0.2, v=2.5, mu_ref=0.006), hetero="lognormal",
                      family="combined")]
    for sd, mu in itertools.product(SDS, MU_POWER):
        out.append(_scen("power", sd, None, muR=mu, rho=1.0, family="H_move, clean"))
    for sd, dl in itertools.product(SDS, SWEEP_D):
        out.append(_scen("rival", sd, "B0", as_=("D", dl), family="C3 direct rival: arm-specific delta_D > 0"))
    for sd, dl in itertools.product(SDS, SWEEP_R):
        out.append(_scen("rival", sd, "B0", as_=("R", dl), family="C2 direct rival: arm-specific delta_R > 0"))
    for i, s in enumerate(out):
        s["i"] = i
    return out


def claim_status(s):
    """Per claim: 'null' (counts toward the bar), 'direct rival' (own-arm positive δ: reported, not counted), or
    'alternative' (the claim's population mean is positive by construction)."""
    st = {}
    as_R = s["as_"][1] if s["as_"][0] == "R" else 0.0
    as_D = s["as_"][1] if s["as_"][0] == "D" else 0.0
    sh_R = s["sh"][1] if s["sh"][0] == "R" else 0.0
    st["C1"] = ("alternative" if (s["muR"] > 0 or sh_R > 0 or as_R > 0) else "null")
    st["C2"] = ("alternative" if s["muR"] > 0 else "direct rival" if as_R > 0 else "null")
    st["C3"] = ("alternative" if (s["muR"] > 0 and s["rho"] > 0) else "direct rival" if as_D > 0 else "null")
    return st


def run_scenario(args):
    s, sims, ss = args
    rng = np.random.default_rng(ss)
    sd = SDS[s["sd"]]
    passes = {c: 0 for c in S.CLAIMS}
    for _ in range(sims):
        K_R, K_D, KS_R, KS_D = draw(rng, sd, s["muR"], s["rho"], s["sh"], s["as_"], s["off"], s["two"], s["hetero"])
        c = S.score_claims(K_R, K_D, KS_R, KS_D)                   # the frozen v3 claim function
        for k in S.CLAIMS:
            passes[k] += int(c[k]["pass"])
    st = claim_status(s)
    return dict({k: v for k, v in s.items()}, sims=sims, status=st, passes=passes,
                rate={k: passes[k] / sims for k in S.CLAIMS},
                wilson95_upper={k: wilson_upper(passes[k], sims) for k in S.CLAIMS})


def _where(r):
    return dict(i=r["i"], sd=r["sd"], base=r["base"], as_=r["as_"], off=r["off"], two=r["two"], hetero=r["hetero"])


def summarize(rows):
    fp = {c: {} for c in S.CLAIMS}
    for c in S.CLAIMS:
        for r in rows:
            if r["kind"] != "null" or r["status"][c] != "null":
                continue
            f = fp[c].setdefault(r["family"], dict(max_fp=-1.0, scenarios=0))
            f["scenarios"] += 1
            if r["rate"][c] > f["max_fp"]:
                f.update(max_fp=r["rate"][c], wilson95_upper=r["wilson95_upper"][c], sims=r["sims"], at=_where(r))
        allr = [r for r in rows if r["kind"] == "null" and r["status"][c] == "null"]
        w = max(allr, key=lambda r: r["rate"][c])
        fp[c]["ALL"] = dict(max_fp=w["rate"][c], wilson95_upper=w["wilson95_upper"][c], sims=w["sims"],
                            scenarios=len(allr), at=_where(w),
                            bar_met=bool(w["rate"][c] <= BAR), bar_met_at_wilson_upper=bool(
                                w["wilson95_upper"][c] <= BAR))
    power = {}
    for r in rows:
        if r["kind"] == "power":
            power[f"mu_R={r['muR']} | {r['sd']}"] = dict(r["rate"], mu_Kp_D=r["muR"] * MD / MR)
    rivals = {}
    for r in rows:
        if r["kind"] == "rival" or (r["kind"] == "null" and "direct rival" in r["status"].values()):
            c = "C3" if r["as_"][0] == "D" else "C2"
            if r["status"][c] != "direct rival":
                continue
            rivals.setdefault(c, []).append(dict(sd=r["sd"], base=r["base"], delta=r["as_"][1], pass_rate=r["rate"][c],
                                                 wilson95_upper=r["wilson95_upper"][c], family=r["family"]))
    for c in rivals:
        rivals[c].sort(key=lambda d: (d["sd"], d["base"], d["delta"]))
    return dict(bar=BAR, false_positive_by_claim_family=fp, power_H_move_clean=power, direct_rivals=rivals)


def check_sds(n=200000, seed=1):
    rng = np.random.default_rng(seed)
    out = {}
    for name, sd in SDS.items():
        K_R, K_D, KS_R, KS_D = draw(rng, sd, 0.0, 0.0, n=n)
        out[name] = dict(target=sd, generated=dict(K_R=float(K_R.std()), Kp_R=float((K_R - KS_R).std()),
                                                   K_D=float(K_D.std()), Kp_D=float((K_D - KS_D).std())))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--sims", type=int, default=4000)
    ap.add_argument("--procs", type=int, default=64)
    a = ap.parse_args()
    raw = Path(a.raw)
    log = raw.with_suffix(".log")
    if raw.exists() or log.exists():
        raise SystemExit(f"refusing to overwrite {raw} or {log}")
    if a.sims < MIN_SIMS:
        raise SystemExit(f"at least {MIN_SIMS} simulations per scenario")
    g = grid()
    seeds = np.random.SeedSequence(SEED).spawn(len(g))
    jobs = [(s, a.sims, seeds[s["i"]]) for s in g]
    t0 = time.time()
    lines = []

    def emit(x):
        print(x, flush=True)
        lines.append(x)

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
    out = dict(prereg="docs/three-arm-prereg-v0.3.md §4", scorer_version=S.SCORER_VERSION,
               scorer_sha256=S._sha(Path(S.__file__).resolve()),
               severity_v3_sha256=S._sha(Path(V3.__file__).resolve()), claim_function="score_claims",
               claim_t=S.CLAIM_T, sims=a.sims, n_seeds=N_SEEDS, rng_seed=SEED,
               model=dict(generative="severity v3 (reused)", share=V3.SHARE, corr_u=V3.CORR_U, corr_eS=V3.CORR_ES,
                          mR=MR, mD=MD, upper80_factors=dict(df4=V3.UP_DF4, df2=V3.UP_DF2)),
               sds=SDS, sd_check=sdcheck, bases=BASES,
               grid=dict(as_deltas=AS_DELTAS, off_p=OFF_P, off_v=OFF_V, mu_ref=MU_REF, two_p=TWO_P, two_v=TWO_V,
                         hetero=HETERO, mu_power=MU_POWER, sweep_delta_D=SWEEP_D, sweep_delta_R=SWEEP_R),
               summary=summ, rows=rows)
    raw.write_text(json.dumps(out, indent=1) + "\n")
    log.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
