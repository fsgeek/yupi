# Paper 1: skeleton v0.4 (2026-10-09)

> **2026-10-09 (later): §4a demoted.** See `docs/inventory-2026-10-09.md` §G. The relay rejected only the lag-4
> proportionality hypothesis, not locality, and the contrary-to-Someya framing is withdrawn. The learner half now
> opens with §4b (the within-cell law). §4a becomes "an intervention that rejected a specific distance hypothesis;
> full-profile reading open". The relay replication (design and prereg drafts) is withdrawn before stamp.
>
> **Status: GOVERNING for paper 1's shape. It supersedes v0.1–v0.3**, which stay on record for their audit trails.
> v0.4 is written from `docs/inventory-2026-10-09.md` (v0.2, reviewed by Claude and Codex independently) and not
> patched from v0.3. Its occasion was Tony's observation that the work was "trying to fit the truth to the paper".
> Rule for every section: a claim enters only with the inventory status it has. Nothing is promoted by the
> outline. Written by the owning instance.

## The centre

**In a world small enough to count, we measure exactly what each trace interface makes knowable about a hidden
system, and where in the trace that knowledge sits. Small transformers trained on those traces are a measured
case.** The learner's shortfall tracks exact long-range information within every interface. But moving that
information closer does not relieve the shortfall in proportion to the move, and that is the result readers will
not expect.

## Sections

| § | content | inventory items | status in the paper |
|---|---|---|---|
| 1 | Introduction: the instrument and its question. The relation to Mason & Anand is **the reviewed bridge paragraph only** (`docs/bridge-draft-2026-10-09.md`, adopted only after review) | bridge | as reviewed |
| 2 | The instrument. Exact ceilings *for a stated observer*. The two-path gate validates the **filter under one shared kernel**, not the kernel. Canonical and pattern tracks. Interventions with ceilings identical class by class (gates A–C) | A1 (reworded), A4 | exact, with the shared-kernel limit stated |
| 3 | Exact observability. For r1–r4, interface value exists only where the window hides history; four regimes at the frozen law, with a thin top rung. Lag profiles cross: richer interfaces move next-KIND information from far to near | A2, A3 | exact |
| 4a | **The relay result (front of the learner half).** Ceiling held identical class by class, information moved, and the gain does not follow the move. At 5 epochs it is V-shaped in Δι; at 15 epochs the right arm flattens. Report it qualitatively, per seed pairing, with the 10-05 CORRECTIONS. The t-values are window-level and are not quoted as strength | B3 | confirmatory rejection, robust in shape |
| 4b | Within-cell law: KIND and actor excess rise with ι_long, held-out and at convergence, **under class-clustered errors** (refit 2026-10-09). Convergence cuts the long-lag cost proportionally more than the overall excess, and does not remove it | B1, B5′ | confirmatory |
| 4c | Cross-cell ordering holds at ε = 1 and fails at ε = ½ (seed spread exceeds the ι gap) | B2 | confirmatory, split |
| 4d | Far better than counting: every seed beats a Witten–Bell table over the ceiling's own classes, by 1.3–5.2× where entities exist. Both learners show the step at ι4 > 0 | B5 | exploratory, per seed |
| 4e | No relay gain where ι4 = 0; gain persists at convergence. **Confounded with posterior shape (A5)**, stated as such | B4 | exploratory |
| 5 | What output-level comparisons could not settle, and why. The plateau (insufficient informative overlap), the regressor horse race (collinearity), move vs bind (a missing variable-but-uninformative control arm). The model, not the window, is the unit, and 5 epochs is a mixed phase. Short, framed as method: each failure names the design that would settle it | C1–C4, B6 | negative results, with the missing design |
| 6 | Limits and next studies: shared-kernel validation; one world and one scale; three seeds per cell; fixed-model, evaluation-time interventions (interchange interventions) for the move-vs-bind question; acquisition dynamics (per-checkpoint censuses, ≥ 8 seeds); belief geometry and the exposure gap (paper 3) | B6, B7, shelved three-arm | — |

## Cut from paper 1

- Belief geometry (B7): controls owed. It moves to the exposure/use work.
- The three-arm confirmatory test: shelved. Its assets (corpus 0582ffbeb4693d27, rungs r1D/r1S, scorer v3, the 12
  unread pilot models) are kept for the fixed-model study.
- Any mechanism claim. Any claim about epistemic honesty or text-only supervision.

## §4a's framing after the literature pass (`docs/literature-pass-2026-10-09.md`)

Someya et al. (ACL 2025, arXiv:2506.05136) already relocated information under transformations that preserve the
ceiling, in natural text. They found loss rising roughly linearly as information is pushed further away. §4a
therefore **does not claim the intervention as new.** It claims a contrary result under stricter conditions: an
exact ceiling held identical class by class, in a structured world, with the source left in place. Gain does not
follow the move, and pushing information *further back* is followed by *better* learning (R4's wrong sign). Pfau
et al. (filler tokens) bears on §5's move-vs-bind confound. Li et al. (arXiv:2610.05292) is to be read before
paper 3.

**This raises the bar for §4a.** A result that contradicts published work rests today on 3 + 3 models. It is
robust in shape (8–9/9 pairings) but unreplicated on fresh models. **Owed before external review: a model-level
replication of §4a on the fresh paired corpus** (r1 and r1R, run 0582ffbeb4693d27). It needs:
- seed-matched models;
- one pre-registered, offset-cancelling contrast per seed, chosen to discriminate the locality prediction (gain ≤ 0
  where the relay moves information further back) from §4a's (gain > 0 there);
- severity computed at the model level before stamping;
- the same two-family pre-stamp review.

Design note: `docs/relay-replication-design-v0.1.md`.

## Before external review

1. The bridge paragraph adopted after its cross-family review.
2. **Done (`literature-pass-2026-10-09.md`), with the qualification above.** A literature pass for §4a's novelty claim, covering relocation and relay-style interventions on learned
   long-range dependence, and for §5's framing (Jonas & Kording; non-identifiability in mechanistic
   interpretability; causal abstraction). Citations verified, not from memory.
3. A GRU baseline, if cheap. Otherwise §4d says the baseline is weak.
4. A draft, and then an adversarial review of the draft as a whole, by both families.
