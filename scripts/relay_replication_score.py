"""Frozen scorer for the relay replication (docs/relay-replication-design-v0.1.md §2–§4), SCORER_VERSION 1.0.
The provenance gates are adapted from three_arm_score_v3.py (3.0, left untouched) to the three rungs r1, r1R, r1S; the
claim function is replaced by the design's sign test. Written and tested before any confirmatory model exists.

  uv run --extra learner python scripts/relay_replication_score.py --census-dir <dir> --raw docs/relay-replication-verdict-<date>.json

NOTHING IS SELECTABLE FROM THE COMMAND LINE but the census directory and the output path. Seeds exactly 1..12 (SEEDS),
the set thresholds ±0.05, the pass count 10, 10,000 bootstrap draws at a fixed generator seed and a 95 % interval are
constants; the CLI refuses any other argument. score_dir() takes underscored overrides for tests only, and a raw
written with any of them non-default is marked frozen_settings: false.

THE UNIT IS THE SEED. Per seed s, with y the realized KIND excess per test window (census by_field.kind) and Δι_R the
signed relay Δι of the window's r1 class (sha-gated per-class cache of the frozen relay exact side):
  back    = { w : Δι_R(w) < −0.05 }            (the relay pushes next-KIND information further back)
  forward = { w : Δι_R(w) >  0.05 }            (the relay moves it closer)
  zero    = { w : Δι_R(w) = 0 exactly }        (the cache's exact Fraction flag, not a float comparison)
  L_s  = mean_back (y_r1,s − y_R,s) − mean_zero (y_r1,s − y_R,s)          (design §2; CONFIRMATORY)
  R_s  = mean_forward (y_r1,s − y_R,s) − mean_zero (y_r1,s − y_R,s)       (descriptive)
  LS_s = mean_back (y_r1,s − y_S,s) − mean_zero (y_r1,s − y_S,s)          (descriptive; self-copy, design §4)

CONFIRMATORY (design §3; score_confirmatory): k = #{s : L_s > 0} (an exact tie L_s == 0 is not > 0). PASS iff
k ≥ PASS_K = 10 of the 12 seeds. The exact one-sided sign-test p = P(Bin(n, 1/2) ≥ k) is reported (k = 10: 79/4096 =
0.0193). Fixed interpretation: a pass carries the design §4 claim text, verbatim; a fail is "not replicated at the
model level (non-answer; ...)", and when k ≤ 2 a locality-direction note is added.

DESCRIPTIVE (never a verdict, labelled so in the raw): mean, sd, t of L; a seed-bootstrap percentile 95 % CI of mean L;
the same summaries of R and LS (LS carries the self-copy note); the set sizes; a per-seed table.

Gates (any failure raises relay_paired.Gate and writes nothing):
  - exactly one census raw <rung>-s<seed>.json per (rung, seed) for the frozen rungs and seeds, and no other
    <anything>-s<n>.json census raw in the directory (another seed or another rung, e.g. the three-arm decoy r1D);
  - each census is k = 7, split test, n None (full split), its per-window file at its recorded sha256, read line by
    line: a duplicate or missing window id is refused; census rung / seed / ε / step agree with the file name;
  - ceiling table: the census's programs and law name the frozen table file, whose bytes in TABLES_DIR hash to the
    census's table_sha256 AND to the frozen TABLE_SHA256[rung];
  - run.json: the seed, and EVERY field of RECIPE at the frozen value (15 epochs, final step 117195; missing = failure);
  - trainer revision (new in 1.0, mandatory): every run.json records git_revision (a full 40-hex commit, non-null)
    and git_dirty false (the literal boolean), all 36 runs carry ONE revision, and it is an ancestor of HEAD;
  - log.jsonl ends at step 117195; ckpt.pt has the census's checkpoint sha256; the census's corpus is the run's
    corpus_dir at the manifest sha256 run.json records; the manifest's rung is the file's, ε = 1, and its run key hashes
    to run 0582ffbeb4693d27; all seeds of a rung share that corpus directory; the train split files hash to the frozen
    TRAIN_SPLIT_SHA256[rung];
  - no two censuses share a run, checkpoint, per-window file or raw; all window id sets are identical, and there are
    exactly N_WINDOWS = 84867 of them; the set is exactly the r1 test split's windows with ≥ K + 1 = 8 records;
  - cross-rung pairing (each arm window is window_map(arm) of the r1 window, same reset flag) and, per census, the
    class-id grouping equals the grouping by the recomputed class key;
  - the relay exact side is the frozen file (EXACT_R_SHA256), r1R's, all_gates true, its ε = 1 per-class cache
    recorded at the frozen DIOTA_R_SHA256 (load_diota re-hashes the cache file); every r1 class key is in the cache;
  - the r1S exact side passed all its gates and reports self_copy_all_zero_exact true (as v3).
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from relay_paired import Gate  # noqa: E402

SCORER_VERSION = "1.0"
DESIGN = "docs/relay-replication-design-v0.1.md"
ROOT = Path(__file__).resolve().parents[1]
RUNGS = ("r1", "r1R", "r1S")
ARMS = ("r1R", "r1S")
EXACT_R = "docs/relay-exact-side-2026-09-30.json"
# sha256 of the relay exact side file and of its ε = 1 per-class Δι cache, frozen 2026-10-09 from the files on disk.
EXACT_R_SHA256 = "07c9f67b70b5e19ac4356e0fcbcaa5a6011fe48d752141676e1b5a56f9c01fd6"
DIOTA_R_SHA256 = "0501876cf99e4aec52cd41955ed39afadbfee8c1031573b108b24bd333dbbdc4"
EXACT_S = "docs/three-arm-exact-side-r1S-2026-10-05.json"
FRESH_RUN = "0582ffbeb4693d27"
FINAL_STEP = 117195
N_WINDOWS = 84867                                    # r1 test split windows with >= 8 records (pairing docs 10-05)
SEEDS = tuple(range(1, 13))                          # design §5: seeds 1..12, all of them, no others
# The recipe (identical to three_arm_score_v3.RECIPE: the pilot runs' run.json). Dotted names nest under "model".
RECIPE = {"batch_size": 256, "epochs": 15, "lr": 0.001, "lr_min": 0.0001, "warmup": 500, "weight_decay": 0.1,
          "grad_clip": 1.0, "max_steps": None, "model.d_model": 128, "model.n_layer": 4, "model.n_head": 4,
          "model.d_mlp": 512, "model.n_pos": 42, "model.vocab_in": 157, "model.vocab_out": 156, "n_params": 838940,
          "steps_per_epoch": 7813, "steps_planned": FINAL_STEP, "steps_total": FINAL_STEP}
EPS = "1"
K = 7
PROGRAMS = "c1prime-loop"
LAW = {"T_ep": 40, "L": 8, "B": 2}
TABLES_DIR = Path("~/.cache/yupi-scratch/ceilings").expanduser()   # learner_window_census.py's default --tables-dir
TABLE_SHA256 = {                                     # as three_arm_score_v3 (computed 2026-10-05)
    "r1": "a1a7903c0536d00a0bb7e11f2f143d33f4bd09841c78633f85cb802d2486c7d3",
    "r1R": "b1e0f3339eca1ef4c3e20def2a1fd88f98ca156523b774e02ae672ee5d091c51",
    "r1S": "ba0a5b3d8960f06ba278ecb81fb1155a8b29f837c32d19d9adb0912e1a028246"}
TRAIN_FILES = ("train.tokens", "train.index", "train.table.jsonl")
_TRAIN_INDEX = "a66efdfd8b3c410c4e8d737feddaaa738b287373b8cebc862de40fae9bab36f4"
_TRAIN_TABLE = "4c716da583820bd02c0f329742fc0f1dfdb46892f09f37670b8fc25e7b5acde2"
TRAIN_SPLIT_SHA256 = {                               # as three_arm_score_v3 (computed 2026-10-05)
    "r1": {"train.tokens": "4f983895f48cefb5cd0b3faa0baf3f14ae50f267fe9564e528980f75619ae199",
           "train.index": _TRAIN_INDEX, "train.table.jsonl": _TRAIN_TABLE},
    "r1R": {"train.tokens": "39a21ebb9c8af742b92e51beb2072a9bb129e02151ad033e9f5dd6f83d7c9651",
            "train.index": _TRAIN_INDEX, "train.table.jsonl": _TRAIN_TABLE},
    "r1S": {"train.tokens": "66a2e679a4f5ff7ad60b63dd28cf8617503617666bbbe04349d586910796f1f8",
            "train.index": _TRAIN_INDEX, "train.table.jsonl": _TRAIN_TABLE}}
BACK = -0.05                                         # back set: Δι_R < BACK (strict)
FWD = 0.05                                           # forward set: Δι_R > FWD (strict)
PASS_K = 10                                          # PASS iff #{s : L_s > 0} >= PASS_K
CI_LEVEL = 0.95
N_BOOT = 10000
RNG_SEED = 20261009
CLAIM_PASS = ("On the windows where an exact, ceiling-identical relay pushes next-KIND information further back, the "
              "typical model's excess is lower with the relay than without it, relative to windows where nothing "
              "moves. That is the opposite sign to the locality account's prediction.")
FAIL_TEXT = "not replicated at the model level (non-answer; not evidence for locality unless k ≤ 2)"
LOCALITY_K = 2
LOCALITY_NOTE = "locality direction: typical model is worse where information is pushed back"
SELF_COPY_NOTE = "self-copy: zero-entropy field, descriptive only (design §4)"
DESCRIPTIVE_LABEL = "descriptive, not scored (design §3): no verdict is read from this block"


# ---- confirmatory sign test (pure) ------------------------------------------------------

def binom_tail(k, n):
    """P(Bin(n, 1/2) >= k), exact."""
    return Fraction(sum(math.comb(n, j) for j in range(max(k, 0), n + 1)), 2 ** n)


def score_confirmatory(L):
    """Design §3: k = #{s : L_s > 0} (ties not > 0); PASS iff k >= PASS_K. Reads only the signs."""
    L = np.asarray(L, dtype=np.float64)
    if L.ndim != 1 or len(L) < 1 or not np.isfinite(L).all():
        raise ValueError("L must be a non-empty 1-d finite array")
    n = len(L)
    k = int((L > 0).sum())
    p = binom_tail(k, n)
    passed = bool(k >= PASS_K)
    return {"statistic": "L", "n": n, "k": k, "n_ties": int((L == 0).sum()), "n_negative": int((L < 0).sum()),
            "pass_k": PASS_K, "pass": passed, "p_one_sided": float(p), "p_exact": str(p),
            "p_null": "P(Bin(n, 1/2) >= k): one-sided sign test of median L <= 0, any distribution",
            "interpretation": CLAIM_PASS if passed else FAIL_TEXT,
            "locality_note": LOCALITY_NOTE if (not passed and k <= LOCALITY_K) else None}


