# Prior-aware kind monitor: result (2026-10-23)

> Owning instance. Scores `prior-aware-monitor-declared-2026-10-23.md` (stamped before any run). Script:
> `scripts/prior_aware_monitor.py`. Raw: `prior-aware-monitor-40-8-2-k7-2026-10-23.json`. τ was fitted on each model's
> val split (0.027–0.041) and scored on test. (The first val capture saved nothing because of a filename bug; the
> re-run was verified on 200 windows before the full capture.)

## Numbers (τ × 1; headline population pure or withheld)

| cell | coverage | balanced acc., covered | balanced acc., abstain = error | pure recall | withheld recall |
|---|---|---|---|---|---|
| r1, ε = 1 | 0.935–0.939 | 0.993–0.994 | 0.908–0.920 | 0.987–0.989 | 0.998–0.999 |
| r1, ε = ½ | 0.933–0.937 | 0.989–0.992 | 0.920–0.924 | 0.980–0.985 | 0.998–0.999 |
| r3, ε = 1 | 0.902–0.914 | 0.992–0.994 | 0.871–0.886 | 0.985–0.989 | 0.998 |
| r3, ε = ½ | 0.843–0.846 | 0.983–0.987 | 0.832–0.833 | 0.970–0.976 | 0.997–0.998 |

**Sensitivity:** at τ × ½, coverage is 0.883–0.962 and covered balanced accuracy 0.982–0.993. At τ × 2, coverage is
0.804–0.911 and covered balanced accuracy 0.982–0.994.

## Predictions

- **A1** (covered balanced accuracy ≥ 0.90 and coverage ≥ 0.80 in ≥ 10 of 12): **holds, 12 of 12.**
- **A2** (pure recall ≥ 0.85 in ≥ 10 of 12): **holds, 12 of 12.**
- **A3** (conservative balanced accuracy above the post hoc mass-blind monitor's in ≥ 10 of 12): **holds, 10 of 12.**
  The exceptions are r3 ε = 1 seed 3 (0.871 vs 0.897) and r3 ε = ½ seed 3 (0.832 vs 0.873).

## Reading

- **A prior-aware observer reads the kind of uncertainty from these learners' single outputs.** Covered balanced
  accuracy is 0.983–0.994, with 84–94 % coverage, at every interface, ε and seed.
- The earlier "cannot certify pure randomness" (declared monitor) and the moderate asymmetry (post hoc monitor) both
  came from ignoring the prior. Near the dominant coin sit many withheld-state laws that are vanishingly rare. A
  mass-blind observer treats each as a live alternative. A Bayes observer does not.
- The mass-weighted look-alike statistic of v3 §4.3, which read "readable", was closer to right than either mass-blind
  monitor.

## How this fits the other results (2026-10-22 to 10-23)

Certifying "this uncertainty is randomness, not hidden state" at these learners' precision needs one of two things:
- **a prior over the alternatives:** single outputs suffice, as this monitor shows;
- **a richer query:** without a prior, the exact two-step margin is about 0.12, against 0.015 at one step
  (`two-step-margin-result-2026-10-23.md`).

Without either, a single output cannot certify it against every rare alternative. Observing more fields of each record
does not help: it adds rare alternatives faster than it removes heavy ones (`certification-margin-interfaces-result`,
with its correction).

This is still one world, and the learner-side two-step test (at k = 6) has not been run.
