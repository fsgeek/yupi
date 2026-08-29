# D8 attribution grid freeze — v0.3 (C1 extension)

> **Status (2026-08-28 18:18 PDT): FROZEN by cost, blind to every v0.3 number.** This is
> the extension grid decided in `d8-attribution-grid-freeze-c1-v0.2.md`
> (Decision section, written before any v0.2 number was read) under D4
> erratum E2 (`d4-budget-freeze-v0.1.md`). Rule **v0.3**, stated in code
> (`d8_benchmark.RULES`, commit dd7c404) before any cell was priced: gate-2
> wall ≤ 3600 s per cell; B4′ build RSS ≤ 4 GB; N_VIS_CAP 9,000,000 (the
> refusal-only guard scaled with the cap); B1, B3 and the 1.5 M path line
> unchanged. Benchmark: `d8-attribution-benchmark-c1-v0.3-2026-08-28.jsonl`
> (628 cost records, every one tagged `rule: v0.3`; asserted free of any
> result-shaped key). Machine-readable admitted set:
> `d8-attribution-grid-freeze-c1-v0.3.json`. **Only the 628 cells refused
> under v0.2 were priced; the 716 v0.2-admitted cells are measured
> (`d8-attribution-c1-2026-08-27.json`) and are neither re-priced nor
> re-admitted here. Nothing measured under v0.3 is cited as v0.2.**

## C1 extension — 173 of 628 candidate cells ADMITTED, 455 refused

Priced Aug 28 12:13–18:14 PDT on 16 workers. Refusals by line: WALL_CAP
alone 340; WALL_CAP + N_VIS_CAP 52; N_VIS_CAP alone 22; B4′ RSS alone 6;
B4′ RSS + WALL_CAP 28; B3 step + WALL_CAP 1; all three 6. 430 refused at
stage A, 198 built (stage B) of which 25 were then refused. Admitted by B:
130 / 37 / 6; by ε: 99 at ε = 1, 74 at ε = ½.

Cost extremes over the admitted set: n_vis ≤ 1,775,212; n_lat ≤ 1,214,350;
support ≤ 666; frontier ≤ 5,885; step ≤ 509 ms; build peak ≤ 2.89 GB;
largest projected gate-2 wall 2,927 s; total 44.87 h single-process.

**Full-context laws newly admitted:** (12, 12, 2) at both ε, all four rungs
— P3b's cells, at 1360–1551 s projected and 2.28 GB (2.17 at r4) for
ε = 1; (14, 14, 1) r1–r3 at both ε (r4 was admitted under v0.2);
(15, 15, 1) r4 at both ε. **B = 3 newly admitted:** only (15, 3, 3) — ε = 1
r2–r4, ε = ½ r1–r3. (12, 12, 3) is refused by N_VIS_CAP at both ε, as
expected (15.7 M measured census at ε = 1).

**The next step up, named and not proposed.** (15, 15, 1) r1–r3 at both ε
are refused by B4′ RSS *alone*: 4.81 GB build peak at 710–890 s projected
wall. Admitting them would need a third erratum with its own reason; none
is offered here.

## Measurement order

(12, 12, 2) first — both ε, all rungs, eight cells — then the remaining
165 admitted cells, one job per cell (`--per-cell`, so the 13.5 h
(ε = ½, T_ep = 12) group does not serialize on one worker), 24 workers,
into `d8-attribution-c1-v0.3-2026-08-28.jsonl` (separate from the v0.2
file), then consolidated to `d8-attribution-c1-v0.3-2026-08-28.json`.
Predictions to score on the result: P3b (Δ_an > 0 at C1 ε = 1, B = 2,
r1–r3, (12, 12, 2)) — preregistered Aug 24, before the census, before E2.

## Provenance

- Rule v0.3 was written in the v0.2 freeze note's Decision section (d46a6b9,
  wall only), amended to include E2's memory line (ae34c92) with the census
  as reason, and put in code (dd7c404) — all three before pricing began.
- The benchmark's `--refused-in` restriction means a v0.2-admitted cell
  cannot appear in this file; the freeze script refuses records priced
  under a different rule.
