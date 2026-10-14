# Paper 1, §4 draft v0.3 (2026-10-13): Learners, a single-configuration case study

> **Status: DRAFT v0.3, owning instance.** It revises v0.2 after the whole-draft review
> (`paper1-whole-review-2026-10-13.md`: W2, W9, W10, W12, W14, W15, W20, W22, W27). Supersedes v0.2. Statuses in
> square brackets.

## 4. Learners: a single-configuration case study

This section uses one architecture (§2.5, 0.84 M parameters), one window law, one corpus size, and three seeds per
cell unless stated otherwise (the table in §2.5). It is a measured case, not a general account of learners. The
model is the unit of inference. The measurement is the shortfall above the model's own interface's ceiling, which
runs at about 1–4 % of that ceiling.

### 4a. Within each content interface, shortfall is higher where far information is

The pre-registered model regresses each test window's KIND shortfall at position 7 on four terms:
- the class's far information ι_kind,4;
- its near part, ι_kind,1 − ι_kind,4;
- the class's ceiling entropy;
- log₂ of the class's law mass.

The criterion was β_long > 0 with t ≥ 3 in every run, on r1–r4.

**KIND:**
- 5 epochs, held-out: 21 of 21 runs pass. [CONFIRMATORY]
- 15 epochs: 24 of 24 pass, of which 21 are held out. [CONFIRMATORY]
- Robustness [EXPLORATORY re-analyses of the confirmatory runs]:
  - errors clustered by class: every run keeps t ≥ 3 (lowest 5.07);
  - fixed effects for the last prefix record's kind × the number of distinct actors, with errors clustered on those
    26–28 coarse cells: every run keeps t ≥ 3 (lowest 3.44 held-out, 3.60 at 15 epochs).

**At a larger size** [EXPLORATORY, not pre-registered]: d = 256 (3.25 M parameters, the same recipe), r1 ε = 1. The four
existing models (15 epochs, seeds 1–3; 45 epochs, seed 1) were censused on 2026-10-13. All four keep β_long > 0:
frozen-model t 7.6–11.3, and under the coarse-cell fixed effects t 5.6–7.1. Their raw bins rise as at d = 128. At this
recipe the larger model has *higher* overall KIND shortfall than d = 128 (it is under-trained at 15 epochs, as the
September size axis found), so this checks only that the association is not specific to one size, in one cell.
[`b1-size-axis-d256-2026-10-13.jsonl`]

**ACTOR**, with ι_{A|K,4}, a lower bound (§2.5):
- 36 of 36 runs pass at 5 epochs (21 held out). [CONFIRMATORY]
- 24 of 24 pass at 15 epochs. [CONFIRMATORY]
- Class-clustered errors: lowest t 3.11.
- **It is not robust to the stronger check.** Under the same coarse-cell fixed effects, the coefficient stays
  positive in all 60 runs, but it shrinks (median 0.81 of its frozen value at 5 epochs, 0.60 at 15). It keeps
  t ≥ 3 in only 24 of 36 runs at 5 epochs and 9 of 24 at 15. The number of distinct actors is mechanically related
  to the actor target, so this check may over-control. Even so, the actor association cannot be called robust.
  [EXPLORATORY; `b1-fe-coarse-robustness-actor-2026-10-13.json`]

**The shape.** In raw per-model bins, with no controls, KIND shortfall rises with ι_4. Above ι_4 = 0.001 it rises
bin by bin in every one of the 45 models (**Figure 4a**). For r1 ε = 1 at 15 epochs it goes from 0.001–0.004 bits at
ι_4 = 0 to 0.028–0.031 above 0.4.

An earlier "plateau" reading came from fits with the entropy control, and that control extrapolates off the support
of the ι_4 = 0 classes (§5.1). The linear coefficient is therefore not a price per bit, and its size is not compared
across cells or budgets. Only its sign, model by model, is claimed.

**What the association is not.** It is a correlation within cells. Classes with more far information may also be
rarer or harder in ways the controls miss. The count baseline (§4d) shows the same direction. A backoff table is
locality-biased by construction, since it mixes in shorter-suffix estimates, which are wrong exactly where far
information exists. The shared direction is therefore consistent with locality, and also with class rarity, and it
separates neither.

**r0**, with kinds only and no entities: the coefficient is positive but not resolved per seed (t 2.5–2.9, ε = ½,
5 epochs, secondary), and the association is not claimed for r0.

### 4b. Longer training does not remove the association (at 15 epochs)

