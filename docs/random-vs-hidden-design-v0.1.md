# Random or hidden? Design note v0.1 (2026-10-15)

> **Status: DESIGN DRAFT, owning instance. Not a pre-registration.** It follows the retired exposure prereg v0.1
> and the feasibility gate (`exposure-prereg-review-2026-10-15.md`, all sections). It goes to two-family review
> before a pre-registration is written from it.

## 1. The question

In one hidden system observed through nested interfaces, the next-event uncertainty an observer faces is two
things, exactly:
- **R(c) = Σ_s P(s | c) H(KIND | s)**, *transition randomness*: what an observer who knew the state would still face;
- **G(c) = H\*(c) − R(c) = I(KIND; S | c)**, the *observation gap*: uncertainty from state the interface withholds.

Their law-mass means: R is interface-invariant by construction (E[H(KIND | S)]); every interface acts through G.
At matched H\*, G/H\* still varies (moderately at ε = 1, substantially at ε = ½; gate result).

**Does a learner trained on the trace treat "the world is random here" differently from "my telemetry hides the
state here"?** For an operator reading a learned model's uncertainty, the difference is the one that matters:
randomness is a property of the system, while hidden state is a property of the telemetry and can be fixed by
logging more.

## 2. Why the one-step output cannot answer it, and what can

The split is not identifiable from a one-step predictive, even an exact one (Bergna, Depeweg & Hernández-Lobato,
arXiv:2605.06413; in Yupana, P\*(· | c) is a belief-weighted mixture and the mixture is not recoverable from its
mean). So the output side uses a *query class*, as the founding letter asks for the exposure gap: the model's
prediction after one more record.

**Hidden state is learned from; randomness is not.** If G(c) = 0, the next record x₁ is independent of S given c,
so seeing it leaves the belief unchanged; the prediction for the event after it changes only through the dynamics.
If G(c) > 0, x₁ also updates the belief over S. Both are exactly computable:
- **Updating** (the exact observer): P\*(x₂ | c, x₁), which is the ceiling at position k + 1 (the next class).
- **Non-updating**: P̃(x₂ | c, x₁) = Σ_s P(s | c) P(x₂ | s, x₁), the prior belief carried through the dynamics
  conditioned on x₁, with no belief update.

Write **Υ(c, x₁) = KL(P\* ‖ P̃)** for the cost of not learning from x₁. Υ = 0 whenever G(c) = 0. It is the exact,
per-continuation size of what hidden state makes learnable from one more record.

**The model's side.** On existing test windows with ≥ 9 records, the model's prediction at position 8 *is* the
query Q(x₂ | c, x₁), with no sampling and no new training. Per window:
- the model's shortfall, KL(P\* ‖ Q);
- where Q sits between the two references: **update fidelity** φ = 1 − KL(P\* ‖ Q) / Υ, where Υ > τ (τ frozen in
  the prereg). φ ≈ 1 means the model learns from x₁ like the exact observer, φ ≈ 0 means it errs as much as a
  non-updating observer, and φ < 0 means it errs more.
- Primary contrast, at matched H\* (bins as in the gate's post hoc check, frozen): the model's shortfall at position 8
  on classes whose step-7 uncertainty was hidden (G/H\* high) against classes where it was random (G/H\* = 0),
  model as the unit, both ε, r1–r4 within interface.

What is predicted and what is not:
- Predicted by construction: Υ = 0 at G = 0, so φ is undefined there; an oracle Q = P\* gives φ = 1.
- Predicted by paper 1's results (not a finding): shortfall is larger where far information sits; any new
  association has to survive ι_4 and H\* as controls.
- **Not predicted by any objective or closed form:** whether a log-loss learner's errors concentrate where
  learning from new records about hidden state is required (low φ at high Υ), as against being spread evenly.

Negative controls (Codex #2 of the exposure review): a context-independent uniform Q; an H\*-only predictor; a
"belief-frozen" learner, i.e. the exact observer that stops updating at position 7 (P̃ itself, φ = 0 by
definition). Any reported association must separate the model from the frozen observer.

## 3. The activation side (second, gated on §2)

Do the model's activations at the step-7 boundary carry R(c) and G(c) separately at matched H\*? Linear probes for
G/H\* within H\* bins, with:
- an untrained-model control (same architecture, random init) and a shuffled-label control;
- ≥ 5 seeds (3 exist per cell; 2 more per chosen cell at the ladder recipe);
- a frozen probe family and capacity, with selectivity reported (Hewitt & Liang control tasks);
- prior work to distinguish: an entropy-aligned axis tracks *total* predictive entropy in LLMs (Agarwal, Dalal &
  Misra, arXiv:2512.23752); none tests R vs G (`literature-random-vs-hidden-2026-10-15.md`).

The probes cut on 2026-10-09 failed on exactly these controls; this side does not run until §2 has been read.

## 4. What only this instrument has

A fixed hidden system whose observation channel is the controlled variable: moving from r0 to r3 moves G and leaves
R's mean fixed. So "does the learner treat hidden as random" can be asked *as a function of the telemetry*, with
the world held fixed. HMM-in-context work (Simplex 2609.17376; Agarwal et al.) fixes the observation channel;
the near misses vary state-reveal density or the process (2602.14814, 2605.20824, 2607.22646; abstracts only).

## 5. Cost

Exact side: one k = 8 pattern pass per ε (≈ 4–8 min each, about 2 GB) plus the non-updating predictive per
(class, x₁) from the k = 7 posterior (the joint is in hand in `ceiling_table`'s construction). Model side: evaluate
the 30 ladder checkpoints at position 8 (the evaluator takes a k list). No training for §2.

## 6. Open, for the reviewers

1. Is φ the right summary, or should the primary be the paired difference KL(P\* ‖ Q) − Υ·(something)? φ is a ratio
   with a noisy denominator where Υ is small.
2. x₁ is the full pattern record (5 tokens), so Υ mixes belief updates from KIND, ACTOR and the entity fields. Is a
   KIND-only x₁ needed as well, and is it well-defined for a model that sees the whole record?
3. The step-8 class differs from the step-7 class plus x₁ only by re-keying; confirm that P\*(x₂ | c, x₁) equals the
   k = 8 table entry in every case, including fresh entities in x₁.
4. Does Υ duplicate paper 1's ι (far information) in another form? ι_m is information older than m records; Υ is
   information about hidden state in the *newest* record. They should be correlated; how much, exactly, is an
   exact-side number to compute before anything else.
5. Five seeds: the existing three per cell share a recipe with the ladder; the two extra must reproduce it
   bit-for-bit up to the seed.
