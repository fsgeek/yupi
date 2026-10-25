# Codex adversarial read of the failure ledger and story (2026-10-25)

> `codex exec --sandbox read-only`, asked to attack the story before it became a narrative. Verbatim below; owner's dispositions follow.

**Sound as a narrow case study; not yet sound as the proposed general narrative.** Existence versus mass is a real distinction here. Observer choices demonstrably matter. “As much as the learner” depends on the selected comparison, and several “defensible core” claims overreach.

The headline JSON numbers reproduce, including R = **0.7323**, Q3’s Spearman **+0.8545**, and Q4’s **−0.9758**. Ranked concerns:

1. **Critical — “Prior-free” conflates two substantially different monitors.**  
   β = 0 still **sums over laws**, imposing a uniform law prior and rewarding multiplicity; it is not the nearest-law monitor ([observer_space.py:44](/home/tony/projects/yupi/scripts/observer_space.py:44)). For the worst learner, the grid reports **0.518 → 0.892**, but the existing nearest-law scores are **0.904 → 0.916** ([grid JSON:165](/home/tony/projects/yupi/docs/learner-quality-observer-grid-2026-10-25.json:165), [scores JSON:288](/home/tony/projects/yupi/docs/learner-quality-scores-r1-eps1-k6-2026-10-25.json:288), [314](/home/tony/projects/yupi/docs/learner-quality-scores-r1-eps1-k6-2026-10-25.json:314)). Across the ladder, the nearest-law gain/error correlation is **+0.297**, versus +0.855 for the grid observer. Thus “richer queries rescue the worst learners most” is strongly **observer-specific**; the dramatic one-step collapse is largely avoidable.

2. **High — “Needs a prior or richer query” is not established as necessity.**  
   The claim at [learner-quality-result:58](/home/tony/projects/yupi/docs/learner-quality-result-2026-10-25.md:58) slides between worst-case certification and average classification. Successful monitors establish sufficiency; unsuccessful monitors establish neither impossibility nor necessity. Empirical mean/median error is not a uniform error bound. Moreover, the experiment separates **one-step world-class labels**, not whether the learner’s own uncertainty—or its two-step uncertainty—is intrinsically random ([learner-two-step-result:46](/home/tony/projects/yupi/docs/learner-two-step-result-2026-10-23.md:46)).

3. **High — R does not identify how much observer versus learner “matters.”**  
   Its range definition depends on both chosen sets ([learner-quality-declared:30](/home/tony/projects/yupi/docs/learner-quality-declared-2026-10-25.md:30)). Recomputing the same JSON gives **R = 0.374** using only β = 1 observers—“learner dominates” under the declared rule—and **2.740** using the full grid—“observer dominates.” Neither alternative is uniquely correct; that is precisely the problem. The ten learners also share one corpus and include related checkpoints. The 10-25 declaration is useful prospective evidence, but it does not turn this range ratio into a general contribution decomposition.

4. **High — The mass-floor correction overcorrects.**  
   Removing individually rare laws is not equivalent to Bayesian weighting. Recomputing the exact rows used by [certification_margin_interfaces.py:30](/home/tony/projects/yupi/scripts/certification_margin_interfaces.py:30), a **10⁻⁴** floor discards **26–48% of withheld-law mass at r3**, versus roughly **5% at r0**. Thus the widened margins partly reflect unequal removal of alternatives across interfaces. The correction’s table is numerically reproducible, but its conclusion about prior-aware certifiability needs the actual integrated monitor comparison ([interfaces-result:55](/home/tony/projects/yupi/docs/certification-margin-interfaces-result-2026-10-22.md:55)). Existential statistics remain appropriate for worst-case guarantees; they “mislead” when used to answer a different question.

5. **High — “A good observer” means an oracle-assisted, family-specific classifier.**  
   It receives the exact matching laws, masses and splits, plus per-learner validation error ([prior-aware-declared:7](/home/tony/projects/yupi/docs/prior-aware-monitor-declared-2026-10-23.md:7)). That is legitimate experimental scope, but no transfer beyond that family follows. The grid varies only the scale of one exponential-TV kernel, not noise-model families; β = 2 tests tempering the correct masses, not independently misspecified priors. High balanced accuracy does not establish calibrated certification probabilities. “Same best observer” means best **within this grid**, with both preferred parameters at its boundaries.

