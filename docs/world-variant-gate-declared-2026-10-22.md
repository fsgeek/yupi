# World-variant gate: declared before any variant table exists (2026-10-22)

> Owning instance (from 2026-10-22). Declared and stamped **before** any variant table is built. It answers the
> v3 blind read's largest concern (`paper1m-v3-blind-review-2026-10-22.md`, point 1): which §4.2–4.3 findings belong to
> this world, and which survive a change to its randomness. It is also the paper's first **prospective** audit: the
> audit is run on candidate worlds before any learner is trained on them, and its outcome decides what (if anything)
> is trained next. Status: EXPLORATORY exact side, with declared predictions and a declared decision rule.

## Correction to the Oct 15 reading

`world-variant-reading-2026-10-15.md` proposed "per-device completion probabilities". The world has **one device**
(`WorldConfig.c1`: `n_devices=1`, queue depth 2, discipline `stochastic`), so that knob does not exist. The
completion knobs that do exist are the scalar `completion_p` (already a `WorldConfig.c1(p=…)` parameter) and a
state-dependent completion probability (a kernel change).

## Variants

All at the frozen window law (40, 8, 2), pattern observer, position 7, KIND, both ε (1 and ½), rungs r0–r4. Every
variant keeps p in (0, 1), so every transition possible at p = 1/3 stays possible: the reachable states and the
posterior support are unchanged; only probabilities move.

| id | completion probability when a request is pending | code change |
|---|---|---|
| V0 | 1/3 (the paper's world; regression) | none |
| V1 | 1/4 | none (`--p 1/4`) |
| V2 | 1/2 | none (`--p 1/2`) |
| V3 | 1/4 with one request pending, 1/2 with two | kernel: completion mass as a function of queue occupancy |

The request completed stays uniform over pending requests in every variant. V3 is a versioned world (a Part II
amendment, to be written with the kernel change). It gets its own kernel tests before any table is built: per-state
probabilities sum to exactly 1, and the d10 check (total completion mass equals the declared value at every reachable
state) is adapted to the occupancy rule.

## Procedure

1. Add `--p` to `scripts/kind_uncertainty_split.py` and `--rows-dir` to `scripts/support_audit_table.py`.
   **Regression gate:** V0 through the modified script must reproduce the pinned `split-v2` rows byte-for-byte
   (`split-v2-rows-sha256-2026-10-15.txt`). If it does not, stop.
2. Build the V1 and V2 rows (four passes, about 9 min and 5 GB each, run in parallel) into separate row
   directories. Never write to `split-v2/`.
3. Run the §4.2 table and the §4.3 exact kind sweep on each variant, with two definitions generalised (below).
4. Implement V3, test it, build its rows, and repeat step 3.

**Generalised definitions** (the v3 definitions are the special case p = 1/3):
- *Device template:* a pure class (G = 0, H\* > 0) whose exact next-KIND law puts mass x on IO_COMPLETE and 1 − x on a
  single other kind, for any x. At V0–V2, x = p. At V3, x ∈ {1/4, 1/2}. This replaces "device coin |H\* − h(1/3)| < 1e-4".
- *Law mechanisms:* the pure side grouped by distinct exact next-KIND law. Reported: the number of laws carrying at
  least 10 % of matched pure mass, and the largest law's share.
- *Bins:* floor(H\*/0.05) as in v3. h(1/2) = 1 bit lies on a bin edge, so every share is also reported with bins
  offset by half a width (floor(H\*/0.05 + ½)). A prediction counts as holding only if it holds under both binnings.

## Predictions (declared; r1–r3, both ε, under both binnings)

- **P1 (V1, V2).** The device template carries at least 80 % of the pure side's mass in every cell. Reason: a scalar
  p moves the coin's entropy (h(1/4) = 0.811, h(1/2) = 1.000 bits) but not the number of places randomness enters.
- **P2 (V1, V2).** The matched high-gap side (G/H\* ≥ 0.5, sharing a bin with a pure class) stays below 5 % of the
  population in every cell.
- **P3 (V3).** By kernel rule, the device template still carries at least 80 % of the pure side. By exact law, the
  largest single law carries less than 70 % of it. That is, the two groupings in audit step 3 disagree. If this
  holds, the procedure must say which grouping a "mechanism" means.
- **P4 (V3).** The matched high-gap side stays below 5 % in every cell.
- **P5 (all).** The exact kind sweep's ambiguous share at δ = 0.05 is at least 10 % of position-7 mass in every cell.
  That is, the §4.3 finding that ambiguous neighbours exist at learner-level precision survives.

No prediction is declared for where the kind ambiguity sets in (v3: between δ = 0.01 and 0.02). It is reported per
variant.

## Decision rule (what each outcome does)

A variant **supports the randomness-against-withheld-state contrast** if, in every r1–r3 cell at both ε, the matched
high-gap side is at least 10 % of the population **and** at least three exact laws each carry at least 10 % of the
matched pure mass. (These are the thresholds of the Oct 15 reading's gate (b), made specific.)

- **If any variant supports the contrast:** v4 reports that the audit, run before training, selects a world in which
  the contrast exists. A learner study on that variant is the next study. It is not part of v4; it gets its own
  declaration.
- **If none does:** v4 reports that the contrast's narrowness survives every reparameterisation of the completion
  probability tried. The narrowness then belongs to *where* the kernel places randomness, not to the value 1/3.
  §4.2's closing sentence ("a consequence of design") becomes a tested statement. No learner is trained.

Either way, every predicted and unpredicted number goes into v4's §4, with its variant, with failed predictions
reported as failed.

## Out of scope here

- The §3.3 lag-profile crossing under the variants. The blind read asked about it, but it uses a different pipeline.
  It is listed as a follow-up and is not part of this gate.
- Per-thread dispatch weights. These change the naming/binding structure (`pattern_filter.py` assumptions) and need
  their own reading.
- Any learner training.
