# Paper 1, Appendix A draft v0.1 (2026-10-13): The instrument in detail

> **Status: DRAFT, owning instance.** Answers whole-draft review W19 (Codex finding 21). Numbers are read from the
> raws named in the provenance list.

## A.1 The computation

```
# Window process: one exact recursion per (law, ε), at the finest rung r4; coarser rungs are projections.
frontier ← {(initial_state, empty window) : 1}
for t = 1 … T_ep:
    next ← {}
    for (state S, last-L-record window w) with mass μ in frontier:
        for (transition τ, probability p) in enabled(S):                 # the kernel; exact Fractions
            w' ← (w + [record_of(τ)])[-L:]
            next[(τ.next_state, w')] += μ · p
    frontier ← next
    for each endpoint T on the grid {B, 2B, …, T_ep} with T = t:        # the window law: T uniform on the grid
        aggregate[(reset_flag, w)] += frontier mass / |grid|, by state  # joint P(window, state)

# Pattern ceilings at position k (here 7): for each rung r and class c = (reset_flag, Π_all(project_r(w_≤k))):
    P*(next record | c) = Σ over (S, binding β) consistent with c of P(S, β | c) · P(record_r(τ) re-keyed by β | S)
    M = Σ_c mass(c) over classes whose window runs ≥ k records         # 0.85 at k = 7
    ceiling_target = Σ_c (mass(c) / M) · H(target of next | c)

# Lag profile: for m < k, the suffix view s_m(c) re-keys the last m records by Π_all,
# and an entity bound only before the suffix becomes fresh:
    P*_m(· | s) = law-mass mixture of the pushed-forward Q_c over classes sharing s
    ι_m(c) = KL(Q_c ‖ P*_m(· | s_m(c)));   lag profile ι_m = Σ_c (mass(c)/M) ι_m(c) = H_m − H*
    # (KIND target; naming-aware targets use the suffix push-forward of Q_c described in §2.5)
```

Every probability is an exact rational. Logarithms are taken in float at the end. The recursion and an independent
path summation share only the three kernel functions (`enabled`, `record_of`, `project`).

## A.2 A worked window (r1, ε = 1, position 7)

A window that begins at reset (flag R) and shows seven r1 records, with threads renamed by first appearance:

```
DISPATCH 0 · DISPATCH 1 · ACQUIRE 0 · DISPATCH 0 · RELEASE 0 · DISPATCH 0 · IO_ISSUE 0
```

Its pattern class has law mass 1/5760. The exact law of the next record:
- `IO_COMPLETE 0` with probability 1/3, because the device completes on this step;
- `DISPATCH 2` (a thread not yet seen in the window) with probability 2/3.

The next-KIND entropy is H(1/3, 2/3) = 0.918 bits. That is the irreducible part the §3 introduction quotes. The
next-KIND law is the same in every state consistent with this window, and still random. A learner that predicts `DISPATCH` must also place
probability on the *fresh* thread name. Its ACTOR term sums the probability over unused drawable names (§2.5).

## A.3 Size and cost at the frozen law (40, 8, 2)

| quantity | ε = 1 | ε = ½ |
|---|---|---|
| reachable states (max over ticks) | 1,953 | 4,173 |
| (state, window) pairs in the frontier (max over ticks) | 1,964,919 | 1,964,919 |
| one recursion pass, wall time | 542 s | 532 s |
| peak memory of that pass | 5.09 GB (4.74 GiB) | 5.23 GB (4.87 GiB) |

Per rung, at the window's last record:

| rung | distinct windows | max posterior support | mean state entropy (ε = 1) | pattern classes at k = 7 |
|---|---|---|---|---|
| r0 | 12,739 | 401 (ε = ½: 578) | 3.947 | 5,540 |
| r1 | 819,073 | 118 | 0.601 | 89,474 |
| r2 | 923,461 | 118 | 0.528 | 116,624 |
| r3 | 991,585 | 118 | 0.405 | 146,455 |
| r4 | 1,524,612 | 101 | 0.390 | 160,363 |

These run on one 64-core workstation (256 GB). The exact side needs no GPU. The budget rule fixed before any
observability curve (Part I D4) is stated in `d4-budget-freeze` and its erratum E3.

## A.4 Reproducibility manifest

| claim | configuration | artefact | protocol |
|---|---|---|---|
| ceilings and lag profiles (§3.1–3.2) | (40, 8, 2), k = 7, both ε | `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`; tables `c1prime-loop-40-8-2-{rung}-eps{ε}-k7.jsonl` (sha256 in the pattern-ceiling raws) | implicit-information design v0.1 |
| state vs predictive (Table 3.0) | (40, 8, 2), last record | `state-vs-predictive-40-8-2-2026-10-13.json` | Part I decomposition |
| ceiling-holding rewrites (§3.3) | r1R, r1D, r1S | `relay-exact-side-2026-09-30.json`, `three-arm-exact-side-r1{D,S}-2026-10-05.json`, `decoy-iota-check-2026-10-05.json` | relay design v0.1, three-arm design |
| reset injectivity (§2.3) | frozen world, L ≤ 8 | `reset-injectivity-r1-2026-10-13.jsonl` | — |
| within-cell association (§4a) | 45 transformers; 4 at d = 256 | `d1-long-lag-verdict-v0.1.md`, `converged-ladder-verdict-v0.1.md`, the FE raws, `b1-size-axis-d256-2026-10-13.jsonl` | D1 and converged-ladder preregs (stamped) |
| relay and 2×2 (§4e) | 5 arms × 3 seeds | `relay-2x2-score-2026-10-13.json` and the verdicts | relay, loss-mask and 2×2 preregs (stamped) |
| code | — | git, OTS-stamped per commit. Runs since 2026-10-09 record their revision lineage in `run.json`; earlier
runs (the 10-02 r1/r1R baselines) do not, and are authenticated instead by the trainer-reproduction gate (exact
step-1000 losses). One gate deviation is disclosed: the r1m runs record a dirty tree, and only an untracked
scorer differed (`relay-2x2-verdict-v0.1.md` §1). | — |

---

## Provenance

- A.3: `window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-12-interned-amended.json`, and
  `pattern-ceilings-40-8-2-k7-2026-09-18.json` (`n_pattern_classes`).
- A.2: `~/.cache/yupi-scratch/ceilings/c1prime-loop-40-8-2-r1-eps1-k7.jsonl`, a line with exactly two outcomes.
- A.1 is a summary of `src/yupi/window_process.py`, `src/yupi/pattern_ceiling.py` and `src/yupi/implicit_info.py`.
  It is not executable code.
