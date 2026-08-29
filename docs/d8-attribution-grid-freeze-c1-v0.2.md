# D8 attribution grid freeze — v0.2 (C1)

> **Status (2026-08-27 07:32 PDT): FROZEN by cost, blind.** Preregistration
> `d8-attribution-prereg-v0.1.md` (commit a39f555) §4. Benchmark:
> `scripts/d8_attribution_benchmark.py` → `d8-attribution-benchmark-c1-2026-08-25.jsonl`
> (1344 cost records — 1340 written Aug 25, the last four Aug 27 07:21–07:24 PDT;
> asserted free of any result-shaped key). Machine-readable admitted set:
> `d8-attribution-grid-freeze-c1-v0.2.json` (`scripts/d8_grid_freeze.py --world c1`).
> Statute: Part II v0.2.6. No C1 entropy, loss, or Δ has been computed or read
> before this freeze; the benchmark discards the tables it builds. The C0b
> freeze (v0.1, commit 31f0632) and its measurement (48200e0) are unchanged.

## Rule (the v0.1 rule, unchanged)

Admit a cell iff every line holds: B1 support ≤ 20000 states and frontier
≤ 70000 expanded transitions per step; B3 ≤ 1.0 s per step; B4′ ≤ 1,500,000
paths per (ε, T) pass and ≤ 2 GB build RSS (D4 freeze, erratum E1);
grid rule projected filter-side (gate 2) wall ≤ 1200 s per cell
single-process. Plus one refusal-only guard added during the benchmark
(commit 0ebe9a9, Aug 26): a stage-A upper bound on the shuffled census
`n_vis` computed from the latent table alone, cap 3,000,000, which refuses
a cell before its visible table is built. It can only refuse; the commit
verified it refuses no cell the v0.1 rule admits (largest admitted census
586,520, 5× inside the cap). See Provenance for the four cells it touched.

## C1 — 716 of 1344 candidate cells ADMITTED, 628 refused

Axes: ε ∈ {1, ½}, rungs r1–r4, B ∈ {1, 2, 3}, T_ep a multiple of B in
[6, 16], L a multiple of B in [B, T_ep].

Refusals by line: WALL_CAP alone 514; B4′ RSS + WALL_CAP 100; B3 step +
WALL_CAP 7; B4′ RSS alone 3; N_VIS_CAP 4. 595 refused at stage A (from the
latent table and a sampled ordered-filter wall, no visible table built),
33 at stage B (built, then refused). **No cell is refused by B1** and none
by B4′ path count (T_ep = 16 is 1,315,454 paths, inside the line).

Admitted by B: B = 1 — 542 cells (9.61 h projected), all T_ep to 16 but
with L thinning past T_ep = 11 (at T_ep = 13–16 only L ≤ 3, plus L = T_ep
at 13 and 14, both ε); B = 2 — 125 cells (3.67 h), complete to
T_ep = 10, then L ∈ {2, 4} at 12 and L = 2 at 14, 16; **B = 3 — 49 cells
(3.54 h): complete at T_ep ∈ {6, 9} at both ε, then only L = 3 at T_ep = 12
(both ε) and 15 (ε = 1).**

Cost extremes over the admitted set: paths per (ε, T) ≤ 1,315,454;
n_vis ≤ 586,520; n_lat ≤ 586,520; support ≤ 739; frontier ≤ 3,572;
step ≤ 772 ms; build peak ≤ 1.42 GB; largest projected gate-2 wall 776 s;
total 16.81 h single-process.

## What the admitted set can and cannot witness (stated before measuring)

- **The decisive C1 condition is inside the fence.** The D8 note (§2) puts
  C1's first wait-queue bucket at tick 7, captured by a B = 3 bucket aligned
  at 7–9 (96 differing buckets at H = 9). **(9, 9, 3) is admitted at both ε**
  (n_vis 341,334; 414 s at ε = 1, 680 s at ε = ½). Witness 7's C1 mechanism
  is measurable here; (12, 12, 3) is not (see Provenance).
- **P3's positive half is outside it.** Prereg §6 P3 predicts Δ_an = 0 at
  C1 ε = 1, B = 2, L = T_ep ≤ 8, r1–r3 — those cells are admitted — and
  Δ_an > 0 at (12, 12, 2), r1–r3. **(12, 12, 2) is refused** on two lines:
  projected wall 1427–1456 s against 1200, and build peak 2.28 GB against
  B4′'s 2 GB. P3 will therefore be scored on its null half only; its
  positive half is NO_CHECK under this freeze. This is recorded now so the
  score cannot be read as a measurement outcome.
- The cross-world comparison at B = 3 sits on T_ep ≤ 9 in C1 against
  T_ep ≤ 15 in C0b. It is reported at the admitted range; the wall rule was
  stated before pricing precisely so that it cannot be moved to fit.

## Decision: extension grid v0.3 (taken now, before any C1 number exists)

