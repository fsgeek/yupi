# Paper 1 (methods), §4 draft v0.3 (2026-10-15): A support audit

> **Status: DRAFT v0.3, owning instance.** v0.2 revised per both final reads (`paper1m-draft-review-2026-10-15.md`, final-read section); v0.1 revised per `paper1m-draft-review-2026-10-15.md` (items 1, 2, 5, 8,
> 10; Codex #5, #11, #13; Claude #10, #13, #14), with the second declared monitor measurement. Governed by
> `paper1-skeleton-v0.9.md` §4. Every number is traced at the end.

## 4. Which contrasts can this world carry, and at what precision?

Exact ceilings tell a learner study what is knowable. They do not tell it whether the comparison it wants exists in
the world: a contrast needs classes on both sides that match on everything but the quantity of interest. Nor do
they tell it whether an output-level question can be answered at the precision a model's predictions have. The
first check, and the exact half of the second, need only the exact class tables, so they could run before any
model is trained; measuring a model's own precision needs the model. We ran them afterwards, on the learner studies of §5, and report what they would have shown.

### 4.1 A motivating error

The §5.1 analysis first read a trained model's shortfall as a *step*: roughly constant once a class has any far
information (ι₄ > 0), rather than rising with it. That reading came from fits that controlled the class's next-KIND
entropy, and it does not survive. Classes with ι₄ = 0 take only three next-KIND entropy values, so the entropy
control was extrapolating far outside the support of one side of the contrast. In raw per-model bins, shortfall
rises with ι₄ above ι₄ = 0.001 in every model. A count of the entropy values on each side of ι₄ = 0 would have shown
the problem before the fit.

### 4.2 Randomness against withheld state

§3.1 splits each class's next-KIND uncertainty exactly into randomness R and withheld state G. The natural learner
question is whether a model treats "the world is random here" differently from "the telemetry hides the state
here". Its cleanest form compares classes of matched H\* whose uncertainty is pure randomness (G = 0, H\* > 0) with
classes where much of it is withheld (G/H\* ≥ 0.5), matched in 0.05-bit H\* bins.

| ε | interface | pure: eligible and matched | of which the device coin | high-gap: eligible | high-gap: matched | graded variation |
|---|---|---|---|---|---|---|
| 1 | r1 / r2 / r3 | 14.6 / 15.6 / 16.7 % | 92 / 91 / 86 % | 39 / 35 / 28 % | 1.4 / 1.2 / 0.9 % | 21 / 24 / 19 % |
| ½ | r1 / r2 / r3 | 16.1 / 17.2 / 18.3 % | 95 / 93 / 89 % | 36 / 32 / 26 % | 1.4 / 1.3 / 0.8 % | 39 / 44 / 38 % |

*Shares of the position-7 population (law mass 0.85; r4 agrees with r3 at this precision). Pure: G = 0, H\* > 0;
high-gap: G/H\* ≥ 0.5; matched: sharing a bin floor(H\*/0.05) with the other side. Every pure class is matched, and
the matched mass lies in three shared bins. Device coin: a pure class whose H\* is the entropy of a 1/3 coin
(0.918 bits). Graded variation: mass in bins where G/H\* spans 0.30 or more between its mass-weighted 10th and 90th
percentiles; restricting to bins with at least 0.5 % of mass and five classes gives 17–22 % (ε = 1) and 36–43 % (ε = ½).*

Two things follow. The clean contrast is narrow: its high-gap side is about 1 % of the population, and its
pure-randomness side is, at 86–95 %, one mechanism (a pending I/O completes with probability 1/3). A graded
contrast has far more mass, but we have not audited how many mechanisms it spans, and do not claim it is balanced.
Small mass does not by itself make a contrast unusable; it says how much of the evaluation the contrast can draw
on, and from what. The narrowness is a consequence of design: Milestone 1 placed randomness only in the scheduler and
the device, to keep exact filtering inside its support budget.

### 4.3 Can one prediction say where the uncertainty comes from?

In general, the split between randomness and withheld state is not identifiable from a predictive distribution, even
an exact one (Bergna et al. 2026); their result concerns unknown generative models. With the kernel known,
structure can restore identification, so we ask the question inside the world for a stated family: the kernel, the
interface and ε are known, and the observer is the pattern observer at position 7. Two senses of "where it comes
from" matter, and they behave differently: the *kind*, which we define as §4.2's two sides (pure randomness, G = 0 with
H\* > 0, against substantial withheld state, G ≥ 0.1 bits; classes in between have no kind), and the *amount of
randomness* R.

**Exact laws.** Classes with identical exact next-KIND laws almost always share their split; the exceptions are
below 0.05 % of position-7 mass on every interface, but real. On r3 at ε = 1, 24 reachable classes share the law
⅓ ACQUIRE, ⅓ IO_COMPLETE, ⅓ RELEASE, with splits including (R, G) = (0.918, 0.667) and (1.585, 0).

**Laws a small distance apart.** Let δ be a total-variation separation between two classes' exact laws. (Two laws can
both be within η of one prediction only if they are within 2η of each other, so δ corresponds to a prediction error of
about δ/2.) For each class we ask whether some class within δ differs from it. These are existential statistics: one
rare neighbour suffices.

