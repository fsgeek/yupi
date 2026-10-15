# One-step identifiability of the random/hidden split in Yupana: declared check (2026-10-15)

> Owning instance. Declared before the run. Exact side only. Purpose: the observation-design note's central claim,
> that a monitor of a single next-KIND prediction cannot tell transition randomness R from observation gap G, is
> general (Bergna et al., arXiv:2605.06413) but not automatic for a known kernel (Codex review #13 of
> `random-vs-hidden-design-v0.1.md`). It must be shown in this world.

**Run.** `scripts/kind_uncertainty_split.py` (rows now carry class key and exact P\*(KIND) as Fractions), pattern
observer, k = 7, both ε, rows to `~/.cache/yupi-scratch/split-v2/`.

**Check.** Group classes of each (rung, ε) by their exact P\*(KIND) vector (Fraction equality, not float). Within a
group the one-step prediction is identical, so anything a monitor computes from it is identical. Report:
- the law mass in groups whose classes' G spans ≥ 0.1 bits (max G − min G);
- the same at ≥ 0.25 bits;
- the number of such groups, and the largest span.

**Declared reading.**
- **Supported in this world:** on at least three of the four content rungs at each ε, ≥ 5 % of law mass lies in
  groups with G span ≥ 0.1 bits. The note may then say that, here, identical one-step predictions hide
  materially different splits, on that much mass.
- **Not supported:** < 1 % on every content rung. The note's claim is then general only, and in Yupana the one-step
  prediction largely determines the split; the note must say so and change its central claim.
- **Between:** report the numbers; the note states the mass, not a general sentence.

## Result (owner, 2026-10-15): NOT SUPPORTED, at both ε

Both exact runs valid (H\* reproduces §3.1 on every rung). Raw: `one-step-identifiability-40-8-2-k7-2026-10-15.json`.
Classes sharing an exact P\*(KIND) vector differ in G by ≥ 0.1 bits in 0–6 groups per (rung, ε), out of 2 k–31 k
groups, carrying < 0.05 % of law mass on every rung (largest span 0.667 bits at ε = 1, r3/r4; 0.541 at ε = ½).

**Reading.** In Yupana, with the kernel known, the one-step prediction almost always determines the split between
transition randomness and observation gap. The general non-identifiability (Bergna et al.) does not bind here,
because the state-conditional next-KIND laws come from a few templates (the 1/3 device coin, uniform choices among
runnable threads), and mixtures of few known templates can be unmixed. This is the same mechanism sparsity
that blocks the learner contrasts (`random-vs-hidden-review-2026-10-15.md`), seen from the monitor's side: a
world with few stochastic mechanisms makes the source of uncertainty readable from one prediction, and for the
same reason makes contrasts between sources unavailable to a learner study.

**Consequence for the observation-design note:** its central claim ("a single prediction cannot tell a monitor
which it is") is false in this world, and the note is not written as conceived. What it would have said survives
as one section of the methods paper: mechanism sparsity cuts both ways.

## Correction (owner, 2026-10-15, after the skeleton v0.7 review): the result holds only at exact precision

The check grouped classes by **exact Fraction equality** of P\*(KIND). That makes it nearly tautological: exact
equality almost only occurs between classes whose posteriors mix the same state-conditional laws in the same
proportions, and within such a group R and G are equal by construction (Claude skeleton review #1–#2). The owner
declared the check without asking what precision a monitor has.

Reproduced by the owner with the reviewer's grid-rounding script (`scratchpad/review3/robust.py`, read before
running), share of law mass in groups whose G spans ≥ 0.1 bits:

| grid tolerance on P\*(KIND) | r1 ε = 1 | r3 ε = 1 | r1 ε = ½ | r3 ε = ½ |
|---|---|---|---|---|
| exact | 0.00 % | 0.01 % | 0.04 % | 0.02 % |
| 0.005 | 0.06 % | 0.11 % | 1.8 % | 5.3 % |
| 0.01 | 0.55 % | 0.50 % | 3.5 % | 7.7 % |
| 0.02 | 2.0 % | 2.4 % | 10.6 % | 12.2 % |
| 0.05 | 60 % | 64 % | 73 % | 82 % |

A trained learner's KIND KL of 0.015–0.04 bits allows total-variation error up to ≈ 0.07–0.12 by Pinsker, so a
monitor reading a learner's output works at roughly the coarsest tolerance shown. Grid cells are a crude
neighbourhood (boundary effects both ways); a declared ball-based check is owed before any number here is cited.

**Corrected reading:** with the kernel known and probabilities read exactly, one prediction determines the split.
At any precision a learner's output actually has, it does not, on most of the mass. "Mechanism sparsity cuts both
ways" is withdrawn as a thesis (skeleton v0.7). The original note's claim, that one prediction does not tell a
monitor which kind of uncertainty it faces, is closer to true here than the uncorrected result said, subject to
that check.
