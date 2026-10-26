# Codex read of the certification story (2026-10-26)

> `codex exec --sandbox read-only`, asked to act as conscience: where the story is wrong, and what each error points to. Verbatim, then the owner's dispositions (verified, classified, and what each points to; see Tony's 10-25 principle).

**Overstated.** The pointwise lemma is correct; the implemented population “guaranteed floor” is assumption-dependent, and requires a trained learner. The robust empirical finding is stronger than a mere anecdote: two steps improve certification in **22/22 models**, but certify a majority of pure windows in **15/22**. ([ladder results:11](/home/tony/projects/yupi/docs/certified-bound-result-2026-10-25.md:11), [cell results:11](/home/tony/projects/yupi/docs/certified-bound-cells-result-2026-10-25.md:11))

Ranked findings:

1. **Critical — the lemma does not establish the reported population floor.**  
   \(e\le B,\ \mu_c>2B\Rightarrow\text{certificate}\) is sound. Multiplying geometric mass by \(q\) additionally assumes class-independent coverage and validation-to-test transfer, explicitly acknowledged in the declaration. V3 still pools errors across **all pure classes**, rather than conditioning on each \(c\). “44/44 valid” means passing a **0.03 tolerance**; v2 and v3 each exceed observed certification in three cases—v3 predicts 0.000289 where observation is zero. **Better claim:** geometry plus the **joint distribution of class and error** yields a certification bound; pooled validation errors give a useful empirical predictor. ([lemma:7](/home/tony/projects/yupi/docs/prospective-certification-declared-2026-10-25.md:7), [assumptions:13](/home/tony/projects/yupi/docs/prospective-certification-declared-2026-10-25.md:13), [v3 implementation:48](/home/tony/projects/yupi/scripts/prospective_certification_v3.py:48), [counterexample:113](/home/tony/projects/yupi/docs/prospective-certification-v3-2026-10-26.json:113))

2. **Critical — the stated certificate-risk argument uses the wrong denominator.**  
   Wrong certificates imply \(e>B\), bounding **unconditional** wrong-certificate probability. The script reports error **among certified windows**; its bound requires division by certificate coverage. Moreover, the nominal 95% bound misses **7.4–10.3%** of ladder test windows at one step. Low observed certificate error does not establish nominal calibration. **Better claim:** empirical selective accuracy survives substantial error-bound miscalibration—worth explaining and calibrating directly. ([incorrect inference:16](/home/tony/projects/yupi/docs/certified-bound-declared-2026-10-25.md:16), [denominator:58](/home/tony/projects/yupi/scripts/certified_bound.py:58), [undercoverage:34](/home/tony/projects/yupi/docs/certified-bound-result-2026-10-25.md:34))

3. **High — “randomness, not hidden state” exceeds the tested alternative.**  
   Alternatives require \(G\ge0.1\); near-pure hidden-state classes are excluded. “Floor 0” correctly means **no alternative-mass cutoff**, not exclusion of every positive hidden-state contribution. **Better, larger story:** certification is a resolution-dependent separation problem: report the depth–error–\(G\) tradeoff, rather than a binary randomness verdict. ([alternative selection:33](/home/tony/projects/yupi/scripts/prospective_certification.py:33), [declared scope:85](/home/tony/projects/yupi/docs/learner-two-step-design-2026-10-23.md:85))

4. **High — the remaining 0.213 is not identified as direction.**  
   V3 retains within-pure class/error dependence and distribution-shift assumptions. Differences between median gaps are not a causal decomposition. Euclidean cosine toward one TV-nearest neighbour also does not measure certificate-boundary crossing. W2’s failure supports **“specific hidden-state bias not established,”** rather than its absence. **Better claim:** quantify certificate geometry directly; direction-sensitive bounds can remain guarantees if their uncertainty sets have justified coverage. ([residual attribution:24](/home/tony/projects/yupi/docs/prospective-certification-v3-result-2026-10-26.md:24), [cosine implementation:58](/home/tony/projects/yupi/scripts/error_direction.py:58), [W2:10](/home/tony/projects/yupi/docs/error-direction-result-2026-10-26.md:10))

5. **Medium — “before training” is false.**  
   Margins are available before training; learner-specific \(B\) and error distributions require trained-model validation outputs. **Better story:** pre-training geometry predicts the precision a learner must attain; post-training calibration predicts attainable certification. ([status:36](/home/tony/projects/yupi/docs/status-2026-10-26.md:36), [calibration:46](/home/tony/projects/yupi/scripts/certified_bound.py:46))

6. **Medium — challenge establishes comparable alternatives, not interaction.**  
   It compares NL1, NL2 and **one-step** PA*. There is no two-step PA* arm establishing “together they add little more.” **Better claim:** additional queries can empirically compensate for unavailable prior information; a factorial comparison could establish substitution. ([arms:70](/home/tony/projects/yupi/scripts/challenge_score.py:70), [PA*:83](/home/tony/projects/yupi/scripts/challenge_score.py:83), [overclaim:42](/home/tony/projects/yupi/docs/challenge-result-2026-10-25.md:42))

