# How Truncated Observers Initialize Belief — first measurements

**v0.2 — 2026-08-13.** Drafted by the day-four instance, same evening as the
full-context injectivity note (0772227), which made this question the
program's critical path. Script: `scripts/window_prior_experiment.py`
(exact arithmetic throughout; reproduces every number here in ~8s; pass an
epsilon as argv[1] — e.g. `1/2` — for the §"v0.2 amendment" runs).
Status: **measured input to the Part II §2 design decision**, which remains
open and belongs to cross-family review. No spec text is edited by this note.
**v0.2 (same day):** the ε<1 caveat was checked hours after v0.1 and
partially killed F5's strong form — see the amendment section at the end.
v0.1's body is preserved unedited above it; read the amendment before
citing F5 or the proposed implication.

## The question and the candidates

Part II §2 leaves open how a windowed/truncated observer's prior is
initialized at window start t₀. Three candidate semantics, all exactly
computable in owned worlds:

- **P1 "marginal"** — the exact unconditional state distribution μ_{t₀}
  (knows the clock and the dynamics, saw no prefix). Bayes-correct:
  filtering P1 forward must equal path-sum conditioning with the prefix
  marginalized.
- **P2 "support-uniform"** — uniform over support(μ_{t₀}) (knows the
  clock, forgot the measure).
- **P3 "clock-free"** — uniform over ⋃_t support(μ_t), t ∈ [0, H]
  (forgot the clock too).

Worlds: **A** = the injectivity note's contention world (3 threads / 1 CPU /
1 lock, both waiter orders reachable), ε=1; **B** = A plus a device with
completion_p = 1/3, skewing the time marginals. H = 12; t₀ ∈ {2, 4, 6};
all four rungs; metrics are posterior support size and total-variation
distance, both exact (TV displayed as float).

## Findings

**F1 — The instrument's first nonzero measurements.** Windowed posteriors
are fat from the first observation: max support 3 / 7 / 12 (world A,
t₀ = 2 / 4 / 6) and 3 / 6 / 10 (world B), versus the provably universal
support-1 of every full-context observer. Uncertainty in this program now
exists, is exactly quantified, and grows with how much prefix the window
discarded.

**F2 — The filter survives its first nondegenerate validation.** Filtering
P1 forward matches path-sum conditioning bit-for-bit (Fraction ==) at every
in-window prefix: **11,892 checks across both worlds, all rungs, all
window starts — through beliefs up to support 12.** The fat-belief code
paths flagged on Aug 13 as green-but-unexercised (losslessness memory,
consequence 4) have now carried real uncertainty and agreed with the
independent enumeration path. `filter.step` needed no changes: it was
prior-agnostic as written. (The committed nondegeneracy *test* still waits
on the §2 decision; this is the measured preview.)

**F3 — Witness 1–2 classes are nonempty in the window regime.** Concrete
exemplars, exact probabilities: world A, t₀=6, after one in-window
DISPATCH at r1/r2 — two states at p = 6/31 each differing *only* in
wait-queue order (0,2) vs (2,0), the wake ambiguity RELATED resolves at
r3; world B, t₀=6, after one IO_COMPLETE — exactly 50/50 over *which*
thread is lock-blocked. The v0.2.2 rescoping of witnesses 1–2 to C1
windows is hereby confirmed mechanically at C0-adjacent scale: the
ambiguity the witnesses need exists under windows and only under windows.

