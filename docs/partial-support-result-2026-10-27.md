# What the observer's world knowledge is worth: result (2026-10-27)

> Declared in `partial-support-declared-2026-10-27.md` (stamped bfb76dd before running). Script
> `scripts/partial_support.py`; numbers in `partial-support-2026-10-27.json`. 22 learners; median AUC(S3), the
> entropy profile, is 0.940.

| fraction of law groups known | mass mode: median AUC(M2) (mass covered) | random mode: median AUC(M2) (mass covered) |
|---|---|---|
| 1.0 | 0.999 (100 %) | 0.999 (100 %) |
| 0.5 | 0.998 (93 %) | 0.948 (50 %) |
| 0.25 | 0.998 (77 %) | 0.928 (25 %) |
| 0.1 | 0.998 (53 %) | 0.968 (9 %) |
| 0.05 | 0.986 (37 %) | 0.886 (5 %) |
| 0.01 | 0.952 (16 %) | 0.926 (0.6 %) |

- **P1 held (22/22).** An observer who knows the most massive tenth of the laws loses almost nothing (0.998). Even
  the top 1 % (16 % of the mass) still beats the entropy profile (0.952 vs 0.940).
- **P2 failed (3/22).** With a random 10 % of the laws, the full-distribution observer still beats the profile in 19
  of 22. **But the random column is a single draw per fraction, and it is not monotone** (0.928 at 25 %, 0.968 at
  10 %), so draw-to-draw noise is large. Four more seeds, a post hoc robustness check, are in the addendum below.
- **The pattern that does not depend on one draw:** random knowledge of *half* the laws already brings the full
  distribution down to near the entropy profile (0.948 vs 0.940). Most of the full distribution's 0.059 advantage is
  knowledge of the *common* laws, not the export alone.

## What it says

- With a little of the right world knowledge (the common cases), exporting the distribution clearly beats exporting
  entropy.
- With arbitrary world knowledge, the distribution is roughly level with a well-shaped entropy profile, which needs no
  world knowledge at all.
- For an LLM auditor, the analogue of "the common laws" is knowing what typical correct answers look like for the kind
  of query. That suggests a concrete design question for monitors: is it the reference distribution an auditor holds,
  more than the richness of the export, that buys certification?

## Addendum: seeds (post hoc, not declared)

Four more random draws (`--seed 1..4`, numbers in `partial-support-seeds-2026-10-27/`), with the mass mode unchanged:

| random fraction | declared seed | seeds 1–4 |
|---|---|---|
| 0.5 | 0.948 | 0.956–0.979 |
| 0.25 | 0.928 | 0.928–0.965 |
| 0.1 | **0.968** | **0.886–0.905** |
| 0.05 | 0.886 | 0.899–0.927 |
| 0.01 | 0.926 | 0.914–0.951 |
| P2 count (random 10 % < S3) | 3 / 22 | 15–16 / 22 |

- **The declared draw was the outlier at 10 %.** Under every other seed, P2's condition holds (15–16 of 22, against
  the declared 12). P2 stays *failed* as declared, and the failure is now understood: it came from one atypical draw,
  not from the world.
- **The robust pattern:** random knowledge of about half the laws keeps the full distribution ahead of the profile
  (0.95–0.98 against 0.94). At a quarter or less it is level with or below the profile, and noisy, because a small
  random subset is dominated by which rare laws it happens to contain.
- **Lesson for declarations:** a random-subset arm needs several seeds *declared*, not one. Next time I declare the
  distribution over seeds, not a single draw.
