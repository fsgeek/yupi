"""EXPLORATORY (2026-10-13; whole-draft review W28): does the KIND within-cell association hold at d = 256? Existing
r1 eps = 1 d = 256 models (15 epochs, seeds 1-3; 45 epochs, seed 1; recipe lr 1e-3, as d = 128), censused
2026-10-13. Frozen model full_plus_log2_class_mass (HC1, gate as b1_fe_coarse_robustness) plus the FE/coarse-cell
check, via b1_fe_coarse_robustness.one(). Not pre-registered.
  uv run python scripts/b1_size_axis_d256.py > docs/b1-size-axis-d256-2026-10-13.jsonl
"""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b1_fe_coarse_robustness as fe  # noqa: E402

for raw in sorted(glob.glob("docs/learner-window-census-r1-eps1-2M-d256-*-2026-10-13.json")):
    r = fe.one(raw)
    r.pop("bins_detail", None)
    print(json.dumps(dict(raw=raw, beta_long_frozen=r["beta_long_frozen"], t_frozen_hc1=r["t_frozen_hc1"],
                          beta_long_fe=r["beta_long_fe"], t_fe_cr1_coarse=r["t_fe_cr1_coarse"],
                          bins=[b["mean_excess"] for b in r["bins"]])), flush=True)
