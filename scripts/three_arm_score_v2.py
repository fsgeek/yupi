"""Frozen scorer for the three-arm test, design v0.2 (docs/three-arm-design-v0.2.md §3, §5), revised to SCORER_VERSION
2.1 after the two pre-stamp reviews of prereg v0.2. Written and tested before any confirmatory model exists.

  uv run --extra learner python scripts/three_arm_score_v2.py --census-dir <dir> --raw docs/three-arm-verdict-<date>.json

NOTHING IS SELECTABLE FROM THE COMMAND LINE but the census directory and the output path. The seeds are exactly 1..12
(SEEDS), τ = 0.1, 10,000 bootstrap draws at a fixed generator seed, a 95 % interval and a 20 % trim are constants; the
CLI refuses any other argument. score_dir() takes underscored overrides for tests only, and a raw written with any
of them non-default is marked frozen_settings: false.

THE UNIT IS THE SEED. Per seed s, with y the realized KIND excess per test window (census by_field.kind) and the
class sets fixed by the exact side (Δι_A from the sha-gated per-class cache, keyed by the window's r1 class):
  moved_A = { w : |Δι_A(w)| > τ },  zero_A = { w : Δι_A(w) = 0 exactly (the cache's Fraction flag) }
  K_A,s   = mean_{moved_A} (y_r1,s − y_A,s) − mean_{zero_A} (y_r1,s − y_A,s)        A ∈ {R, D}   (r1 control)
  KS_A,s  = the same contrast with the self-copy, y_r1,s − y_S,s, on A's sets
  K'_A,s  = K_A,s − KS_A,s = mean_{moved_A} (y_S,s − y_A,s) − mean_{zero_A} (y_S,s − y_A,s)  (self-copy control)
  k'_A,s  = K'_A,s / m_A,   m_A = mean |Δι_A| over moved_A
  F_s     = mean over all windows of y_r1,s − y_S,s
A field × class interaction δ_A (the added OBJECT field helping or hurting differently on moved_A and zero_A,
whatever the field carries) enters K_A and KS_A alike and cancels in K'_A. That is why the ratio uses K'.

Readings, in order (score_seeds):
  i.   P_V: one-sample t of K_R across seeds ≥ 3; else "no replication".
  ii.  P_R': one-sample t of K'_R ≥ 3; else NO_RELAY_GAIN (the relay does not beat the self-copy where it moves
       information). No ratio is computed after (i) or (ii) fails.
  iii. ρ = T(k'_D) / T(k'_R), T the 20 %-trimmed mean across seeds (floor(0.2 n) dropped from each end; 2 each side
       at n = 12), with a seed-level percentile bootstrap 95 % CI (seeds resampled jointly, N_BOOT draws, RNG_SEED).
       A draw with T(k'_R) ≤ 0 counts as +inf for the upper bound and −inf for the lower; their number is reported.
       "move-dominant" if the CI lower bound > 0.5; "binding-dominant" if the CI upper bound < 0.5; else
       "unresolved".
  Descriptive only: t and TOST (±0.002 bits) of KS_R and KS_D. They gate nothing.
  Secondary, independent of the reading: H_field, TOST of mean F within ±0.001 bits.

Gates (any failure raises relay_paired.Gate and writes nothing):
  - exactly one census raw <rung>-s<seed>.json per (rung, seed) for the frozen seeds, and no census raw for any
    other seed in the directory;
  - each census is k = 7, split test, n None (full split), its per-window file at its recorded sha256; census rung /
    seed / ε / step agree with the file name;
  - run.json: the seed, and EVERY field of RECIPE (architecture, optimizer, schedule, run length) equal to the pilot
    runs' values (field missing = failure). The lr schedule itself is code (warmup then cosine to lr_min over
    steps_planned, src/yupi/learner/train.py); its parameters lr, lr_min, warmup, steps_planned are gated;
  - log.jsonl ends at step 117195; ckpt.pt has the census's checkpoint sha256; the census's corpus is the run's
    corpus_dir, at the manifest sha256 run.json records; the manifest's rung is the file's, ε = 1, and its run key
    hashes to run 0582ffbeb4693d27; all seeds of a rung share that corpus;
  - no two censuses share a run, checkpoint, per-window file or raw; all window id sets are identical;
  - the window id set is exactly the r1 corpus test split's windows with ≥ K + 1 = 8 records (evaluate()'s rule for
    k = 7; at this corpus that equals the windows with ≥ 7 records), so the count matches the full split;
  - cross-rung pairing: each arm corpus's test window i is window_map(arm) applied to the r1 corpus's test window i
    (same reset flag); the per-window rows record only a census-local integer class id (the census stores labels only
    for ≤ 5000 classes), so per census the check is that the partition of windows by that id is EXACTLY the
    partition by the class key recomputed from the rung's records (an id ↔ key bijection over the scored windows);
  - every r1 class key is in both Δι caches; the r1R and r1D exact sides passed all their gates;
  - the r1S exact side (EXACT_S) passed all its gates and every d_iota_kind_4 entry reports
    self_copy_all_zero_exact true.
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

SCORER_VERSION = "2.1"
ROOT = Path(__file__).resolve().parents[1]
RUNGS = ("r1", "r1R", "r1D", "r1S")
ARMS = ("r1R", "r1D", "r1S")
EXACT = {"r1R": "docs/relay-exact-side-2026-09-30.json", "r1D": "docs/three-arm-exact-side-r1D-2026-10-05.json"}
EXACT_S = "docs/three-arm-exact-side-r1S-2026-10-05.json"
FRESH_RUN = "0582ffbeb4693d27"
FINAL_STEP = 117195
SEEDS = tuple(range(1, 13))                          # prereg: seeds 1..12, all of them, no others
# The pilot runs' recipe (run.json of the 12 threearm-pilot runs, identical across rungs and seeds), frozen here.
# Dotted names are nested under "model". Gated field by field; a missing field fails.
RECIPE = {"batch_size": 256, "epochs": 15, "lr": 0.001, "lr_min": 0.0001, "warmup": 500, "weight_decay": 0.1,
          "grad_clip": 1.0, "max_steps": None, "model.d_model": 128, "model.n_layer": 4, "model.n_head": 4,
          "model.d_mlp": 512, "model.n_pos": 42, "model.vocab_in": 157, "model.vocab_out": 156, "n_params": 838940,
          "steps_per_epoch": 7813, "steps_planned": FINAL_STEP, "steps_total": FINAL_STEP}
EPS = "1"
K = 7
TAU = 0.1
ALPHA = 0.05
PV_T = 3.0
PRP_T = 3.0
RHO_SPLIT = 0.5
TRIM = 0.2
CI_LEVEL = 0.95
N_BOOT = 10000
RNG_SEED = 20261005
MARGINS = dict(field_interaction=0.002, field=0.001)     # KS descriptive TOST; H_field secondary
NO_RELAY_GAIN = "no relay-specific gain (relay does not beat the self-copy where it moves information)"
READINGS = ("no replication", NO_RELAY_GAIN, "move-dominant", "binding-dominant", "unresolved")


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


def trimmed_mean(x, trim=TRIM, axis=-1):
    """Symmetric trimmed mean: sort, drop floor(trim · n) values from each end, average the rest."""
    x = np.sort(np.asarray(x, dtype=np.float64), axis=axis)
    n = x.shape[axis]
    g = int(math.floor(trim * n))
    return np.take(x, np.arange(g, n - g), axis=axis).mean(axis=axis)


def bootstrap_rho(k_R, k_D, n_boot=N_BOOT, rng_seed=RNG_SEED, level=CI_LEVEL, trim=TRIM):
    """Seed-level percentile bootstrap of ρ = T(k_D) / T(k_R), T the trimmed mean; seeds resampled jointly (one
    index set per draw for both arrays). A draw with T(k_R) ≤ 0 is +inf for the upper bound and −inf for the lower."""
    k_R, k_D = np.asarray(k_R, dtype=np.float64), np.asarray(k_D, dtype=np.float64)
    n = len(k_R)
    idx = np.random.default_rng(rng_seed).integers(0, n, size=(n_boot, n))
    den, num = trimmed_mean(k_R[idx], trim, axis=1), trimmed_mean(k_D[idx], trim, axis=1)
    bad = den <= 0
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(bad, np.nan, num / np.where(bad, 1.0, den))
    a = (1 - level) / 2
    lo = float(np.quantile(np.where(bad, -np.inf, r), a, method="inverted_cdf"))
    hi = float(np.quantile(np.where(bad, np.inf, r), 1 - a, method="inverted_cdf"))
    tR, tD = float(trimmed_mean(k_R, trim)), float(trimmed_mean(k_D, trim))
    return dict(point=tD / tR if tR > 0 else None, trimmed_mean_k_R=tR, trimmed_mean_k_D=tD, ci=[lo, hi],
                level=level, trim=trim, n_trimmed_each_end=int(math.floor(trim * n)), n_boot=int(n_boot),
                rng_seed=rng_seed, n_nonpositive_denominator=int(bad.sum()),
                method="percentile, seeds resampled jointly, ratio of trimmed means")


def score_seeds(K_R, K_D, KS_R, KS_D, mR, mD, F, margins, n_boot=N_BOOT, rng_seed=RNG_SEED):
    """The v2.1 readings from per-seed contrasts (module docstring, readings i–iii)."""
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
    arrs["Kp_R"], arrs["Kp_D"] = arrs["K_R"] - arrs["KS_R"], arrs["K_D"] - arrs["KS_D"]
    kp_R, kp_D = arrs["Kp_R"] / mR, arrs["Kp_D"] / mD
    per_seed = {k: a.tolist() for k, a in arrs.items()}
    per_seed.update(kp_R=kp_R.tolist(), kp_D=kp_D.tolist())
    summary = {k: _summary(v) for k, v in dict(arrs, kp_R=kp_R, kp_D=kp_D).items()}
    pv, pr = summary["K_R"], summary["Kp_R"]
    P_V = dict(t=pv["t"], df=pv["df"], threshold=PV_T, **{"pass": bool(pv["t"] >= PV_T)})
    P_Rp = dict(t=pr["t"], df=pr["df"], threshold=PRP_T, **{"pass": bool(pr["t"] >= PRP_T)})
    sc = {a: dict(t=summary[a]["t"], **tost(arrs[a], margins["field_interaction"])) for a in ("KS_R", "KS_D")}
    sc["note"] = "descriptive only: a field × class interaction cancels in K' and gates nothing"
    h = tost(arrs["F"], margins["field"])
    H_field = dict(result="equivalent" if h["equivalent"] else "not equivalent", **h)
    rho = None
    if not P_V["pass"]:
        reading = READINGS[0]
    elif not P_Rp["pass"]:
        reading = READINGS[1]
    else:
        rho = bootstrap_rho(kp_R, kp_D, n_boot, rng_seed)
        lo, hi = rho["ci"]
        if lo > RHO_SPLIT:
            reading = "move-dominant"
        elif hi < RHO_SPLIT:
            reading = "binding-dominant"
        else:
            reading = "unresolved"
    return dict(scorer_version=SCORER_VERSION, n_seeds=n, mR=float(mR), mD=float(mD), margins=dict(margins),
                per_seed=per_seed, summary=summary, P_V=P_V, P_Rp=P_Rp, self_copy_contrast=sc, rho=rho,
                reading=reading, H_field=H_field,
                rules=dict(P_V=f"t(K_R) >= {PV_T} (r1 control)",
                           P_Rp=f"t(K'_R) >= {PRP_T}, K' = K - KS (self-copy control)",
                           rho=f"T(k'_D)/T(k'_R), T = {TRIM:g}-trimmed mean; {CI_LEVEL:.0%} seed bootstrap CI",
                           move_dominant=f"CI lower > {RHO_SPLIT}", binding_dominant=f"CI upper < {RHO_SPLIT}",
                           self_copy_contrast="KS_R, KS_D t and TOST reported, not gating",
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


def _flat(d, pre=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_flat(v, pre + k + "."))
        else:
            out[pre + k] = v
    return out


def check_recipe(rj, seed, tag):
    """run.json must show the seed and every RECIPE field at its frozen value (a missing field fails)."""
    if rj.get("seed") != seed:
        raise Gate(f"GATE: {tag}: run.json seed {rj.get('seed')!r}, expected {seed}")
    flat = _flat(rj)
    for f, want in RECIPE.items():
        if f not in flat:
            raise Gate(f"GATE: {tag}: run.json lacks the recipe field {f!r}")
        got = flat[f]
        same = (got is None and want is None) or (got is not None and want is not None
                                                   and type(got) is not bool and got == want)
        if not same:
            raise Gate(f"GATE: {tag}: run.json recipe field {f} = {got!r}, expected {want!r}")


def _check_one(cd, rung, seed):
    raw = cd / f"{rung}-s{seed}.json"
    if not raw.is_file():
        raise Gate(f"GATE: census {raw} is missing")
    c, rows = load_census(raw)                       # per-window sha256, k = 7, full test split
    tag = f"census {raw.name}"
    if c.get("n") is not None or c.get("split") != "test" or c.get("k") != K:
        raise Gate(f"GATE: {tag} is not a k = {K}, full (n None) test-split census")
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
    check_recipe(rj, seed, tag)
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
    provenance)}, sorted window ids). `seeds` is SEEDS on the CLI path; tests pass small worlds."""
    cd = Path(census_dir).expanduser()
    seeds = list(seeds)
    if len(set(seeds)) != len(seeds):
        raise Gate(f"GATE: duplicate seed in {seeds}")
    if len(seeds) < 2:
        raise Gate("GATE: at least two seeds are needed")
    want = {f"{r}-s{s}.json" for r in RUNGS for s in seeds}
    pat = re.compile(r"^(%s)-s(\d+)\.json$" % "|".join(RUNGS))
    extra = sorted(p.name for p in cd.glob("*.json") if pat.match(p.name) and p.name not in want)
    if extra:
        raise Gate(f"GATE: census raws for seeds outside {seeds} are in {cd}: {extra}")
    cen = {(r, s): _check_one(cd, r, s) for r in RUNGS for s in seeds}
    for field in ("run", "checkpoint_sha256", "per_window_sha256", "raw_sha256"):
        vals = [p[field] for _, _, p in cen.values()]
        if len(set(vals)) != len(vals):
            raise Gate(f"GATE: duplicate {field} across census raws")
    for r in RUNGS:
        if len({str(_path(cen[(r, s)][0]["corpus"]).resolve()) for s in seeds}) != 1:
            raise Gate(f"GATE: the seeds of rung {r} were censused on different corpora")
    ids = sorted(next(iter(cen.values()))[1])
    for (r, s), (_, rows, _) in cen.items():
        if sorted(rows) != ids:
            raise Gate(f"GATE: census {r}-s{s} window id set differs from the others")
    return cen, ids