From 5 to 15 epochs, β_long stays positive with t ≥ 3 in every model, in all 8 cells. [CONFIRMATORY: "does not remove
it"] The pre-registration also predicted that the coefficient would shrink "no more than" the overall shortfall.
That failed in 8 of 8 cells (0.39–0.69 against 0.51–0.76). We report the failure, and we do not read it as a cost
shrinking, because that would compare coefficient magnitudes across budgets. At 15 epochs, validation loss is still
falling slowly (§2.5), so this says nothing about an asymptote.

### 4c. Across interfaces

There is no cross-interface claim. Of the scored orderings:
- r2 > r3 at ε = 1 passed;
- r0 lowest passed at both ε;
- the ε = ½ three-way ordering failed.

A seed-resolved counterexample also exists: r1 > r3 at ε = 1 at nearly equal ι_4. Details are in §3.4.

### 4d. The transformer against a count table

The comparison learner is a Witten–Bell table over the ceiling's own pattern classes, built from the same 2 M
windows. The ratios below are count shortfall over transformer shortfall, so a ratio above 1 means the transformer
did better.
- **Content rungs:** every transformer seed does better, by 1.33–5.22 times.
- **r0:** close. At ε = 1 every transformer seed is slightly better (1.07–1.14). At ε = ½ the table is better
  (0.74–0.87). No uncertainty analysis separates the two.
- The table's shortfall grows with the number of classes, and the transformer's does not.

[EXPLORATORY; one baseline; a recurrent baseline is pre-registered separately]

### 4e. A near copy at a fixed ceiling, as a 2×2

**The original comparison.** The relay (§3.3) holds the ceiling identical class by class. At 15 epochs, all three
r1R models have lower KIND shortfall than all three r1 models (0.0095–0.0130 against 0.0146–0.0158), and lower ACTOR
shortfall seed for seed. The pre-registered prediction priced the gain by Δι_4, the change in information beyond four
records, and it failed. At 5 epochs the gain rose where ι_4 fell and also where it rose. At 15 epochs the gain did
not track Δι_4. These pre-registered tests used window-level errors, which §2.5 rules out as evidence of strength.
So we report only that the pricing prediction failed in shape, model by model, and quote no standard errors.
[pre-registered prediction failed; precision not interpreted] Δι_4 is one point on a profile, and an earlier
full-profile reading is withdrawn (it had no committed source).

**Separating presence from supervision.** In the original recipe the copy is both an input and a training target.
Two pre-registered follow-ups were each reviewed by both families before stamping. They vary only the OBJECT slot.
There are five arms, with KIND shortfall at 15 epochs for seeds 1, 2 and 3:

| arm | OBJECT input | OBJECT target | KIND shortfall | ACTOR shortfall |
|---|---|---|---|---|
| r1 | placeholder | placeholder (trivial) | 0.0157, 0.0146, 0.0158 | 0.0312, 0.0299, 0.0314 |
| r1m | placeholder | none | 0.0176, 0.0209, 0.0170 | 0.0346, 0.0438, 0.0409 |
| r1Rs | placeholder | relay value | 0.0125, 0.0141, 0.0142 | 0.0296, 0.0400, 0.0342 |
| r1Rm | relay copy | none | 0.0281, 0.0411, 0.0307 | 0.0328, 0.0363, 0.0345 |
| r1R | relay copy | relay value | 0.0130, 0.0095, 0.0125 | 0.0278, 0.0262, 0.0308 |

**Pre-registered contrasts, on KIND** (seed-paired; the floor is p = 1/8):
- **Loss-masked arm, reading T:** r1Rm is above every r1R model, so supervision contributes given the copy.
- **C1** (r1Rm against r1m; same mask, different input): **an unscored copy in the input cost the learner,
  relative to a constant placeholder.** This cannot tell an informative but unscored copy from a varying decoy field.
- **C2** (r1Rs against r1; same mask, different target): **supervising the OBJECT slot with the relay value helped
  without the copy present.** r1Rs did learn the lookup, paying 0.00004 bits per slot. C2 cannot tell lookup
  supervision from any nontrivial target in that slot.
- **C3** (r1R against r1Rs; same targets, different input): **whether showing the copy adds to supervision is not
  resolved.** No interaction is claimed.

**Post hoc, and they qualify the above:**
- C2's separation margin is 0.0005 bits.
- Removing OBJECT from the loss altogether (r1m against r1) moved KIND by a comparable amount, in every seed, so
  small recipe changes move this shortfall.
- On ACTOR, none of C1–C3 resolves under the decision rule. C1 leans the other way: the unscored copy is better than
  the placeholder on ACTOR in every seed, though the ranges overlap.
- Summing KIND and ACTOR, only r1R is below every r1 model.

**Reading.** The relay gives no support to the simple form of the placement hypothesis, "a near copy helps a learned
reader". On KIND, a copy helped only where its slot was supervised, and an unscored copy hurt. ACTOR evidence is
inconclusive. Whether the copy adds anything once supervised is open. Three seeds, one world, one budget.
[readings as labelled; everything not pre-registered is EXPLORATORY]

---

## Provenance

- 4a KIND: `d1-long-lag-verdict-v0.1.md`, `converged-ladder-verdict-v0.1.md`, `b1-clustered-refit-2026-10-09.json`,
  `b1-fe-coarse-robustness-2026-10-13.json`, Figure 4a (`scripts/fig_b1_raw_bins.py`).
- 4a ACTOR: `actor-long-lag-verdict-v0.1.md`, `b1-clustered-refit-actor-2026-10-09.json`,
  `b1-fe-coarse-robustness-actor-2026-10-13.json`.
- 4b: `converged-ladder-verdict-v0.1.md` §C2. Convergence diagnostics: §2.5.
- 4c: §3.4.
- 4d: `count-baseline-comparison-2026-10-04.json` (per-seed ratios recomputed 2026-10-13).
- 4e: `relay-intervention-verdict-v0.1.md` (with its 10-05 corrections), `relay-lossmask-verdict-v0.1.md`,
  `relay-2x2-verdict-v0.1.md`, `relay-2x2-score-2026-10-13.json`, `relay-2x2-object-ce-r1Rs-2026-10-13.jsonl`,
  and the census raws named there.
