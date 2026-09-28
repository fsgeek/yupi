**Review: "What the Trace Surrenders, I: Exact Per-Interface Ceilings for a Small Transformer on a Finite Scheduler World" (skeleton as outlined)**

I checked the claims against docs/learner-first-results-40-8-2-2026-09-18.md §§2, 10, 14, 17, 20, 21, 22.1, docs/exit-clause-40-8-2-note-v0.1.md with its tables, and docs/corpus-track-40-8-2-note-v0.1.md.

## Summary

The paper builds a finite, OS-like stochastic world. In it the exact Bayesian posterior over hidden state can be computed for every observation window, under a five-rung interface ladder (r0 to r4). The exact side is carefully done:
- a two-path gate over 8.5M windows
- a frozen window law, (40,8,2)
- adjacent content-rung separations above δ = 0.01 at both ε
- divergent history classes exhibited

On the learner side, a 0.84M-parameter transformer is scored against the pattern-level (renaming-invariant) next-record ceiling at k = 7 within L = 8. The headline has two parts. First, the learner's excess is not monotone in the interface (r2 is worst; r1 ≈ r3). Second, an exposed field can move the exact ceiling by about as much as the learner's whole shortfall. A probe section finds the exact next-kind belief linearly recoverable, with an interface ordering at layer 1 only.

As an instrument, this is a clean piece of engineering with unusually honest provenance. As a paper, the learner-side lesson is under-theorized, under-controlled and quantitatively overstated in places. The contribution that survives review is the instrument. The skeleton knows this, but the abstract does not yet reflect it.

**Current score: weak reject (4/10).** Most of that is the learner half.

## Three strongest objections

**1. The central learner comparison has no baseline that would tell us what "excess" means. Its null hypothesis is a strawman.**

H3-learner's null is that excess is "flat or monotone in the same direction as the ceilings". Nothing predicts that. There is no argument that approximation error should track the Bayes-optimal entropy of the target. So rejecting the null is not informative.

The worry becomes concrete once you consider a count-based learner. At k = 7 there are about 32,755 pattern classes (§15 census) against about 1.7M training windows with at least 7 records. A learner that canonicalizes names by first appearance and keeps a smoothed count table over prefixes would likely sit very close to the ceiling on every rung. If so, the transformer's "excess" is a statement about this architecture's inductive bias and optimization at 5 epochs. It is not a statement about trace-available information being "not organized accessibly". That distinction is the proposal's own gap 2 versus sample complexity.

The skeleton lists n-gram and GRU baselines as owed (§5 item 5). I would make a canonicalize-and-count baseline the first owed item, ahead of the GRU. It is the natural estimator for this world. If it closes the gap, the paper's learner framing has to change.

**2. The r2 penalty has a simpler explanation already in the data, and the proposed decoy control does not test it.**

- r3 exposes OBJECT and RELATED, which is more than r2 exposes, yet costs the learner the same as r1 (0.059 vs 0.060, sd 0.001 / 0.007). "Any exposed field costs the learner" is therefore already falsified by r3.
- The live alternative is latent-inference load. At r2 the ceiling needs the owner to be inferred from history: §17.2 finds a third of (window, lock) examples uncertain, at 0.236 bits each. At r3 and r4 the owner is printed and that load is exactly 0. A learner whose excess scales with how much hidden-state tracking the ceiling needs would produce exactly r1 ≈ r3 < r2. That result is expected, not surprising.
- The ctrl-irr decoy preserves P(field | EVENT_KIND). That makes it trivially predictable from the kind, so it tests "one more cheap token". It does not test "one more state-dependent field", and it cannot separate the load hypothesis from the lock-specific one.
- The controls that would separate them:
  - an r2 variant where the owner is revealed intermittently, at a controlled rate;
  - a decoy that depends on a hidden variable the learner must track but which is irrelevant to the other fields;
  - regressing per-cell excess on an exact latent-load quantity, for example Σ I(next; hidden | prefix) at the ceiling.
- A second confound is that tokens per record differ across rungs. Matched epochs therefore give unmatched token budgets and unmatched attention spans at k = 7. The skeleton never mentions this.

**3. The "ceiling shift ≈ learner shortfall" comparison, which is the second half of the lesson, is mis-specified.**

