"""Scorer for docs/gru-baseline-prereg-v0.1.md (written before any GRU was trained beyond a CPU smoke test).

Gates (any failure refuses):
  R  reference: one() on the 10-02 transformer r1 eps1 seed-1 census reproduces the COMMITTED frozen-model fit in
     docs/converged-ladder-bintest-kind-2026-10-02.json (beta_long and se, full_plus_log2_class_mass) to 1e-12, so
     the regression code is checked against history, not against itself (Codex pre-stamp finding 3).
  per GRU model: run.json model.arch == "gru", d_model 256, n_layer 2; checkpoint step == census step == 117195;
     census k == 7, split test, n equal to the transformer census of the cell; census sha256 matches its JSONL.
Per GRU model (m_long = 4, model full_plus_log2_class_mass, fields beta_long / t):
  frozen HC1 (G1), class-clustered CR1 (b1_clustered_refit.one), FE last-kind x actor-count with coarse-cell CR1
  (b1_fe_coarse_robustness.one); KIND and ACTOR means; quality floor: mean KIND shortfall < the count table's.
  uv run python scripts/gru_baseline_score.py --raw docs/gru-baseline-score-2026-10-13.json
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b1_clustered_refit as cr  # noqa: E402
import b1_fe_coarse_robustness as fe  # noqa: E402

CELLS = ["r1-eps1", "r2-eps1", "r3-eps1", "r4-eps1", "r1-eps1_2", "r2-eps1_2", "r3-eps1_2", "r4-eps1_2"]
RUNS = Path.home() / ".cache/yupi-scratch/runs/gru"
GRU_RAW = "docs/learner-window-census-gru-{c}-2M-e15-seed1-2026-10-13.json"
TF_RAW = "docs/learner-window-census-{c}-2M-e15-seed{s}-2026-10-02.json"
FINAL = 7813 * 15


def gate_reference():
    ref = [r for r in json.load(open("docs/converged-ladder-bintest-kind-2026-10-02.json"))["runs"]
           if r["census_raw"] == "docs/learner-window-census-r1-eps1-2M-e15-seed1-2026-10-02.json"][0]
    b, se = ref["full_plus_log2_class_mass"]["beta"][1], ref["full_plus_log2_class_mass"]["se"][1]
    got = fe.one("docs/learner-window-census-r1-eps1-2M-e15-seed1-2026-10-02.json")
    t_ref = b / se
    if abs(got["beta_long_frozen"] - b) > 1e-12 or abs(got["t_frozen_hc1"] - t_ref) > 1e-9:
        raise SystemExit(f"GATE R: frozen fit does not reproduce the committed 10-02 fit ({got['beta_long_frozen']} vs {b})")
    return dict(beta=b, se=se, t=t_ref)


def mean_fields(raw):
    c = json.load(open(raw))
    pw = c["per_window_file"]
    if hashlib.sha256(Path(pw).read_bytes()).hexdigest() != c["per_window_sha256"]:
        raise SystemExit(f"GATE: {pw} sha256 mismatch")
    n = k = a = 0.0
    for line in open(pw):
        r = json.loads(line); n += 1; k += r["by_field"]["kind"]; a += r["by_field"]["actor"]
    return c, dict(n=int(n), kind=k / n, actor=a / n)


def gate_model(cell, c):
    run = RUNS / f"c1prime-loop-40-8-2-{cell}-2M-gru256x2-e15-s1"
    rj = json.load(open(run / "run.json"))
    m = rj["model"]
    if m.get("arch") != "gru" or m["d_model"] != 256 or m["n_layer"] != 2 or rj["seed"] != 1:
        raise SystemExit(f"GATE: {run} is not the registered GRU")
    ck = torch.load(run / "ckpt.pt", map_location="cpu", weights_only=False)
    if ck["step"] != FINAL or c.get("step") != FINAL:
        raise SystemExit(f"GATE: {run} incomplete (ckpt {ck['step']}, census {c.get('step')})")
    if c.get("k") != 7 or c.get("split") != "test":
        raise SystemExit(f"GATE: {cell} census is not k = 7 test")
    return dict(run=str(run), git_revision=rj.get("git_revision"), git_dirty=rj.get("git_dirty"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    out = {"prereg": "docs/gru-baseline-prereg-v0.1.md", "gate_reference": gate_reference(), "cells": {}}
    count = json.load(open("docs/count-baseline-comparison-2026-10-04.json"))["cells"]
    for cell in CELLS:
        raw = GRU_RAW.format(c=cell)
        c, mf = mean_fields(raw)
        g = gate_model(cell, c)
        tf = [mean_fields(TF_RAW.format(c=cell, s=s))[1] for s in (1, 2, 3)]
        if mf["n"] != tf[0]["n"]:
            raise SystemExit(f"GATE: {cell} window count {mf['n']} != transformer {tf[0]['n']}")
        f = fe.one(raw)
        k = cr.one(raw)["full_plus_log2_class_mass"]
        cnt = count[cell]["count_kind"]
        out["cells"][cell] = dict(
            gates=g, gru=mf, transformer_seeds=[x["kind"] for x in tf], count_kind=cnt,
            above_floor=mf["kind"] < cnt,
            g1=dict(beta_long=f["beta_long_frozen"], t_hc1=f["t_frozen_hc1"],
                    met=f["beta_long_frozen"] > 0 and f["t_frozen_hc1"] >= 3),
            cr1_class=dict(beta_long=k["beta_long"], t=k["t_cr1_class"]),
            fe_coarse=dict(beta_long=f["beta_long_fe"], t=f["t_fe_cr1_coarse"]), bins=[b["mean_excess"] for b in f["bins"]])
    inf = [c for c, v in out["cells"].items() if v["above_floor"]]
    out["summary"] = dict(
        informative=len(inf), under_floor=len(out["cells"]) - len(inf),
        g1_met_informative=sum(out["cells"][c]["g1"]["met"] for c in inf),
        nonpositive_informative=sum(out["cells"][c]["g1"]["beta_long"] <= 0 for c in inf),
        positive_t_below_3_informative=sum(out["cells"][c]["g1"]["beta_long"] > 0 and out["cells"][c]["g1"]["t_hc1"] < 3 for c in inf))
    Path(a.raw).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["summary"]))
    for c, v in out["cells"].items():
        print(c, "gru %.5f" % v["gru"]["kind"], "tf", ["%.5f" % x for x in v["transformer_seeds"]], "count %.5f" % v["count_kind"],
              "floor ok" if v["above_floor"] else "UNDER FLOOR", "G1 t %.2f" % v["g1"]["t_hc1"], "CR1 t %.2f" % v["cr1_class"]["t"],
              "FE t %.2f" % v["fe_coarse"]["t"])


if __name__ == "__main__":
    main()
