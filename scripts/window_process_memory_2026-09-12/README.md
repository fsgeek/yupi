# Window-process memory redesign — probes and gates (2026-09-12)

Scratch-grade scripts, kept because their logs are evidence in
`docs/window-process-interning-note-v0.1.md`. Run with
`PYTHONPATH=src:scripts/window_process_memory_2026-09-12`, programs
`c1prime-loop`, from the repo root.

- `frontier_denominators.py T_ep` — per-tick lcm of the frontier's mass
  denominators, both ε (log: `docs/window-process-frontier-denominators-*.log`).
- `census_original.py T_ep eps` — the 2026-09-04 recursion: staged RSS and the
  object-identity census (`docs/window-process-memory-census-original-*.log`).
- `wp_interned.py` — the experiment copy of the interned recursion (superseded
  by `src/yupi/window_process.py`; kept as what `gate_32_*` ran).
- `gate_32_interned_vs_original.py T_ep eps` — interned vs original in one
  process, every rung's aggregate and mass_T compared with `==`.
- `stages_interned.py T_ep eps` — staged RSS of the interned recursion, coarse
  aggregates vs coarse mass_T, and the compact mass_T form.
- `window_process_old.py` — verbatim `git show 0e55a09:src/yupi/window_process.py`
  (the 2026-09-04 recursion), the reference side of `gate_40.py`.
- `gate_40.py eps` — the committed module vs `window_process_old.py` at
  (40,8,2): every rung's aggregate equal with the same key order (outer and,
  since the Codex read [rv-3], inner), every rung's mass_T equal, and the
  MassT denominator report [rv-7]; raws
  `docs/window-gate-interned-full-order-40-8-2-2026-09-12*.json`. The
  earlier raws `docs/window-gate-interned-40-8-2-2026-09-12*.json` were
  produced by this script before the inner-order lines were added (outer
  order only), and `docs/window-gate-interning-only-40-8-2-2026-09-12*.json`
  by it against an uncommitted working-tree stage — see next item.
- `window_process_interning_only.py` — a RECONSTRUCTION [rv-4] of that
  stage (shared objects, dict-of-Fractions mass_T, no MassT), rebuilt from
  the committed module; agrees with it at (8,4,2) on every rung; not claimed
  byte-identical to what ran. Evidence for the note's §3 number, not the gate.