# ---- descriptive (pure) -----------------------------------------------------------------

def _summary(x):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if n > 1 else float("nan")
    se = sd / math.sqrt(n) if n > 1 else float("nan")
    t = mean / se if se > 0 else (math.copysign(math.inf, mean) if mean != 0 else 0.0)
    return dict(n=n, mean=mean, sd=sd, se=se, t=t, df=n - 1)


def bootstrap_mean(x, n_boot=N_BOOT, rng_seed=RNG_SEED, level=CI_LEVEL):
    """Seed-level percentile bootstrap of the mean of x."""
    x = np.asarray(x, dtype=np.float64)
    idx = np.random.default_rng(rng_seed).integers(0, len(x), size=(n_boot, len(x)))
    m = x[idx].mean(axis=1)
    a = (1 - level) / 2
    return dict(ci=[float(np.quantile(m, a, method="inverted_cdf")),
                    float(np.quantile(m, 1 - a, method="inverted_cdf"))],
                level=level, n_boot=int(n_boot), rng_seed=rng_seed, method="percentile, seeds resampled")


def score_seeds(L, R, LS, seeds, sets, n_boot=N_BOOT, rng_seed=RNG_SEED):
    """The confirmatory sign test on L and the descriptive block."""
    arrs = {k: np.asarray(v, dtype=np.float64) for k, v in dict(L=L, R=R, LS=LS).items()}
    n = len(arrs["L"])
    if any(a.ndim != 1 or len(a) != n for a in arrs.values()) or len(seeds) != n:
        raise ValueError("per-seed arrays and seeds must be 1-d and of equal length")
    if not all(np.isfinite(a).all() for a in arrs.values()):
        raise ValueError("per-seed arrays must be finite")
    conf = score_confirmatory(arrs["L"])
    per_seed = [dict(seed=int(s), L=float(arrs["L"][j]), R=float(arrs["R"][j]), LS=float(arrs["LS"][j]),
                     L_positive=bool(arrs["L"][j] > 0)) for j, s in enumerate(seeds)]
    descriptive = dict(label=DESCRIPTIVE_LABEL, L=_summary(arrs["L"]),
                       L_bootstrap=bootstrap_mean(arrs["L"], n_boot, rng_seed),
                       R=dict(_summary(arrs["R"]), note="relay moves information closer: both accounts predict a "
                                                        "gain, so this arm is reported but not tested (design §1)"),
                       LS=dict(_summary(arrs["LS"]), note=SELF_COPY_NOTE),
                       sets=dict(sets), per_seed=per_seed)
    return dict(scorer_version=SCORER_VERSION, n_seeds=n, confirmatory=conf, descriptive=descriptive,
                rules=dict(L=f"mean over Δι_R < {BACK} of (y_r1 − y_R) minus mean over Δι_R = 0 exactly",
                           confirmatory=f"PASS iff #{{s : L_s > 0}} >= {PASS_K} of {n} (ties not > 0)",
                           p="exact one-sided binomial P(Bin(n, 1/2) >= k)",
                           descriptive="mean / sd / t / bootstrap CI of L, R and LS: not scored"))


