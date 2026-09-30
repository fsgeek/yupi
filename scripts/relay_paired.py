"""The relay intervention's frozen paired analysis (docs/relay-intervention-prereg-v0.1.md,
"Frozen analysis", predictions R1, R2, R4; R3 is the frozen implicit_info_bintest.py run on
the r1ʀ census raws and is not reimplemented here).

  uv run python scripts/relay_paired.py \\
      --r1 docs/learner-window-census-r1-eps1-2M-seed{1,2,3}-2026-09-21.json \\
      --r1R docs/learner-window-census-r1R-eps1-2M-seed{1,2,3}-<date>.json \\
      [--exact-side docs/relay-exact-side-2026-09-30.json] [--eps 1] [--arm primary|secondary] \\
      --raw docs/relay-paired-<arm>-<date>.json

Per test window w with ≥ 7 records (k = 7; the same windows at both rungs):
  Δexcess_w = mean over the r1 seeds of by_field.kind − mean over the r1ʀ seeds of by_field.kind
  Δι_w      = Δι_kind,4 of w's class (r1 class → the committed per-class table of the exact side)
OLS of Δexcess on (1, Δι), HC1 errors (the frozen verdict's estimator, imported from
implicit_info_bintest.py unchanged). The relay field's own excess (by_field.relay at r1ʀ)
is reported separately and enters nothing.

  R1  slope > 0, t ≥ 3, 0.0165 ≤ slope ≤ 0.066
  R2  exact-zero set (Δι_kind,4 = 0 as equal Fraction mixtures): |mean Δexcess − intercept| ≤ 2 se,
      se the set mean's standard error (the intercept is the reference value, prereg wording)
  R4  set Δι < −0.05: (mean Δexcess − intercept) < 0 with t = (mean − intercept) / se ≤ −3,
      se the set mean's standard error; the same t with the intercept's se added in quadrature
      is reported beside it (not scored)
The secondary arm (15 epochs) reports R1, R2, R4 without thresholds.

Gates (any failure refuses to write a verdict): each census raw's per-window file has its
recorded sha256; rungs are r1 / r1R, same ε, k = 7, test split, all windows; the seeds within
a rung share one corpus and one window set, and the window sets are equal across rungs; per
raw, class id ↔ class key is a bijection (keys recomputed from the corpus); for every window
the r1 records equal drop_relay of the r1ʀ records (whole window) and so the r1 class equals
drop_relay of the r1ʀ class; the per-class Δι table has the exact side's sha256 and its r1ʀ
key equals the window's r1ʀ class.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from implicit_info_bintest import ols_hc1  # noqa: E402  (the frozen estimator, imported unchanged)

from yupi.corpus.vocab import VOCAB  # noqa: E402
from yupi.corpus.writer import read_split  # noqa: E402
from yupi.interfaces import drop_relay  # noqa: E402
from yupi.learner.evaluate import surface_records  # noqa: E402
from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import serial_key  # noqa: E402

K = 7
R1_BAND = (0.0165, 0.066)
R1_T, R4_T, R2_SE = 3.0, -3.0, 2.0
R4_CUT = -0.05


class Gate(SystemExit):
    pass


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---- the analysis (pure) --------------------------------------------------------------

def _mean_se(a):
    a = np.asarray(a, dtype=np.float64)
    n = len(a)
    return dict(n=int(n), mean=float(a.mean()) if n else None,
                se=float(a.std(ddof=1) / np.sqrt(n)) if n > 1 else None)


def analyse(d_excess, d_iota, zero_exact, relay_excess=None, arm="primary"):
    """The frozen analysis on per-window arrays: Δexcess, Δι_kind,4, the exact-zero flag,
    and (reported only) the r1ʀ relay field's excess. Returns the verdict dict."""
    y = np.asarray(d_excess, dtype=np.float64)
    x = np.asarray(d_iota, dtype=np.float64)
    z = np.asarray(zero_exact, dtype=bool)
    beta, se = ols_hc1(y, np.column_stack([np.ones(len(y)), x]))
    icpt, slope = float(beta[0]), float(beta[1])
    se_i, se_s = float(se[0]), float(se[1])
    t_s = slope / se_s
    zero = _mean_se(y[z])
    zero["minus_intercept"] = zero["mean"] - icpt
    zero["within_2se"] = abs(zero["minus_intercept"]) <= R2_SE * zero["se"]
    neg = _mean_se(y[x < R4_CUT])
    diff = neg["mean"] - icpt
    neg.update(minus_intercept=diff, t=diff / neg["se"], t_with_intercept_se=diff / float(np.hypot(neg["se"], se_i)))
    out = dict(n=int(len(y)), mean_d_excess=float(y.mean()), mean_d_iota=float(x.mean()),
               ols=dict(terms=["1", "d_iota_kind_4"], beta=[icpt, slope], se=[se_i, se_s],
                        t=[icpt / se_i, t_s]),
               slope=slope, slope_se=se_s, slope_t=t_s, intercept=icpt, intercept_se=se_i,
               R2_zero_set=zero, R4_set=dict(cut=R4_CUT, **neg))
    if relay_excess is not None:
        out["relay_field_excess_r1R"] = _mean_se(relay_excess)
    if arm == "primary":
        out["verdict"] = dict(
            R1="PASS" if (slope > 0 and t_s >= R1_T and R1_BAND[0] <= slope <= R1_BAND[1]) else "FAIL",
            R2="PASS" if zero["within_2se"] else "FAIL",
            R4="PASS" if (diff < 0 and neg["t"] <= R4_T) else "FAIL",
            R3="not computed here: the frozen implicit_info_bintest.py (m = 4) on each r1R census raw")
        out["thresholds"] = dict(R1=dict(t_min=R1_T, band=list(R1_BAND)), R2=dict(k_se=R2_SE),
                                 R4=dict(cut=R4_CUT, t_max=R4_T))
    else:
        out["verdict"] = "secondary arm: R1, R2, R4 reported without thresholds (prereg)"
    return out


