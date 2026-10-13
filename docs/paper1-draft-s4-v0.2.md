# Paper 1, §4 draft v0.2 (2026-10-13): Learners as a measured case

> **Status: DRAFT v0.2, owning instance.** It revises v0.1 after the two-family review of 2026-10-13
> (dispositions in `paper1-review-2026-10-13.md`) and supersedes it. Numbers re-read or recomputed by the owner are
> marked in the provenance list. Statuses appear in square brackets.

## 4. Learners as a measured case

Every learner is a 0.84 M-parameter decoder trained from scratch (§2.5). The model is the unit. Claims are stated
per model, and window-level t statistics are not used as evidence of strength.

### 4a. Within each content interface, shortfall is higher where far information is

The pre-registered model regresses each test window's KIND shortfall at position 7 on four terms:
- the class's exact far information ι_kind,4;
- its near part, ι_kind,1 − ι_kind,4;
- the class's ceiling entropy;
- log₂ of the class's law mass.

The criterion was β_long > 0 with t ≥ 3 in every run, on the content rungs r1–r4.
- **5 epochs, held-out models:** 21 of 21 runs pass. That is three seeds per cell, six for r2 and r4 at ε = ½, and
  r2 ε = 1 on seeds 4–6. [CONFIRMATORY]
- **15 epochs (converged):** 24 of 24 runs pass. Three of these, r1 ε = 1, had been evaluated before the
  pre-registration, so 21 are held out. [CONFIRMATORY]
- **The actor's identity:** the same holds with ι computed for the next record's actor given its kind. 36 of 36 runs
  pass at 5 epochs (21 held out, 15 existing), and 24 of 24 converged, where two runs sit near the line (t 3.07 and
  3.17). For the actor, unlike KIND, the near term is also positive in most cells, but the far term is larger.
  [CONFIRMATORY; the actor ι is a lower bound under suffix naming]

**Robustness, exploratory.**
- Re-run with errors clustered by class, every converged run keeps t ≥ 3. With the mass control, the lowest t is
  5.07 for KIND and 3.11 for the actor. Clustering moves the standard errors by factors of 0.98–1.13, with a median
  of 1.04. With 20–33 k classes for about 85 k windows, class clustering is a weak check.
- A stronger check adds fixed effects for the last prefix record's kind and the number of distinct actors, and
  clusters errors on those 26–28 coarse cells. Every run keeps β_long > 0 with t ≥ 3: 21 of 21 held-out (lowest t
  3.44) and 24 of 24 converged (lowest t 3.60). [EXPLORATORY robustness of confirmatory runs;
  `b1-fe-coarse-robustness-2026-10-13.json`]

**What the coefficient is not.** The model is linear. In raw per-model bins, with no controls, shortfall rises with
ι_4. Above ι_4 = 0.001 it rises bin by bin in every one of the 45 models (bins at 0.01, 0.05, 0.2 and 0.4). For r1
ε = 1 at 15 epochs it goes from 0.001–0.004 bits at ι_4 = 0 to 0.028–0.031 above 0.4. The two lowest bins are noisy.
**Figure 4a** (`figures/b1-raw-bins-2026-10-13.png`, from `scripts/fig_b1_raw_bins.py`) shows every model, one line
each. The 5-epoch held-out set covers five of the eight cells. One r4 ε = ½ model at 5 epochs is the high-excess
basin noted in the learner results. The
"plateau" seen in earlier binned fits appears only after the entropy control is added, and that control
extrapolates off the support of the ι_4 = 0 classes (§5.1). β_long is therefore not a price per bit, and its size is
not compared across cells or budgets. The claim is the sign, model by model. It is a correlation within cells:
classes with more far information may be harder in ways the controls miss.

**r0** shows kinds only and has no entities. There the coefficient is positive in the secondary analysis (ε = ½,
5 epochs), but it is not resolved per seed (t 2.5–2.9), and the law is not claimed for r0.

### 4b. Convergence does not remove the far association