| δ | kind differs (ε = 1 / ½, r1–r4) | R differs by ≥ 0.1 bits (ε = 1, r1 and r3) |
|---|---|---|
| 0.01 | 0.1–0.2 % / 0.6–1.7 % | — |
| 0.02 | 14–17 % / 17–19 % | 1.8–2.4 % |
| 0.05 | 16–18 % / 20–23 % | 43–44 % |

*Shares of all position-7 mass. Opposite-sign R/G swaps of at least 0.05 bits each occur on about 3 % of mass at
δ = 0.02 and 18–21 % at δ = 0.05 (ε = 1, r1 and r3).*

The two senses fail in different ways. The kind becomes ambiguous early, between δ = 0.01 and 0.02, and then saturates
near a fifth of the mass; R stays pinned to δ = 0.02 and then fails widely. (G itself, the amount of withheld state,
differs on 49–51 % of mass at δ = 0.02, mostly because a small perturbation moves H\*.)

**Measured on trained models.** We ran twelve trained models (r1 and r3, both ε, three seeds each) on their test
windows. For each window, the *look-alike set* is the classes whose exact law is at least as close to the model's
output as the true class's law is. This set is calibrated by an oracle that knows the true class, so the statistics
below are prior-mass shares of look-alikes, not error rates of any monitor.
- The models' TV to the exact law: median 0.015–0.027, mean 0.027–0.041; 19–31 % of windows exceed 0.05.
- Look-alike mass of the other *kind*: 0.5–1.4 % on average; 1.3–3.9 % of windows have 10 % or more. (Here every
  class with G = 0, including deterministic ones, counted as pure; windows whose class has no kind, 16–18 % of mass,
  score zero; and a window's own R and G were taken as the mean over classes sharing its exact law, which differs from
  the class's own value only on collision groups, below 0.05 % of mass. Since at most 39 % of windows score zero by
  construction, shares conditioned on the rest are at most 1/0.61 times these: under 2.3 % on average and 6.4 % of
  windows, still within the declared "readable" thresholds.)
- Look-alike mass differing in R by 0.1 bits or more: 5–11 % on average; 10–23 % of windows have 10 % or more,
  higher at ε = ½ and on r1 than on r3.

We declared rules for calling each result readable or not before each run. The R measurement came first and fell
between the rules in every cell; the kind measurement was declared after it, at a reviewer's prompting, and before it
ran. The kind meets the "readable" rule in every cell and seed; for R we report the numbers only. Set against the
exact sweep, the models' median error (0.015–0.027, i.e. a separation of roughly 0.03–0.05) sits where the kind has
already become ambiguous on a fifth of the mass existentially, yet the look-alike mass of the other kind stays small:
the ambiguous neighbours exist but are rare.

### 4.4 The audit as a procedure

The checks use only the exact class tables, which a study computing exact ceilings already has:
1. **State the estimand and the matching variables** (e.g. shortfall difference between G = 0 and G/H\* ≥ 0.5,
   matched on H\* to 0.05 bits).
2. **Compute the eligible and matched mass on each side**, per interface and ε, as shares of the population the
   learner will be evaluated on.
3. **Report the mechanism composition** of each side, for example by grouping classes by their exact next-event law
   or by the kernel rule that produces it, with the dominant share.
4. **State the admissible family** for any identifiability claim (what a monitor is assumed to know), and test it
   inside the world, distinguishing the senses of the question.
5. **Sweep precision**: repeat any identifiability check over a range of separations; once models exist, place their
   measured output precision on the same axis.

Steps 1–5's exact parts run on a workstation CPU from the existing tables; the model measurement needs one forward pass
per model over its test windows (each twelve-model run took under a quarter of an hour of wall time as parallel CPU
processes, by the commit and file timestamps recorded in the declaration note).

---

## Provenance

- 4.1: `paper1-draft-s4-v0.3.md` §4a ("The shape"); `paper1-draft-s5-v0.4.md` §5.1.
- 4.2 and the kind sweep: `scripts/support_audit_table.py` → `support-audit-table-40-8-2-k7-2026-10-15.json`, from the `split-v2` rows (`scripts/kind_uncertainty_split.py`; hashes in `split-v2-rows-sha256-2026-10-15.txt`); the
  table recomputed by the owner 2026-10-15 and matching Codex's independent recomputation (whole-draft review #3).
  Milestone 1 design: `yupana-m1-spec-draft.md` (D1).
- 4.3 exact: `one-step-identifiability-40-8-2-k7-2026-10-15.json`; collision re-derived from the r3 ε = 1 rows.
  Separation: `identifiability-tolerance-40-8-2-k7-2026-10-15.json` (G); `scripts/review/tolerance_r_g_swap.py` (R and
  swaps, r1 and r3 at ε = 1). Trained models: `learner-precision-monitor-40-8-2-k7-2026-10-15.json` (R) and
  `learner-precision-monitor-gkind-40-8-2-k7-2026-10-15.json` (kind), both declared in
  `learner-precision-monitor-check-2026-10-15.md` before running.
- Bergna, Depeweg & Hernández-Lobato, arXiv:2605.06413.
