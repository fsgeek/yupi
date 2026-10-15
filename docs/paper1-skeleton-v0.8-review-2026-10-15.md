# Skeleton v0.8 review record (2026-10-15)

> Both families: **DRAFT AFTER FIXES**, independently. Owning instance. The shape (instrument → exact results →
> support audit → relay factorial) is accepted by both; the fixes are scoping and one unmeasured premise.

## Converged
- **Pinsker used backwards** (Claude #1, Codex #1). Already corrected in `identifiability-tolerance-check-2026-10-15.md`;
  addressed by measurement in `learner-precision-monitor-check-2026-10-15.md` (declared d027f05, running). Codex adds:
  at ε = ½ the bound reaches ≈ 0.107 (KIND KL up to 0.0329).
- **The U statistic is existential** (Claude #2, Codex #5): local susceptibility to an alternative, not monitor error.
  Codex reproduced all 32 U values and confirms the group-extremes algorithm is exact for the declared statistic.
  Claude's mass-weighted variants and R/G-swap statistics (reproduced by the owner for r1, r3 at ε = 1) are the
  honest summaries; at δ = 0.02 R stays readable, by δ = 0.05 it does not.
- **§4(b) scoping** (Claude #6, Codex #3–#4): "G = 0, H\* > 0" (deterministic classes add a fourth value, H\* = 0);
  15.6–17.2 % pooled over r1–r3 of the position-7 population (law mass 0.85); coin 89–92 % of it; "~1 %" is the
  contrast G/H\* ≥ 0.5 vs positive-entropy G = 0 in floor(H\*/0.05) bins (0.82–1.44 %); the graded-support figures
  (wide-spread share 17–43 % of position-7 mass) are exploratory bin statistics and must be printed with their
  definition. Both: do not turn the narrow contrast into "the question cannot be studied here".
- **§5 relay wording** (Claude #7): add C2's caveats (0.0005-bit margin; any nontrivial slot target; C4 comparable).
  Codex finds the source draft already states the unresolved increment.
- **Withdrawn thesis survives in sources** (Claude #5, Codex #6): `paper1-draft-s5-v0.4.md` §5.5's "a world small enough
  for exact posteriors has few sources of randomness" and `literature-methods-2026-10-15.md`'s positioning must not
  govern the draft.
- **§4(d) is empty and is the contribution** (Claude #8, Codex #8): a worked procedure with estimand, matching
  variables, eligible mass, mechanism composition, admissible posterior family, precision sensitivity. Claude:
  lead with §5.1's withdrawn plateau reading as the error the audit would have caught.

## New, single reviewer
- **Codex #2: exact precision does not determine the split either.** Positive-mass exact collisions exist (≤ 0.046 %
  of covered mass); a reachable one on r3, ε = 1: 24 classes with P\*(ACQUIRE) = P\*(IO_COMPLETE) = P\*(RELEASE) = ⅓
  and splits including (R, G) = (0.918, 0.667) and (1.585, 0). Adopted: "outside rare collision groups (< 0.05 %)";
  this collision replaces the constructed box.
- Claude #4: a monitor confuses classes at separation up to 2δ, not δ; say which model is meant. Adopted.
- Claude #9 / Codex #1: one learner population for KL ranges, named. Adopted.
- Codex #7: all central numbers reproduce (R 0.608521 / 0.544118; G 0.567 → 0.302 / 0.560 → 0.240; 3–5× ratios;
  45/45 are evaluations, not seeds). "One size" to be qualified by the exploratory d = 256 check.
