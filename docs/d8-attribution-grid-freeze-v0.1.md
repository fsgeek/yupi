# D8 attribution grid freeze — v0.1 (C0b)

> **Status (2026-08-25 11:21 PDT): FROZEN by cost, blind.** Preregistration
> `d8-attribution-prereg-v0.1.md` (commit a39f555) §4. Benchmark:
> `scripts/d8_attribution_benchmark.py` → `d8-attribution-benchmark-c0b-2026-08-25.jsonl`
> (1344 cost records; asserted free of any result-shaped key). Machine-readable
> admitted set: `d8-attribution-grid-freeze-c0b-v0.1.json`. Statute: Part II v0.2.6
> (commit 8dc36b2). No entropy, loss, or Δ was computed or read
> before this freeze; the benchmark discards the tables it builds.

## Rule (stated in the benchmark module before any cell was priced)

Admit a cell iff every line holds: B1 support ≤ 20000 states and frontier
≤ 70000 expanded transitions per step; B3 ≤ 1.0 s per step;
B4′ ≤ 1,500,000 paths per (ε, T) pass and ≤ 2 GB build memory; grid rule
projected filter-side (gate 2) wall ≤ 1200 s per cell single-process,
projected as n_vis · median t_shuf + n_lat · median t_ord from a deterministic
sample of 8 observations per channel.

## C0b — all 1344 candidate cells ADMITTED, none refused

Axes: both disciplines, ε = 1, rungs r1–r4, B ∈ {1, 2, 3}, T_ep a multiple
of B in [6, 16], L a multiple of B in [B, T_ep] (968 cells at B = 1, 264 at
B = 2, 112 at B = 3). Cost extremes over the set: paths per endpoint ≤ 362;
distinct shuffled observations n_vis ≤ 12,552; ordered windows n_lat ≤ 1,806;
support ≤ 7 states; frontier ≤ 43;
step ≤ 14 ms; build peak ≤ 19 MB;
largest projected gate-2 wall 16 s (stochastic (15,15,3) r4);
total projected gate-2 wall 0.36 h single-process. Every line is at least
two orders of magnitude inside its budget; the C0b world is cheap everywhere on
this grid, so the freeze admits it whole.

## C1 — NOT frozen here

The C1 benchmark is running (launched 11:15 PDT; at (9,9,3) r1 the census is
already 341,334 observations at ~414 s projected wall, so the wall cap will
refuse cells at larger T_ep). Its admitted set will be frozen in a separate
stamped note (v0.2) when its benchmark completes; **no C1 cell is measured
before that.** Measurement order per the prereg: C0b now, then C1 at B = 3,
then the remaining C1 cells.

## Provenance notes

- The benchmark processes were launched by this instance with output names
  dated 2026-08-24; the runs happened on 2026-08-25 (session crossed
  midnight). The C0b file was renamed to its real date before commit;
  content unchanged (append-only JSONL, one record per cell).
- The measurement runner (`scripts/d8_attribution.py`) refuses any cell not
  in the freeze JSON.
