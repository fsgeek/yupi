# C1 Window Uncertainty — Offset vs. State (v0.1)

**Status: exploratory measured note (Aug 17 2026, 19:04 PDT, ninth
instance).** Non-governing. Resolves open thread 6 of
`instrument-status-2026-08-14.md` ("cursor ablation / I(U;h)
decomposition — deferred, deliberately unclaimed") in its simplest form.
Script `scripts/c1_offset_vs_state.py`; raw
`docs/c1-offset-vs-state-{12-2-2,14-4-2,14-8-2}-raw-2026-08-17.json`.
Single-path (the joint (U, S_T) posteriors themselves are two-path gated
by `window_filter` ⟂ `window_enumerator`; this script only aggregates
them by path enumeration). No predictions were pre-stated — the run
adjudicates a factual claim made in external review, quoted below.

## The claim

Review (Aug 17, via Tony): under truncated, offset-unanchored windows,
"the uncertainty is mostly about where in a nearly deterministic
trajectory the window sits, not about what the world did. A model
trained on those traces learns to identify trajectory and position,
which is a lookup with extra steps."

## Definitions

Windows as in `c1_predictive_targets.py` (Part II §2 law; T uniform on
{B..T_ep}, U = max(0, T−L), RESET flag). Per window w the exact joint
posterior over (U, S_T). Law-mass-weighted means of
H(U|w), H(S_T|w), H(S_T|w,U) = Σ_u P(u|w) H(S_T|w,u), and
I(U; S_T|w) = H(S_T|w) − H(S_T|w,U). Bits.

## Results

| law | ε | rung | windows | H(U\|w) | H(S\|w) | H(S\|w,U) | I(U;S\|w) | H(S\|w,U)/H(S\|w) |
|---|---|---|---|---|---|---|---|---|
| (12,2,2) | 1 | r1 | 186 | 1.3998 | 3.0598 | 1.6600 | 1.3998 | 0.543 |
| (12,2,2) | 1 | r2 | 209 | 1.3321 | 2.9265 | 1.5944 | 1.3321 | 0.545 |
| (12,2,2) | 1 | r3 | 283 | 1.3106 | 2.7812 | 1.4706 | 1.3106 | 0.529 |
| (12,2,2) | 1 | r4 | 293 | 1.3104 | 2.7799 | 1.4696 | 1.3104 | 0.529 |
| (12,2,2) | 1/2 | r1 | 186 | 1.2475 | 2.3040 | 1.0565 | 1.2475 | 0.459 |
| (12,2,2) | 1/2 | r2 | 209 | 1.1898 | 2.2266 | 1.0367 | 1.1898 | 0.466 |
| (12,2,2) | 1/2 | r3 | 283 | 1.1795 | 2.1587 | 0.9791 | 1.1795 | 0.454 |
| (12,2,2) | 1/2 | r4 | 293 | 1.1795 | 2.1586 | 0.9791 | 1.1795 | 0.454 |
| (14,4,2) | 1 | r1 | 3497 | 0.8436 | 1.3436 | 0.5000 | 0.8436 | 0.372 |
| (14,4,2) | 1 | r2 | 3922 | 0.7608 | 1.2136 | 0.4527 | 0.7608 | 0.373 |
| (14,4,2) | 1 | r3 | 4577 | 0.7266 | 1.0962 | 0.3695 | 0.7266 | 0.337 |
| (14,4,2) | 1 | r4 | 4698 | 0.7258 | 1.0944 | 0.3686 | 0.7258 | 0.337 |
| (14,4,2) | 1/2 | r1 | 3497 | 0.6227 | 0.7976 | 0.1749 | 0.6227 | 0.219 |
| (14,4,2) | 1/2 | r2 | 3922 | 0.5676 | 0.7270 | 0.1595 | 0.5676 | 0.219 |
| (14,4,2) | 1/2 | r3 | 4577 | 0.5510 | 0.6769 | 0.1258 | 0.5510 | 0.186 |
| (14,4,2) | 1/2 | r4 | 4698 | 0.5510 | 0.6767 | 0.1257 | 0.5510 | 0.186 |
| (14,8,2) | 1 | r1 | 65547 | 0.1266 | 0.1511 | 0.0245 | 0.1266 | 0.162 |
| (14,8,2) | 1 | r2 | 67820 | 0.0980 | 0.1190 | 0.0211 | 0.0980 | 0.177 |
| (14,8,2) | 1 | r3 | 68688 | 0.0923 | 0.1091 | 0.0167 | 0.0923 | 0.153 |
| (14,8,2) | 1 | r4 | 68794 | 0.0920 | 0.1086 | 0.0166 | 0.0920 | 0.153 |
| (14,8,2) | 1/2 | r1 | 65547 | 0.0703 | 0.0727 | 0.0024 | 0.0703 | 0.033 |
| (14,8,2) | 1/2 | r2 | 67820 | 0.0517 | 0.0533 | 0.0015 | 0.0517 | 0.029 |
| (14,8,2) | 1/2 | r3 | 68688 | 0.0490 | 0.0498 | 0.0008 | 0.0490 | 0.016 |
| (14,8,2) | 1/2 | r4 | 68794 | 0.0490 | 0.0498 | 0.0008 | 0.0490 | 0.016 |

max |I(U;S|w) − H(U|w)| over 24 cells: 9.21e-15

## Findings (v0.1)

1. **The offset is a function of the state: H(U | w, S_T) = 0.**
   I(U;S_T|w) = H(U|w) in all 24 cells (max discrepancy 9e-15, float
   arithmetic on exact posteriors). Given the endpoint state, the number
   of elapsed steps is determined — deterministic workloads (D1) make the
   program counters a clock. "Position" and "what the world did" are not
   two variables here; position is a coordinate of state. The clean
   decomposition is H(S_T|w) = H(U|w) + H(S_T|w,U): clock share plus
   world-given-clock share.
2. **The world-given-clock share is ≈½ at L=2 and falls with L:** ε=1:
   0.53–0.55 at (12,2,2), 0.34–0.37 at (14,4,2), 0.15–0.18 at (14,8,2);
   ε=½: 0.45–0.47, 0.19–0.22, 0.02–0.03. The review's claim is **false at
   the shortest windows and true by L=8**; the clock share grows with L,
   and it is the residual world-given-clock term that vanishes toward
   the synchronization horizon.
3. **Rung-invariant to a few percent** in every law: the content ladder
   moves H(S_T|w) (r1→r4: 3.06→2.78 at (12,2,2) ε=1) but not this split.
   Consistent with the ceilings notes: content is a weak variable under
   truncation.
4. **ε=½ lowers every term and shifts the split toward the clock** —
   structure (cursor/temporal correlation) rather than entropy, as the
   window-prior v0.3.2 correction argued.

## What this does and does not say

- It does not measure what a *model* learns; it measures what the exact
  posterior contains. "Lookup with extra steps" is a claim about
  representation, testable only after training (M2/M5). What it says is
  that at short windows the posterior a model must represent has ~half
  its entropy in the world-given-clock component, at every content rung.
- It says the training window length L is a design constraint with a
  number attached: below L≈4 at T_ep=14, the belief has interior that is
  not the clock; by L=8 it is mostly clock; by L*≈10–12 (proposed δ) it
  is nothing.
- Related: `full-context-injectivity-note-v0.1.md` (L = T_ep: H(S_T|w)=0
  exactly, every rung); `c1-sync-sweep-v0.1.md` §2d (adjacent-rung gaps
  on the L axis).

## Caveats

- Three laws, one T_ep pair; ε ∈ {1, ½}. No pre-stated predictions
  (stated above). H(S_T|w) is state entropy, not query entropy — the
  queries load on a subset of state; the split for a query is not given
  here.
