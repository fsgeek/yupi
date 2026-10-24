# Learner-side two-step test: result (2026-10-23)

> Owning instance. Scores `learner-two-step-declared-2026-10-23.md` (settings frozen and predictions stamped at 71152a2,
> before test). Scripts: `scripts/learner_two_step.py` (enumerator), `scripts/learner_two_step_score.py`. Raw:
> `learner-two-step-40-8-2-k6-2026-10-23.json`. 10,000 eligible test windows per model, 0 unmatched class keys. Pure /
> withheld denominators per model: r1 ε = 1, 1,056 / 4,631; r1 ε = ½, 982 / 4,526; r3 ε = 1, 1,366 / 4,045;
> r3 ε = ½, 1,265 / 3,974.
>
> **Run note.** In the 12-wide test run, r3 ε = ½ seed 3 was killed by its 4 GB memory cap (journal: OOM kill inside
> its scope; nothing else was affected). It was re-run alone under 12 GB, peaking at 3.1 GB (one window had 13,409
> leaves), with the same frozen settings and seed. The other eleven ran once.

## Per seed (1 / 2 / 3)

| cell | sufficient share of pure windows, one → two steps | mass-blind, conservative balanced | prior-aware, conservative balanced |
|---|---|---|---|
| r1, ε = 1 | 0.318 / 0.753 / 0.797 → 0.749 / 0.854 / 0.877 | 0.907 / 0.957 / 0.976 → 0.974 / 0.983 / 0.983 | 0.921 / 0.935 / 0.935 → 0.917 / 0.923 / 0.926 |
| r1, ε = ½ | 0.443 / 0.502 / 0.288 → 0.778 / 0.793 / 0.731 | 0.887 / 0.911 / 0.809 → 0.978 / 0.971 / 0.983 | 0.960 / 0.961 / 0.956 → 0.942 / 0.945 / 0.938 |
| r3, ε = 1 | 0.815 / 0.773 / 0.754 → 0.811 / 0.772 / 0.766 | 0.942 / 0.941 / 0.938 → 0.945 / 0.928 / 0.934 | 0.925 / 0.921 / 0.924 → 0.898 / 0.880 / 0.879 |
| r3, ε = ½ | 0.364 / 0.047 / 0.185 → 0.630 / 0.461 / 0.604 | 0.862 / 0.646 / 0.861 → 0.940 / 0.914 / 0.926 | 0.865 / 0.862 / 0.871 → 0.856 / 0.849 / 0.858 |

The two-step mass-blind monitor's coverage is 0.962–0.995, and its covered balanced accuracy is 0.939–0.997.

## Predictions

- **L1 fails at one seed of r3 ε = 1.** It holds for every seed of r1 ε = 1, r1 ε = ½ and r3 ε = ½. At r3 ε = 1 the
  sufficient share was declared to *fall*. It fell at seeds 1 and 2 (by 0.004 and 0.001) and rose at seed 3 (by
  0.012). At r3 ε = 1 the second step neither helps nor hurts the sufficient condition (|Δ| ≤ 0.012). It does not
  lower it as predicted.
- **L2 holds,** 6 of 6 seeds in the two ε = ½ cells. Mass-blind conservative balanced accuracy goes from
  0.809–0.911 to 0.971–0.983 at r1, and from 0.646–0.862 to 0.914–0.940 at r3.
- **L3 holds in three cells and fails at r3 ε = 1.** The prior-aware monitor at two steps is within 0.018 of one step
  at r1 ε = 1, r1 ε = ½ and r3 ε = ½. At r3 ε = 1 it is *worse*, by 0.027–0.045.
- **L4 holds,** 12 of 12. The test/val ratio of the median two-step error is 0.964–1.053.

## Reading

- **Asking more substitutes for a prior, for these learners.** With two steps, a monitor that knows the kernel family
  but uses no prior reaches conservative balanced accuracy of 0.914–0.983 in every cell and seed. With one step, the
  prior-aware monitor reached 0.862–0.961. Without a prior, one step reached 0.646–0.976. The gain is largest exactly
  where the one-step margin is narrow (ε = ½).
- **Where one step already had room (r3 ε = 1), the second step buys nothing,** and it costs the prior-aware observer
  0.03–0.045. This is the cost the error-compounding account predicted for that cell. It appears in the prior-aware
  monitor, not in the sufficient condition, where it was declared. So the account is supported in direction but
  misplaced in where it shows: L1 fails and L3 fails, both at the same cell.
- **Scope** (per design v2 §4): this monitor, on this population, in this world, with the labels defined by the
  one-step split at k = 6. A success here does not certify two-step uncertainty as pure. It separates one-step-pure
  classes from one-step-substantially-withheld ones.
