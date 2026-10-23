# Operational kind monitor: result (2026-10-22)

> Owning instance. Scores `kind-classifier-declared-2026-10-22.md` (stamped at 7f4fc98 before any run). Script:
> `scripts/learner_kind_classifier.py`. Raw: `kind-classifier-40-8-2-k7-2026-10-22.json` (12 models, 84,949–85,105
> windows each, 0 unmatched class keys). Headline margin m = 0.005.

## Numbers (headline population: windows whose class is pure or withheld)

| cell | coverage | balanced acc., covered | balanced acc., abstain = error | pure recall, covered | withheld recall, covered | plain acc., covered | prior-only plain acc. |
|---|---|---|---|---|---|---|---|
| r1, ε = 1 | 0.80–0.83 | 0.704 / 0.856 / 0.895 | 0.51–0.59 | 0.41–0.79 | 1.000 | 0.98–0.99 | 0.79 |
| r3, ε = 1 | 0.77–0.82 | 0.92 / 0.82 / 0.93 | 0.54–0.64 | 0.63–0.86 | 1.000 | 0.98 | 0.74 |
| r1, ε = ½ | 0.76 | 0.77 / 0.81 / 0.73 | 0.51–0.52 | 0.46–0.61 | 0.999–1.000 | 0.985–0.988 | 0.76 |
| r3, ε = ½ | 0.70–0.71 | 0.70 / 0.63 / 0.58 | 0.49–0.51 | 0.17–0.40 | 1.000 | 0.965–0.973 | 0.70 |

*Balanced accuracy, covered, is listed for seeds 1 / 2 / 3. Other columns give ranges over seeds. The prior-only
baseline always says "withheld" (the majority in every cell); its balanced accuracy is 0.5 by construction.*

**Oracle-q** (the same monitor fed the true exact law): coverage 0.977–1.000 and covered balanced accuracy 1.000 in every
model.

## Predictions

| | declared | observed | verdict |
|---|---|---|---|
| K1 | oracle-q coverage ≥ 0.97, covered balanced accuracy ≥ 0.99 | 0.977–1.000; 1.000 | **holds** |
| K2 | every model: covered balanced accuracy ≥ 0.90 and coverage ≥ 0.80 | 2 of 12 models meet both | **fails** |
| K3 | cell ordering of conservative balanced accuracy is the reverse of mean look-alike other-kind mass | look-alike order r1ε1 (0.00704) < r3ε1 (0.00718) < r1ε½ (0.00924) < r3ε½ (0.01379); monitor order r3ε1 (0.602) > r1ε1 (0.560) > r1ε½ (0.512) > r3ε½ (0.497) | **fails** strictly: the top two swap, and their look-alike values differ by 0.00014; the lower two agree |

## Declared reading

- **r3, ε = ½: not operationally readable.** Covered balanced accuracy is below 0.75 in all three seeds.
- **r1 ε = 1, r3 ε = 1, r1 ε = ½: between.** Numbers only.
- **No cell is operationally readable.**

The look-alike rule called the kind readable in every cell. The two disagree, so, as declared, v4 drops the name
"readable" from the look-alike rule.

## What the confusion shows (read from the raw, not inferred)

- **Withheld-state windows are recognised almost perfectly.** Recall is at least 0.999 on covered windows; 1–29
  windows per model (of 36,208–45,271) are called pure.
- **Pure-randomness windows are mostly abstained on, not misclassified.** Even at m = 0, 63–90 % of pure windows are
  abstained on (8,570–14,078 per model; 9,476 of 14,208 in the best model, r3 ε = 1 seed 1). At m = 0 the monitor abstains only when the nearest exact law's
  kind is deterministic or none (0 < G < 0.1 bits), or on an exact distance tie with the other kind. So most
  pure-randomness outputs lie nearest to laws that carry a *small* amount of withheld state.
- §4.3's look-alike statistic scored those no-kind neighbours as zero: it counted only look-alikes of the opposite kind.
  By construction it could not register this failure: no-kind neighbours entered its denominator, never its numerator.
- **Plain accuracy on covered windows is 0.965–0.988, against 0.70–0.79 for always saying "withheld".** This is the
  reviewer's warning made concrete: accuracy alone would have reported success.
- **The margin sweep:** at m = 0.02, covered pure recall falls to 0.000–0.307 (median
  below 0.01). Pure laws have withheld laws within about
  0.02, consistent with the exact sweep's onset.

## What this means for v4

- The sentence "the kind meets a pre-declared readability rule in every cell" goes. In its place:
  - an observer that sees only the model's output and knows the kernel family identifies withheld state reliably;
  - it cannot identify pure randomness at these models' precision: it abstains on most such windows, because the
    model's output lies nearest to laws with a little withheld state;
  - balanced accuracy, counting abstentions as errors, is 0.49–0.64, against 0.5 for the prior.
- This narrows the paper. The kind *is* recoverable from exact laws (oracle-q is perfect). It is not, operationally,
  from these learners' outputs. The gap between the two is the learners' imprecision, measured at about the distance
  that separates pure laws from small-withheld laws.
- §4.3's look-alike numbers stay as reported, and v4 states what they count and what they do not (no-kind neighbours).
