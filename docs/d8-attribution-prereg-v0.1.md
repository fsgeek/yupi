# D8 order-mode attribution — preregistration v0.1

> **Status (2026-08-24 15:15 PDT): PREREGISTRATION, stamped before any attribution
> quantity is computed.** Contract for the D8 order-mode measurement
> (Part II §4 order modes; §9 witness 7; v0.2.6 canonical-naming track).
> Estimands, factorization, attribution rules, gates, and reporting are
> fixed here per the Codex contract adopted on 2026-08-24 (via Tony; the
> contract's terms are recorded in the Aug-24 handoff and reproduced in §1–§3
> below — this file is the first committed copy). Anything not fixed here is
> exploratory and will be labeled so. Statute at writing: Part II v0.2.6
> (commit 94b60ae).

## 0. What is being measured, in one sentence

How much of the exact posterior a learner loses when the D8 channel shuffles
records within delivered buckets — and *which coordinates of the world state*
that loss lives in. The ordered and shuffled modes deliver the same records
at the same bucket boundaries (matched disclosure latency); the difference is
purely order. The D8 note (`d8-shuffled-channel-note-v0.1.md`, v0.1.1)
established that the channel erases *named state coordinates* — cursor,
wait-queue order, allocator labels — and that which ones depends on rung, B,
ε, and contention. This measurement attributes the loss to those coordinates
under the statutory window law, with the remainder measured, not asserted.

## 1. Estimands

Fix a condition: world (C0b or C1), discipline $d$, scheduler $\varepsilon$,
rung $r$, window law $(T_{ep}, L, B)$. Under the joint law (uniform endpoint
$T$, offset $U = \max(0, T-L)$, latent window, final state $S_T$) let

- $O_{ord}$ = (RESET flag, ordered projected window) — Part II §2 base
  observation;
- $O_{shuf}$ = (RESET flag, the bucketed visible window) — the same window
  passed through the within-bucket permutation channel with likelihood
  $m/B!$ (Part II §4; `shuffled.channel_likelihood`).

The channel acts on $O_{ord}$ alone, so $(S_T, U) \perp O_{shuf} \mid O_{ord}$ and
the two preregistered estimands are conditional mutual informations that
reduce to differences of posterior entropies:

