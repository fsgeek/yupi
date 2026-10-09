# Paper 1 — skeleton, decisions, and readiness (v0.2, 2026-10-04)

> **2026-10-09: superseded by `docs/paper1-skeleton-v0.4.md` (written from the reviewed inventory).**
>
> **2026-10-05: amended by `docs/paper1-skeleton-v0.3.md` (deltas: the decoy design and the plateau). Read v0.3 first.**
>
> **Status: GOVERNING for paper 1's shape. It supersedes v0.1** (`docs/paper1-skeleton-v0.1.md`). v0.1's §0–§1
> audit record, its corrections C1/C2 (§4) and the cut list it adopts all still stand, and are not repeated
> here. Written by the instance of 2026-10-02/04, which owns the project. The PI's terms are unchanged: "ready"
> means ready for **external review**, and a result goes in only if **it teaches something most readers won't
> already know.**

## 0. Why v0.2

v0.1's D1 asked what predicts a small transformer's excess over the exact ceiling. That question has now been
answered by three confirmatory tests and two exploratory follow-ups. The answer is not the one v0.1 or the
2026-10-02 handoff anticipated ("shortfall tracks distance; richer interfaces help by moving information
closer"). Both halves of that lesson failed their own tests.

| source | status | finding |
|---|---|---|
| `d1-long-lag-verdict-v0.1.md` | confirmatory | within cells, KIND excess rises with exact long-lag information ι_kind,4 (21/21 held-out runs) |
| `actor-long-lag-verdict-v0.1.md` | confirmatory | the same holds for actor identity (36/36) |
| `converged-ladder-verdict-v0.1.md` | confirmatory | both survive convergence (C1 24/24, A4 24/24); per-bit cost roughly halves (C2 clause FAILS: it shrank more than the excess); **the cross-cell ordering by ι fails at ε = ½ (C3)** |
| `relay-intervention-verdict-v0.1.md` | confirmatory | **the causal distance reading fails.** Moving information closer, with ceilings identical class by class, does not help in proportion to the move. The gain is V-shaped in Δι; at 15 epochs the slope is 0 |
| `relay-v-diagnosis-results-v0.1.md` (+ corrections) | exploratory | no relay gain where there is no long-range information (the exact-zero set is exactly ι4 = 0); the gain sits in classes with long-range dependence and ~60 % of it persists at 15 epochs |
| `relay-free-difficulty-results-v0.1.md` (+ corrections) | exploratory, data-suggested | which rung's ι4 indexes the learner is **unresolved** (separation does not survive last-kind fixed effects); the learner's cost is a **plateau** (~0.015–0.024 bits for any ι4 in (0, 0.4]) rising only at the top: it behaves like the *presence* of long-range dependence, not its quantity |

## 1. Decisions (owner, 2026-10-04)

**D1′. The learner half's lesson.** It is now a lesson about method, demonstrated on transformers:

> *An exact information quantity can predict a learner's shortfall within every interface and still not be its
> cause. An instrument whose ceilings are identical class by class can run the intervention that separates the
> two.* In Yupana, small transformers' excess is higher in histories that carry long-range dependence, for what
> happens next and for who does it, at the converged budget. Moving that information closer does not relieve the
> cost in proportion to the move. Distance in the trace is not the cause. Exploratory analysis suggests the cost
> behaves like the *presence* of long-range dependence, a class type, more than its amount in bits.

This passes the inclusion test better than v0.1's lesson. "Small models lose distant information" is something
readers already believe. "The exact regressor was right and the causal story built on it was wrong, and only an
exact instrument could tell" is not.

**D2′. What paper 1 may claim from the learner side:**
- **Within cells (confirmatory):** excess ~ ι_long for KIND and actor, at both budgets.
- **Causal (confirmatory, negative):** the relay intervention rejects distance as the cause.
- **Exploratory, labelled as such, and confirmatory only if §3 item 2 passes:** the plateau shape (presence over
  quantity); no relay gain without long-range dependence; a relay gain in classes with it that persists at
  convergence.
- **Withdrawn after review (2026-10-04), not to be revived without new data:** relay-free indexing (H-free), "the
  relay is a speed-up", "no lasting advantage", and β_long as a marginal price per bit.
- **Not claimed:**
  - that ι ranks interfaces (C3 failed);
  - that any mechanism is identified ("binding assembly" is a named, untested candidate);
  - anything about transformers in general beyond this scale and world.

**D3′. The bridge to Mason & Anand is argued, not asserted.** CLAUDE.md calls Yupi "the constructive
complement" of the impossibility result. The paper must state the relation precisely or not make it. The
precise form: the impossibility says text-only observation cannot verify an agent's epistemic state under bounded
supervision. Yupana exhibits a world where the state *is* known, and measures how much of it each text interface
carries and how much a learner recovers. That is an illustration and a measurement, not a corollary. §1 says
exactly that, and the paragraph gets an adversarial review before the draft circulates (§3 item 4).

**D4′. Unchanged from v0.1:** D3 (common target), D4's out-of-scope list, D5 (r4 naming). The cross-L context axis,
synchronization markers, the binding/lexical splits, H1 and size claims all remain out.

## 2. Section outline (v0.1's, with §4 rewritten)

| § | Section | Teaches |
|---|---|---|
| 1 | Introduction | In a world small enough to count, we measure exactly what each trace interface carries and where a learner falls short. D3′ states the relation to the impossibility result precisely. |
| 2 | The instrument | Exact ceilings are exact *for a stated observer*. Canonical vs pattern tracks. The two-path gate (8,542,940 posteriors), with what it does and does not validate. |
| 3 | Exact observability | Interface value exists only where the window hides history. Four regimes at the frozen law. Exact attribution (D8 C0b). The lag profiles cross: richer interfaces move next-KIND information from far to near. |
| 4 | **What the learner's shortfall tracks, and what it doesn't** | Within-cell law (KIND, actor, converged). The cross-cell ordering fails, and why (seed spread vs ι gap). **The relay: identical ceilings, a causal test, a rejected mechanism.** The plateau (presence over quantity) and the relay's residual gain, with their evidential status. The order-m ceilings as the n-gram baseline; the count baseline. |
| 5 | Belief geometry | v0.1's §5, unchanged. |
| 6 | Limits | v0.1's list, plus: three seeds per cell (seed spread rivals cross-cell effects); one relay interface; the exploratory status of §4's positive reading. |

## 3. Readiness for external review, in blocking order

Items 1, 3, 4 and 5 of v0.1 are **done**: order-m ceilings and ι, the per-window D1 test (then confirmed on held-out
models), the budget choice (d = 128, 15 epochs), and the converged ladder. v0.1 item 6's relay half is done as
the causal test.

1. **Count baseline** (v0.1 item 2). A canonicalize-and-count learner scored under the same contract. Reviewer
   objection 1 is still open: is gap 2 about transformers at all? CPU only.
2. **Confirmatory test of what survived.** The D2′ exploratory claims become claims only if they hold on models
   that did not suggest them: fresh seeds (4–6) of r1, r1ʀ and the decoy (item 3) at ε = 1, 5 and 15 epochs, plus
   ε = ½ if its paired corpus is cheap to build. Predictions are stamped before training: (i) the cost profile is a
   plateau (bins vs ι4 = 0: every low bin positive, and the lowest bin not below the median bin); (ii) zero paired
   relay gain on ι4 = 0 classes; (iii) a positive paired gain on ι4 > 0 classes at 15 epochs. GPU, under the
   Hamut'ay lease. **Before stamping, compute each prediction's severity** (what share of the rival readings'
   outcomes it would reject), per the lesson of C2's band.
3. **A relay-matched decoy** (the other half of v0.1 item 6). Part II's ctrl-irr is specified but unbuilt, and its
   "preserve P(field | kind)" does not match the relay. The matched decoy uses the same slot, the same KIND
   alphabet and is window-local, but carries **no binding content**: decoy_t = the KIND of record t − 1. Like the
   relay, it is a deterministic function of the window prefix, so the KIND ceiling is identical class by class
   (relay design §3's argument, gated the same way). It carries nothing the learner can't read one record back.
   If the decoy yields the same residual gain as the relay, the gain comes from field count or format, not from
   what the relay says. Train it alongside item 2's seeds, under the same stamp.
4. **The bridge paragraph** (D3′), with one adversarial reviewer from another model family.
5. Belief-geometry completions (v0.1 item 7), unchanged.
6. Ceiling normalization, estimator fixes, the exposure-gap note v0.2, Clause 3, the exact-side reruns (v0.1
   items 8–12), unchanged.
7. Literature (v0.1 item 13), plus a search for prior *intervention* tests of learned long-range dependence
   (relocation or relay-style manipulations) before §4 claims novelty for the method.
8. Appendices (v0.1 item 14), plus the 2026-10-02 scorecards and the two-family review records.

## 4. What would change this document

- If item 2 fails, §4 reports the within-cell law and the rejected mechanism only, and the plateau reading is
  presented as a hypothesis.
- If item 3 shows the decoy gains as much as the relay, the relay's gain is about field count, not binding
  content, and §4 says so.
- If item 1 puts the count learner on the ceiling, gap 2 is a statement about transformers at this scale, and
  §4 opens with that.

Any change is a v0.3, with the reason stated here.
