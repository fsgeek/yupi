# What an entropy-only observer can see: declared before computing (2026-10-27)

> Steward from 2026-10-27, first declaration. Arm A0 of the escape-hatch direction: Mason & Anand's tensor interface
> exports per-token entropy, and its evaluation (ai-honesty exp27) had no knowable query with many correct answers.
> In the exact world, how much of the randomness-vs-hidden-state distinction survives when the observer sees only the
> entropy of the next-KIND law, rather than the law itself? No learner is involved: these are ceilings.

## Population

- Rows: `~/.cache/yupi-scratch/two-step-2026-10-23/k6/c1prime-loop-40-8-2-{r0..r4}-eps{1,1_2}-k6.jsonl` (10 cells).
  Each row is a window class with `mass`, `h_star` (= r + g), `g`, `p_star` (next KIND) and `p2` (next two KINDs).
- RESET-class masses are halved (keys starting `(True,`), as in `scripts/learner_two_step_score.py:family`.
- Labels: **pure** (g = 0, h_star > 0) and **withheld** (g ≥ 0.1). Deterministic classes and classes with
  0 < g < 0.1 are excluded.
- Depth: one step uses H(p_star) and the law p_star. Two steps use the joint entropy H(p2) and the law p2.

## Measures (per cell, per depth)

- **AUC_H:** mass-weighted AUC of entropy for withheld against pure (ties count ½). It is the best a threshold on
  entropy can rank.
- **BA_H:** Bayes-optimal balanced accuracy from entropy alone. Group classes by entropy (to 1e-9). Assign each
  group to the label with the larger label-normalised mass.
- **BA_P:** the same, with classes grouped by the full law. It is the full-distribution ceiling.

## Predictions

- **E1.** AUC_H > 0.5 at one step in all 10 cells. Hidden state adds entropy on average.
- **E2.** The median one-step AUC_H across cells is ≤ 0.85. Entropy mixes randomness with hidden state.
- **E3.** BA_P − BA_H ≥ 0.10 at one step in at least 7 of 10 cells. The law carries substantially more than its
  entropy.
- **E4.** From one step to two, BA_P gains more than BA_H in at least 7 of 10 cells. A second question helps an
  observer who sees the distribution more than one who sees only its entropy.

## What each outcome points to

- If E2 and E3 hold, an entropy-only monitor confuses rich randomness with hidden state even with perfect
  precision. The real-model test (Arm B) then predicts that determined-but-open queries are flagged as unknowable.
- If E2 fails (entropy separates well), Yupana's randomness is too uniform across windows to stand in for the "name a
  fruit" case. That would be a fact about the garden, not a vindication of entropy, and Arm B carries the question.
- If E1 fails in some cell, hidden state *lowers* entropy there. That would be worth understanding before Arm B.