# ---- joining the censuses (pure given loaded inputs) -------------------------------------

def join(r1_rows, r1R_rows, recs_r1, recs_r1R, diota):
    """Per-window arrays from loaded inputs.
    r1_rows / r1R_rows: per seed, {i: per-window census row} (row: key, by_field).
    recs_r1 / recs_r1R: {i: (reset, records)} surface records of each rung's window.
    diota: {r1 serial class key: (r1R serial class key, Δι_kind,4, zero_exact)}.
    Returns (ids, d_excess, d_iota, zero_exact, relay_excess, gates)."""
    sets = [frozenset(r) for r in r1_rows + r1R_rows]
    if len(set(sets)) != 1:
        raise Gate("GATE: window sets differ across seeds or rungs")
    ids = sorted(sets[0])
    for rows_list, recs, name in ((r1_rows, recs_r1, "r1"), (r1R_rows, recs_r1R, "r1R")):
        for s, rows in enumerate(rows_list):
            id_of, key_of = {}, {}
            for i in ids:
                reset, rr = recs[i]
                key = serial_key((reset, pattern_all(rr[:K])[0]))
                cid = rows[i]["key"]
                if id_of.setdefault(key, cid) != cid or key_of.setdefault(cid, key) != key:
                    raise Gate(f"GATE: class id <-> key not a bijection in {name} seed index {s} at window {i}")
    d_ex, d_io, z, relay = [], [], [], []
    for i in ids:
        (reset1, rec1), (resetR, recR) = recs_r1[i], recs_r1R[i]
        if reset1 != resetR or drop_relay(recR) != tuple(rec1):
            raise Gate(f"GATE: window {i}: r1 records are not drop_relay of the r1R records")
        p1 = pattern_all(rec1[:K])[0]
        pR = pattern_all(recR[:K])[0]
        if drop_relay(pR) != p1:
            raise Gate(f"GATE: window {i}: r1 class is not drop_relay of the r1R class")
        k1, kR = serial_key((reset1, p1)), serial_key((resetR, pR))
        if k1 not in diota:
            raise Gate(f"GATE: window {i}: class {k1} missing from the Δι table")
        tkR, di, ze = diota[k1]
        if tkR != kR:
            raise Gate(f"GATE: window {i}: the Δι table's r1R class differs from the window's")
        e1 = np.mean([rows[i]["by_field"]["kind"] for rows in r1_rows])
        eR = np.mean([rows[i]["by_field"]["kind"] for rows in r1R_rows])
        d_ex.append(e1 - eR)
        d_io.append(di)
        z.append(ze)
        relay.append(np.mean([rows[i]["by_field"]["relay"] for rows in r1R_rows]))
    return ids, np.array(d_ex), np.array(d_io), np.array(z), np.array(relay)


# ---- loading ---------------------------------------------------------------------------

