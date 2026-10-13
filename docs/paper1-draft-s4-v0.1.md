# Paper 1, §4 draft v0.1 (2026-10-13): Learners as a measured case

> **Status: DRAFT, owning instance. Not reviewed.** Written from skeleton v0.5 as corrected on 2026-10-13 (causal,
> correlational and open claims kept apart). Each number was re-read from the verdict or raw named in the
> provenance list. Statuses appear in square brackets.

## 4. Learners as a measured case

Every learner here is a 0.84 M-parameter decoder trained from scratch (§2.5). The model is the unit throughout:
claims are stated per model, or per seed pairing, and window-level t statistics are not used as evidence of
strength.

### 4a. Within every interface, the shortfall sits where far information is

For each test window at position 7 we regress the learner's KIND shortfall on:
- the class's exact long-range information ι_kind,4;
- its short-range part (ι_kind,1 − ι_kind,4);
- the class's ceiling entropy H_kind;
- log₂ of the class's law mass, as a frequency control.

The model was frozen and stamped before any held-out census existed.

- **Held-out models, 5 epochs:** β_long > 0 with t ≥ 3 in 21 of 21 runs. Pooled per cell, β_long exceeds β_short
  in 5 of 5 cells. β_short is small (−0.000 to +0.003 bits per bit) but not always zero: it is resolved in r3 and r4
  at ε = ½. [CONFIRMATORY]
- **Converged models, 15 epochs:** 24 of 24 runs pass. [CONFIRMATORY]
- **Errors clustered by class.** ι is a class property, so window-level errors could overstate precision. Re-run
  with errors clustered by class, every converged run keeps t ≥ 3, with a minimum of 5.07 and the mass control
  included. Clustering inflates standard errors by only 4–12 %. [B1, refit 2026-10-09]

**The law extends from *what happens* to *who does it*.** With ι computed for the next record's actor given its
kind, the same model passes in 36 of 36 runs at 5 epochs and 24 of 24 converged. Under class clustering the
lowest converged t is 3.11, so two runs sit near the line. For identities, unlike kinds, near history is not
free either: β_short is positive in most cells, but the long-range term is 4–12 times larger. [CONFIRMATORY; the
actor ι is a lower bound under suffix naming]

**The cost lives where identities must be carried.** On r0, which shows kinds only and no entities, the same
pooled coefficient is about a tenth of the content rungs'. [secondary, not scored]

**What the coefficient is not.** The model is linear with no step term. Binned fits show a cost that is roughly
present-or-absent across ι_4 ∈ (0, 0.4], rising only above that, and the step's own identification is limited
(§5). β_long is therefore not a price per bit, and its magnitude is not compared across cells or budgets. Only the
sign and the per-model significance are claimed. This is a correlation within cells: classes with more far
information are, so far as we can tell, also hard in other ways that the controls do not exhaust.

### 4b. Convergence shrinks the far cost faster than the rest, and does not remove it

Going from 5 to 15 epochs on matched seeds, the pooled β_long falls to 0.39–0.69 of its 5-epoch value. Over the
same budgets the KIND shortfall falls only to 0.51–0.76. The far cost does not vanish: it stays positive in 8 of 8
cells. [CONFIRMATORY. The stamped clause predicted "no more than" the overall shrinkage, and that clause FAILED
8/8. The finding is the reverse of the prediction, and the pre-registered band was too wide to test the sentence.]

### 4c. Across interfaces, the profile orders learners only where its gaps exceed seed spread

At ε = 1 the converged shortfall is larger on r2 than on r3, with every seed separated, as their far
information orders them (§3.4). At ε = ½ the predicted order r2 > r1 > r3 fails: r1 and r3 differ by a sixth of
r1's between-seed sd, while ι puts them 0.033 bits apart. r0, with no entities, has the lowest shortfall at both
ε, seed-resolved. The paper therefore states the law within interfaces only. [CONFIRMATORY, split]

### 4d. Far better than counting

The comparison learner is a Witten–Bell count table over the ceiling's own pattern classes, trained on the same
2 M windows. Wherever entities exist, every converged transformer seed beats it, by 1.3–5.2 times per seed. On
r0, which has few classes, the two coincide (count/transformer 1.1 at ε = 1 and 0.8 at ε = ½). The count
learner's shortfall grows with the number of classes (r1 < r2 < r3 ≈ r4 at ε = 1), and the transformer's does
not. The transformer generalizes across histories that the table keeps apart. [EXPLORATORY, one baseline; a GRU
is not run]