# ---- per-seed contrasts from per-window excess (pure) -----------------------------------

def seed_arrays(y, x, z, seeds):
    """y: {(rung, seed): per-window KIND excess, one window order}; x: signed Δι_R per window; z: exact-zero flag per
    window, same order. Returns per-seed L, R, LS and the set sizes."""
    x, z = np.asarray(x, dtype=np.float64), np.asarray(z, dtype=bool)
    back, fwd = x < BACK, x > FWD
    if not back.any() or not fwd.any() or not z.any():
        raise Gate(f"GATE: an empty back (Δι_R < {BACK}), forward (Δι_R > {FWD}) or exact-zero set")
    if (z & (x != 0)).any():
        raise Gate("GATE: a window is flagged exact-zero but its Δι_R is not 0")

    def contrast(D, M):
        return float(D[M].mean() - D[z].mean())

    out = dict(L=[], R=[], LS=[])
    for s in seeds:
        D = y[("r1", s)] - y[("r1R", s)]
        DS = y[("r1", s)] - y[("r1S", s)]
        out["L"].append(contrast(D, back))
        out["R"].append(contrast(D, fwd))
        out["LS"].append(contrast(DS, back))
    out = {k: np.array(v) for k, v in out.items()}
    out["sets"] = dict(back=int(back.sum()), forward=int(fwd.sum()), zero=int(z.sum()), n_windows=int(len(x)))
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