**E1 (unanchored, the learner's own condition):**
$$\Delta_{un} = I((U, S_T);\, O_{ord} \mid O_{shuf}) = \mathbb E[H(U,S_T \mid O_{shuf})] - \mathbb E[H(U,S_T \mid O_{ord})].$$

**E2 (anchored — TIME_CLASS unmasked, modeled as conditioning on $U$):**
$$\Delta_{an} = I(S_T;\, O_{ord} \mid O_{shuf}, U) = \mathbb E[H(S_T \mid O_{shuf}, U)] - \mathbb E[H(S_T \mid O_{ord}, U)].$$

Identity to be verified, not assumed: $\Delta_{un} - \Delta_{an} = I(U; O_{ord}
\mid O_{shuf}) \ge 0$ — the offset term. (The D10 verdict's "offset-mixture
amplification" is this term under a different contrast; here it is named and
reported on its own.) Expectations are law-mass means; exact rationals inside,
$\log_2$ in floats at print only (Part II §6). Per-observation gains
$g(v) = H(\cdot \mid O_{shuf}=v) - \mathbb E[H(\cdot \mid O_{ord}) \mid O_{shuf}=v] \ge 0$
are computed for every distinct shuffled observation $v$.

Both estimands are **canonical-track quantities** (Part II v0.2.6, Clause
2′): $\sigma = \sigma_0$. They are not random-naming ceilings; σ/binding is
a candidate *additional* attribution coordinate at the corpus layer, noted
here and not measured.

## 2. Coordinate factorization (a bijection, gated)

$S_T$ is factored into five coordinate functions; with $U$ a sixth for E1:

| symbol | coordinate | definition (function of $(U, S_T)$) |
|---|---|---|
| $U$ | offset | `law.offset(T)` (E1 only; conditioned on in E2) |
| $\kappa$ | cursor | `rr_cursor` (Part II §1, v0.2.6) |
| WQ | wait-queue order | per lock, the ordering of `lock_wq[l]` relative to its sorted-by-thread-index form (the *set* of waiters belongs to ρ) |
| DQ | device-queue order | per device, the ordering of the issuing threads in `dev_q[dev]` relative to sorted-by-thread-index form (the *set* of issuers belongs to ρ) |
| REQ | request identity | the map issuing-thread → request id over `dev_q` (allocator labels) |
| ρ | remainder | `pc`, `status` with IO_BLOCKED's id stripped, `running`, `lock_owner`, the waiter set per lock, the sorted issuer list per device |

**Gate F (executable):** $(\kappa, \mathrm{WQ}, \mathrm{DQ}, \mathrm{REQ}, \rho) \mapsto S_T$
is a bijection on every reachable state at every measured law (reconstruct and
compare). Coordinates may be correlated; that is why order-of-attribution is
handled by §3, not by defining them away.

## 3. Attribution rules

For a coordinate tuple $c = (c_1, \dots, c_n)$ that jointly determines the
target ($n = 6$ with $U$ first for E1; $n = 5$ for E2), the chain rule gives
exactly
$$\Delta = \sum_{k=1}^{n} I(c_k;\, O_{ord} \mid O_{shuf}, c_{<k}),$$
each term $\ge 0$ and computable as a difference of conditional entropies
from the exact joint. Three attributions are preregistered and all three are
reported; none is chosen after the fact:

1. **Semantic chain order (primary narrative):** $U \to \kappa \to \mathrm{WQ}
   \to \mathrm{DQ} \to \mathrm{REQ} \to \rho$ — from the channel inward:
   where the window sits, then scheduler metadata, then synchronization
   orders, then allocator labels, then everything else. The **remainder term
   is a RESULT**: it is reported as measured and is not required to be zero
   (D8 note v0.1.1 §3: the coarse-rung remainder is already nonzero at C0b).
2. **Shapley values** over the $n$ coordinates (average marginal contribution
   over all $n!$ orders; $2^n$ conditional entropies per observation model).
3. **Min/max** of each coordinate's chain term over all $n!$ orders — the
   order-sensitivity envelope.

**Gates A (executable):** every chain term $\ge 0$; chain sum $= \Delta$ and
Shapley sum $= \Delta$ (telescoping identities, checked to $10^{-9}$ in the
float print layer); the semantic order's terms lie within the min/max
envelope.

**Structural-zero controls (executable assertions, Part II §9 form):**
- Z1: the $\kappa$ term is exactly 0 in every $\varepsilon = 1$ cell (κ is a
  constant coordinate there, Part II v0.2.6 Clause 1) — under every order.
- Z2: the WQ term is exactly 0 in every C0b cell (no locks).
- Z3 (channel null): at $B = 1$ the permutation channel is the identity, so
  $\Delta_{un} = \Delta_{an} = 0$ exactly and every term is 0, every cell.
  **$B = 1$ is the null control for D8. Full context ($L = T_{ep}$) is NOT a
  null for D8** — within-bucket order is hidden regardless of context length
  — and is reported as an ordinary cell.

## 4. Conditions and the grid rule (the grid is frozen by cost, blind)

Worlds and axes, all reported, none dropped after a Δ is seen:
- **C0b** (both disciplines), $\varepsilon = 1$, rungs r1–r4, $B \in \{1, 2, 3\}$.
- **C1**, $\varepsilon \in \{1, \tfrac12\}$, rungs r1–r4, $B \in \{1, 2, 3\}$;
  $B = 3$ is the decisive C1 condition (the first C1 wait-queue bucket needs
  $B \ge 3$ — D8 note §2).
- Laws: $T_{ep}$ a multiple of $B$ with $6 \le T_{ep} \le 16$ (E1/B4′
  admits 16, refuses 18); every $L$ a multiple of $B$ with $B \le L \le T_{ep}$.

**Grid rule.** A blind cost benchmark (`scripts/d8_attribution_benchmark.py`)
runs each candidate cell's shuffled and ordered filters over the complete
census of distinct observations and records **cost only** — distinct
observation count, peak support, bit length, wall clock, path count — against
the frozen D4 budget (B1 20,000 states/step; B2 8 GB; B3 1 s/step; B4′ ≤ 10⁶
paths, $T_{ep} \le 16$). It prints no entropy, no Δ, no posterior; the
posteriors it computes are discarded. The admitted set is written to
`d8-attribution-grid-freeze-v0.1.md` and committed (stamped) before the
measurement script runs. Cells outside the budget are listed as refused with
their cost; a refused cell is never measured "exploratorily" and then cited.
Ordering after the freeze: C0b first ($\varepsilon = 1$, anchored and
unanchored), then C1 at $B = 3$, then the remaining C1 cells.

## 5. Gates (all must pass before any number in §7 is read)

1. **Z3 null:** $B = 1$ cells exactly zero (both estimands, all terms).
2. **Two-path, complete census:** at every measured law, for every distinct
   shuffled observation (the `_visible_windows` census — all within-bucket
   permutations, not reversals), the recursive shuffled window filter equals
   independent path summation bit-for-bit, and the ordered window filter
   equals its path summation likewise; the law mass of every observation is
   computed on both sides and agrees. **Uncapped.** A cell whose census the
   budget cannot complete is *refused by §4*, not capped; a capped gate is
   not a passed gate (D10 verdict v0.1.1, gate-2 lesson).
3. **Gate F** bijection on every reachable state.
4. **Gates A** (nonnegativity, chain and Shapley sums, envelope).
5. **Z1, Z2** structural zeros.
6. Ordered mode equals identity serialization of the per-record filter (`test_ordered_bucket_equals_per_record_filter` in
   `tests/test_shuffled_channel.py`) at every
   measured law.
7. An existence statement ("the channel hides X at this cell") cites
   $> 1$ distinct enumerated shuffled observation with $g(v) > 0$, never a
   single handcrafted bucket.

## 6. Predictions (existence-level only; sources are committed green tests)

The Tier-1 lesson stands: this instance's numeric priors are unreliable, so
no numeric prediction is made. The following are existence predictions whose
source is a named committed test, cited at the test's *actual* condition,
not the note's summary of it. Each is checkable against the artifact by the
prediction-checker script (owed; see §8).

- **P1** (source: `test_w7_c0b_supplies_noncommuting_bucket_at_masked_lineage`,
  C0b, both disciplines, r1–r3, $B = 3$, $H = 6$ from reset): $\Delta_{an} > 0$
  at C0b $(6, 6, 3)$, r1–r3, both disciplines, with a nonzero REQ-or-ρ share
  (the allocator mechanism). *Not predicted:* the split between REQ and ρ.
- **P2** (source: `test_c0b_shuffled_channel_is_null_at_r4_only`, C0b, r4,
  $B \le 4$, $H \le 8$ from reset): $\Delta_{an} = \Delta_{un} = 0$ at every C0b
  r4 cell with $T_{ep} \le 8$, $B \in \{2, 3\}$. *Not predicted:* C0b r4 at
  $T_{ep} \ge 10$ (the test's horizon boundary is exactly the D8 note's own
  reversal).
- **P3** (source: `test_c1_B2_allocator_bucket_appears_at_H12_at_masked_lineage`,
  C1, $\varepsilon = 1$, r1–r3, $B = 2$: null at $H = 8$, bucket at $H = 12$):
  $\Delta_{an} = 0$ at C1 $\varepsilon = 1$, $B = 2$, r1–r3, $T_{ep} \le 8$,
  $L = T_{ep}$; $\Delta_{an} > 0$ at $T_{ep} = 12$, $L = T_{ep}$, r1–r3.
  *Not predicted:* truncated cells ($L < T_{ep}$) at any of these — the window
  law changes what the channel sees, and the D10 verdict showed offset
  mixing amplifies rather than merely inherits.
- **P4** (source: `test_at_eps_half_B2_channel_carries_only_cursor_information`,
  C1, $\varepsilon = \tfrac12$, r4, $B = 2$, $H = 4$ from reset): no §4 cell
  matches this test's condition ($T_{ep} = 4$ is below the grid), so **P4 is
  recorded as having no in-grid check**; the κ term's share at C1
  $\varepsilon = \tfrac12$, $B = 2$, r4, $L = T_{ep}$, $T_{ep} \ge 6$ is
  reported without a prediction.
- **Z1–Z3** are predictions by theorem and are gated, not scored.

A failed prediction is preserved in place with its source test named; it is a
finding about the generalization from that test's condition to the cell, not
about the measurement.

## 7. Reporting (per cell: world, discipline, ε, rung, law)

$\Delta_{un}$, $\Delta_{an}$, the offset term; per-endpoint $T$: the anchored
gain restricted to windows generated at $T$ and the unanchored gain likewise
(law means co-reported, never substituted for cells); chain terms in semantic
order; Shapley values; min/max envelope per coordinate; prevalence $P(g(v) > 0)$
as exact law mass with the count of distinct shuffled observations and of
informative ones; $\max g$, quantiles {50, 90, 99} of $g$ over law mass; the
collapse label "numerically collapsed" iff $\Delta < \delta = 0.01$ bits (Part
II v0.2.5) — **collapsed and informative are different words** (D10 verdict);
cost columns. Raw JSON is append-only under versioned dated names
(`d8-attribution-<world>-<date>.json`); the note that reads them cites this
file and the grid freeze by commit hash. The predeclared reading of the
$(\Delta_{an}, \text{offset term})$ pair per cell:

| $\Delta_{an}$ | offset term | reading |
|---|---|---|
| $> 0$ | $> 0$ | order hides state and where the window sits |
| $> 0$ | $= 0$ | order hides state only; anchoring adds nothing |
| $= 0$ | $> 0$ | order hides only window placement — the anchored learner is unharmed |
| $= 0$ | $= 0$ | order modes coincide at this cell |

## 8. Provenance and deviations

Scripts, raws, and the reading note cite this preregistration by commit hash.
Deviations are recorded as deviations. The blind benchmark and grid freeze
precede the measurement script; the measurement script refuses to run on a
cell not in the freeze. The prediction-checker script (`scripts/check_predictions.py`,
owed since Aug 22) is built before §6 is scored: it takes a prediction as
(cell selector, quantity, relation) and evaluates it against every committed
artifact at the same $(T_{ep}, B)$, so that "does something already committed
know the answer" is a command, not a recollection.

*Decision rights:* none of this changes a threshold, a frozen decision, or the
statute; the PI's rights over scope and publication are unchanged. Reviewers
are asked to attack §2's factorization (is ρ hiding a coordinate that should
be named?), §3's semantic order (is "from the channel inward" the right
narrative order, given that Shapley and the envelope are reported anyway?),
and §6's scoping of each prediction to its source test's condition.
