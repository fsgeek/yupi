"""Can prediction R3 of the relay pre-registration run? (docs/relay-intervention-prereg-v0.1.md)

R3 is the frozen scripts/implicit_info_bintest.py (sha256 c73fab6b…, m = 4) run on each
r1ʀ census raw. It opens, for a census raw with rung "r1R" and eps "1" at k = 7:
  ~/.cache/yupi-scratch/implicit/c1prime-loop-40-8-2-r1R-eps1-k7-kind-m123456.jsonl  (ι cache)
  ~/.cache/yupi-scratch/ceilings/c1prime-loop-40-8-2-r1R-eps1-k7.jsonl               (k7 table)
and keys each window by serial_key((reset, pattern_all(surface_records(toks)[1][:7])[0])),
calling surface_records WITHOUT a rung (it cannot pass one).

  uv run python scripts/relay_r3_inputs_check.py --raw docs/relay-r3-inputs-check-<date>.json

Gates (no model is read; the census rows are synthetic, kind excess = 0):
  1. the frozen script's sha256 is c73fab6b…;
  2. both files exist and have the sha256 the exact side recorded
     (docs/relay-exact-side-2026-09-30.json);
  3. ι values: the cache's iota_4 equals the Δι table's iota4_r1R for every r1ʀ class
     (exactly), and the table-mass mean of iota_m equals the exact side's r1ʀ lag profile
     (m = 1..6, to 1e-12);
  4. keying: over every r1ʀ test window with ≥ 8 records (the k = 7 census set), the key
     without a rung equals the key with rung "r1R", and is in the cache and in the table;
  5. end to end: the frozen script's own `windows()` and `analyse()` run on a synthetic
     r1ʀ census raw of those windows (the real one exists only after r1ʀ models are
     censused), return every window, and give the ι columns the cache holds.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import implicit_info_bintest as B  # noqa: E402  (frozen; imported, never edited)

from yupi.corpus.vocab import VOCAB  # noqa: E402
from yupi.corpus.writer import read_split  # noqa: E402
from yupi.learner.evaluate import surface_records  # noqa: E402
from yupi.naming import pattern_all  # noqa: E402
from yupi.pattern_ceiling import load_table, serial_key  # noqa: E402

FROZEN_SHA = "c73fab6b76180b6a3851bcea89369f958aab81987a7f39bdd2a49ad32dd7acfc"
K = 7
EXACT = "docs/relay-exact-side-2026-09-30.json"
CORPUS = "corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d"
WORK = Path.home() / ".cache/yupi-scratch/relay/r3-check"


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--eps", default="1")
    ap.add_argument("--corpus", default=CORPUS)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    tag = f"r1R-eps{a.eps.replace('/', '_')}"
    cache = B.CACHE / f"c1prime-loop-40-8-2-{tag}-k{K}-kind-m123456.jsonl"
    table_p = B.TABLES / f"c1prime-loop-40-8-2-{tag}-k{K}.jsonl"
    es = json.load(open(EXACT))
    dsum = next(d for d in es["d_iota_kind_4"] if d["eps"] == a.eps)
    dtab = next(d for d in es["derived_tables"] if d["eps"] == a.eps and d["k"] == K)
    g = {}
    g["1_frozen_sha256"] = _sha("scripts/implicit_info_bintest.py") == FROZEN_SHA
    g["2_files"] = dict(cache=str(cache), cache_exists=cache.exists(), table=str(table_p), table_exists=table_p.exists())
    g["2_files"]["cache_sha256_equal"] = cache.exists() and _sha(cache) == dsum["r1R_iota_sha256"]
    g["2_files"]["table_sha256_equal"] = table_p.exists() and _sha(table_p) == dtab["r1R_sha256"]
    g["2_ok"] = all(v for k, v in g["2_files"].items() if k.endswith(("exists", "equal")))
    if not (g["1_frozen_sha256"] and g["2_ok"]):
        raise SystemExit(f"GATE FAILED before loading: {g}")

    iota = {}
    for line in open(cache):
        d = json.loads(line)
        iota[d["k"]] = d
    n_diota, n_eq = 0, 0
    for line in open(dsum["per_class_file"]):
        d = json.loads(line)
        n_diota += 1
        n_eq += iota[d["kR"]]["iota_4"] == d["iota4_r1R"]
    table = load_table(table_p)
    tot = sum(float(m) for m, _ in table.values())
    prof = {r["m"]: r["mean_iota_kl"] for r in es["lag_profiles"] if r["rung"] == "r1R" and r["eps"] == a.eps}
    means = {m: sum(float(mass) * iota[serial_key(key)][f"iota_{m}"] for key, (mass, _) in table.items()) / tot
             for m in range(1, 7)}
    g["3_iota"] = dict(n_classes_cache=len(iota), n_classes_table=len(table), n_diota=n_diota,
                       iota4_equal_to_diota_table=n_eq,
                       mean_iota_minus_exact_side={m: means[m] - prof[m] for m in means})
    g["3_ok"] = (len(iota) == len(table) == n_diota == n_eq
                 and all(abs(v) < 1e-12 for v in g["3_iota"]["mean_iota_minus_exact_side"].values()))

    split = read_split(Path(a.corpus), "test")
    skeys = {serial_key(k) for k in table}
    rows, ids_of, n_long, n_eq_key, n_in = [], {}, 0, 0, 0
    for i, (toks, _) in enumerate(split):
        toks = tuple(VOCAB[t] for t in toks)
        reset0, recs0 = surface_records(toks)
        resetR, recsR = surface_records(toks, "r1R")
        if len(recsR) < K + 1:
            continue
        n_long += 1
        k0 = serial_key((reset0, pattern_all(recs0[:K])[0]))
        kR = serial_key((resetR, pattern_all(recsR[:K])[0]))
        n_eq_key += k0 == kR
        n_in += (kR in iota) and (kR in skeys)
        cid = ids_of.setdefault(kR, len(ids_of))
        rows.append(dict(i=i, key=cid, structural=0.0, naming=0.0,
                         by_field=dict(kind=0.0, actor=0.0, relay=0.0, related=0.0, lineage=0.0)))
    g["4_keying"] = dict(n_windows_k7=n_long, key_without_rung_equals_r1R=n_eq_key, key_in_cache_and_table=n_in)
    g["4_ok"] = n_long == n_eq_key == n_in == 84949

    WORK.mkdir(parents=True, exist_ok=True)
    pw = WORK / f"synthetic-census-{tag}-k{K}-test.jsonl"
    with open(pw, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    craw = WORK / f"synthetic-census-{tag}-k{K}-test.json"
    craw.write_text(json.dumps(dict(k=K, rung="r1R", eps=a.eps, seed=0, corpus=a.corpus, split="test",
                                    per_window_file=str(pw), per_window_sha256=_sha(pw),
                                    note="SYNTHETIC (kind excess 0): gate of relay_r3_inputs_check.py, not a census")) + "\n")
    c, (y, lo, sh, h, fm) = B.windows(str(craw), 4)
    an = B.analyse(y + 0.01 * lo, lo, sh, h, fm)       # a planted β_long = 0.01 so the fit is not degenerate
    exp_lo = np.array([iota[serial_key((surface_records(tuple(VOCAB[t] for t in split[r["i"]][0]), "r1R")[0],
                                        pattern_all(surface_records(tuple(VOCAB[t] for t in split[r["i"]][0]), "r1R")[1][:K])[0]))]["iota_4"]
                       for r in rows[:2000]])
    b_long = an["full_plus_log2_class_mass"]["beta"][1]
    g["5_frozen_windows"] = dict(n=int(len(y)), iota_long_equal_first_2000=bool(np.array_equal(lo[:2000], exp_lo)),
                                 planted_beta_long_recovered=b_long, synthetic_census=str(craw))
    g["5_ok"] = len(y) == 84949 and g["5_frozen_windows"]["iota_long_equal_first_2000"] and abs(b_long - 0.01) < 1e-9
    ok = all(g[k] for k in g if k.endswith("_ok")) and g["1_frozen_sha256"]
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    out = dict(prereg="docs/relay-intervention-prereg-v0.1.md", prediction="R3", eps=a.eps, k=K, corpus=a.corpus,
               git=git + ("+dirty" if dirty else ""), all_gates=ok, gates=g)
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(g, indent=1))
    print("ALL GATES PASSED" if ok else "GATE FAILED", "->", a.raw)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