def load_census(raw):
    """A census raw and its per-window rows {i: row}, read line by line; a duplicate or missing id is refused."""
    raw = Path(raw)
    c = json.loads(raw.read_text())
    pw = Path(c["per_window_file"])
    if not pw.is_file() or _sha(pw) != c.get("per_window_sha256"):
        raise Gate(f"GATE: {pw} sha256 differs from {raw.name}'s per_window_sha256 (or the file is missing)")
    if c.get("k") != K or c.get("split") != "test" or c.get("n") is not None:
        raise Gate(f"GATE: {raw.name} is not a k = {K}, full (n None) test-split census")
    rows = {}
    with open(pw) as f:
        for ln, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            if not isinstance(r, dict) or "i" not in r:
                raise Gate(f"GATE: {pw} line {ln} has no window id")
            if r["i"] in rows:
                raise Gate(f"GATE: {pw} has a duplicate window id {r['i']!r} (line {ln})")
            rows[r["i"]] = r
    return c, rows


def table_name(rung):
    return f"{PROGRAMS}-{LAW['T_ep']}-{LAW['L']}-{LAW['B']}-{rung}-eps{EPS.replace('/', '_')}-k{K}.jsonl"


def check_tables(rungs=RUNGS):
    out = {}
    for r in rungs:
        p = TABLES_DIR / table_name(r)
        if not p.is_file():
            raise Gate(f"GATE: ceiling table {p} is missing")
        got = _sha(p)
        if got != TABLE_SHA256[r]:
            raise Gate(f"GATE: ceiling table {p} sha256 {got} is not the frozen table sha256 for {r}")
        out[r] = got
    return out


