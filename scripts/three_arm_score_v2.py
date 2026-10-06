"""Frozen scorer for the three-arm test, design v0.2 (docs/three-arm-design-v0.2.md §3, §5), with the pilot's
change (docs/three-arm-pilot-v0.1.md, result): r1 is the control for K; the self-copy checks for a field × class
interaction and carries the secondary H_field test. Written and tested before any confirmatory model exists.

  uv run --extra learner python scripts/three_arm_score_v2.py --census-dir <dir> --seeds 1 2 ... 12 \\
      --raw docs/three-arm-verdict-<date>.json

Margins are frozen here (prereg v0.2 §4), not taken from the command line: field interaction ±0.002 bits, H_field
±0.001 bits.

THE UNIT IS THE SEED. Per seed s, with y the realized KIND excess per test window (census by_field.kind) and the
class sets fixed by the exact side (Δι_A from the sha-gated per-class cache, keyed by the window's r1 class):
  moved_A = { w : |Δι_A(w)| > τ },  zero_A = { w : Δι_A(w) = 0 exactly (the cache's Fraction flag) }
  K_A,s   = mean_{moved_A} (y_r1,s − y_A,s) − mean_{zero_A} (y_r1,s − y_A,s)        A ∈ {R, D}
  KS_A,s  = the same contrast with the self-copy, y_r1,s − y_S,s, on A's sets
  k_A,s   = K_A,s / m_A,   m_A = mean |Δι_A| over moved_A
  F_s     = mean over all windows of y_r1,s − y_S,s

Rules, in order (score_seeds):
  a. P_V: one-sample t of K_R across seeds ≥ 3; else the reading is "no replication" and no ratio is computed.
  b. Field × class interaction: if the one-sample t of KS_R or of KS_D has |t| ≥ 3 (EVIDENCE of an interaction),
     "mechanism withheld: field × class interaction". The TOST against ±margin_field_interaction is reported but does
     not gate (severity v2: at 12 seeds an equivalence gate withheld the mechanism in up to 99 % of simulations).
  c. ρ = mean k_D / mean k_R, seed-level percentile bootstrap 90 % CI (seeds resampled jointly). A draw with
     mean k_R ≤ 0 counts as +inf for the upper tail and −inf for the lower; their number is reported.
  d. "move-dominant" if the CI lies entirely above 0.5 (moving KIND information without binding content reproduces
     more than half of the relay's per-bit gain); "binding-dominant" if it lies entirely below 0.5; otherwise
     "unresolved". (Severity v2: the band readings of the first draft had ~1 % power for H_bind.)
  e. Secondary, independent of the reading: H_field, TOST of mean F within ±margin_field.

Gates (any failure raises relay_paired.Gate and writes nothing): exactly one census raw <rung>-s<seed>.json per
(rung, seed), and no other census raw in the directory; each census is k = 7, full test split, its per-window file
at its recorded sha256; census rung / seed / ε / step agree with the file name; the run dir's run.json shows the
seed, 15 epochs, d_model 128, lr 1e-3, the census's corpus and that corpus manifest's sha256; its log.jsonl ends at
step 117195; its ckpt.pt has the census's checkpoint sha256; the corpus manifest's rung is the file's rung, ε = 1,
and its run key hashes to run 0582ffbeb4693d27; no two censuses share a run, checkpoint or per-window file; all
window id sets are identical; every r1 class key (recomputed from the r1 corpus's test split) is in both Δι caches.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relay_paired import Gate, load_census  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNGS = ("r1", "r1R", "r1D", "r1S")
EXACT = {"r1R": "docs/relay-exact-side-2026-09-30.json", "r1D": "docs/three-arm-exact-side-r1D-2026-10-05.json"}
FRESH_RUN = "0582ffbeb4693d27"
FINAL_STEP = 117195
RECIPE = dict(epochs=15, d_model=128, lr=1e-3)
EPS = "1"
K = 7
TAU = 0.1
ALPHA = 0.05
PV_T = 3.0
RHO_SPLIT = 0.5
FI_T = 3.0
N_BOOT = 10000
RNG_SEED = 20261005
MARGINS = dict(field_interaction=0.002, field=0.001)     # prereg v0.2 §4
READINGS = ("no replication", "mechanism withheld: field × class interaction", "move-dominant", "binding-dominant",
            "unresolved")


# ---- Student t, numpy-free (scipy is not installed) ------------------------------------

def _betacf(a, b, x):
    """Continued fraction for the regularized incomplete beta (modified Lentz)."""
    tiny, eps = 1e-300, 1e-15
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 10000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    """P(T ≤ t) for Student's t with df degrees of freedom."""
    if math.isinf(t):
        return 1.0 if t > 0 else 0.0
    tail = 0.5 * betainc(df / 2.0, 0.5, df / (df + t * t))
    return 1.0 - tail if t > 0 else tail