Both learners show the same step: higher shortfall in every class with any far information. This bears on
mechanism. The step is not specific to attention. But a backoff table is not distance-free: Witten–Bell mixes in
shorter-suffix estimates, which are wrong exactly where ι_m > 0, so it carries a locality bias by construction.
The shared step is consistent with locality as an inductive bias of any learner that shares strength across
histories, as Someya et al. found for LSTMs and transformers alike. It does not single out the transformer.
[EXPLORATORY reading]

### 4e. A near copy helps, at a fixed ceiling

The relay (§3.3) holds the ceiling identical class by class and adds, at each record, the kind of the same actor's
previous record. Models trained on r1R are compared with models trained on r1, on paired windows. The relay
field's own prediction cost is reported separately and is negligible (≤ 2 × 10⁻⁴ bits).

**The causal fact.** At the converged budget, the relay lowers the learner's KIND shortfall in **9 of 9** seed
pairings, with mean gains of 0.0017–0.0063 bits. The ceiling is the same, so what the trace makes knowable did
not settle what the learner learned. [ROBUST per pairing. The pre-registered tests were stated on window-level
errors (below); this per-pairing statement was computed afterwards, on 10-05.]

**Where the gain falls.** The gain is near zero where the relay leaves far information unchanged, and it is
present where ι_4 > 0. At 15 epochs, the contrasts against the zero set are positive in 9 of 9 pairings.
[EXPLORATORY, partly checked per pairing; confounded with posterior shape, since classes with ι_4 = 0 take only
three entropy values]

**What the relay did not show.** The pre-registered prediction priced the gain by Δι_4, the change in information
lying beyond four records. It was rejected. At 5 epochs the gain is V-shaped in Δι_4: it rises where ι_4 falls and
also where ι_4 rises. At 15 epochs the slope on Δι_4 is zero. [CONFIRMATORY rejection, robust in shape in 8–9/9
pairings; magnitudes unreliable] But a rise in ι_4 is not information moved further back. Where the relay raises
ι_4, it still moves information closer at lags 1–2, and over lags 1–6 it moves information closer on net.
Regressing the gain on the full profile Δι_1..6 loads mainly on the farthest lags. [EXPLORATORY, collinear
regressors] So the relay rejected one pricing of distance, and did not reject locality.

**The mechanism is open.** The relay's field could help because it shortens distance, or because it hands the
learner a binding fact ("this actor's last event was …"). The arms we ran (relay, decoy, self-copy) cannot separate
these. Any field that varies may help through arm-specific effects that a zero-entropy control cannot absorb (§5).

---

## Provenance

- 4a KIND: `d1-long-lag-verdict-v0.1.md` (P1–P4; stamped fbe0178), `converged-ladder-verdict-v0.1.md` C1;
  class-clustered `b1-clustered-refit-2026-10-09.{json,log}` (converged: 24/24 at t ≥ 3, min t 5.07 with the
  mass control, median se ratio 1.04–1.05). Actor: `actor-long-lag-verdict-v0.1.md` (A1–A3),
  `converged-ladder-verdict-v0.1.md` A4, `b1-clustered-refit-actor-2026-10-09.log` (min t 3.11 with the mass
  control). The r0 tenth: the d1 verdict secondary arm (pooled 0.0036 against 0.029–0.041).
- The "per bit" caution: the 2026-10-04 header on both verdicts. The step's identification: inventory C1.
- 4b: `converged-ladder-verdict-v0.1.md` §C2.
- 4c: `converged-ladder-verdict-v0.1.md` C3/C4; cell means re-read from `converged-ladder-c3c4-2026-10-02.json`
  on 2026-10-13.
- 4d: `count-baseline-results-v0.1.md` §1–§2; per-seed ranges from inventory B5 (the committed comparison raw
  `count-baseline-comparison-2026-10-04.json`). Per-seed ratios recomputed 2026-10-13 from that raw: 1.33–5.22 across r1–r4.
- 4e: `relay-intervention-verdict-v0.1.md` with its 10-05 CORRECTIONS; per-pairing 15-epoch gains from
  `three-arm-prereg-review-2026-10-05.md` addendum ("all 9 pairings are positive: mean gain 0.0017–0.0063");
  the full-profile reading from inventory §G.