def check_train_split(corpus, rung):
    out = {}
    for f in TRAIN_FILES:
        p = Path(corpus) / f
        if not p.is_file():
            raise Gate(f"GATE: {rung} train split file {p} is missing")
        got = _sha(p)
        if got != TRAIN_SPLIT_SHA256[rung][f]:
            raise Gate(f"GATE: {rung} train split file {p} sha256 {got} is not the frozen one")
        out[f] = got
    return out


def _is_ancestor(rev):
    r = subprocess.run(["git", "merge-base", "--is-ancestor", rev, "HEAD"], capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0


def check_trainer_revision(run_jsons):
    """run_jsons: {tag: run.json dict}. Mandatory (1.0): every run records git_revision (full hash) and git_dirty
    False, one revision across all runs, an ancestor of HEAD."""
    for tag, rj in sorted(run_jsons.items()):
        rev = rj.get("git_revision")
        if rev is None:
            raise Gate(f"GATE: {tag}: run.json records no git_revision (missing or null)")
        if not isinstance(rev, str) or not re.fullmatch(r"[0-9a-f]{40}", rev):
            raise Gate(f"GATE: {tag}: git_revision {rev!r} is not a full commit hash")
        if rj.get("git_dirty", None) is not False:
            raise Gate(f"GATE: {tag}: git_dirty is {rj.get('git_dirty', '<missing>')!r}, expected false: the "
                       f"trainer ran from a dirty (or unrecorded) tree")
    vals = {rj["git_revision"] for rj in run_jsons.values()}
    if len(vals) != 1:
        raise Gate(f"GATE: the runs record {len(vals)} different trainer git revisions: {sorted(vals)[:4]}")
    rev = next(iter(vals))
    if not _is_ancestor(rev):
        raise Gate(f"GATE: trainer git revision {rev} is not an ancestor of HEAD")
    return dict(field="git_revision", revision=rev, git_dirty=False, ancestor_of_head=True, n_runs=len(run_jsons))


def _check_one(cd, rung, seed, tables):
    raw = cd / f"{rung}-s{seed}.json"
    if not raw.is_file():
        raise Gate(f"GATE: census {raw} is missing")
    c, rows = load_census(raw)
    tag = f"census {raw.name}"
    if c["rung"] != rung:
        raise Gate(f"GATE: {tag} declares rung {c['rung']!r}, the file name says {rung!r}")
    if c["seed"] != seed:
        raise Gate(f"GATE: {tag} declares seed {c['seed']!r}, expected {seed}")
    if c["eps"] != EPS:
        raise Gate(f"GATE: {tag} has eps {c['eps']!r}, expected {EPS}")
    if c["step"] != FINAL_STEP:
        raise Gate(f"GATE: {tag} was taken at step {c['step']}, expected the final step {FINAL_STEP}")
    if c.get("programs") != PROGRAMS or c.get("law") != LAW:
        raise Gate(f"GATE: {tag}: programs {c.get('programs')!r} / law {c.get('law')!r} do not name the frozen "
                   f"ceiling table {table_name(rung)}")
    if c.get("table_sha256") != tables[rung]:
        raise Gate(f"GATE: {tag}: table_sha256 {c.get('table_sha256')!r} is not the sha256 of the ceiling table "
                   f"{table_name(rung)} on disk")
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
                corpus=c["corpus"], corpus_manifest_sha256=rj["corpus_manifest_sha256"],
                table_sha256=c["table_sha256"], census_git=c.get("git"), trainer_git_revision=rj.get("git_revision"))
    return c, rows, prov, rj


