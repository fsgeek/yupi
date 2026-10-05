# Is the learner's long-range difficulty a property of the relay-free history? Design v0.1 (2026-10-04)

> **Status: EXPLORATORY. The design is committed before the script first runs.** The idea comes from
> `docs/relay-v-diagnosis-results-v0.1.md` point 2, which saw the relay's gain track ι4_r1 and ignore ι4_r1R. That
> makes this a follow-up suggested by data, and it cannot be confirmatory however it comes out. A confirmatory
> version needs new seeds or a fresh corpus pair. **Stop rule: one pass.** After it, skeleton v0.2 is written,
> whatever the result.

## Question

Each rung has its own exact long-lag information about the next KIND: ι4_r1 for the relay-free history,
ι4_r1R for the same history with the relay shown. The relay itself adds no information. Which of the two indexes
a learner's KIND excess?

- **H-free (relay-free difficulty).** The learner's long-range difficulty belongs to the underlying history
  (its binding structure), and the relay discounts it. **At r1ʀ, ι4_r1 carries the effect and ι4_r1R does not.**
- **H-acct (the accounting tracks the learner).** Each learner's difficulty follows its own rung's exact
  accounting. **At r1ʀ, ι4_r1R carries the effect and ι4_r1 does not.**
- **Control, r1 censuses.** The r1 learner never sees the relay. So ι4_r1R should add nothing at r1 beyond its
  correlation with ι4_r1. If it does add something, then ι4_r1R stands in for some property of the class, and
  neither reading is clean.

## Data and model

The windows are the 84,949 paired test windows, as in the diagnosis. The response is the KIND excess
(`by_field.kind`), averaged over the three seeds of one rung and one arm. There are four fits: r1 at 5 and 15
epochs, and r1ʀ at 5 and 15 epochs. The census files are the ones the relay verdict used.

Model F: excess ~ 1 + ι4_r1 + ι4_r1R + 1[ι4_r1 > 0] + short_r1 + short_r1R + H_kind + log2mass. Here short_x is
ι1_x − ι4_x, and H_kind and log2mass are the class's exact KIND entropy and law mass. The pair shares both, by
construction. The indicator models the jump at zero long-range information that the diagnosis found. The
standard errors are CR1, clustered by r1 class. Also reported: each fit without the indicator.

## Reading (fixed now, from the r1ʀ 5-epoch fit; the 15-epoch fit is reported beside it)

- **H-free** stands out if b(ι4_r1) > 0 with t ≥ 3, b(ι4_r1R) has t < 2, and the r1 control shows the same
  pattern. At r1 this is the expected pattern, so the control fails only if b(ι4_r1R) > 0 with t ≥ 3 there.
- **H-acct** stands out if b(ι4_r1R) > 0 with t ≥ 3 and b(ι4_r1) has t < 2, with the control as above.
- Otherwise the result is **mixed**, and it is reported as such.

Script: `scripts/relay_free_difficulty.py`. Output: `docs/relay-free-difficulty-2026-10-04.json`.