def t_ppf(p, df):
    """Quantile of Student's t by bisection on t_cdf (to ~1e-12)."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie in (0, 1)")
    lo, hi = -1.0, 1.0
    while t_cdf(lo, df) > p:
        lo *= 2.0
    while t_cdf(hi, df) < p:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return 0.5 * (lo + hi)


# ---- seed-level statistics (pure) ------------------------------------------------------

def _summary(x):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    mean, sd = float(x.mean()), float(x.std(ddof=1))
    se = sd / math.sqrt(n)
    t = mean / se if se > 0 else (math.copysign(math.inf, mean) if mean != 0 else 0.0)
    return dict(n=n, mean=mean, sd=sd, se=se, t=t, df=n - 1)


def tost(x, margin, alpha=ALPHA):
    """Two one-sided t-tests that the mean of x lies within (−margin, +margin); equivalent iff both reject,
    i.e. iff the (1 − 2α) t interval lies inside the margins."""
    s = _summary(x)
    q = t_ppf(1 - alpha, s["df"])
    ci = (s["mean"] - q * s["se"], s["mean"] + q * s["se"])
    if s["se"] > 0:
        t_lower, t_upper = (s["mean"] + margin) / s["se"], (s["mean"] - margin) / s["se"]
    else:
        t_lower = math.inf if s["mean"] > -margin else -math.inf
        t_upper = -math.inf if s["mean"] < margin else math.inf
    eq = bool(t_lower > q and t_upper < -q)
    return dict(mean=s["mean"], sd=s["sd"], se=s["se"], df=s["df"], margin=margin, alpha_each=alpha,
                t_crit=q, t_lower=t_lower, t_upper=t_upper, ci90=list(ci), equivalent=eq)


def bootstrap_rho(k_R, k_D, n_boot=N_BOOT, rng_seed=RNG_SEED, level=0.90):
    """Seed-level percentile bootstrap of ρ = mean k_D / mean k_R; seeds resampled jointly (one index set per
    draw for both arrays). A draw with mean k_R ≤ 0 is +inf for the upper bound and −inf for the lower."""
    k_R, k_D = np.asarray(k_R, dtype=np.float64), np.asarray(k_D, dtype=np.float64)
    n = len(k_R)
    idx = np.random.default_rng(rng_seed).integers(0, n, size=(n_boot, n))
    den, num = k_R[idx].mean(axis=1), k_D[idx].mean(axis=1)
    bad = den <= 0
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(bad, np.nan, num / np.where(bad, 1.0, den))
    a = (1 - level) / 2
    lo = float(np.quantile(np.where(bad, -np.inf, r), a, method="inverted_cdf"))
    hi = float(np.quantile(np.where(bad, np.inf, r), 1 - a, method="inverted_cdf"))
    point = float(k_D.mean() / k_R.mean()) if k_R.mean() > 0 else None
    return dict(point=point, ci90=[lo, hi], level=level, n_boot=int(n_boot), rng_seed=rng_seed,
                n_nonpositive_denominator=int(bad.sum()), method="percentile, seeds resampled jointly")


def score_seeds(K_R, K_D, KS_R, KS_D, mR, mD, F, margins, n_boot=N_BOOT, rng_seed=RNG_SEED):
    """The v0.2 readings from per-seed contrasts (module docstring, rules a–e)."""
    arrs = {k: np.asarray(v, dtype=np.float64) for k, v in
            dict(K_R=K_R, K_D=K_D, KS_R=KS_R, KS_D=KS_D, F=F).items()}
    n = len(arrs["K_R"])
    if any(a.ndim != 1 or len(a) != n for a in arrs.values()):
        raise ValueError("per-seed arrays must be 1-d and of equal length")
    if n < 2:
        raise ValueError("at least two seeds are needed")
    if not all(np.isfinite(a).all() for a in arrs.values()):
        raise ValueError("per-seed arrays must be finite")
    if not (mR > 0 and mD > 0 and math.isfinite(mR) and math.isfinite(mD)):
        raise ValueError("mR and mD (mean |Δι| on the moved sets) must be positive")
    if not {"field_interaction", "field"} <= set(margins):
        raise ValueError("margins needs 'field_interaction' and 'field'")
    k_R, k_D = arrs["K_R"] / mR, arrs["K_D"] / mD
    per_seed = {k: a.tolist() for k, a in arrs.items()}
    per_seed.update(k_R=k_R.tolist(), k_D=k_D.tolist())
    summary = {k: _summary(v) for k, v in dict(arrs, k_R=k_R, k_D=k_D).items()}
    pv = summary["K_R"]
    P_V = dict(t=pv["t"], df=pv["df"], threshold=PV_T, **{"pass": bool(pv["t"] >= PV_T)})
    fi = {a: tost(arrs[a], margins["field_interaction"]) for a in ("KS_R", "KS_D")}
    fi["evidence"] = {a: dict(t=summary[a]["t"], flagged=bool(abs(summary[a]["t"]) >= FI_T)) for a in ("KS_R", "KS_D")}
    fi["pass"] = not any(v["flagged"] for v in fi["evidence"].values())     # gates on EVIDENCE of interaction only
    fi["equivalent_both"] = bool(fi["KS_R"]["equivalent"] and fi["KS_D"]["equivalent"])   # reported, not gating
    h = tost(arrs["F"], margins["field"])
    H_field = dict(result="equivalent" if h["equivalent"] else "not equivalent", **h)
    rho = None
    if not P_V["pass"]:
        reading = READINGS[0]
    else:
        rho = bootstrap_rho(k_R, k_D, n_boot, rng_seed)       # mean k_R > 0 here, since t ≥ 3 and mR > 0
        lo, hi = rho["ci90"]
        if not fi["pass"]:
            reading = READINGS[1]
            rho["note"] = "reported only: the mechanism reading is withheld (field × class interaction)"
        elif lo > RHO_SPLIT:
            reading = "move-dominant"
        elif hi < RHO_SPLIT:
            reading = "binding-dominant"
        else:
            reading = "unresolved"
    return dict(n_seeds=n, mR=float(mR), mD=float(mD), margins=dict(margins), per_seed=per_seed, summary=summary,
                P_V=P_V, field_interaction=fi, rho=rho, reading=reading, H_field=H_field,
                rules=dict(P_V=f"t(K_R) >= {PV_T}",
                           field_interaction=f"withheld iff |t(KS_R)| or |t(KS_D)| >= {FI_T}; TOST reported",
                           move_dominant=f"rho 90% CI entirely above {RHO_SPLIT}",
                           binding_dominant=f"rho 90% CI entirely below {RHO_SPLIT}",
                           H_field=f"TOST alpha {ALPHA} each, secondary"))


# ---- per-seed arrays from per-window excess (pure) --------------------------------------

def seed_arrays(y, sets, seeds, tau=TAU):
    """y: {(rung, seed): per-window KIND excess, one window order}; sets: {"r1R"|"r1D": (|Δι| array, exact-zero
    bool array)} in the same order. Returns the per-seed contrasts and the arms' mean |Δι| on their moved sets."""
    out, info = {}, {}
    masks = {}
    for arm, (x, z) in sets.items():
        x, z = np.abs(np.asarray(x, dtype=np.float64)), np.asarray(z, dtype=bool)
        M = x > tau
        if not M.any() or not z.any():
            raise Gate(f"GATE: {arm} has an empty moved set (|Δι| > {tau}) or an empty exact-zero set")
        if (M & z).any():
            raise Gate(f"GATE: {arm}: a window is flagged exact-zero but has |Δι| > {tau}")
        masks[arm] = (M, z)
        info[arm] = dict(moved=int(M.sum()), zero=int(z.sum()))
        out["m" + arm[-1]] = float(x[M].mean())

    def contrast(D, arm):
        M, z = masks[arm]
        return float(D[M].mean() - D[z].mean())

    for arm in ("r1R", "r1D"):
        A = arm[-1]
        out[f"K_{A}"] = np.array([contrast(y[("r1", s)] - y[(arm, s)], arm) for s in seeds])
        out[f"KS_{A}"] = np.array([contrast(y[("r1", s)] - y[("r1S", s)], arm) for s in seeds])
    out["F"] = np.array([float((y[("r1", s)] - y[("r1S", s)]).mean()) for s in seeds])
    out["sets"] = info
    return out