def gate_censuses(census_dir, seeds):
    """All provenance gates that need no corpus records or Δι cache. Returns ({(rung, seed): (census, rows,
    provenance)}, sorted window ids, run-level provenance). `seeds` is SEEDS on the CLI path; tests pass small worlds."""
    cd = Path(census_dir).expanduser()
    seeds = list(seeds)
    if len(set(seeds)) != len(seeds):
        raise Gate(f"GATE: duplicate seed in {seeds}")
    want = {f"{r}-s{s}.json" for r in RUNGS for s in seeds}
    pat = re.compile(r"^(.+)-s(\d+)\.json$")
    extra = sorted(p.name for p in cd.glob("*.json") if pat.match(p.name) and p.name not in want)
    if extra:
        raise Gate(f"GATE: census raws outside rungs {RUNGS} x seeds {seeds} are in {cd}: {extra}")
    tables = check_tables()
    full = {(r, s): _check_one(cd, r, s, tables) for r in RUNGS for s in seeds}
    cen = {k: v[:3] for k, v in full.items()}
    for field in ("run", "checkpoint_sha256", "per_window_sha256", "raw_sha256"):
        vals = [p[field] for _, _, p in cen.values()]
        if len(set(vals)) != len(vals):
            raise Gate(f"GATE: duplicate {field} across census raws")
    splits = {}
    for r in RUNGS:
        dirs = {str(_path(cen[(r, s)][0]["corpus"]).resolve()) for s in seeds}
        if len(dirs) != 1:
            raise Gate(f"GATE: the seeds of rung {r} were censused on different corpora")
        splits[r] = dict(corpus=next(iter(dirs)), **check_train_split(next(iter(dirs)), r))
    trainer = check_trainer_revision({f"{r}-s{s}": v[3] for (r, s), v in full.items()})
    ids = sorted(next(iter(cen.values()))[1])
    for (r, s), (_, rows, _) in cen.items():
        if sorted(rows) != ids:
            raise Gate(f"GATE: census {r}-s{s} window id set differs from the others")
    if len(ids) != N_WINDOWS:
        raise Gate(f"GATE: scored window count {len(ids)} is not the frozen {N_WINDOWS}")
    prov = dict(table_sha256={r: dict(file=str(TABLES_DIR / table_name(r)), sha256=tables[r]) for r in RUNGS},
                train_split_sha256=splits, trainer_git=trainer,
                census_git=sorted({str(p["census_git"]) for _, _, p in cen.values()}))
    return cen, ids, prov


def check_window_set(n_records, ids):
    """The scored ids must be exactly the r1 test split's windows with >= K + 1 records, N_WINDOWS of them."""
    want = sorted(i for i, n in n_records.items() if n >= K + 1)
    if len(ids) != len(want) or len(ids) != N_WINDOWS:
        raise Gate(f"GATE: scored window count {len(ids)}; the test split has {len(want)} windows with "
                   f">= {K + 1} records; frozen {N_WINDOWS}")
    if list(ids) != want:
        raise Gate(f"GATE: the scored window set is not the test split's windows with >= {K + 1} records")


def _key(rec):
    from yupi.naming import pattern_all
    from yupi.pattern_ceiling import serial_key
    reset, records = rec
    return serial_key((reset, pattern_all(records[:K])[0]))


def check_class_pairing(recs, rows_by_census, ids):
    """(1) every arm window i is window_map(arm) of r1 window i, same reset flag; (2) per census, the partition by the
    row's class id equals the partition by the recomputed class key. Returns the r1 class keys in ids order."""
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


def corpus_gates(cen, ids):
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


def check_relay_exact(path=EXACT_R):
    """The frozen relay exact side: file sha, r1R's, all gates, and the ε = 1 per-class cache at the frozen sha."""
    p = _path(path)
    got = _sha(p)
    if got != EXACT_R_SHA256:
        raise Gate(f"GATE: relay exact side {path} sha256 {got} is not the frozen {EXACT_R_SHA256}")
    es = json.loads(p.read_text())
    if es.get("rung_name") != "r1R" or es.get("all_gates") is not True:
        raise Gate(f"GATE: relay exact side {path} is not r1R's or did not pass all its gates")
    ent = [d for d in es.get("d_iota_kind_4") or [] if d.get("eps") == EPS]
    if len(ent) != 1 or ent[0].get("per_class_sha256") != DIOTA_R_SHA256 or ent[0].get("gate") is not True:
        raise Gate(f"GATE: relay exact side {path}: the eps {EPS} Δι cache is not the frozen one (sha {DIOTA_R_SHA256})")
    return dict(exact_side=str(path), exact_side_sha256=got, per_class_sha256=DIOTA_R_SHA256)


