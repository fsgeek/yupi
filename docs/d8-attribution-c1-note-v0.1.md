# D8 order-mode attribution — C1 reading note v0.1

> **Status (2026-08-28 12:06 PDT): measured under preregistration
> `d8-attribution-prereg-v0.1.md` (commit a39f555) and grid freeze
> `d8-attribution-grid-freeze-c1-v0.2.md` (commit d46a6b9, stamped b9a5bc4;
> blind by cost, 716 of 1344 cells admitted). Artifact:
> `d8-attribution-c1-2026-08-27.json` (716 cells; raw append-only JSONL
> alongside). Predictions scored by `scripts/check_predictions.py` on
> `d8-attribution-predictions-v0.1.json`. Truthsayer pass owed.
> Canonical-naming track (Part II v0.2.6 Clause 2′). The extension grid
> v0.3 (`d4-budget-freeze-v0.1.md` E2; rule 3600 s / 4 GB) is NOT priced or
> measured yet; nothing here is a v0.3 number.**

## 0. Headline, stated first

**In C1 the order channel's loss is the scheduler cursor at ε = ½, and at
ε = 1 it is almost nothing with full context and large under truncation.**
The allocator mechanism that was C0b's *entire* loss is absent from every
admitted full-context C1 cell — as the pre-measurement census said it would
be (`d8-bucket-census-c1-2026-08-27.json`: at ε = 1 the allocator bucket first
exists at ticks 10–12, and every full-context cell containing it is refused
under v0.2). What full context leaves at ε = 1 is one thing: at (9, 9, 3)
the lock wait-queue costs **exactly 1/108 bits** (Δ_an = Δ_un = 0.009259…,
prevalence exactly 1/108, max per-observation gain exactly 1.0 — one bit
lost on one observation class), attributed 100 % to WQ with envelope width
0, and **identical at r1, r2, r3 and r4**: lineage does not remove it, unlike
C0b's allocator loss, which r4 removed exactly. Every other ε = 1
full-context cell with B ≥ 2 (16 of 20) is exactly zero. At ε = ½ every
B ≥ 2 cell is informative and none is collapsed: full-context Δ_an from 0.116
to 0.280 bits, κ (round-robin cursor) share 1.000 by chain and by Shapley at
every full-context B = 2 cell with envelope width exactly 0, and 0.988 by
Shapley at (9, 9, 3) with envelope 0.007; equal at r1–r4 everywhere with full
context, because no rung exposes the cursor. Under truncation C1 is a
different world at both ε: Δ_an up to 0.287 bits at ε = 1 (14, 2, 2) and
0.391 at ε = ½ (12, 3, 3); the coordinates are **redundant, not separable**
(envelope widths up to 0.11 at ε = 1, 0.21 at ε = ½); the offset term
I(U; O_ord | O_shuf) is positive in 94 of 134 truncated B ≥ 2 cells, up to
0.223 bits; and the rungs finally differ — 27 laws where r1, r2, r3 are not
identical and 26 where r4 < r1, all truncated. One scorable C1 prediction
(P3a) passed 6/6; the other (P3b) has no admitted cell.

## 1. Gates (prereg §5) — all passed, uncapped

Two-path on **every** distinct observation of both channels: 15,888,849
shuffled observations and 10,134,321 ordered windows across the 716 cells,
posterior and law mass bit-for-bit (recursive filter vs. aggregated path
table under a literal permutation count). Gate F bijection on 642,762
distinct (U, S_T). Full-coordinate identity, nonnegativity, chain-sum,
Shapley-sum and envelope-containment identities in every cell (the most
negative chain term anywhere is −2.2e−16). **Z1** (κ ≡ 0 at ε = 1): exact 0
under every prefix in all 369 ε = 1 cells; not applicable at ε = ½ (347
cells, flag recorded False, i.e. not gated). **Z2** (WQ ≡ 0) is a C0b gate
and does not apply — WQ is live in C1. **Z3**: all 542 B = 1 cells have every
loss exactly 0.0. Gate 6 by construction + suite witness. Cost: max support
739 states, max frontier 3,572; 20.68 CPU-hours of cell wall; the B = 3 run
took 1 h 32 min (Aug 27 07:33–09:05 PDT) and the remaining 667 cells 2 h 15
min (Aug 28 09:47–12:02 PDT), 24 workers each. The measured/projected wall
ratio on the B = 3 cells over 60 s was median 1.01, max 1.47.

