# Implicit information at (40, 8, 2), k = 7: first results (v0.1, 2026-09-28)

> **Status: EXPLORATORY.** This is readiness items 1 and 3 of `docs/paper1-skeleton-v0.1.md`
> (decision D1). The definitions are in `docs/implicit-information-design-v0.1.md`.
> Written by the instance of 2026-09-28. The computation was interrupted once by a host
> crash (see the c527c0e commit message). Every raw below was produced after recovery,
> and all exact-side gates pass (identity ≤ 3e-14; record-target cross-check against the
> committed ceiling raw ≤ 1.5e-13).

## 1. The exact side: the lag profiles cross

ι_m is the law-mass mean of KL(P*(·|prefix) ‖ P*(·|last m records)). It is the exact
information about the next record that lies more than m records back. Values for the
next KIND (the naming-free common target) at ε = 1, from
`implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`:

| m | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| 1 | 0.535 | 0.712 | 0.756 | **0.800** | 0.800 |
| 2 | 0.384 | 0.525 | 0.569 | **0.578** | 0.578 |
| 3 | 0.257 | 0.379 | 0.420 | **0.424** | 0.424 |
| 4 | 0.176 | 0.257 | **0.282** | 0.259 | 0.259 |
| 5 | 0.107 | 0.168 | **0.184** | 0.172 | 0.172 |
| 6 | 0.061 | 0.080 | **0.086** | 0.078 | 0.078 |

The whole-record target (`implicit-info-lag-record-…json`) and ε = ½ show the same
crossing. On the KIND target at ε = ½, r3 drops below r1 from m = 4.

1. **A richer interface relocates predictive information from far to near.** At short
   lag, r3 carries the most history information about the next KIND. From m = 4, r2
   carries the most, and r3 falls to r1's level or below. Printing the owner at r3
   (RELATED) turns information that r2 must carry across four or more records into
   information in the last few.
2. **The lineage field is invisible to this quantity.** r3 and r4 agree to 1e-4 at every
   m, as the ceilings do (learner note, correction C1).
3. **The order-1 KIND observer is rung-independent** (H_1 = 1.711 at ε = 1 for every
   rung). One renamed record carries only its kind, so short-lag ι mostly re-expresses
   the ceiling.

The cell-level ordering at long lag, r1 ≈ r3 < r2, matches the learner's KIND excess
ordering (three-seed means at ε = 1, from the census raws: r1 0.021, r2 0.029, r3 0.019).
That is four cells and one ordering. **It is suggestive, not a test.**

## 2. The learner side: within-cell tests

**Per window, m ≤ 2** (`implicit-info-join-k7-2026-09-28.json`, 15 census runs, the
class-id gate held). Spearman ρ of the realized excess with ι_1 is 0.01–0.12, no better
than with the class's entropy H*. Per-window realized excess is dominated by sampling
noise, and m ≤ 2 is the wrong lag (§1.3).

**Per class, long lag** (`implicit-info-lagjoin-k7-2026-09-28.json`). This is a WLS of
the class-mean KIND excess on ι_kind,4, the short part (ι_kind,1 − ι_kind,4), and
H_kind, over classes with at least 30 windows:
- β_long is within |t| ≤ 1.2 in 13 of 15 runs. H_kind is the steadier predictor (t 1.5–3.1
  in r1 and r2).
- **The exceptions are r4 seeds 2 and 5**, the high-excess basin of §14/§15: β_long
  +0.057 (t 2.5) and +0.057 (t 2.8). There, the extra loss sits where the long-range
  information is. This is consistent with §21.2 (poor seeds form the belief late).
- **Caveat that governs the reading:** classes with at least 30 windows cover only
  **5–9 % of windows**, and they are the frequent, short-memory ones. The long-lag tail
  lives in rare classes that this test cannot see. The within-cell null is therefore
  underpowered exactly where D1 lives.

## 3. What this changes

- The **exact-side finding (§1)** is a candidate for paper 1's §3 as it stands. It is
  exact, gated, and it teaches something the ceiling ladder alone hides: interfaces
  differ in *when* information is available, not only in *how much*.
- D1 is **not yet tested properly**. The test that can see the long-lag tail pools rare
  classes by their ι_4 value rather than by class identity (bins of ι_4, law-mass
  weighted, prefix-only), or uses a larger test split. The next step is that binned
  version, before any confirmatory prediction is stamped.
- Seeds 2–3 at 15 epochs and d = 256 at 45 epochs are running (the size follow-up). The
  converged ladder re-run (readiness item 5) will carry the D1 prediction if the binned
  test supports it.