def load_census(raw):
    c = json.load(open(raw))
    pw = c["per_window_file"]
    if _sha(pw) != c["per_window_sha256"]:
        raise Gate(f"GATE: {pw} sha256 differs from {raw}'s per_window_sha256")
    if c["k"] != K or c["split"] != "test" or c["n"] is not None:
        raise Gate(f"GATE: {raw} is not a k = 7, full test-split census")
    rows = {}
    for line in open(pw):
        r = json.loads(line)
        rows[r["i"]] = r
    return c, rows


def load_records(corpus, ids, rung):
    split = read_split(Path(corpus), "test")
    return {i: surface_records(tuple(VOCAB[t] for t in split[i][0]), rung) for i in ids}


def load_diota(exact_side, eps):
    es = json.load(open(exact_side))
    s = next(d for d in es["d_iota_kind_4"] if d["eps"] == eps)
    path = s["per_class_file"]
    if _sha(path) != s["per_class_sha256"]:
        raise Gate(f"GATE: {path} sha256 differs from the exact side's per_class_sha256")
    out = {}
    for line in open(path):
        d = json.loads(line)
        out[d["k"]] = (d["kR"], d["d_iota4"], d["zero_exact"])
    return out, dict(file=path, sha256=s["per_class_sha256"], mean_d_iota4_law=s["mean_d_iota4"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r1", nargs="+", required=True)
    ap.add_argument("--r1R", nargs="+", required=True)
    ap.add_argument("--exact-side", default="docs/relay-exact-side-2026-09-30.json")
    ap.add_argument("--eps", default="1")
    ap.add_argument("--arm", choices=("primary", "secondary"), default="primary")
    ap.add_argument("--raw", required=True)
    a = ap.parse_args(argv)
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    c1 = [load_census(r) for r in a.r1]
    cR = [load_census(r) for r in a.r1R]
    for (c, _), rung in [(x, "r1") for x in c1] + [(x, "r1R") for x in cR]:
        if c["rung"] != rung or c["eps"] != a.eps:
            raise Gate(f"GATE: census {c['run']} is rung {c['rung']} eps {c['eps']}, expected {rung} eps {a.eps}")
    for cs in (c1, cR):
        if len({c["corpus"] for c, _ in cs}) != 1:
            raise Gate("GATE: seeds of one rung were censused on different corpora")
    ids = sorted(c1[0][1])
    recs1 = load_records(c1[0][0]["corpus"], ids, "r1")
    recsR = load_records(cR[0][0]["corpus"], ids, "r1R")
    diota, dmeta = load_diota(a.exact_side, a.eps)
    ids, y, x, z, relay = join([r for _, r in c1], [r for _, r in cR], recs1, recsR, diota)
    res = analyse(y, x, z, relay, a.arm)
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    out = dict(prereg="docs/relay-intervention-prereg-v0.1.md", arm=a.arm, eps=a.eps, k=K, git=git + ("+dirty" if dirty else ""),
               inputs=dict(r1=[dict(raw=r, run=c["run"], seed=c["seed"], checkpoint_sha256=c["checkpoint_sha256"],
                                    per_window_sha256=c["per_window_sha256"], corpus=c["corpus"]) for r, (c, _) in zip(a.r1, c1)],
                           r1R=[dict(raw=r, run=c["run"], seed=c["seed"], checkpoint_sha256=c["checkpoint_sha256"],
                                     per_window_sha256=c["per_window_sha256"], corpus=c["corpus"]) for r, (c, _) in zip(a.r1R, cR)],
                           d_iota=dmeta, exact_side=a.exact_side),
               gates="all passed (census sha256, rungs, window sets, class bijection, drop_relay pairing, Δι table)",
               **res)
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print(f"n={res['n']} slope {res['slope']:+.5f} ± {res['slope_se']:.5f} (t {res['slope_t']:+.2f}) "
          f"intercept {res['intercept']:+.5f} ± {res['intercept_se']:.5f}")
    zz, nn = res["R2_zero_set"], res["R4_set"]
    print(f"R2 zero set n={zz['n']} mean {zz['mean']:+.5f} ± {zz['se']:.5f} (minus intercept {zz['minus_intercept']:+.5f})")
    print(f"R4 Δι<{R4_CUT} n={nn['n']} mean−intercept {nn['minus_intercept']:+.5f} (t {nn['t']:+.2f}; "
          f"with intercept se {nn['t_with_intercept_se']:+.2f})")
    print("verdict", res["verdict"], "->", a.raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
