"""Scoring computation for C3 and C4 of docs/converged-ladder-prereg-v0.1.md (2026-09-30).

The KIND-excess cell mean is "the census's mean of by_field.kind (the realized estimator of KIND
KL) over the k = 7 test windows. The between-seed spread is reported with it." (prereg, Frozen
analyses). Per run: verify the per-window file's sha256 against the census raw, then take the
plain mean of by_field.kind over every row. Per cell: the mean over seeds of the run means, with
the between-seed sd, min and max.

Cross-checks per run (none of them enters the scored number):
  - the row count equals the raw's summary.n, and the per-window mean of `structural` equals
    summary.mean (the file is the one the summary was built from);
  - for the classes the raw lists (the top 20 by summed excess; the full class list is not in
    the raw, so sum n * by_field.kind / total n cannot be formed over all classes), the
    per-window mean of by_field.kind over the class's rows equals the class's by_field.kind,
    and the n-weighted sum over the listed classes equals the per-window sum over those classes.

C3 (means): eps = 1/2: r2 > r1 > r3; eps = 1: r2 > r3 (r1 eps = 1 excluded). Seed resolution,
reported beside each pairwise ordering: every seed of the higher cell exceeds every seed of
the lower one (min(higher) > max(lower)).
C4: r0 has the lowest KIND excess of every cell at its eps. At eps = 1 reported with and
without r1 eps = 1 (15-epoch seeds, censused 2026-10-02). r4 cell means reported, no prediction.

    uv run --extra learner python scripts/converged_ladder_c3c4.py \\
        --raw docs/converged-ladder-c3c4-2026-10-02.json
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

DATE = "2026-10-02"
CELLS = ["r0-eps1", "r1-eps1", "r2-eps1", "r3-eps1", "r4-eps1",
         "r0-eps1_2", "r1-eps1_2", "r2-eps1_2", "r3-eps1_2", "r4-eps1_2"]
SEEDS = (1, 2, 3)


def census_path(cell, seed):
    return f"docs/learner-window-census-{cell}-2M-e15-seed{seed}-{DATE}.json"


def run_mean(raw):
    c = json.load(open(raw))
    pw = Path(c["per_window_file"])
    sha = hashlib.sha256(pw.read_bytes()).hexdigest()
    if sha != c["per_window_sha256"]:
        raise SystemExit(f"GATE: {pw} sha256 {sha} differs from {raw}'s per_window_sha256")
    if c["k"] != 7 or c["split"] != "test" or c["n"] is not None:
        raise SystemExit(f"GATE: {raw} is not a k = 7 full test-split census")
    kind, struct, by_key = [], [], {}
    for line in open(pw):
        r = json.loads(line)
        kind.append(r["by_field"]["kind"])
        struct.append(r["structural"])
        by_key.setdefault(r["key"], []).append(r["by_field"]["kind"])
    kind, struct = np.asarray(kind), np.asarray(struct)
    s = c["summary"]
    listed = s["classes"]
    cls_max_abs = max(abs(float(np.mean(by_key[cl["key"]])) - cl["by_field"]["kind"]) for cl in listed)
    cls_n_ok = all(len(by_key[cl["key"]]) == cl["n"] for cl in listed)
    listed_n = sum(cl["n"] for cl in listed)
    listed_wsum = sum(cl["n"] * cl["by_field"]["kind"] for cl in listed)
    listed_rowsum = sum(float(np.sum(by_key[cl["key"]])) for cl in listed)
    xc = dict(rows=int(len(kind)), summary_n=s["n"], rows_eq_summary_n=len(kind) == s["n"],
              structural_mean_rows=float(struct.mean()), structural_mean_summary=s["mean"],
              structural_mean_abs_diff=abs(float(struct.mean()) - s["mean"]),
              n_classes_total=s["n_classes"], n_classes_listed=len(listed),
              listed_classes_window_share=listed_n / len(kind),
              listed_classes_n_match=cls_n_ok, listed_classes_max_abs_diff_by_field_kind=cls_max_abs,
              listed_classes_weighted_mean_kind=listed_wsum / listed_n,
              listed_classes_rows_mean_kind=listed_rowsum / listed_n,
              full_class_list_reconstruction="not possible: the raw lists only the top classes")
    return dict(raw=raw, run=c["run"], step=c["step"], seed=c["seed"], rung=c["rung"], eps=c["eps"],
                per_window_file=str(pw), per_window_sha256=sha, sha256_verified=True,
                n=int(len(kind)), mean_kind_excess=float(kind.mean()),
                se_kind_excess=float(kind.std(ddof=1) / np.sqrt(len(kind))), crosscheck=xc)


def cell_summary(runs):
    m = np.array([r["mean_kind_excess"] for r in runs])
    return dict(seeds=[r["seed"] for r in runs], seed_means=m.tolist(), mean=float(m.mean()),
                sd_between_seeds=float(m.std(ddof=1)), min=float(m.min()), max=float(m.max()),
                range=float(m.max() - m.min()))


def ordering(cells, hi, lo):
    a, b = cells[hi], cells[lo]
    return dict(higher=hi, lower=lo, mean_higher=a["mean"], mean_lower=b["mean"], diff=a["mean"] - b["mean"],
                mean_order_holds=a["mean"] > b["mean"], seed_resolved=a["min"] > b["max"],
                min_higher=a["min"], max_lower=b["max"])


def lowest(cells, ref, others):
    return dict(cell=ref, mean=cells[ref]["mean"], compared_with=others,
                others_means={o: cells[o]["mean"] for o in others},
                lowest=all(cells[ref]["mean"] < cells[o]["mean"] for o in others),
                seed_resolved=all(cells[ref]["max"] < cells[o]["min"] for o in others),
                margin_to_next=min(cells[o]["mean"] for o in others) - cells[ref]["mean"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    runs = {cell: [run_mean(census_path(cell, s)) for s in SEEDS] for cell in CELLS}
    for cell, rs in runs.items():
        rung, eps = cell.split("-eps")
        for r in rs:
            if r["rung"] != rung or r["eps"] != eps.replace("_", "/") or r["step"] != 117195:
                raise SystemExit(f"GATE: {r['raw']} is {r['rung']} eps {r['eps']} step {r['step']}, expected {cell} step 117195")
    cells = {cell: cell_summary(rs) for cell, rs in runs.items()}
    c3 = dict(
        eps1_2=dict(prediction="r2 > r1 > r3", pairs=[ordering(cells, "r2-eps1_2", "r1-eps1_2"),
                                                      ordering(cells, "r1-eps1_2", "r3-eps1_2"),
                                                      ordering(cells, "r2-eps1_2", "r3-eps1_2")]),
        eps1=dict(prediction="r2 > r3 (r1 eps=1 excluded)", pairs=[ordering(cells, "r2-eps1", "r3-eps1")]))
    c3["eps1_2"]["mean_order_holds"] = all(p["mean_order_holds"] for p in c3["eps1_2"]["pairs"][:2])
    c3["eps1"]["mean_order_holds"] = c3["eps1"]["pairs"][0]["mean_order_holds"]
    c4 = dict(eps1_with_r1=lowest(cells, "r0-eps1", ["r1-eps1", "r2-eps1", "r3-eps1", "r4-eps1"]),
              eps1_without_r1=lowest(cells, "r0-eps1", ["r2-eps1", "r3-eps1", "r4-eps1"]),
              eps1_2=lowest(cells, "r0-eps1_2", ["r1-eps1_2", "r2-eps1_2", "r3-eps1_2", "r4-eps1_2"]))
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "scripts"], capture_output=True, text=True).stdout.strip()
    out = dict(prereg="docs/converged-ladder-prereg-v0.1.md", predictions=["C3", "C4"],
               estimator="mean of by_field.kind over the k = 7 test windows per run; cell = mean over seeds 1-3",
               git=git + ("+dirty" if dirty else ""), runs=runs, cells=cells, C3=c3, C4=c4,
               r4_no_prediction={c: cells[c] for c in ("r4-eps1", "r4-eps1_2")})
    Path(a.raw).write_text(json.dumps(out, indent=1) + "\n")
    for cell in CELLS:
        c = cells[cell]
        print(f"{cell:10} mean {c['mean']:.5f}  sd {c['sd_between_seeds']:.5f}  seeds "
              + " ".join(f"{v:.5f}" for v in c["seed_means"]))
    for k, v in c3.items():
        for p in v["pairs"]:
            print(f"C3 {k}: {p['higher']} > {p['lower']}: {p['mean_higher']:.5f} vs {p['mean_lower']:.5f} "
                  f"diff {p['diff']:+.5f} holds={p['mean_order_holds']} seed-resolved={p['seed_resolved']}")
    for k, v in c4.items():
        print(f"C4 {k}: r0 {v['mean']:.5f} lowest={v['lowest']} seed-resolved={v['seed_resolved']} margin {v['margin_to_next']:+.5f}")
    for cell, rs in runs.items():
        for r in rs:
            x = r["crosscheck"]
            print(f"xcheck {cell} s{r['seed']}: rows==n {x['rows_eq_summary_n']} struct diff {x['structural_mean_abs_diff']:.2e} "
                  f"listed classes n ok {x['listed_classes_n_match']} max|Δ kind| {x['listed_classes_max_abs_diff_by_field_kind']:.2e} "
                  f"(listed share {x['listed_classes_window_share']:.4f})")
    print("->", a.raw)


if __name__ == "__main__":
    main()