6. **Medium — The eightfold headline and broader audit language need tighter scope.**  
   Eightfold describes **k = 7 coin medians**. The learner experiment uses k = 6, where widening is **2.4–6.2×**; its same-position comparisons are controlled, so this is a narrative mismatch, not a fatal experimental confound ([two-step-margin-result:59](/home/tony/projects/yupi/docs/two-step-margin-result-2026-10-23.md:59)). Likewise, “generalised across four parameterisations” means completion-probability variants preserving the same dominant mechanism, not independent worlds ([world-variant-result:91](/home/tony/projects/yupi/docs/world-variant-gate-result-2026-10-22.md:91)).

**Single most efficient falsification experiment:** run a **validation-calibrated one-step challenge**, requiring no retraining. For all ten frozen learners, compare nearest-law one/two-step monitors against the current best prior-aware monitor; extend c below ¼, select thresholds on validation at matched coverage, then freeze everything and evaluate fresh, paired k = 6 test windows. Predeclare that a one-step nearest-law monitor within **0.01** of the best prior-aware monitor, with negligible depth gain for the poorest learners, defeats the “needs a prior/richer query” and dramatic “rescue” claims. The existing JSON already makes this a serious threat, rather than another experiment selected to elaborate the story.

---

## Owner's dispositions (2026-10-25)

**Finding 1 is confirmed and is worse than stated.** Recomputed from the committed JSON:

| learner | nearest-law, one step | nearest-law, two steps | β = 0 summed, one step | best prior-aware (grid) |
|---|---|---|---|---|
| range over the 10 learners | 0.884–0.975 | 0.916–0.988 | 0.518–0.943 | 0.899–0.981 |

- The nearest-law two-step monitor uses **no prior**, and it **beats the grid's best prior-aware observer in all 10
  learners**.
- The "prior-free collapse" was the β = 0 *summed* observer, which effectively puts a uniform prior over laws and
  rewards multiplicity. This is ledger F10: a fourth observer artefact of the owner's making.

**Withdrawn or narrowed:**
1. *"Certification needs a prior or a richer query"*: **withdrawn as stated.** At k = 6 a nearest-law one-step monitor
   reaches 0.884–0.975. What the evidence supports: (a) at k = 7, mass-blind one-step monitors were trapped by rare
   near-pure neighbours, and a prior or a second step fixed that; (b) a second step improves the nearest-law monitor
   for every learner (+0.012 to +0.075). Sufficiency, not necessity (finding 2).
2. *"The second step rescues the worst learners most"*: **withdrawn.** It belongs to the β = 0 summed observer. For
   nearest-law monitors the gain/error correlation is +0.30 (Codex), which is weak.
3. *"One observer design is best for every learner"*: **narrowed to "within the grid".** An out-of-grid nearest-law
   two-step monitor beats it.
4. *R = 0.73, "comparable"*: **kept as the declared verdict, with the reviewer's caveat.** R depends on the observer
   set: 0.37 with β = 1 only, 2.74 with the full grid. It is not a decomposition of contributions.
5. *Mass-floor correction* (finding 4): **accepted.** A floor removes 26–48 % of withheld mass at r3 against about
   5 % at r0, so the "4–7× wider at rich interfaces" claim mixes margin with unequal removal of alternatives. To be
   replaced by an integrated monitor comparison, not floors.
6. Findings 5 and 6: **accepted as scope.** The observer is oracle-assisted and family-specific. The eightfold figure is
   k = 7; k = 6 is 2.4–6.2×. "Four parameterisations" means completion-probability variants of one mechanism.

**Next:** the reviewer's falsification experiment, declared before running. It is a validation-calibrated challenge
between nearest-law one- and two-step monitors and the best prior-aware monitor (c extended below ¼), at matched
coverage, on fresh paired test windows.