## 2. Predictions (prereg §6), scored as written

| | as written | verdict | reading |
|---|---|---|---|
| P3a | Δ_an = 0 at C1 ε = 1, B = 2, r1–r3, T_ep ≤ 8, L = T_ep | **PASS** 6/6 | exactly 0 at (6,6,2) and (8,8,2); also exactly 0 at (10,10,2), outside the prediction |
| P3b | Δ_an > 0 at C1 ε = 1, B = 2, r1–r3, (12, 12, 2) | **NO_CHECK** | cell refused under v0.2 (wall + B4′ RSS); reachable under v0.3/E2, not yet measured |
| P4 | — | NO_CHECK (as preregistered) | source condition below the grid |
| P1, P1-mech, P2 | C0b | unchanged (PASS, PASS, FAIL 4/36) | see the C0b note |

P3a's null half passing is consistent with the census (no order-sensitive
bucket of any kind at C1 ε = 1, B = 2, H ≤ 10 from reset) and is therefore
not surprising; it is recorded as a pass, not as evidence for the mechanism.
The positive half is the reason E2 was enacted; it is measured under v0.3
or not at all.

## 3. What the channel hides in C1, by cell class

- **B = 1 (542 cells):** exactly nothing — Z3.
- **ε = 1, full context, B ≥ 2 (20 cells):** 16 exactly zero — (6,6,2),
  (8,8,2), (10,10,2), (6,6,3) at all four rungs. The 4 informative cells are
  (9,9,3) r1–r4, each exactly 1/108 bits, 100 % WQ (chain, Shapley, envelope
  all agree; width 0), collapsed under δ = 0.01 by 0.0007. The rung ladder
  does nothing here: the wait-queue order is state that no rung's records
  encode, including lineage.
- **ε = 1, truncated, B ≥ 2 (69 cells):** 57 informative, 53 not collapsed;
  Δ_an from 0.0032 to 0.287 bits, largest at the one-bucket windows
  (14,2,2), (12,2,2), (16,2,2), (10,2,2). The chain story names ρ (the
  status/progress coordinate) first with 0.14–0.18 bits; the order-free
  Shapley values move ~0.05 bits of that into REQ/WQ/DQ, and the envelopes
  say why: at (14,2,2) ρ ranges over [0.175, 0.287], WQ over [0, 0.069], DQ
  over [0, 0.069], REQ over [0.0004, 0.069]. **The coordinates are
  redundant** — whichever the chain asks first takes the shared part — so
  no single-coordinate claim is made for ε = 1 truncated cells; the
  order-independent statement is only that ρ carries ≥ 0.175 bits at
  (14,2,2) and REQ ≥ 0.0004. Per-observation gains exceed 1 bit at the
  single-bucket B = 3 windows (max_g 1.49 at (9,6,3) r1, 1.57 at (12,3,3),
  1.75 at (15,3,3)).
- **ε = ½, full context, B ≥ 2 (20 cells): all informative, none collapsed.**
  B = 2: Δ_an = 0.19333 / 0.14500 / 0.11600 at T_ep = 6 / 8 / 10 with
  prevalence exactly 1/3, 1/4, 1/5 (= 2/T_ep) and Δ_an · T_ep/2 = 0.5800 at
  all three laws to four digits; κ share 1.000 by chain and Shapley, envelope
  width exactly 0. B = 3: 0.22393 at (6,6,3), 0.27975 at (9,9,3); κ share
  1.000 by chain, 0.988 by Shapley at (9,9,3) with the remainder in ρ/DQ
  (envelope width 0.007). r1 = r2 = r3 = r4 to every stored digit at all 20
  cells. The 2/T_ep regularity is reported, not explained; its
  per-endpoint anchored values are equal across endpoints in the artifact,
  which is the pattern the offset-free (full-context) law produces when a
  fixed fraction of each endpoint's observations is order-ambiguous.
