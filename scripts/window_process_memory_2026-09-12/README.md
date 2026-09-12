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
  (40,8,2): every rung's aggregate equal with the same key order, every
  rung's mass_T equal; raws `docs/window-gate-interning-40-8-2-*.json`.