def check_self_copy_exact(path=EXACT_S):
    es = json.loads(_path(path).read_text())
    if es.get("rung_name") != "r1S" or es.get("all_gates") is not True:
        raise Gate(f"GATE: r1S exact side {path} is not r1S's or did not pass all its gates")
    ents = es.get("d_iota_kind_4") or []
    if not ents or any(e.get("self_copy_all_zero_exact") is not True for e in ents):
        raise Gate(f"GATE: r1S exact side {path}: not every d_iota_kind_4 entry has self_copy_all_zero_exact true")
    return dict(exact_side=str(path), exact_side_sha256=_sha(_path(path)), self_copy_all_zero_exact=True)


def relay_sets(keys):
    """Per window (keys' order): signed Δι_R and the exact-zero flag from the sha-gated cache, by r1 class."""
    from relay_paired import load_diota
    prov = check_relay_exact(EXACT_R)
    dio, meta = load_diota(str(_path(EXACT_R)), EPS)          # re-hashes the per-class file against the exact side
    missing = [k for k in set(keys) if k not in dio]
    if missing:
        raise Gate(f"GATE: {len(missing)} r1 classes missing from the relay Δι cache")
    x = np.array([dio[k][1] for k in keys], dtype=np.float64)
    z = np.array([bool(dio[k][2]) for k in keys])
    return x, z, dict(prov, **meta), len(set(keys))


def frozen_settings(seeds, n_boot, rng_seed):
    return bool(tuple(seeds) == SEEDS and n_boot == N_BOOT and rng_seed == RNG_SEED)


def score_dir(census_dir, raw, *, _seeds=SEEDS, _n_boot=N_BOOT, _rng_seed=RNG_SEED):
    """The whole scoring. The underscored overrides exist for tests ONLY; the CLI cannot reach them."""
    if Path(raw).exists():
        raise SystemExit(f"refusing to overwrite {raw}")
    frozen = frozen_settings(_seeds, _n_boot, _rng_seed)
    s_prov = check_self_copy_exact(EXACT_S)
    check_relay_exact(EXACT_R)
    cen, ids, run_prov = gate_censuses(census_dir, _seeds)
    keys = corpus_gates(cen, ids)
    x, z, r_prov, n_classes = relay_sets(keys)
    y = {k: np.array([rows[i]["by_field"]["kind"] for i in ids], dtype=np.float64) for k, (_, rows, _) in cen.items()}
    arr = seed_arrays(y, x, z, list(_seeds))
    res = score_seeds(arr["L"], arr["R"], arr["LS"], list(_seeds), arr["sets"], n_boot=_n_boot, rng_seed=_rng_seed)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    out = dict(design=DESIGN, frozen_settings=frozen, git=git + ("+dirty" if dirty else ""),
               scorer_sha256=_sha(Path(__file__).resolve()),
               relay_paired_sha256=_sha(Path(__file__).resolve().parent / "relay_paired.py"),
               seeds=list(_seeds), back=BACK, forward=FWD, eps=EPS, k=K, n_windows=len(ids), n_r1_classes=n_classes,
               recipe=dict(RECIPE, final_step=FINAL_STEP, corpus_run=FRESH_RUN),
               censuses={f"{r}-s{s}": p for (r, s), (_, _, p) in cen.items()},
               d_iota=dict(r1R=r_prov, r1S=s_prov), provenance=run_prov, gates="all passed", **res)
    Path(raw).write_text(json.dumps(out, indent=1) + "\n")
    c = res["confirmatory"]
    print(json.dumps(dict(k=c["k"], n=c["n"], **{"pass": c["pass"]}, p_one_sided=c["p_one_sided"],
                          interpretation=c["interpretation"], locality_note=c["locality_note"],
                          trainer_git=run_prov["trainer_git"]["revision"], frozen_settings=frozen, raw=str(raw)),
                     indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                 allow_abbrev=False)
    ap.add_argument("--census-dir", required=True)
    ap.add_argument("--raw", required=True)
    a = ap.parse_args(argv)                      # any other argument (seeds, n_boot, thresholds, ...) is an error
    return score_dir(a.census_dir, a.raw)


if __name__ == "__main__":
    sys.exit(main())