- **ε = ½, truncated, B ≥ 2 (65 cells):** all informative, none collapsed;
  Δ_an from 0.116 to 0.391 bits; κ dominant everywhere (chain term
  0.114–0.386), with WQ ≤ 0.0124, DQ ≤ 0.0283, ρ ≤ 0.0217 and REQ ≤ 0.00033
  by chain; envelope widths up to 0.21 at the
  one-bucket B = 2 windows — κ is separable at full context and redundant
  with the rest under truncation.
- **Offset term** I(U; O_ord | O_shuf): positive in 94 cells, all truncated
  (94 of the 134 truncated B ≥ 2 cells), up to 0.223 bits at ε = ½ (16,2,2);
  the 40 truncated cells with an exactly-zero offset term are the same
  five laws at both ε — (6,3,3), (6,4,2), (8,6,2), (9,6,3), (10,8,2), all
  four rungs — every one a window shortened by at most three ticks. (A first
  draft said "all at ε = 1"; the pre-commit check refuted it.) **No cell has Δ_an = 0
  with a positive offset term.**
- **Rungs.** With full context r1 = r2 = r3 = r4 at every law at both ε
  where all four rungs are admitted (0 unequal laws; the one full-context
  law with a partial rung set, (14,14,1), has r4 alone and is a B = 1 zero). Under truncation 27 laws have r1, r2, r3 not identical
  (14 at ε = 1, 13 at ε = ½) and 26 have r4 < r1 (14 / 12); r3 ≠ r4 at 8
  laws, all with T_ep ≥ 12 and L ≤ 4. In C0b the lower rungs never differed
  and only lineage moved the loss; in C1 lineage never moves the
  full-context loss and the lower rungs differ only when the window is cut.

## 4. What this does and does not say

- It says the D8 channel in C1, at the admitted laws, is a **cursor eraser at
  ε = ½** — clean, order-independent, rung-independent — and at ε = 1 with
  full context a near-null that leaves exactly one wait-queue bit on 1/108
  of the mass at (9,9,3). It does not say what C1's allocator mechanism
  costs: no admitted full-context cell contains it (census), and P3b is
  unmeasured. The cross-world comparison the prereg is for — does C0b's
  allocator loss reappear in C1, with what share — is deferred to v0.3.
- It says truncation is where C1's order channel carries information at
  ε = 1, and that there the loss is not a single coordinate. That is a
  measured fact about redundancy, not a failure of attribution; the
  envelopes are the honest report.
- "Collapsed" and "informative" remain different words: 146 of 716 cells are
  informative; 138 are not collapsed (Δ_an); at ε = 1 the gap is 8 cells,
  four of them the 1/108-bit (9,9,3) family.
- The 2/T_ep pattern at ε = ½, B = 2 full context and the exact 1/108 at
  (9,9,3) are exact rationals from the artifact; neither is explained here.
  Candidates for a short theorem, not claims.

## 5. Deviations and provenance

- **Idle day.** The B = 3 run finished Aug 27 09:05 PDT; the remaining 667
  cells were launched Aug 28 09:47 PDT. The watcher set to report completion
  was `pgrep -f` on a string its own command line contained, so it never
  fired, and the second launch had not been chained. No effect on the
  measurement (append-only file; the measurement code is identical at both
  commits — ae34c92 between them touched only docs and added
  `scripts/d8_bucket_census.py`); recorded because a day of wall clock is
  part of the trace.
- Between the freeze (d46a6b9) and this note, D4 erratum E2 was enacted
  (ae34c92) with the census as its reason; no v0.2 cell was read before E2
  was written (the B = 3 run was in progress), and no v0.2 number is changed
  by it.
- `scripts/check_predictions.py` reports `d8-bucket-census-c1-2026-08-27.json`
  as an unknown artifact family; it is a structural census, not a result
  artifact, and carries no prediction-checkable quantity. Left as a warning.
- The four (12,12,3) ε = ½ benchmark cells were priced on Aug 27 after the
  original run died with a reboot; see the freeze note's provenance.
- Predictions were checked by the script on the consolidated artifact, not
  by recollection; every number in §0–§3 was checked against the artifact by
  an assertion script before this note was committed (see the commit).
