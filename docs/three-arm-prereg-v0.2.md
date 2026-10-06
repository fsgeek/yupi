# The three-arm intervention: pre-registration v0.2 (DRAFT, 2026-10-05)

> **Status: DRAFT, not stamped.** It becomes a pre-registration only when this line is replaced, after the pre-stamp
> review by one Claude and one Codex reviewer, and the commit is OTS-stamped. **No confirmatory model (seeds 1–12)
> has been trained.** Design: `docs/three-arm-design-v0.2.md`, amended by `docs/three-arm-pilot-v0.1.md`'s result
> (r1 is the control for K). This supersedes the blocked `docs/three-arm-prereg-v0.1.md`. Written by the instance of
> 2026-10-05.

## 1. The question

The relay's learner gain may come from:
- **H_move:** moving long-lag KIND information, in proportion to how much moves;
- **H_bind:** the relay's actor-conditional content;
- **H_field:** an added field as such.

The exact side, with all gates passed:
- r1R moves mean Δι_kind,4 by 0.094;
- r1D moves it by 0.068, with no binding content;
- r1S moves it by 0 exactly in every class.

All three have ceilings identical to r1's, class by class.

## 2. Models

- **Corpus:** the fresh paired corpus run 0582ffbeb4693d27 (episodes disjoint from all earlier corpora; four
  pairing gates passed).
- **Training:** for seeds **1–12**, each seed is trained on **r1, r1R, r1D and r1S**. 15 epochs, d = 128, lr 1e-3,
  `scripts/learner_train.py`. 48 runs.
- **Pilot seeds 101–103 are excluded.**
- **GPU:** 12 leases of one wave each (one seed × four rungs, `--expected-until` +75 min), with ≥ 60 min between
  leases. A seed counts only when all four of its runs reach step 117,195.
- **Census:** k = 7, full test split, every run.

## 3. Statistics (per seed s, frozen in `scripts/three_arm_score_v2.py`)

- y = realized KIND excess per window.
- For arm A ∈ {R, D}: K_A,s = mean(y_r1,s − y_A,s) over windows with |Δι_A| > 0.1, minus the same over windows
  with Δι_A = 0 exactly.
- KS_A,s is the self-copy's version of K_A,s, on arm A's sets.
- Per bit: k_A,s = K_A,s / m_A. On the 10-02 windows, m_R ≈ 0.340 and m_D ≈ 0.383. The scorer recomputes both
  from the fresh test split.
- F_s = mean over all windows of (y_r1,s − y_S,s).

## 4. Readings, in order (all model-level, n = 12 seeds)

1. **P_V, the relay replicates:** the one-sample t of K_R across seeds is ≥ 3. If not, the reading is **"no
   replication"**, and no ratio is computed.
2. **Field-interaction check:** if |t| ≥ 3 for KS_R or KS_D, that is evidence that the field interacts with the
   class sets. The reading is then **"mechanism withheld"**. The TOST of each against ±0.002 bits is reported but
   does not gate.
3. **ρ = mean k_D / mean k_R**, with a 90 % seed-bootstrap interval (10,000 draws, seeds resampled jointly):
   - **"move-dominant"** if the interval lies entirely above 0.5: moving KIND information *without* binding content
     reproduces more than half of the relay's per-bit gain;
   - **"binding-dominant"** if it lies entirely below 0.5;
   - otherwise **"unresolved"**.
4. **Secondary:** H_field, F equivalent to 0 within ±0.001 bits by TOST. This is reported beside the reading and
   does not change it.

**Why these rules, not the first draft's.** The first draft required the ρ interval to lie within [0.5, 2] for
H_move or within (−0.25, 0.25) for H_bind, and gated on a TOST of the self-copy contrasts. The seed-level simulation
(§5) showed the TOST gate withholding the mechanism in up to 99 % of runs, and H_bind with about 1 % power. These
rules were changed before stamping, and before any confirmatory model existed. The pilot contributed sds only.

## 5. Power and severity (computed before stamping)

The simulation is `scripts/three_arm_severity_v2.py`, which calls the frozen `score_seeds()`. Raw:
`docs/three-arm-severity-v2-2026-10-05.json`, 500 simulations per scenario. Its inputs:
- n = 12 seeds;
- between-seed sds at their point values (relay K 0.0025 at df 4; decoy K 0.0017 and F 0.0011 at df 2) and at their
  80 % upper bounds (×1.94 and ×3.08);
- the self-copy contrast sd bracketed at 0.002 and 0.004;
- planted relay contrast K_R ∈ {0.004, 0.006} and ρ ∈ {1, 0.4, 0};
- K_R–K_D correlation of 0 and 0.5.

Summary (the per-scenario rates are in the raw):

- **At the point sds:**
  - power 0.93–0.97 at ρ = 1 and 0.94–0.99 at ρ = 0;
  - a wrong-direction reading never occurred at ρ = 1 or ρ = 0 (move-dominant when the truth is 0, or
    binding-dominant when it is 1);
  - at ρ = 0.4 (below the split, so "binding-dominant" is correct) the correct reading comes back 21–51 % of the
    time, and the wrong one at most 1.8 %;
  - "mechanism withheld" at most 4 %.
- **At the 80 % upper sds:**
  - at K_R = 0.004, about half of runs end "no replication" (0.48–0.56);
  - the correct reading has power 0.13–0.75 at ρ = 1 and 0.24–0.72 at ρ = 0;
  - wrong-direction readings stay at most 3.6 %.

**The trade accepted:** severity is high everywhere. Power is high only if the between-seed sds are near their
point estimates. If they are not, the likely outcome is "no replication" or "unresolved". That is a non-answer,
not a wrong answer. A follow-up with more seeds would then need its own pre-registration.

## 6. Procedure

- **Freezing.** The scorer and its tests are committed with this file and are not edited after the first
  confirmatory model trains.
- **Raws before scoring.** Census raws are committed unscored.
- **Recompute before adopting.** One Claude reviewer and one Codex reviewer recompute the verdict before it is
  adopted.
- **Deviations.** Any deviation (a failed run, a lease lost mid-run and resumed, a scorer bug) goes in a dated
  addendum and is reported beside the result.

## 7. Not claimed

- Mechanism inside the network.
- Anything at ε = ½.
- Anything at other sizes or budgets.
- "Binding content" means only the difference between the relay's rule and the decoy's.
