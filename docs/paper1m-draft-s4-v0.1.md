# Paper 1 (methods), §4 draft v0.1 (2026-10-15): A support audit

> **Status: DRAFT v0.1, owning instance.** Governed by `paper1-skeleton-v0.9.md` §4. Every number is traced in the
> provenance list at the end and was reproduced by the owner on 2026-10-15. Not yet reviewed.

## 4. Which contrasts can this world carry, and at what precision?

Exact ceilings tell a learner study what is knowable. They do not tell it whether the comparison it wants to make
exists in the world. A contrast needs classes on both sides that match on everything except the quantity of
interest, and an output-level question needs an answer that a model's predictions are precise enough to carry. An
exact oracle can check both before any model is trained. This section runs those checks on Yupana and reports what
they found.

### 4.1 A motivating error

Our §4 learner analysis first read the shortfall of a trained model as a *step*: roughly constant once a class has
any far information (ι₄ > 0), rather than rising with it. That reading came from fits that controlled the class's
next-KIND entropy. It does not survive. Classes with ι₄ = 0 take only three next-KIND entropy values, so the entropy
control was extrapolating far outside the support of one side of the contrast. The raw per-model bins rise with ι₄
in every model (Figure 4a). The data could have shown this before the fit was run. A count of the entropy values on
each side of ι₄ = 0 takes seconds.

### 4.2 Randomness against withheld state

§3 splits each class's next-KIND uncertainty exactly: H\* = R + G, with R the randomness that an observer of the
hidden state would still face and G the part due to state the interface withholds. A natural learner question
follows: does a model treat "the world is random here" differently from "the telemetry hides the state here"? The
cleanest version compares classes of matched H\* whose uncertainty is pure randomness (G = 0) with classes where
much of it is withheld (G/H\* ≥ 0.5).

The support for that contrast is small:
- the pure-randomness classes with H\* > 0 are 15.6 % (ε = 1) and 17.2 % (ε = ½) of the position-7 population, pooled
  over r1–r3;
- they take only three values of H\*, and one of them, the device-completion coin (0.918 bits), is 89 % and 92 % of
  their mass;
- the high-gap classes that share a 0.05-bit H\* bin with them are 0.8–1.4 % of the population per rung.

So the clean contrast is, in effect, one mechanism (a pending I/O completes with probability 1/3) against everything
else. A graded version has more support: within 0.05-bit H\* bins, the share G/H\* spans 0.30 or more between its
10th and 90th percentiles on 17–22 % of the population at ε = 1 and 36–43 % at ε = ½. We have not audited how many
mechanisms that variation spans, and do not claim it is mechanism-balanced.

The narrowness is not an accident of analysis. Milestone 1 placed randomness only in the scheduler and the device,
to keep exact filtering inside its support budget. The audit measures the price of that choice.

### 4.3 Can the source of uncertainty be read from one prediction?

The same split bears on a monitor that reads a model's output. In general, the randomness/withheld-state split is
not identifiable from a predictive distribution, even an exact one (Bergna et al. 2026). That result quantifies over
unknown generative models. With the kernel known, structure can restore identification, so the question has to
be asked inside the world, for a stated family: known kernel, interface and ε, pattern observer, position 7.

**At exact precision, almost.** Classes with identical exact next-KIND laws almost always share their split. The
exceptions are rare (below 0.05 % of mass on every rung) but real. On r3 at ε = 1, 24 reachable classes share the
law ⅓ ACQUIRE, ⅓ IO_COMPLETE, ⅓ RELEASE, with splits including (R, G) = (0.918, 0.667) and (1.585, 0).

**At finite precision, the amount of uncertainty blurs before its kind.** Suppose a monitor knows the prediction
only to within δ in total variation. Within such a ball, G changes by 0.1 bits or more on 49–51 % of mass at
δ = 0.02 (ε = 1). But R changes that much on only 1.8–2.4 %, and opposite-sign swaps between R and G occur on about
3 %. At that precision the monitor can tell *what kind* of uncertainty it faces but not *how much*. By δ = 0.05 the
kind blurs too: R differs on 43–44 % of mass and swaps on 18–21 %.

**Measured on trained models.** Where do actual learners fall? We ran twelve trained models (r1 and r3, both ε,
three seeds each) on their test windows. For each window we took the classes whose exact law is at least as close
to the model's output as the true class's, and asked how much of their prior mass differs from the truth in R by
0.1 bits or more:
- the models' median TV to the exact law is 0.015–0.027, so they sit near the boundary;
- on average, 5–11 % of that look-alike mass disagrees about R;
- 10–23 % of windows carry 10 % or more such disagreement;
- ambiguity is higher at ε = ½ and on r1 than on r3.

A monitor of these models would mostly read the kind of uncertainty correctly from one prediction, and would be
wrong about it on a minority of windows that is not small. We pre-declared a rule for calling the result
"readable" or "not readable"; every cell falls between, so we report the numbers and no general sentence.

### 4.4 The audit as a procedure

The checks above are cheap. All use only the exact class tables, and those already exist for the ceilings:
1. **State the estimand and the matching variables.** Example: shortfall difference between G = 0 and G/H\* ≥ 0.5,
   matched on H\* to 0.05 bits.
2. **Compute the eligible mass on each side**, and the mass in matched cells. Report both as shares of the
   population the learner is evaluated on, with the denominator stated.
3. **Count the mechanisms in each matched cell.** For example, group classes by their exact next-event law, or by the
   kernel rule that produces it. Report the share of the dominant one.
4. **State the admissible family** for any identifiability claim (what the monitor is assumed to know), and test it
   inside the world.
5. **Sweep precision.** Repeat any identifiability check over a range of tolerances, and place measured learner
   precision on the same axis.

Steps 1–3 for §4.2 take under a minute of CPU over existing tables. Steps 4–5 took minutes for the exact sweep and
under a quarter of an hour of wall time for the twelve-model measurement (twelve parallel CPU processes). The learner study they would have redirected took GPU-days.

---

## Provenance

- 4.1: `paper1-draft-s4-v0.3.md` §4a ("The shape"); `paper1-draft-s5-v0.4.md` §5.1; Figure 4a.
- 4.2: `split-v2` class rows (`scripts/kind_uncertainty_split.py`, sha-pinned in
  `kind-uncertainty-split-40-8-2-k7-eps*-2026-10-15.json`); owner recomputation 2026-10-15 (15.64 / 17.19 %, coin
  89.39 / 92.29 %, high-gap 0.82–1.44 %, wide-spread 17.1–22.0 / 35.7–43.0 %), matching Codex v0.8 review #3–#4.
  Milestone 1 design: `yupana-m1-spec-draft.md` (D1, line 112).
- 4.3 exact: `one-step-identifiability-40-8-2-k7-2026-10-15.json`; the collision: Codex v0.8 review #2, re-derived by
  the owner from the r3 ε = 1 rows (24 classes, 0.009 % of mass). Finite precision: `identifiability-tolerance-40-8-2-k7-2026-10-15.json`;
  R/G swap figures reproduced with `scratchpad/review4c/alt2.py` (r1, r3, ε = 1; the ε = ½ R figures are owed).
  Learners (run 2026-10-15, launched after the declaration commit d027f05 at 10:37, finished by 10:48 PDT):
  `learner-precision-monitor-40-8-2-k7-2026-10-15.json`, declared in
  `learner-precision-monitor-check-2026-10-15.md` before any model ran.
- Bergna, Depeweg & Hernández-Lobato, arXiv:2605.06413.
