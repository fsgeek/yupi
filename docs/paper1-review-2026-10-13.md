# Two-family review of the paper 1 drafts (2026-10-13): record and dispositions

> Reviewed: skeleton v0.5 (corrected centre), §2 v0.1, §3 v0.1, §4 v0.1. Read-only adversarial reviews by a Claude
> subagent and by Codex (GPT), run independently in parallel. Their full texts are in this session's transcript,
> summarised here. Owner's rule: adopt only after checking. A number the owner reproduced is marked **R**; one
> adopted on the reviewer's computation and not reproduced is marked **(rev.)**. Results: §3 v0.2, §4 v0.2, §2
> v0.2 (in place), §1/§6 v0.2 (in place), skeleton v0.6, inventory §I, and the loss-masked relay pre-registration.

## Blocking

| # | finding | by | disposition |
|---|---|---|---|
| B1 | The relay's "9/9 pairings" is 3 vs 3 complete separation (exact p = 1/20), computed post hoc on the secondary arm. The relay value is also a training target, so auxiliary supervision is a third rival mechanism | Claude (1), Codex (7) | **Adopted.** Seed means **R**; that the loss scores every position **R** (`data.py`, `train.py:168`). Reworded in §4e and v0.6. The loss-masked arm was pre-registered and launched (`relay-lossmask-prereg-v0.1.md`) |
| B2 | Inconsistent status labels for the relay | Claude (2) | **Adopted:** EXPLORATORY throughout |
| B3 | B5′ "proportionally more" compares coefficient magnitudes across budgets, which the drafts disallow, with non-clustered se | Claude (3), Codex (12) | **Adopted:** only "does not remove it" stays confirmatory, the failed clause is reported, and "own index" is cut. The per-model 21/24 is not used **(rev.)** |
| B4 | Causal distance language survives in skeleton §1 framing and in §3 ("a difference in where the information sits") | Claude (4), Codex (1) | **Adopted:** v0.6 calls producer/consumer locality motivation; §3.3 rewritten |
| B5 | Structural-ID injectivity was transferred to the pattern observer, which keeps binding uncertainty from reset | Codex (2) | **Adopted.** The reasoning was checked by the owner: renaming removes identity. §2.3 and §3.1 are scoped. The 4-state example is **(rev.)** |
| B6 | The ceiling includes future randomness; it is a Bayes predictive loss, not an observation gap or a state-identifiability measure | Codex (3) | **Adopted.** It matches Part I's own decomposition. §2.1 and §3 intro rewritten |

## Should-fix

| # | finding | by | disposition |
|---|---|---|---|
| S1 | The "plateau" exists only after controls, because the H control extrapolates off the ι_4 = 0 support; raw bins rise steadily | Claude (5) | **Adopted** in §4a. Raw bins are **(rev.)**, and reproducing them is owed (v0.6 item 3) |
| S2 | §3.4 reads Δι_4 as "the profile", and the r1 ε = 1 inversion is omitted | Claude (6), Codex (13) | **Adopted.** Inversion **R** from the c3c4 raw; profile sums **R** |
| S3 | "Full-profile reading favours distance" has no committed source; its coefficients alternate in sign; Δι_2 +0.023 does not reproduce | Claude (7), Codex (10) | **Adopted: withdrawn.** Inventory §I |
| S4 | The zero set: on it, near-lag moves buy nothing | Claude (8) | **Noted**, not used. Owner has not reproduced it |
| S5 | The r0 "tenth" breaks the no-magnitude rule and is not resolved per seed | Claude (9) | **Adopted:** scope is r1–r4, r0 is "not resolved", and the identity-carrying claim is cut |
| S6 | Someya et al. is not cited at ι's definition; ι = H_m − H\* is their m-local entropy less the ceiling; their exactness is understated | Claude (10), Codex (5) | **Adopted** in §3.2, §1 and v0.6 |
| S7 | Producer/consumer framing; the relay is a familiar back-reference pattern and a consumer-window transformation | Claude (11), Codex (6) | **Adopted** as motivation. Citations owed (v0.6 item 4) |
| S8 | The §2.4 slot rule is too broad | Claude (12) | **Adopted** |
| S9 | Gate letters do not match the raws | Claude (13) | **Adopted** |
| S10 | Seed inventory is wrong; "held-out" is only partly true | Claude (14), Codex (16) | **Adopted**, checked against the d1 prereg |
| S11 | Class clustering is a weak check; a stronger FE/coarse-cluster run kept t ≥ 3.8 on r1 ε = 1 | Claude (15) | **Adopted** as owed across cells. The 3.8 is **(rev.)** |
| S12 | The withdrawn step returns as a mechanism argument in §4d | Codex (4) | **Adopted:** the mechanism argument is cut |
| S13 | Near-zero gain and an unresolved slope were stated as "zero" | Codex (8) | **Adopted:** slope and se quoted from the raw |
| S14 | Regional means were generalised pointwise (about half the mass has a negative summed change) | Codex (9) | **Adopted.** The half is **(rev.)** |
| S15 | β_short "resolved" rests on pooled HC1 | Codex (11) | **Adopted:** descriptive in v0.2 |
| S16 | §3's gate tolerances are overstated | Codex (14) | **Adopted** |
| S17 | "The arms we ran" overstates the three-arm status | Codex (15) | Already fixed in §5 v0.1. §4e says it is shelved |

## Minor

All adopted, from Claude (16)–(21) and Codex (17)–(19):
- §4d wording on r0 and "every class";
- the reserved name slices (**R**, `vocab.py:18`);
- the injectivity note's scope and review status;
- the `programs.py` docstring (still to do);
- stale §3 cross-references;
- the "different classes" wording (sign agreement 65 % **R** from the raw);
- the warmup;
- the r4 − r3 target (KIND gain 9e-6 **R**);
- the per-seed relay-field excess (**R**: 0.000278, 0.000153, 0.000088);
- the clustering se ratio range (**R**: 0.981–1.126 converged, 1.028–1.186 held-out).

## What both reviewers verified as correct

- Every §3 ceiling and lag value, and the ε = ½ crossing.
- Δι_4 0.0936 and 0.0678, the correlation 0.290, and the sign fractions.
- The 0.85 coverage and the parameter count.
- The d1 and actor scorecards, the clustered-refit minima, and the count ratios 1.33–5.22.
- The relay 15-epoch gains and contrasts, and the §3.4 absolute losses.
- No subset is selected on a realized field.

## Verdicts, in short

**Claude:** centre paper 1 as an observation-design measurement paper. §3 is the result, the learners are a
measured case, the relay is an exploratory pilot motivating a loss-masked, fixed-model follow-up, and the
producer/consumer framing is kept only as pricing a known denormalization pattern.

**Codex:** "There is a defensible paper here as an exact observation-design instrument with a measured learner
case… Resolve the blocking observer and measurement distinctions before external review."

The owner agrees with both, and skeleton v0.6 is written to them. Neither reviewer endorsed the framing
uncritically. Both rejected parts of it, which is the test this review was meant to pass.
