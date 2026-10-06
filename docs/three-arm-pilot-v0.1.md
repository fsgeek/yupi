# Three-arm blind variance pilot v0.1 (2026-10-05)

> **Status: PILOT, BLIND, not a test.** Design v0.2 §4 needs the between-seed sd of the contrasts K_A,s, and 3
> templates cannot estimate it: the power for n = 8 runs from 0.31 to 1.00 across an 80 % interval of the sd. Written
> by the instance of 2026-10-05.

- **Models:** seeds 101, 102, 103, each trained on r1, r1R, r1D and r1S of the fresh corpus 0582ffbeb4693d27.
  15 epochs, d = 128, lr 1e-3, which is design v0.2's recipe. 12 runs.
- **Never confirmatory.** These seeds are excluded from the confirmatory test, whose seeds are 1..n, and no pilot
  number about an arm's *effect* is read.
- **Blind.** The pilot censuses write their raws to `~/.cache/yupi-scratch/runs/threearm-pilot/census/` and are
  never opened by hand. The only reader is `scripts/three_arm_pilot_sd.py`, committed with this note before any
  pilot model trains. It prints and stores **only between-seed standard deviations**: of K_R,s and K_D,s (self-copy
  control, τ ∈ {0.05, 0.1, 0.2}) and of the r1-vs-self field contrast. It reports no means, ratios or signs. The
  confirmatory prereg uses these sds, inflated to the upper end of their 80 % interval, with the effect sizes it
  plants, to set n.
- **What this pilot cannot avoid:** the sds are computed from the same models that carry the effects. Blindness is
  procedural: the script reports sds only, and the owner does not open the census raws. It is not cryptographic.
- **GPU (design v0.2 §6):** three leases of one wave each (one seed × four rungs, about 50–55 min), with ≥ 60 min
  between leases. Runs are resumable.

## Result (2026-10-05 evening; `docs/three-arm-pilot-sd-2026-10-05.json`, sds only)

All 12 runs reached step 117,195. Each one-wave lease took about 69 min against the 50 estimated, running about
9 min past its declared `--expected-until` but inside its 90 min TTL. Later leases declare 75 min.

Between-seed sd at τ = 0.1:
- K_R: 0.0042 with the self-copy as control, 0.0026 with r1 as control;
- K_D: 0.0006 (self-copy control) and 0.0017 (r1 control);
- field contrast F (r1 − self-copy): 0.0011.

**The owner's design error:** 3 seeds give df = 2, exactly the template problem the pilot was meant to solve. An
80 % upper bound on a df-2 sd is about 3× the point value. Pooling the pilot with the 10-02 15-epoch templates
(r1 control only) gives df = 4.

**What the pilot does settle:** for the relay contrast, the self-copy control adds variance rather than removing
it. K is a difference of class-set means, so a uniform field effect cancels in it already. Prereg v0.2 therefore
uses **r1 as the control for K**. The self-copy keeps the job of checking that the field does not interact with the
class sets (K_S ≈ 0 under every reading), plus the secondary H_field test.