def check_window_set(n_records, ids):
    """n_records: {window index: record count} over the r1 corpus's WHOLE test split. The scored ids must be exactly
    the windows evaluate() scores at k = K (≥ K + 1 records), so their count is the full split's."""
    want = sorted(i for i, n in n_records.items() if n >= K + 1)
    if len(ids) != len(want):
        raise Gate(f"GATE: scored window count {len(ids)} differs from the test split's {len(want)} windows with "
                   f">= {K + 1} records")
    if list(ids) != want:
        raise Gate(f"GATE: the scored window set is not the test split's windows with >= {K + 1} records")


def _key(rec):
    from yupi.naming import pattern_all
    from yupi.pattern_ceiling import serial_key
    reset, records = rec
    return serial_key((reset, pattern_all(records[:K])[0]))


def check_class_pairing(recs, rows_by_census, ids):
    """recs: {rung: {i: (reset, records)}} from each rung's corpus test split; rows_by_census: {(rung, seed): {i:
    row}}. Checks (1) every arm window i is window_map(arm) of r1 window i, same reset flag; (2) per census, the
    partition of windows by the row's class id equals the partition by the class key recomputed from the rung's
    records. Returns the r1 class keys in ids order."""
    from yupi.interfaces import window_map
    for arm in ARMS:
        wm = window_map(arm)
        for i in ids:
            r0, r1 = recs["r1"][i]
            ra, xa = recs[arm][i]
            if ra != r0 or tuple(xa) != tuple(wm(r1)):
                raise Gate(f"GATE: {arm} test window {i} is not paired with r1 window {i} (window map differs)")
    keys = {r: [_key(recs[r][i]) for i in ids] for r in RUNGS}
    for (rung, seed), rows in rows_by_census.items():
        fwd, back = {}, {}
        for i, k in zip(ids, keys[rung]):
            if "key" not in rows[i]:
                raise Gate(f"GATE: census {rung}-s{seed} window {i} records no class id")
            cid = rows[i]["key"]
            if fwd.setdefault(cid, k) != k:
                raise Gate(f"GATE: census {rung}-s{seed}: class id {cid} covers two recomputed {rung} classes")
            if back.setdefault(k, cid) != cid:
                raise Gate(f"GATE: census {rung}-s{seed}: one recomputed {rung} class carries two class ids")
    return keys["r1"]