> *(2026-08-28: v0.3 is now frozen — `d8-attribution-grid-freeze-c1-v0.3.md`, 173 of the 628 v0.2-refused cells admitted, (12,12,2) among them.)*

> *(2026-08-27 08:04 PDT, before any v0.2 number was read — the B = 3 run was in progress:
> D4 erratum E2 is ENACTED (`d4-budget-freeze-v0.1.md`, E2), so v0.3's rule
> is (wall ≤ 3600 s, build RSS ≤ 4 GB), which reaches (12, 12, 2) at both ε
> and (14, 14, 1) ε = 1 r1–r3. The reason is a structural census
> (`scripts/d8_bucket_census.py` → `d8-bucket-census-c1-2026-08-27.json`):
> at ε = 1 the allocator mechanism — C0b's entire loss — first exists in C1
> at ticks 10–12 and every full-context cell containing it is refused under
> v0.2, so the instrument as frozen cannot measure that interface cost. The
> paragraphs below are preserved as written at freeze time; where they say
> "proposed to the PI" and "(3600 s, 2 GB)", E2 supersedes them.)*

A separately stamped extension grid will be priced and frozen **after** the
v0.2 measurement is complete and its note written, under a rule stated
here: the v0.1 lines with the gate-2 wall cap raised to **3600 s per cell**;
B1, B3, and B4′ unchanged. Every cell it admits is labeled as v0.3 in the
artifact; nothing measured under v0.3 is cited as v0.2. Under this rule the
known candidates are the WALL_CAP-only refusals with projected wall
≤ 3600 s: 182 cells, 108 h single-process, mostly B = 1 (120) and B = 2 (45),
with 17 at B = 3 — none of them L = T_ep at B = 3. Stage-A cells are
re-priced blind before admission (their wall is an estimate).

**What v0.3 does not reach, and why:** (12, 12, 2) — P3's positive cell —
fails B4′'s 2 GB build line (2.28 GB at every rung; 2.17 GB at r4) as well
as the wall. B4′ is a D4 statute line (erratum E1, enacted by the PI); the
researcher does not move it. A D4 erratum E2 raising B4′ build RSS to 4 GB
per process is **proposed to the PI** with these facts: B2's own line is
8 GB per filtering process; the box reports 125 GB today
(`free -g`; the D4 freeze was written against 256 GB — noted, not
explained); 24 workers × 4 GB = 96 GB. If E2 is enacted before v0.3 is
priced, v0.3's rule is (3600 s, 4 GB) and admits (12, 12, 2) at both ε (all
rungs) and (14, 14, 1) ε = 1 r1–r3 (2.22 GB, 350–391 s — the three B4′-RSS-only
refusals); if not, v0.3 runs at (3600 s, 2 GB) and P3's positive
half stays NO_CHECK. Either way the decision is written before the number.

(12, 12, 3) stays out under any rule this instance would state: its ε = 1
census is 15.7 million observations, 6 h projected per cell, 1.8–2.0 h just
to build, and it consumed a session.

## Measurement order (prereg §4)

C1 at B = 3 first (49 cells, `scripts/d8_attribution.py FREEZE OUT
--only c1 --B 3 --workers 24`, output `d8-attribution-c1-2026-08-27.jsonl`),
then the remaining admitted C1 cells into the same append-only file, then
consolidate to `d8-attribution-c1-2026-08-27.json`. The runner refuses any
cell not in the freeze JSON.

## Provenance notes

- The C1 benchmark was launched Aug 25 11:15 PDT (16 workers) by the
  previous instance; 1340 records were written by 21:17 PDT. The four
  (12, 12, 3) ε = ½ cells were in progress when the box was rebooted
  (uptime shows 2026-08-27 06:44 PDT); the process died with it. Their
  ε = 1 siblings each built 15.66–15.80 M visible observations in
  6492–7078 s and were refused (B4′ RSS + WALL_CAP, 19,855–21,791 s projected).
- The four ε = ½ cells were priced on Aug 27 07:21–07:24 PDT by this
  instance, single worker, under the code at commit b59457a — i.e. **after**
  the N_VIS_CAP guard existed. Each was refused by N_VIS_CAP at stage A
  (n_vis upper bound 82.2–82.6 M against 3 M; n_lat 76,340) in 37–39 s.
  Their stage-A wall *estimates* were 696–865 s, under the 1200 s cap, so
  the v0.1 rule alone would have built them; the guard is the only line
  that refused them without a build. Given the ε = 1 siblings' measured
  census, the projected wall of a built cell would have been far above the
  cap; the guard changed the cost of refusal, not the verdict.
- The benchmark JSONL is append-only; the 1340 earlier records are
  byte-identical to the Aug 25 file (the four new lines are appended).
- `scripts/d8_attribution.py` gained a `--B` filter in this commit so the
  prereg's "B = 3 first" order is executable; suite 201 green.