7. **Low — numerical reporting needs correction.**  
   Double `argsort` is not tie-correct Spearman: recalculation gives v1 one/two-step **0.891/0.889**, rather than 0.906/0.866. The three-step “within 0.015” statement fails at r0, ε=1: **0.326139−0.305595=0.020544**. Neither changes the central depth result. **Better claim:** retain the substantive pattern with correct uncertainty and ranking calculations. ([ranking:63](/home/tony/projects/yupi/scripts/prospective_certification.py:63), [claim:16](/home/tony/projects/yupi/docs/three-step-margin-result-2026-10-26.md:16), [JSON:14](/home/tony/projects/yupi/docs/three-step-margin-k5-2026-10-26.json:14))

**Checks that passed:** RESET halving correctly converts six-record eligibility to eight-record eligibility. Class-based margins and majority-labelled law groups are conceptually different; inspecting all four k6 tables found their pure/withheld law sets agree here, so this causes no current numerical discrepancy. Existential floor-zero margins correctly retain rare alternatives. ([RESET rationale:89](/home/tony/projects/yupi/docs/learner-two-step-design-2026-10-23.md:89), [grouping:42](/home/tony/projects/yupi/scripts/learner_two_step_score.py:42))

**Single next experiment:** freeze a learner and calibration, then run a fresh, class-stratified **matched-error direction intervention**: compare real outputs with simplex-valid adversarial outputs at the same per-window TV error. Measure the actual joint sufficient event \(e\le B,\ \mu_c>B+e\), certification, and selective risk. This separates dependence/transfer error from geometric slack and directly tests whether benign error direction explains the excess certification.

---

## Owner's dispositions (2026-10-26)

All numeric claims were recomputed: tie-correct Spearman of v1 is 0.891 / 0.889; floor > observed in 3 cases for v2
and v3 (0.0002–0.0003 against 0, r1 ε = ½, one step); two steps improve certification in 22 of 22 and certify a
majority in 15 of 22; the three-step coin/all difference reaches 0.0205.

| # | verdict | correction made | what it points to |
|---|---|---|---|
| 1 | **Correct.** The pointwise lemma is a guarantee. The population number L/L2/L3 is an *estimate* resting on class-independent coverage and val→test transfer, and it exceeded observation in 3 cases. | "Guaranteed floor" is renamed: **the lemma is the guarantee; L-family numbers are calibrated predictors of certifiability.** | A bound built from the *joint* distribution of class and error, with stated coverage, could restore a population guarantee. That is a better and larger claim. |
| 2 | **Correct.** My B2 argument divided by the wrong population: e > B bounds the *unconditional* wrong-certificate rate, so the rate among certified windows can be up to P(e > B)/coverage. The nominal one-step bound also missed 7.4–10.3 % of test windows. | The declaration's reasoning is annotated. B2's numbers stand, as an empirical observation, not as the guarantee claimed. | Selective accuracy that survives a miscalibrated bound is itself a finding worth explaining. Next: calibrate B directly for selective risk (conformal-style). |
| 3 | **Correct scope.** "Randomness, not hidden state" means *not hidden state of at least γ = 0.1 bits*. | The status sentence now says so. | **A larger story: certification as a surface over depth × learner error × γ.** The exact μ(γ) family already exists; the learner side would chart which (depth, γ) a given learner can certify. |
| 4 | **Correct.** Differences of median gaps are not a causal decomposition; Euclidean cosine toward one neighbour is not boundary-crossing; W2's failure means "specific hidden-state bias not established", not "absent". | The v3 result's decomposition table is relabelled descriptive, and the error-direction reading is softened. | A matched-error direction intervention (the reviewer's next experiment) would *identify* the direction effect. |
| 5 | **Correct.** Margins are pre-training; B and error distributions need trained-model validation outputs. | The status doc is fixed: "geometry before training; certifiability after calibration". | Pre-training geometry says what *precision* a learner must reach for a given depth and γ. That is a design target for builders, and it is prospective. |
| 6 | **Correct.** No two-step PA\* arm, so "together they add little more" was not tested. | The challenge result is corrected. | A factorial (prior × depth) run would establish or refute substitution. It is cheap (existing dumps). |
| 7 | **Correct, minor.** | Spearman tie-corrected in the records; the three-step "within 0.015" is fixed to "within 0.021". | Nothing new; better arithmetic. |

**Not over-conceded this time.** The core empirical finding stands, and the reviewer states it: two steps improve
certification in 22 of 22 models and certify a majority in 15 of 22. What changed is its framing: from a "guaranteed
floor" to a pointwise guarantee plus calibrated prediction, with γ made explicit.
