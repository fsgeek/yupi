# Supplement: provenance of every number in the methods paper

Each section's sources: result files, scripts and review records in the repository, all OpenTimestamps-stamped.

## From 2. The instrument

- All of §2: `paper1-draft-s2-v0.3.md` §2.1–2.5 and its provenance; Appendix A (`paper1-appendix-A-instrument-v0.1.md`).
- R/G validation row: `kind-uncertainty-split-40-8-2-k7-eps*-2026-10-15.json` (minimum class G −8.9 × 10⁻¹⁶).
- Injectivity: `reset-injectivity-r1-2026-10-13.jsonl`.

## From 3. What each interface lets an observer know, exactly

- 3.1: `kind-uncertainty-split-40-8-2-k7-eps1-2026-10-15.json`, `…-eps1_2-…`; R = 0.608521 / 0.544118 at every rung;
  each H\* reproduces the ceilings of `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`. Reproduced by Codex
  (v0.8 review #7).
- 3.2: `state-vs-predictive-40-8-2-2026-10-13.json`; ratios 4.7 / 4.3 / 4.4 (ε = 1) and 4.3 / 3.1 / 4.0 (ε = ½),
  reproduced by Codex (v0.8 review #7).
- 3.3: `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json` (s3 v0.4 §3.2 table); KL and entropy-difference routes agree
  to 3 × 10⁻¹⁴.
- 3.4: `three-arm-exact-side-r1S-2026-10-05.log` (gates A–C); relay construction, `paper1-draft-s3-v0.4.md` §3.3.
- Zhao et al., Log20, SOSP 2017; Someya et al., ACL 2025.

## From 4. Which contrasts can this world carry, and at what precision?

- 4.1: `paper1-draft-s4-v0.3.md` §4a ("The shape"); `paper1-draft-s5-v0.4.md` §5.1.
- 4.2 and the kind sweep: `scripts/support_audit_table.py` → `support-audit-table-40-8-2-k7-2026-10-15.json`, from the `split-v2` rows (`scripts/kind_uncertainty_split.py`; hashes in `split-v2-rows-sha256-2026-10-15.txt`); the
  table recomputed by the owner 2026-10-15 and matching Codex's independent recomputation (whole-draft review #3).
  Milestone 1 design: `yupana-m1-spec-draft.md` (D1).
- 4.3 exact: `one-step-identifiability-40-8-2-k7-2026-10-15.json`; collision re-derived from the r3 ε = 1 rows.
  Separation: `identifiability-tolerance-40-8-2-k7-2026-10-15.json` (G); `scripts/review/tolerance_r_g_swap.py` (R and
  swaps, r1 and r3 at ε = 1). Trained models: `learner-precision-monitor-40-8-2-k7-2026-10-15.json` (R) and
  `learner-precision-monitor-gkind-40-8-2-k7-2026-10-15.json` (kind), both declared in
  `learner-precision-monitor-check-2026-10-15.md` before running.
- Bergna, Depeweg & Hernández-Lobato, arXiv:2605.06413.

## From 5. The learner case

- 5.1: `paper1-draft-s4-v0.3.md` §4a–4b and its provenance (B1 raws; `b1-fe-coarse-robustness-2026-10-13.json` and
  `-actor-`; `b1-size-axis-d256-2026-10-13.jsonl`; `converged-ladder-*-2026-10-02.json`).
- Baselines: `count-baseline-comparison-2026-10-04.json`; `gru-baseline-verdict-v0.1.md`, `gru-baseline-score-2026-10-13.json`.
- 5.2: `relay-lossmask-verdict-v0.1.md`, `relay-2x2-verdict-v0.1.md`; table as in `paper1-draft-s4-v0.3.md` §4e.