# ---- provenance gates ------------------------------------------------------------------

def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _path(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def _check_one(cd, rung, seed):
    raw = cd / f"{rung}-s{seed}.json"
    if not raw.is_file():
        raise Gate(f"GATE: census {raw} is missing")
    c, rows = load_census(raw)                       # per-window sha256, k = 7, full test split
    tag = f"census {raw.name}"
    if c["rung"] != rung:
        raise Gate(f"GATE: {tag} declares rung {c['rung']!r}, the file name says {rung!r}")
    if c["seed"] != seed:
        raise Gate(f"GATE: {tag} declares seed {c['seed']!r}, expected {seed}")
    if c["eps"] != EPS:
        raise Gate(f"GATE: {tag} has eps {c['eps']!r}, expected {EPS}")
    if c["step"] != FINAL_STEP:
        raise Gate(f"GATE: {tag} was taken at step {c['step']}, expected the final step {FINAL_STEP}")
    run = _path(c["run"])
    rj = json.loads((run / "run.json").read_text())
    if rj.get("seed") != seed:
        raise Gate(f"GATE: {tag}: run.json seed {rj.get('seed')!r}, expected {seed}")
    if rj.get("epochs") != RECIPE["epochs"]:
        raise Gate(f"GATE: {tag}: run.json epochs {rj.get('epochs')!r}, expected {RECIPE['epochs']}")
    if rj.get("model", {}).get("d_model") != RECIPE["d_model"]:
        raise Gate(f"GATE: {tag}: run.json d_model {rj.get('model', {}).get('d_model')!r}, expected {RECIPE['d_model']}")
    if rj.get("lr") != RECIPE["lr"]:
        raise Gate(f"GATE: {tag}: run.json lr {rj.get('lr')!r}, expected {RECIPE['lr']}")
    if rj.get("steps_total") != FINAL_STEP:
        raise Gate(f"GATE: {tag}: run.json steps_total {rj.get('steps_total')!r}, expected step {FINAL_STEP}")
    steps = [json.loads(l).get("step") for l in (run / "log.jsonl").read_text().splitlines() if l.strip()]
    steps = [s for s in steps if s is not None]
    if not steps or steps[-1] != FINAL_STEP or max(steps) != FINAL_STEP:
        raise Gate(f"GATE: {tag}: log.jsonl does not end at the final step {FINAL_STEP}")
    if _sha(run / "ckpt.pt") != c["checkpoint_sha256"]:
        raise Gate(f"GATE: {tag}: {run / 'ckpt.pt'} sha256 differs from the census's checkpoint_sha256")
    corpus = _path(c["corpus"])
    if _path(rj.get("corpus_dir", "")).resolve() != corpus.resolve():
        raise Gate(f"GATE: {tag}: the census's corpus is not the run's corpus_dir")
    mpath = corpus / "manifest.json"
    if _sha(mpath) != rj.get("corpus_manifest_sha256"):
        raise Gate(f"GATE: {tag}: corpus manifest sha256 differs from run.json's corpus_manifest_sha256")
    m = json.loads(mpath.read_text())
    if m.get("rung") != rung:
        raise Gate(f"GATE: {tag}: the corpus manifest's rung is {m.get('rung')!r}, expected {rung!r}")
    if m.get("epsilon") != EPS:
        raise Gate(f"GATE: {tag}: the corpus manifest's epsilon is {m.get('epsilon')!r}, expected {EPS}")
    run_id = hashlib.sha256(bytes.fromhex(m.get("run_key_hex", ""))).hexdigest()[:16]
    if run_id != FRESH_RUN or corpus.name != FRESH_RUN:
        raise Gate(f"GATE: {tag}: corpus run {run_id} ({corpus.name}), expected {FRESH_RUN}")
    prov = dict(raw=str(raw), raw_sha256=_sha(raw), run=str(run), checkpoint_sha256=c["checkpoint_sha256"],
                per_window_file=c["per_window_file"], per_window_sha256=c["per_window_sha256"],
                corpus=c["corpus"], corpus_manifest_sha256=rj["corpus_manifest_sha256"])
    return c, rows, prov


def gate_censuses(census_dir, seeds):
    """All provenance gates that need no corpus records or Δι caches. Returns ({(rung, seed): (census, rows,
    provenance)}, sorted window ids)."""
    cd = Path(census_dir).expanduser()
    seeds = list(seeds)
    if len(set(seeds)) != len(seeds):
        raise Gate(f"GATE: duplicate seed in --seeds {seeds}")
    if len(seeds) < 2:
        raise Gate("GATE: at least two seeds are needed")
    want = {f"{r}-s{s}.json" for r in RUNGS for s in seeds}
    pat = re.compile(r"^(%s)-s(\d+)\.json$" % "|".join(RUNGS))
    extra = sorted(p.name for p in cd.glob("*.json") if pat.match(p.name) and p.name not in want)
    if extra:
        raise Gate(f"GATE: census raws not in --seeds are in {cd}: {extra}")
    cen = {(r, s): _check_one(cd, r, s) for r in RUNGS for s in seeds}
    for field in ("run", "checkpoint_sha256", "per_window_sha256", "raw_sha256"):
        vals = [p[field] for _, _, p in cen.values()]
        if len(set(vals)) != len(vals):
            raise Gate(f"GATE: duplicate {field} across census raws")
    ids = sorted(next(iter(cen.values()))[1])
    for (r, s), (_, rows, _) in cen.items():
        if sorted(rows) != ids:
            raise Gate(f"GATE: census {r}-s{s} window id set differs from the others")
    return cen, ids


def class_sets(r1_corpus, ids):
    """Per window (in ids order): the r1 class key recomputed from the r1 corpus's test split, and per arm the
    |Δι| and exact-zero flag from the sha-gated cache. Returns (sets, provenance)."""
    from relay_paired import load_diota, load_records
    from yupi.naming import pattern_all
    from yupi.pattern_ceiling import serial_key
    recs = load_records(str(_path(r1_corpus)), ids, "r1")
    keys = [serial_key((recs[i][0], pattern_all(recs[i][1][:K])[0])) for i in ids]
    sets, prov = {}, {}
    for arm, es in EXACT.items():
        esj = json.loads(_path(es).read_text())
        if esj.get("rung_name") != arm or esj.get("all_gates") is not True:
            raise Gate(f"GATE: exact side {es} is not {arm}'s or did not pass all its gates")
        dio, meta = load_diota(str(_path(es)), EPS)
        missing = [k for k in set(keys) if k not in dio]
        if missing:
            raise Gate(f"GATE: {len(missing)} r1 classes missing from {arm}'s Δι cache")
        sets[arm] = (np.abs(np.array([dio[k][1] for k in keys], dtype=np.float64)),
                     np.array([bool(dio[k][2]) for k in keys]))
        prov[arm] = dict(exact_side=es, exact_side_sha256=_sha(_path(es)), **meta)
    return sets, prov, len(set(keys))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--census-dir", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, required=True)
    ap.add_argument("--tau", type=float, default=TAU)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--rng-seed", type=int, default=RNG_SEED)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args(argv)
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    cen, ids = gate_censuses(a.census_dir, a.seeds)
    sets, dprov, n_classes = class_sets(cen[("r1", a.seeds[0])][0]["corpus"], ids)
    y = {k: np.array([rows[i]["by_field"]["kind"] for i in ids], dtype=np.float64) for k, (_, rows, _) in cen.items()}
    arr = seed_arrays(y, sets, a.seeds, a.tau)
    res = score_seeds(arr["K_R"], arr["K_D"], arr["KS_R"], arr["KS_D"], arr["mR"], arr["mD"], arr["F"], MARGINS,
                      n_boot=a.n_boot, rng_seed=a.rng_seed)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    out = dict(prereg="docs/three-arm-prereg-v0.2.md", design="docs/three-arm-design-v0.2.md", control_for_K="r1", git=git + ("+dirty" if dirty else ""),
               scorer_sha256=_sha(Path(__file__).resolve()), seeds=a.seeds, tau=a.tau, eps=EPS, k=K,
               n_windows=len(ids), n_r1_classes=n_classes, sets=arr["sets"],
               recipe=dict(RECIPE, final_step=FINAL_STEP, corpus_run=FRESH_RUN),
               censuses={f"{r}-s{s}": p for (r, s), (_, _, p) in cen.items()}, d_iota=dprov,
               gates="all passed", **res)
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(dict(reading=res["reading"], P_V=res["P_V"], rho=res["rho"] and res["rho"]["ci90"],
                          H_field=res["H_field"]["result"], raw=a.raw), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