- **The field is not exposed at r2.** The 0.121 bits is I(next; owner) at r2, for a field that r2 does not expose. The field r2 actually adds is OBJECT, and it moves the learner-facing ceiling from 1.377 to 1.359 bits, only 0.018 (§2 table). The abstract's "the owner field that r3 adds would be worth 0.121 bits per window" is closer, but it is still not the ceiling shift.
- **It is a sum over locks.** §17.2 computes 0.121 "per window (summing the visible locks)". A sum of per-lock mutual informations is not I(next; all owners): owners are correlated, and MI is not additive. The ceiling's actual r2 to r3 drop is 0.076–0.077 bits per window by the note's own reading 3, which also bundles in RELATED.
- **The units differ.** 0.121 is per window, over the whole next-record entropy of 1.596. The learner gap is structural bits per record on the k = 7 continuing-window base.
- **The ratio is stale.** "About three times" comes from the 3-seed r2 to r1 gap of +0.036. With the six-seed r2 the gap is 0.026, so the ratio is about 4.6×. Without r2 seed 3 it is 0.020, about 6×.

The honest comparison is ΔH* between adjacent rungs, on one base, next to Δexcess.

## Claims I do not believe as stated

- **"The exact ceilings fall monotonically down the interface ladder"** is presented as the contrast to the learner. That holds for canonical state entropy (0.60 to 0.39). It does not hold for the ceiling the learner is actually scored against: the pattern predictive H* is identical at r3 and r4 "to three decimals at every k and both ε" (§3.4). So the r3/r4 comparison of learner excess has no ceiling step, and at least one rung of claim (1) does not apply. Separately, the state-entropy ladder in the abstract and the next-record H* that the learner faces are different quantities. The abstract juxtaposes them without saying so.
- **Corpus-track numbers in §2 ("3.5–3.9× in state entropy").** The corpus-track note's own banner says these numbers "are not cited as corpus-track ceilings until [Clause 3] is discharged". The skeleton labels them "thread-naming lower bounds" in RQ1 but uses them as a teaching point in §2's table row.
- **"Layer-1 ordering means the first block doesn't take up the extra information."** OIR = 1 − KL_repr/(H(Z̄) − H(Z|h)), with H(Z̄) = 2.43 fixed. Back-computing from §21, layer-1 KL_repr rises from about 0.23 (r1) to about 0.35 (r4). "Absolute extraction flat at about 1.2 bits" is the same fact restated: the extra KL roughly equals the ceiling's reduction in H(Z|h), which is 0.09 bits. So neither "mechanical artifact" nor "fixed extraction" is established. The claim is a four-point near-equality with no uncertainty on it. Report per-seed extracted bits with ranges. And without an untrained-network probe it cannot be said what layer-1 OIR 0.77–0.84 means: at k = 1 OIR is 1.000 at every layer, which random features may also achieve.
- **"On kind-only traces the model is within 0.005 bits per record of the ceiling"** is true but uninformative. r0 has no entities and about 1 bit of ceiling. It is a positive control and should be framed only that way.
- **"All six r2 seeds lie above all r1 and r3 seeds."** This is true at ε = 1. It rests on 3 seeds each for r1 and r3, at one recipe known to be under-converged: §22.1 moves r1 seed 1 from 0.064 to 0.047 at 15 epochs, a shift as large as the whole r2 to r1 gap. The ladder has already reshaped once, from 200k windows to 2M. Under exchangeability, min(6) > max(3) has p ≈ 1/84 for each comparison, but the comparison was chosen after looking. At ε = ½ it fails.
- **"Every content rung yields a point-mass posterior from reset at full context (a structural-injectivity argument)."** In the abstract this reads as a result. It is a proof sketch on a quotient. The exhaustive A/B/C checks have not been rerun on the corrected kernel, and the two-path gate shares that kernel.
- **"Every adjacent content-rung pair separates by more than δ."** The r3 to r4 step clears δ by 1.13–1.42×. δ's band was fixed after a sweep, and r0 was excluded by researcher decision. The statement is true on the canonical track but fragile, and invisible on the pattern track (see the first bullet). Say so in the abstract.

## What would change my score

- **To weak accept, as an instrument paper:** retitle and rewrite the abstract so the instrument is the contribution, with the learner results as a demonstration. Fix the ceiling-shift comparison (objection 3). Report the pattern-track H* next to the canonical ladder in F1, and state plainly that r3 = r4 there. Recompute ceilings on the base the excess uses (the 0.85-mass issue). Discharge Clause 3 or drop the corpus-track state-entropy figures.
- **To accept, with the learner lesson:**
  - a converged-budget ladder with at least 6 seeds per cell and OTS-stamped predictions;
  - the canonicalize-and-count and n-gram baselines;
  - a control that separates latent-inference load from lock-specific cost (objection 2), in place of or alongside the P(field | kind) decoy;
  - token-budget matching across rungs;
  - untrained-probe controls for §5.

  If the non-monotone ladder survives all of that, and the paper can state it as "excess tracks latent-inference load, not ceiling entropy" with an exact load quantity on the x-axis, that is a genuine and publishable learner-side finding. The current framing is not.