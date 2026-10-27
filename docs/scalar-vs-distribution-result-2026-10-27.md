# The escape hatch's scalar against the full distribution: result (2026-10-27)

> Declared in `scalar-vs-distribution-declared-2026-10-27.md` (stamped 68d6a38 before running). Script
> `scripts/scalar_vs_distribution.py`; per-learner numbers in `scalar-vs-distribution-2026-10-27.json`.

**C1 and C2 held in 22 of 22 learners.**

| | range over 22 learners | median gap |
|---|---|---|
| M1 (one step, full distribution) vs S1 (one-step entropy) | 0.973–1.000 vs 0.848–0.922 | +0.092 |
| M2 (two steps, full distribution) vs S3 (entropy profile) | 0.976–1.000 vs 0.907–0.948 | +0.059 |

A second question shrinks the scalar's cost by about a third, from 0.092 to 0.059 in AUC, provided the scalar is
exported as a per-step profile and not summed.

## The comparison is not between equals

M is computed against the world's full set of exact laws. The observer knows every pure and withheld law and needs
only the learner's output to place it. The entropy observers know nothing about the world, only that "higher first,
lower next" points to hidden state. The gap above therefore mixes two things: what the export carries (a distribution
against a scalar) and what the observer knows (the support of the world's laws against nothing). This is the
support-known caveat raised at succession. It now has a number attached, but the number cannot yet be split into its
two parts.

## What it points to

The partial-support arm. Give the M observer only a fraction of the laws (random, or the most massive ones) and trace
AUC(M) from support-known down toward support-free. The point where M falls to the entropy profile's level is the
price of the observer's world knowledge, in this world. It is also the analogue of the gap a real LLM auditor faces:
it never has the support.
