# Paper 1: skeleton v0.6 (2026-10-13)

> **Status: GOVERNING for paper 1's shape. Supersedes v0.5.** Written after the two-family adversarial review of
> the §2–§4 drafts (dispositions in `paper1-review-2026-10-13.md`). Both reviewers, working independently, said
> the earned result is the exact side, and that the learner half is a measured case with one exploratory
> intervention. This skeleton adopts that. Owning instance.

## The centre

**In one hidden system small enough to count, we vary only how it is observed. We measure exactly two things for
each interface: how much it lets an observer know about what happens next (the ceiling, a Bayes predictive loss),
and where in the window that knowledge sits (the lag profile).** The two come apart:
- interfaces ranked by ceiling are not ranked the same way at a given lag;
- the lag profiles of richer and poorer interfaces cross;
- the presentation can be changed with the ceiling held identical class by class.

This is the paper's result, and it is exact (§3).

**Small transformers are a measured case** (§4):
- Within each content interface, a converged learner's shortfall from the ceiling is higher in classes with more
  far information. This holds for event kind and for entity identity, on held-out models. It is correlational and
  confirmatory, and it survives class-clustered errors.
- Training longer does not remove that association (confirmatory).
- The learners beat a count table over the ceiling's own classes by 1.3–5.2× per seed (exploratory).
- No cross-interface ordering is claimed, since a seed-resolved counterexample exists.

**One intervention, exploratory, examined as a 2×2.** With the ceiling held identical, three relay models beat three
controls. Two pre-registered follow-ups then separated the copy's *presence* from its *supervision*. On KIND:
- an unscored copy cost the learner;
- supervising the slot without the copy helped a little;
- the copy's increment once supervised is not resolved.
Post hoc: none of these resolves on ACTOR, where the unscored copy if anything helped; small recipe changes move the
shortfall by comparable amounts; and only the full relay beats r1 on both fields together. The simple placement
hypothesis, "a near copy helps a learned reader", finds no support. What placement does appears to depend on what
the learner is trained to produce, and it differs by field (§4e; `relay-2x2-verdict-v0.1.md`).

**What is ours and what is not.** Someya et al. (ACL 2025) used entropy-preserving transformations, exact PFSA
local entropies, and learner KL against the inherent entropy. Our ι_m is their m-local entropy less the
full-window entropy. So we do not claim exact ceilings or entropy-preserving relocation as new. We claim:
- one *fixed* hidden system observed through several interfaces, as a controlled variable;
- predictive laws matched class by class under intervention;
- naming-aware entity targets (binding), measured alongside kind;
- within-interface analyses with the model as the unit;
- the systems framing: Log20's identifiability objective (SOSP '17) priced against a learned consumer.

**Producer and consumer locality: motivation only. Its one test found no support for it** (see above). Traces are written where activity happens, and learned
consumers may pay for where information sits. That is the hypothesis the instrument is built to test, and paper 1
does not establish it. The relay is a consumer-side transformation of a window. Back-reference fields are a
familiar log-design pattern, for example:
- per-transaction previous-record links (ARIES prevLSN);
- the scheduler's previous-task state on a context switch (Linux `sched_switch`);
- parent and related activity identifiers in tracing (OpenTelemetry, ETW).
These are candidate citations, to be verified before use. §1 frames the relay as pricing that familiar
denormalization for a learned reader, not as a new principle.

## Sections

| § | content | status |
|---|---|---|
| 1 | Telemetry for debuggers vs learned readers; Log20; Someya; the adopted Mason & Anand analogy paragraph | as reviewed |
| 2 | Instrument: world, window law, rungs, naming, pattern observer, shared-kernel gate limit, structural-observer injectivity (scoped), window-level rungs, learners, estimator, model as unit | exact / method |
| 3 | Ceiling as Bayes predictive loss; ladder; lag profile = m-local entropy minus ceiling; crossing; ceiling-holding rungs; one cross-interface pair and its counterexample | **exact: the result** |
| 4a | Within-cell association, KIND and actor, r1–r4 | confirmatory (correlational) |
| 4b | Convergence does not remove it; the "no more than" clause failed and is reported | confirmatory / failure reported |
| 4c | No cross-interface claim (see §3.4) | — |
| 4d | Count baseline | exploratory |
| 4e | Relay: 3 vs 3 separation, the Δι_4 pricing rejected, three rival mechanisms, the loss-masked arm | exploratory, plus pre-registered arm |
| 5 | What output-level comparisons could not settle, and the designs that would | negative, as method |
| 6 | Limits; next studies (fixed-model interventions, full-profile locality test, acquisition dynamics, exchange rate, exposure) | — |

## Owed before external review (updated 2026-10-13, night)

**Current drafts:** `paper1-draft-s1-s6-s7-v0.3.md` (title, abstract, §1, §6, §7), `-s2-v0.3`, `-s3-v0.3`, `-s4-v0.3`,
`-s5-v0.3`, and Figure 4a. Whole-draft review dispositions: `paper1-whole-review-2026-10-13.md`.

Done:
- the loss-masked arm and the 2×2;
- the FE robustness check (KIND 45/45; ACTOR not robust);
- the raw-bin figure;
- injectivity at r1;
- Table 3.0 (state vs predictive);
- related work;
- the d = 256 size check.

Owed:
1. ~~A recurrent (GRU) baseline.~~ Run 2026-10-13: all 8 models are under the floor, worse than the count table, so
   uninformative. A *tuned* recurrent baseline is owed (`gru-baseline-verdict-v0.1.md`).
2. The instrument appendix (W19): pseudocode, a worked window, state/class/frontier counts, cost, a reproducibility
   manifest.
3. The remaining citation checks listed at the end of §7.
4. A third whole-draft review by both families.

## Cut (unchanged)

Belief geometry; the three-arm test; any mechanism claim; any claim about epistemic honesty or text-only
supervision; "the learner builds its own index".

## Addendum 2026-10-15 (new owner): two additions, adopted into the next skeleton revision

1. **§3.0 gains the KIND split for the pattern observer at k = 7** (`kind-uncertainty-split-40-8-2-k7-eps*-2026-10-15.json`,
   exact): H\* = R + G, with R = E[H(KIND | S)] and G = I(KIND; S | c). R's law-mass mean is interface-invariant
   by construction (0.6085 bits at ε = 1, 0.5441 at ε = ½), so an interface acts only through the observation gap:
   r0 0.567 → r3 0.302 bits at ε = 1 (0.560 → 0.240 at ε = ½). About half of r0's next-KIND uncertainty and a third
   of r3's is hidden state. This aligns §3.0 (structural observer, last record) with §3.1–3.2 (pattern observer,
   k = 7) on the KIND target, which the third review asked for.
2. **§5 gains a fifth item: mechanism sparsity.** Classes whose next-KIND uncertainty is pure randomness (G = 0)
   take three H\* values per ε, one of them (the device-completion coin, 0.918 bits) holding ~90 % of their mass;
   matched-H\* contrasts between random and hidden uncertainty cover ~1 % of mass. With §5.1's three-value finding
   for ι = 0 classes, this is the same constraint met twice: a world small enough for exact posteriors has few
   stochastic mechanisms, so learner contrasts at matched exact quantities collapse onto one or two of them.
   Candidate design: a world variant whose random sources have many entropies and interact with hidden state;
   and, for any exact testbed, an overlap check on mechanisms before a learner contrast is designed.
   Evidence: `exposure-prereg-review-2026-10-15.md`, `random-vs-hidden-review-2026-10-15.md`.