def check_self_copy_exact(path=EXACT_S):
    es = json.loads(_path(path).read_text())
    if es.get("rung_name") != "r1S" or es.get("all_gates") is not True:
        raise Gate(f"GATE: r1S exact side {path} is not r1S's or did not pass all its gates")
    ents = es.get("d_iota_kind_4") or []
    if not ents or any(e.get("self_copy_all_zero_exact") is not True for e in ents):
        raise Gate(f"GATE: r1S exact side {path}: not every d_iota_kind_4 entry has self_copy_all_zero_exact true")
    return dict(exact_side=str(path), exact_side_sha256=_sha(_path(path)),
                eps=[e.get("eps") for e in ents], self_copy_all_zero_exact=True)


def corpus_gates(cen, ids):
    """Load each rung's corpus test split; window-set and cross-rung pairing gates. Returns r1 class keys."""
    from yupi.corpus.vocab import VOCAB
    from yupi.corpus.writer import read_split
    from yupi.learner.evaluate import surface_records
    corpora = {r: next(c["corpus"] for (rr, _), (c, _, _) in cen.items() if rr == r) for r in RUNGS}
    recs, n_records = {}, None
    for r in RUNGS:
        split = read_split(_path(corpora[r]), "test")
        allrec = [surface_records(tuple(VOCAB[t] for t in w), r) for w, _ in split]
        if r == "r1":
            n_records = {i: len(x[1]) for i, x in enumerate(allrec)}
        elif len(allrec) != len(n_records):
            raise Gate(f"GATE: {r} test split has {len(allrec)} windows, r1 has {len(n_records)}")
        recs[r] = {i: allrec[i] for i in ids}
    check_window_set(n_records, ids)
    rows = {k: rws for k, (_, rws, _) in cen.items()}
    return check_class_pairing(recs, rows, ids)


