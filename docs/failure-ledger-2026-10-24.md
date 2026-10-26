# Where the predictions failed, Oct 22–24: why, what it taught, what is left (2026-10-24)

> Owning instance, at Tony's request: "look at the space where our predictions failed: why did they fail, what did we
> learn from this, and what is there left to discover?" No venue. This is a map for deciding whether there is a story
> we can defend.

## 1. The ledger

| # | declared | what happened | why (status) |
|---|---|---|---|
| F1 | P3: occupancy-dependent completion splits the pure side into two laws | One law kept 77–87 % | Pure classes are those where occupancy is known, and they sit overwhelmingly at one pending request (checked). |
| F2 | K2: the declared kind monitor reads the kind (≥ 0.90 balanced, ≥ 0.80 coverage) | 2 of 12 models | The monitor abstained whenever the nearest law had no kind, and pure laws are ringed by near-pure laws at TV ≈ 0.001 (checked). |
| F3 | K3: monitor accuracy orders cells inversely to look-alike mass | Top two cells swapped | Look-alike values differed by 0.00014. Probably noise (not checked). |
| F4 | M1 (high half): beyond 0.6 μ the output has moved toward the mixtures | 4 of 12 models keep 15–21 % certified pure | **Open.** Error direction is not uniformly toward mixtures. |
| F5 | I1: margin non-decreasing across interfaces | One dip (0.0038 → 0.0034) | The whole reading was an existential artefact. With a mass floor, rich interfaces widen the margin 4–7× (checked). |
| F6 | T2's mechanism: rare neighbours give themselves away at the second step | Ratio held; mechanism not shown | The ratio is larger only because rare neighbours shrink the one-step margin. Two-step margins are about 0.12 everywhere (checked). |
| F7 | L1: at r3 ε = 1 the second step lowers the sufficient share | Flat (Δ ≤ 0.012) | One-step error there is already far inside the margin. The second step has nothing to add (inferred from the ratios). |
| F8 | L3: prior-aware within 0.02 between one and two steps | r3 ε = 1 worse by 0.027–0.045 | **Mostly the monitor's noise scale:** τ = mean error is too broad. At τ × ¼ the gap is 0.007–0.008, and one-step accuracy rises to 0.96 (post hoc, 2026-10-24). |

| F9 | Q3 (10-25): the prior-free two-step gain shrinks as learners get worse | Reversed: Spearman +0.85; the gain is largest for the worst learners | Prior-free one-step observers of poor learners fall into the rare-neighbour trap; the wider two-step margin rescues them (inferred; `learner-quality-result-2026-10-25.md`). |
| F10 | (10-25 interpretation) prior-free observers collapse at one step; two steps rescue the worst learners most | The collapse belonged to the β = 0 *summed* observer (a uniform law prior). A nearest-law monitor, with no prior, gets 0.884–0.975 at one step and 0.916–0.988 at two, beating the best prior-aware observer in all 10 | A fourth observer artefact of the owner's making; found by Codex (`story-codex-review-2026-10-25.md`). |
| F11 | W2/W3 (10-26): learners err toward hidden-state alternatives in particular | 13/22 and 15/22; direction idiosyncratic per model | Points instead to class-dependent precision: learners are more precise on pure windows (post hoc; `error-direction-result-2026-10-26.md`). |
| F11 revised | (10-26, later) the cosine test was the wrong instrument | At the certificate boundary, real errors certify *less* than random-direction errors of the same size in 19/22 (`direction-intervention-result-2026-10-26.md`) | A modest lean toward hidden state relative to chance, about 18 % of the way to adversarial. The weak form of the PACMI hypothesis has support; the baseline needs a fairer null. |

Pattern B update (10-25): across real quality differences, observer and learner are *comparable* (R = 0.73), not observer-dominated; see `learner-quality-result-2026-10-25.md`.