**F4 — Rung separation is nonzero inside windows, and shows up first as
recovery rate.** In both worlds, r1 ≡ r2 and r3 ≡ r4 exactly (the arity
argument, echoed inside windows: one lock makes OBJECT deterministic;
ACTOR + I5 makes LINEAGE redundant), but r3/r4 wash out a wrong prior
measurably faster than r1/r2 — e.g. world A, t₀=2, step 3:
E[TV(P3‖P1)] = 0.89 at r1 vs 0.62 at r3. Richer interfaces buy faster
recovery from prior error — the first measured rung difference of the
project. (Max support was rung-invariant in these worlds; the support-
separating configurations are C1's job.)

**F5 — Forgetting the measure is cheap; forgetting the clock is not.**
- P2 vs P1: cost ≤ 0.07 TV at its worst (A t₀=6 step 1: 0.067; B: 0.028),
  exact merge (posterior equality, not approximation) within ≤ 4
  observations in every cell, and *identically zero* at t₀ ∈ {2, 4} in
  both worlds — μ_{t₀} is uniform-on-support surprisingly often at ε=1,
  and even where it isn't, likelihoods dominate almost immediately.
- P3 vs P1: initial TV 0.75–0.96, washout slow (still 0.26–0.29 at step 6
  for t₀=6), monotone but dragging across most of the window.

**Reading:** the Part II §2 decision is *load-bearing about clock and
support, second-order about the measure*. An observer that knows its
offset and the reachable set is near-Bayes within a few ticks no matter
what measure it assumes; an observer without the clock spends most of a
short window paying for it.

## Proposed implication (for review, not decided here)

Define the canonical M1 windowed observer as **clock-known,
support-uniform** (P2): it is implementable without oracle access to
μ_{t₀}'s measure, and measurably near-equivalent to the Bayes-correct
prior within a few observations. Keep P1 as the calibration ceiling
(and the filter-validation identity), and treat P3 (clock-free) as a
separate, *harder* observer class worth studying deliberately rather than
adopting accidentally. The window-prior clause of Part II §2 should
name the observer's clock knowledge explicitly — the experiment says that
is the choice that matters.

## Caveats, named

Two small worlds; ε = 1 only (the near-uniformity of μ_t that makes P2 so
cheap may soften at ε < 1 — rerun there before freezing anything); fifo
only; H = 12; TV and support only (no entropy curves yet); both worlds
terminate, which forces eventual merging of all observers — long-lived
worlds may not merge, and P3's slow washout would then be a permanent tax.
The C1-scale version of this experiment, per the D4/D9 precedence rule,
must wait for the D4 benchmark freeze.

---

## v0.2 amendment — the ε<1 rerun (same day)

The first caveat above was checked the same evening (both worlds,
ε = 1/2, same t₀ grid; the mixture regime puts rr_cursor into the state
and skews μ_t away from uniform). The bit-for-bit gate passed everywhere
again — thousands of further checks, now covering fat beliefs under
cursor dynamics. The findings move as follows.

**F5's strong form is dead.** At ε = 1/2, P2's initial cost is 0.25–0.46
TV (versus ≤ 0.07 at ε = 1) — the ε=1 near-uniformity of μ_{t₀} was doing
the heavy lifting, as the caveat suspected. Worse, and new: **the P2
residual can persist to the end of the window on sparse rungs.** World A,
t₀=4, r1/r2: E[TV] plateaus at 0.047 from step 4 onward with 15% of
window mass never merging; t₀=6 r1/r2 is still unmerged in 18% of mass at
step 6. On r3/r4 the same cells reach *exact* zero by step 4, in both
worlds. Mechanism: whenever the window never re-observes the ambiguous
subspace (lock owner after the relevant threads terminate; cursor value
at ε<1), the posterior ratio over that subspace stays frozen at the prior
ratio — a wrong measure survives verbatim in the final belief. Sparse
interfaces resolve fewer subspaces, so they preserve prior error; richer
interfaces erase it.

**What survives:** clock dominance is unchanged — P3 starts at 0.79–0.96
TV at ε = 1/2 and still dwarfs P2 in every cell, so the ordering
P3 ≫ P2 ≥ P1 and the "clock and support are load-bearing" conclusion
stand. Fat beliefs, F2's gate result, F3's witness exemplars, and F4's
recovery-rate rung separation all carry over.

**New finding (upgraded from side-effect to result): prior residue is
rung-dependent.** The gap a wrong prior leaves in the final belief is
itself a function of the observation interface — sparse rungs freeze it
in, rich rungs wash it out. This means rung comparisons made under any
non-Bayes prior *conflate* interface information with prior-error
erasure; observability curves must either use the exact marginal prior or
explicitly separate the residue term.

**Revised proposal for review** (replacing v0.1's): the canonical M1
*measurement* observer should be **P1 (the exact marginal)** — the
instrument owns the oracle, that is the point of Yupana — with P2
retained as the *model of a learned observer* whose rung-dependent
residue is a measurable quantity in its own right (a learned model's
implicit window prior is an empirical object the instrument can now be
pointed at), and P3 as the deliberately hard class. Part II §2's clause
should still name clock knowledge explicitly; v0.2 adds that it must also
name the prior's *measure*, because at ε<1 the measure demonstrably
survives into conclusions.