def class_sets(keys):
    """Per window (in the keys' order): per arm the |Δι| and exact-zero flag from the sha-gated cache, keyed by the
    window's r1 class. Returns (sets, provenance, number of r1 classes)."""
    from relay_paired import load_diota
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


def score_dir(census_dir, raw, *, _seeds=SEEDS, _tau=TAU, _n_boot=N_BOOT, _rng_seed=RNG_SEED):
    """The whole scoring. The underscored overrides exist for tests ONLY; the CLI cannot reach them."""
    if Path(raw).exists():
        raise SystemExit(f"refusing to overwrite {raw}")
    frozen = (tuple(_seeds) == SEEDS and _tau == TAU and _n_boot == N_BOOT and _rng_seed == RNG_SEED)
    s_prov = check_self_copy_exact(EXACT_S)
    cen, ids = gate_censuses(census_dir, _seeds)
    keys = corpus_gates(cen, ids)
    sets, dprov, n_classes = class_sets(keys)
    dprov["r1S"] = s_prov
    y = {k: np.array([rows[i]["by_field"]["kind"] for i in ids], dtype=np.float64) for k, (_, rows, _) in cen.items()}
    arr = seed_arrays(y, sets, list(_seeds), _tau)
    res = score_seeds(arr["K_R"], arr["K_D"], arr["KS_R"], arr["KS_D"], arr["mR"], arr["mD"], arr["F"], MARGINS,
                      n_boot=_n_boot, rng_seed=_rng_seed)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    out = dict(prereg="docs/three-arm-prereg-v0.2.md", design="docs/three-arm-design-v0.2.md",
               control_for_K="r1", control_for_Kp="r1S", frozen_settings=frozen,
               git=git + ("+dirty" if dirty else ""), scorer_sha256=_sha(Path(__file__).resolve()),
               seeds=list(_seeds), tau=_tau, eps=EPS, k=K, n_windows=len(ids), n_r1_classes=n_classes,
               sets=arr["sets"], recipe=dict(RECIPE, final_step=FINAL_STEP, corpus_run=FRESH_RUN),
               censuses={f"{r}-s{s}": p for (r, s), (_, _, p) in cen.items()}, d_iota=dprov,
               gates="all passed", **res)
    Path(raw).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(dict(reading=res["reading"], P_V=res["P_V"], P_Rp=res["P_Rp"],
                          rho=res["rho"] and res["rho"]["ci"], H_field=res["H_field"]["result"],
                          frozen_settings=frozen, raw=str(raw)), indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                 allow_abbrev=False)
    ap.add_argument("--census-dir", required=True)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args(argv)                      # any other argument (seeds, τ, n_boot, ...) is an error
    return score_dir(a.census_dir, a.raw)


if __name__ == "__main__":
    sys.exit(main())
