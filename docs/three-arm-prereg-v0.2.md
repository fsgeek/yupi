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
- **Training:** for seeds **1–12** (exactly; the scorer refuses any other set), each seed is trained on **r1, r1R, r1D and r1S**. 15 epochs, d = 128, lr 1e-3,
  `scripts/learner_train.py`. 48 runs.
- **Pilot seeds 101–103 are excluded.**
- **GPU:** 12 leases of one wave each (one seed × four rungs, `--expected-until` +75 min), with ≥ 60 min between
  leases. A seed counts only when all four of its runs reach step 117,195.
- **Census:** k = 7, full test split, every run.

## 3. Statistics (per seed s; frozen in `scripts/three_arm_score_v2.py`, SCORER_VERSION 2.1)

- y = realized KIND excess per window. The class sets are fixed by the exact side: moved_A = {|Δι_A| > 0.1},
  zero_A = {Δι_A = 0 exactly}.
- **K_A,s** = mean(y_r1,s − y_A,s) over moved_A, minus the same over zero_A (r1 control), for A ∈ {R, D}.
- **KS_A,s** = the same contrast for the self-copy, on A's sets.
- **K'_A,s = K_A,s − KS_A,s**, which equals mean(y_S,s − y_A,s) over moved_A minus over zero_A (self-copy
  control). A field effect, and any interaction between the field and the class sets, cancels in K' by
  construction.
- **k'_A = K'_A / m_A**, where m_A is the mean |Δι_A| over moved_A, recomputed from the fresh test split.
- F_s = mean over all windows of (y_r1,s − y_S,s).

## 4. Readings, in order (model-level, seeds 1–12 exactly; every setting is frozen in code)

1. **P_V, the relay replicates against no field:** t(K_R) ≥ 3. If not, the reading is **"no replication"**.
2. **P_R', the relay beats the self-copy where it moves information:** t(K'_R) ≥ 3. If not, the reading is **"no
   relay-specific gain"**: the relay's advantage is not distinguishable from carrying any field.
3. **ρ' = T(k'_D) / T(k'_R)**, where T is the 20 %-trimmed mean across seeds (2 trimmed from each end at n = 12).
   The interval is a seed-bootstrap 95 % CI (10,000 draws, seeds resampled jointly; a draw with T(k'_R) ≤ 0 sets
   that tail to ±∞).
   - **"move-dominant"** if the CI lies entirely above 0.5: moving KIND information *without* binding content
     reproduces more than half of the relay's per-bit, field-adjusted gain.
   - **"binding-dominant"** if the CI lies entirely below 0.5. This includes a decoy that is useless per bit,
     harmful per bit, or whose information is harder to use.
   - Otherwise **"unresolved"**.
4. **Reported, not gating:** KS_R and KS_D (t, and TOST at ±0.002), and the secondary H_field (F equivalent to 0
   within ±0.001 by TOST).

**How these map to §1:**
- "Move-dominant" supports H_move over H_bind.
- "Binding-dominant" supports the relay's actor-conditional content over moving information. It is *not* evidence
  of entity binding in the network.
- H_field is answered by gate 2 and the secondary test.
- The per-bit normalization assumes a gain roughly linear in |Δι|. The arms' |Δι| distributions differ, with heavy
  tails (the top 1 % of windows carry 36–52 % of the |Δι| variance), so ρ' is a per-bit summary, not a law.

**History of the rules (all changed before stamping, with no confirmatory model in existence; the pilot gave sds
only):**
- **First draft:** a TOST field gate and band readings. Severity v2 showed about 99 % withholding and about 1 %
  power.
- **v2 rules:** an |t| ≥ 3 interaction gate and a split at 0.5 on r1-controlled K, with a 90 % percentile
  interval. Both pre-stamp reviewers blocked them: small interactions flipped readings in 25–50 % of runs, and 10 %
  off-phase seeds gave about 21 % confidently wrong readings.
- **Rules 2.1:** this section.

## 5. Power and severity (computed before stamping)

`scripts/three_arm_severity_v3.py` calls the frozen `score_seeds()` with n_boot = 10,000. 560 scenarios × 500
simulations. Raw: `docs/three-arm-severity-v3-2026-10-05.json`.

The generative model shares r1 noise across arms explicitly and hits the pilot-based sds at "point":
sd(K_R) 0.0025, sd(K_D) 0.0017, sd(K'_R) 0.0042, sd(K'_D) 0.0006. "Upper80" multiplies these by 1.94 (df 4) and
3.08 (df 2). Rivals planted:
- field × class interactions δ ∈ {0, ±0.0015, +0.004};
- off-phase seeds: with probability 0.1 a seed's decoy or relay per-bit value is replaced by an extreme (−1.85× or
  +2.5×).

**Severity (the highest confidently wrong-direction rate, by family, point / upper80):**
- clean: 0.008 / 0.016;
- interaction δ: 0.010 / 0.022;
- off-phase decoy −1.85: 0.030 / 0.042;
- off-phase relay +2.5: 0.030 / 0.040;
- other off-phase: ≤ 0.012.

Every rate above 1 % occurs at ρ' = 0.6, next to the split. At ρ' ∈ {0, 1} the wrong rate is 0 at point sds and
≤ 0.006 at upper80. **Bar: ≤ 0.05 in every scenario. Met.**

**Power (clean, point sds):**
- μ_R = 0.006: 0.95 at ρ' = 1 and 0.96 at ρ' = 0. At ρ' = 0.6 and 0.4 the reading is mostly "unresolved".
- μ_R = 0.004: 0.49 at ρ' = 1 and 0.61 at ρ' = 0. About 38 % of runs end "no relay-specific gain", because
  sd(K'_R) > sd(K_R).
- At upper80: power about 0–0.11.

**CI coverage:** 0.94 at point sds without off-phase seeds, and 0.93 pooled. At upper80 it is 0.76–0.79, and as
low as 0.46 in one scenario, probably because the interval is computed only when P_R' passes, which selects runs
where K'_R is overestimated.

**The trade, accepted by the owner:** wrong answers are rare in every scenario simulated. A clear answer needs an
effect near the 10-02 size *and* between-seed sds near the pilot's estimate. Otherwise the likely outcomes are
"no relay-specific gain", "unresolved" or "no replication". These are non-answers, and they are reported as such.
More seeds would need their own pre-registration.

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
