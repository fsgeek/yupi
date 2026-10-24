# Codex review of the learner two-step design (2026-10-23)

> `codex exec --sandbox read-only`, adversarial, on docs/learner-two-step-design-2026-10-23.md (commit 096c3c8). Verbatim output below; dispositions are in the design's v2.

**The experiment is viable, but the design is not sound as written.** The main blockers are the definition of q2 and the lack of a controlled enumeration error.

1. **Blocking — q2 mixes incompatible normalisation conventions.** The draft multiplies five raw record-7 probabilities but normalises KIND 8 over KINDS ([design:12](/home/tony/projects/yupi/docs/learner-two-step-design-2026-10-23.md:12)). Existing `kind_output` removes **only PAD**; the classifier then separately divides by the KIND sum ([evaluate.py:217](/home/tony/projects/yupi/src/yupi/learner/evaluate.py:217), [classifier:118](/home/tony/projects/yupi/scripts/learner_kind_classifier.py:118)). Record-7 KIND needs the same explicit convention.

   This fails even for a perfect model: after six records with RESET, the exact window-ending probability is ½. Raw record-7 weights therefore sum to ½, whereas P2 sums to one ([pattern_filter.py:161](/home/tony/projects/yupi/src/yupi/pattern_filter.py:161)). PAD is the end token; there is no additional END token ([data.py:23](/home/tony/projects/yupi/src/yupi/learner/data.py:23)).

   Masked slots create another ambiguity: multiplying their predicted MASKED probabilities loses mass; forcing MASKED with weight one defines a constrained rollout. Both require an explicit choice and accounting for excluded mass. Global renormalisation afterwards can reweight KIND 7 according to field-completion probabilities. Require `sum(q2)=1` and `sum_k2 q2(k1,k2)=q1(k1)` under the declared convention.

2. **High — fresh-name compression is an uncontrolled approximation.** Exact renaming invariance does not establish model invariance. Replacing  
   `Σ_t q(t|h) F(h,t)` with `q(fresh|h) F(h,t_rep)` requires invariance of the **whole remaining rollout**, including later record-7 fields. Checking only downstream KIND distributions under three representatives does not establish that ([design:26](/home/tony/projects/yupi/docs/learner-two-step-design-2026-10-23.md:26)).

   The fallback also leaves unsampled windows unchecked and permits failures on up to 5% of sampled windows—potentially concentrated in the smaller pure population. Its 0.01 tolerance already exceeds the monitor’s 0.005 margin. Enumerate names fully, or establish a mass-weighted bound on the resulting q2 error.

   Bindings must grow within each branch: a fresh ACTOR becomes a bound candidate for RELATED, distinct from another fresh thread. That is how both the evaluator and `pattern_all` work ([evaluate.py:284](/home/tony/projects/yupi/src/yupi/learner/evaluate.py:284), [naming.py:137](/home/tony/projects/yupi/src/yupi/naming.py:137)). Fresh pools exclude reserved names ([evaluate.py:67](/home/tony/projects/yupi/src/yupi/learner/evaluate.py:67)).

3. **High — θ does not control total error.** Many individually small branches can carry substantial combined mass. “Dropped mass reported” is insufficient unless it is the **prefix-probability-weighted mass of disjoint pruned subtrees**, with a specified treatment of the residual ([design:24](/home/tony/projects/yupi/docs/learner-two-step-design-2026-10-23.md:24)). Use a cumulative error budget. If the normalised approximation has TV error bounded by η, each distance can move by η and the pure/withheld distance gap by 2η. Decisions must remain stable under that uncertainty.

4. **High — the measurement does not establish the claimed certification.** Average accuracy and coverage on sampled windows cannot establish correctness against every rare alternative. Success supports this particular monitor on the sampled population; failure does not show that these learners cannot exploit the two-step information ([design:45](/home/tony/projects/yupi/docs/learner-two-step-design-2026-10-23.md:45)).

   Comparing error with the **median margin** is also insufficient. For a pure class with separation μ, a sufficient nearest-family condition is  
   `2 × prediction_error + 0.005 < μ`, with enumeration uncertainty included. Error comparable to μ does **not** imply failure. The manuscript already states the factor-of-two geometry ([manuscript:254](/home/tony/projects/yupi/docs/paper1m-manuscript-v3.md:254)). Report classwise comparisons.

   Finally, labels remain **one-step** G labels, excluding `0<G<0.1`; success neither certifies two-step uncertainty as pure nor rules out all hidden-state contribution.

5. **Medium — exact-family masses and the scored population differ.** The k=6 producer includes windows with at least six records ([window_process.py:252](/home/tony/projects/yupi/src/yupi/window_process.py:252)); the proposed test requires eight. Under the frozen law, those populations have mass 0.90 and 0.85 respectively. RESET classes have raw mass 0.10 in the table but 0.05 in the eight-record population. **Halve RESET-class masses before regrouping prior weights.** The conditional P2 laws remain applicable because endpoint selection is independent of dynamics ([pattern_filter.py:161](/home/tony/projects/yupi/src/yupi/pattern_filter.py:161)).

6. **Medium — existing monitor code needs deliberate adaptation.** `family()` hardcodes k=7, reads `split-v2`, and groups by `p_star`, not `p2` ([classifier:25](/home/tony/projects/yupi/scripts/learner_kind_classifier.py:25), [classifier:43](/home/tony/projects/yupi/scripts/learner_kind_classifier.py:43)). Existing classification also considers deterministic/none groups before abstaining; “nearest pure versus nearest withheld” changes that rule ([classifier:61](/home/tony/projects/yupi/scripts/learner_kind_classifier.py:61)). Apply the same declared rule to both resolutions.

The four open points:

1. **θ:** use cumulative mass control and decision-stability bounds; a fixed token threshold plus descriptive mass reporting is inadequate.
2. **Fresh representatives:** the proposed check/fallback is inadequate. Prefer full enumeration initially; validate any compression against complete rollouts on validation data.
3. **Masked fields:** **yes, one placeholder branch**, with all five slots fed to preserve token positions. Specify whether its weight is forced to one or carries model probability; the current five-conditional formula leaves this unresolved ([interfaces.py:49](/home/tony/projects/yupi/src/yupi/interfaces.py:49)).
4. **Sampling/separation:** 10,000 eligible windows is reasonable for coarse aggregate metrics, not rare-class certification. Sample uniformly after eligibility filtering, pair windows across methods/seeds, and report label denominators and uncertainty. `--n` currently takes the first N windows **before** eligibility filtering ([evaluate.py:335](/home/tony/projects/yupi/src/yupi/learner/evaluate.py:335)). Fit τ2 and settle approximation choices on val, then freeze them before test. Existing τ fitting correctly reads separate val outputs ([prior_aware_monitor.py:37](/home/tony/projects/yupi/scripts/prior_aware_monitor.py:37)); I found no episode-range overlap in the four underlying corpora.

Checks that passed: the pinned k=6 rows for all four trained cells normalise exactly and marginalise exactly to `p_star`; their hashes match. Token indexing is also straightforward: preserve the optional leading RESET, query KIND 7 at `off+30`, and KIND 8 at `off+35` **after a synthetic record 7**. The evaluator establishes these offsets ([evaluate.py:350](/home/tony/projects/yupi/src/yupi/learner/evaluate.py:350)). Reusing the observed record-7 continuation would instead measure a teacher-forced conditional.