At 15 epochs β_long stays positive, with t ≥ 3 in every model, in all 8 r1–r4 cells. [CONFIRMATORY: "does not remove
it"] The pre-registration also predicted that the coefficient would shrink "no more than" the overall shortfall.
It failed in 8 of 8 cells: the pooled coefficient fell to 0.39–0.69 of its 5-epoch value, while the KIND shortfall
fell to 0.51–0.76. We report that failure. We do not read it as a far *cost* shrinking faster, because it compares
coefficient magnitudes across budgets, which §4a sets aside. [CONFIRMATORY failure; descriptive otherwise]

### 4c. Across interfaces

See §3.4. The one scored ordering that passed, r2 > r3 at ε = 1, sits beside a seed-resolved counterexample, r1 > r3
at nearly equal ι_4. The ε = ½ ordering failed. The paper makes no cross-interface claim.

### 4d. Far better than counting

The comparison learner is a Witten–Bell count table over the ceiling's own pattern classes, built from the same
2 M windows. On every content rung, every converged transformer seed beats it, by 1.33–5.22 times per seed. On r0,
which has few classes and no entities, the table matches or beats the transformer (ratios 1.07–1.14 at ε = 1 and
0.74–0.87 at ε = ½). The table's shortfall grows with the number of classes (r1 < r2 < r3 ≈ r4 at ε = 1), and the
transformer's does not. [EXPLORATORY; one baseline, and a recurrent baseline is not run]

In binned fits, both learners have higher shortfall in classes with far information than in classes without it.
At the low end the comparison is not identified (§5.1), so we draw no conclusion about mechanism from it.
[EXPLORATORY]

### 4e. A near copy at a fixed ceiling

The relay (§3.3) holds the ceiling identical class by class. Three models trained on r1R are compared with three
trained on r1 (ε = 1, 15 epochs, the same paired corpus).

**What was observed.** Every r1R model has a lower KIND shortfall than every r1 model:

| | seed 1 | seed 2 | seed 3 |
|---|---|---|---|
| r1 | 0.01570 | 0.01464 | 0.01576 |
| r1R | 0.01296 | 0.00947 | 0.01252 |

That is complete separation of 3 against 3, with an exact one-sided permutation p of 1/20. With three models a side,
this design can give no smaller p. The 15-epoch arm was pre-registered as secondary and reported without
thresholds. This summary was computed afterwards. [EXPLORATORY] The gain is not a reallocation. The actor
shortfall is also lower on r1R (0.0262–0.0308 against 0.0299–0.0314), though the two sets overlap. The copy is free to an ideal observer: given the window and the record's own KIND and ACTOR, its value is
determined. It also costs no trace length, since r1 already carries the slot as a masked placeholder. Predicting it
costs r1R models 0.00009–0.00028 bits per scored window, an order of magnitude below the smallest gain.

**What the relay did not show.** The pre-registered test priced the gain by Δι_4. It was rejected. At 5 epochs the
gain rises where ι_4 falls and also where ι_4 rises. At 15 epochs the seed-mean fit's slope on Δι_4 is 0.0005, with a
window-level se of 0.0024. [CONFIRMATORY rejection of the Δι_4 pricing; robust in shape in 8–9 of 9 pairings;
magnitudes not interpreted] An earlier exploratory reading said that a regression on the full profile Δι_1..6
"favours distance". It is withdrawn. The original fit has no committed specification or raw. Refits by the Claude
reviewer give coefficients that alternate in sign across adjacent, collinear lags, so they do not read as a
distance price.

**Three rival mechanisms, and the one the loss-masked arm settles.**
1. *Distance:* the copy shortens how far back the learner must look.
2. *Binding content:* the copy hands the learner a fact ("this actor's last event was …").
3. *Auxiliary supervision:* r1R models are trained to *produce* the relay value, which is the lookup the KIND
   prediction needs.

A pre-registered arm, r1Rm, is r1R with the OBJECT slot left out of the training loss
(`relay-lossmask-prereg-v0.1.md`, stamped before training; verdict `relay-lossmask-verdict-v0.1.md`). It keeps
the copy in the input and removes it as a target. Its three models have KIND shortfalls of 0.028, 0.041 and 0.031.
That is above every r1R model, which meets the pre-registered reading "supervision contributes" (exact p = 1/20).
It is also above every r1 model, which the pre-registration did not foresee [EXPLORATORY]. A copy that is present
but never trained on leaves the learner *worse* than having no copy. On identical inputs, r1Rm matches r1R at
records 1–5 and falls behind only at records 6–8, where the far information is.

So, within these arms, the relay's gain requires training the learner to produce the back-reference. Presenting
it is not enough, and on its own it hurts. A pure distance reading predicted that r1Rm would do no worse than r1,
and every model contradicts it. The result is closer to sub-task supervision (Abbe et al. 2024) than to an input
index. Why an unsupervised variable field hurts is not established. A candidate is that the learner must learn,
with no direct signal, to read a varying token stream. Paper 1 reports the observation and not a mechanism.

---

## Provenance

- 4a counts: the d1 verdict (P1–P4), the actor verdict (A1–A3), the converged-ladder verdict (C1, A4). Seed
  inventory: Codex finding 16 and Claude finding 14, checked against `d1-long-lag-prereg-v0.1.md:28`. Clustering:
  `b1-clustered-refit-2026-10-09.json`, with SE ratios recomputed by the owner on 2026-10-13 (converged 0.981–1.126,
  median 1.039; held-out 1.028–1.186). Fixed-effects check and raw bins: run by the owner on 2026-10-13, all 45
  runs (`scripts/b1_fe_coarse_robustness.py` → `b1-fe-coarse-robustness-2026-10-13.json`; it gates on reproducing
  the frozen HC1 fit to 1e-9). This reproduces Claude findings 5 and 15.
- 4b: `converged-ladder-verdict-v0.1.md` §C2. The ratios were reproduced by Codex (finding 12).
- 4d: `count-baseline-comparison-2026-10-04.json`, per-seed ratios recomputed by the owner on 2026-10-13.
- 4e (loss-masked arm): `relay-lossmask-verdict-v0.1.md` (censuses `learner-window-census-r1Rm-*-2026-10-13.json`;
  by-position check `relay-lossmask-kind-by-position-2026-10-13.jsonl`).
- 4e: the r1 and r1R seed means, the actor shortfalls and the relay-field excess were all recomputed by the owner on
  2026-10-13 from the census JSONLs (Codex also reproduced the means). Slope and se:
  `relay-paired-secondary-2026-10-02.json`. Withdrawal of the full-profile reading: Codex finding 10 and Claude
  finding 7.
