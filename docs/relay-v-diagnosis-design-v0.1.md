# Why is the relay's gain V-shaped? Diagnosis design v0.1 (2026-10-04)

> **Status: EXPLORATORY, design committed before any of these regressions has been run.** Written by
> the instance of 2026-10-02/04, which owns the project. It follows `docs/relay-intervention-verdict-v0.1.md`:
> the paired gain Δexcess (r1 KIND excess − r1ʀ KIND excess; positive means the relay helped) rises with
> |Δι_kind,4| on both sides, and at 15 epochs the slope on Δι is 0. Nothing here is confirmatory. If a
> candidate stands out, it becomes a separately stamped prediction on new models. **Stop rule: one pass,
> these candidates only.** Any further idea goes in a new note.

## What the relay is

relay_t is the KIND of the most recent earlier record, in the same window, with the same actor as record
t (`docs/relay-intervention-design-v0.1.md` §2). In words: **what this thread did last.** That is
entity-binding history, made explicit as a literal field. It adds no information (the ceiling is
identical class by class), but it is exactly the kind of fact a small transformer has to otherwise
assemble by matching actor names across records.

## Data

The same paired windows and the same per-window Δexcess that `scripts/relay_paired.py` builds: its
frozen `join` is imported unchanged, with all of its gates. Both arms (primary 5 epochs, secondary
15 epochs), n = 84,949 windows each. Per window, from its r1 class k and its r1ʀ class kR:
- ι4_r1 = ι_kind,4(k) and ι4_r1R = ι_kind,4(kR), from the committed per-class caches
  (`~/.cache/yupi-scratch/implicit/c1prime-loop-40-8-2-{r1,r1R}-eps1-k7-kind-m123456.jsonl`), with
  sha256 recorded. By construction Δι = ι4_r1 − ι4_r1R. The script checks this against the Δι table
  (exact to float tolerance) and refuses to run if it fails.
- n_relay = the number of non-NONE relay values among the 7 prefix records, read from kR.
- log2 class mass, from the r1 k = 7 table. It is identical across the pair.

## Candidates (fixed now)

- **A, distance** (the prereg's reading, kept as the reference): Δexcess = a + β(ι4_r1 − ι4_r1R).
  In the unconstrained two-term model it predicts **b_r1 > 0, b_r1R < 0, b_r1 ≈ −b_r1R.**
- **B, long-range structure**: an explicit binding field helps most in classes that have much
  long-range structure at *either* rung, whichever way the relay moves it. It predicts
  **b_r1 > 0 and b_r1R > 0.** The V would then be an artefact: both tails of Δι are classes with a
  large ι at one rung or the other.
- **C, explicitness**: the gain scales with how much binding content the relay makes explicit in the
  prefix, whatever the exact information accounting says. It predicts **c(n_relay) > 0, and when
  n_relay is added the ι terms weaken.**

## Models (OLS; standard errors cluster-robust by r1 class, CR1, because every regressor is class-level)

- M1: Δexcess ~ 1 + ι4_r1 + ι4_r1R + log2mass
- M2: Δexcess ~ 1 + n_relay + log2mass
- M3: Δexcess ~ 1 + ι4_r1 + ι4_r1R + n_relay + log2mass

Also reported, descriptively: the Δι⁺/Δι⁻ split (Δexcess ~ 1 + max(Δι, 0) + max(−Δι, 0)), the
correlation between ι4_r1 and ι4_r1R, the variance inflation factors in M3, and, for each model, the
predicted mean on the exact-zero set against its observed mean (R2's 13-se gap: does any model close it?).

## Reading (fixed now)

The reading uses the primary arm. The secondary arm is reported beside it and must agree in sign for a
candidate to "stand out".
- **A** stands out if in M1 b_r1 > 0 and b_r1R < 0, each |t| ≥ 3, and |b_r1 + b_r1R| has |t| < 2.
- **B** stands out if in M1 and M3 b_r1 > 0 and b_r1R > 0, each with t ≥ 3.
- **C** stands out if in M2 and M3 c > 0 with t ≥ 3, and in M3 neither ι term has |t| ≥ 3.
- Otherwise, or if two candidates both stand out: **mixed**. It is reported, and no confirmatory test is
  written from it.

Script: `scripts/relay_v_diagnosis.py`, committed with this note before it is run. Output:
`docs/relay-v-diagnosis-2026-10-04.json`.