Corrections of interpretation that were not declared predictions, but belong here:
- "The training could not answer its question": that was an overstatement.
- "The pure side cannot be certified from one output": that was mass-blindness.
- "Observing more doesn't help": that was an existential artefact.

## 2. Two patterns, not eight accidents

**A. Existence versus mass.**
- F1, F5 and F6, and two of the three interpretive corrections, came from reasoning about which laws *exist* near
  which.
- The outcome was decided by where the *prior mass* sits.
- Richer interfaces multiply rare classes. Exact worlds make every rare class visible and exact. An existential
  statistic ("is there a law within δ?") is therefore dominated by laws no observer would ever meet.
- v3 printed this caution once (§4.3, "one rare neighbour suffices") and then reasoned past it four times.

**B. The observer dominates the observed.**
- F2, F8 and the post hoc monitor: three times, a limit attributed to the learners was mostly in the monitor. Its
  abstention rule, its neglect of the prior and its noise scale were each a choice of mine.
- Each time, changing the observer moved the conclusion more than anything about the learners did.

Both patterns are about the *observer*, not the learner. That fits Yupi's founding variable (the observation
interface) better than the paper drafts did. The interface is one part of the observer. The prior, the query and the
noise model are the others.

## 3. What the failures taught, as claims we could defend now (one world)

1. **Certification needs something beyond a single output.**
   - In the exact world, telling pure randomness from substantial hidden state at learner precision requires a prior,
     a richer query, or both.
   - Two-step queries widen the exact margin roughly eightfold.
   - For these learners, a prior-free two-step monitor reaches 0.91–0.98.
2. **Existential statistics mislead in exact worlds,** in a direction that grows with telemetry richness.
3. **The observer's own choices can move conclusions about a learner more than the learner does.** This happened
   three times, with numbers.
4. **The audit procedure** (support, mass, composition) generalised across four parameterisations. One of its numbers
   (the ambiguity onset) did not.

## 4. What is left to discover (ordered by how much it could change the story)

1. **The observer's design space, measured as a space.**
   - The prior (none / the true one / a wrong one), the query (1, 2, k steps) and the noise model (scale, tail)
     together decide what a monitor concludes.
   - So far we have points in that space, not its shape. Mapping it would turn pattern B from an anecdote into a
     result.
   - **The wrong-prior arm matters most for PACMI.** In the wild, a monitor's prior is never the true one.
2. **Why do the learners' errors compound about fourfold at the second step?**
   - Is it the record-7 entity predictions, which the KIND of record 8 depends on? Or the conditional KIND itself?
   - The enumerator can split q2's error into the k1 marginal and the conditional, per slot.
3. **Error direction (F4).** Do learners err toward mixtures, i.e. toward "hidden state"? Four models say not
   uniformly. This is the PACMI-shaped question of whether models over-attribute their uncertainty to what they
   can't see.
4. **Deeper queries.** Does a third step keep widening the margin, and when does the learners' compounding error win?
   There should be an optimal query depth per learner. That is a concrete, exact prediction we could make.
5. **Representation dependence.**
   - The R/G split depends on what counts as state (the reviewer's point 3, and Tupay's wall-clock flakiness).
   - A learner that cannot track some state sees randomness where the world has hidden state.
   - Is a learner's *effective* state representation measurable as the split it behaves as if it believed?
6. **Smaller and unexplained:**
   - why r0's neighbours of the coin are heavy mixtures;
   - the V3 r1-to-r2 jump at ε = ½.

## 5. What this suggests the story might be

The founding story was what the trace surrenders. The draft story became what an exact world can settle. The failures
point somewhere between: **what an observer can certify about a model's uncertainty is decided as much by the
observer's prior, query and noise model as by the model, and an exact world can measure each part.**

That is a hypothesis about the story, not the story. Items 1 and 4 of §4 would test it. If mapping the observer
space shows the learner's own contribution is small and stable, the story holds. If the learner's contribution
dominates once the observer is good, it does not, and the certification result (§3.1) stands on its own as a smaller
story.
