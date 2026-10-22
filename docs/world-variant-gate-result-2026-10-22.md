# World-variant gate: result (2026-10-22)

> Owning instance. Scores `world-variant-gate-declared-2026-10-22.md` (stamped at 707a5e2 before any variant table
> existed). V3 is defined in `world-variant-v3-definition-2026-10-22.md`. Audit outputs are in
> `world-variant-gate-V{1,2,3}-audit-2026-10-22.json`, by `scripts/variant_support_audit.py`; the row hashes are in
> `world-variant-gate-rows-sha256-2026-10-22.txt` (rows are in `~/.cache/yupi-scratch/variant-gate-2026-10-22/`).

## Gates

- **V0 regression:** passed. The modified `kind_uncertainty_split.py` reproduces the pinned `split-v2` rows
  byte-for-byte, and the §3.1 ceiling gate holds.
- **Audit-script regression:** passed. On the pinned rows, `variant_support_audit.py` reproduces §4.2 (r1 pure 14.6 %,
  coin 92 %, matched high-gap 1.4 %; r3 coin 86 %, 0.9 %). At V0 the device template equals the coin exactly.
- **V3 support:** passed. The reachable states and transition edges are identical to V0 at both ε.

## Predictions (r1–r3, both ε, both binnings)

| | declared | observed (range over cells) | verdict |
|---|---|---|---|
| P1 (V1, V2) | device template ≥ 80 % of pure | 84.8–96.3 % | **holds** |
| P2 (V1, V2) | matched high-gap < 5 % | 0.47–1.60 % | **holds** |
| P3 (V3), by rule | device template ≥ 80 % of pure | 85.3–93.7 % | holds |
| P3 (V3), by law | largest single law < 70 % of pure | 76.9–86.9 % | **fails** |
| P4 (V3) | matched high-gap < 5 % | 0.68–1.74 % | **holds** |
| P5 (all) | kind-ambiguous share at δ = 0.05 ≥ 10 % | V1 19–27 %, V2 12–18 %, V3 14–24 % | **holds** |

**P3 failed.** I predicted that occupancy dependence would split the device's pure side into two laws (1/4 and 1/2),
so that grouping by law and grouping by kernel rule would disagree. They do not. One law still carries 77–87 % of the
pure side. Checked at r1 ε = 1 and r3 ε = ½: the dominant law is the one-pending coin (¼ IO_COMPLETE, ¾ DISPATCH)
at 83 % and 80 %, and the two-pending coin (½, ½) carries only 3–4 %. Pure classes are those where the occupancy is
known, and these are overwhelmingly one-pending.
The audit procedure's step 3 ("by law or by kernel rule") therefore needs no disambiguation in this world. The
prediction's premise was wrong, not the procedure.

## Decision rule

The rule: a variant supports the contrast if the matched high-gap side is ≥ 10 % and ≥ 3 laws each carry ≥ 10 % of
the matched pure mass. **No variant supports it.** The matched high-gap side is below 2 % everywhere, and exactly one
law carries ≥ 10 % of the matched pure mass in every cell of every variant.

So, as declared: the contrast's narrowness survives every completion-probability reparameterisation tried (scalar
1/4, 1/2, and occupancy-dependent). It belongs to *where* the kernel places randomness, not to the value 1/3. §4.2's
"a consequence of design" is now a tested statement for this family of variants. **No learner is trained.** This is
the audit used prospectively: it ran on candidate worlds before any training, and each world failed the declared
adequacy criterion for this contrast.

*Correction (same day, after the reviewer's second read): an earlier version ended "it said the training would not
answer its question". That is stronger than the experiment shows. The two failures differ in kind:*
- *The **mass** failure (matched high-gap < 2 %) is a fact about the natural evaluation population. A targeted sampling
  scheme could oversample the matched classes, which are rare but not absent.*
- *The **composition** failure (exactly one law carries ≥ 10 % of the matched pure mass) does not yield to sampling.
  However many examples are drawn, the pure side is one mechanism, so a contrast drawn from these worlds compares
  "withheld state" with "the device coin", not with randomness in general.*

*Also: a passed audit would have been permission to proceed, one necessary condition met, and not evidence that the
inference would be valid. A failed audit can rule out a planned comparison under its declared criteria; a passed
audit cannot rule one in.*

## Unpredicted: where the kind ambiguity sets in moves with the world

v3 reported that kind ambiguity sets in between δ = 0.01 and 0.02. I declared no prediction for it.

| variant | ε = 1, r1–r3: δ = 0.01 / 0.02 / 0.05 | ε = ½, r1–r3: δ = 0.01 / 0.02 / 0.05 |
|---|---|---|
| V0 (paper) | 0.1–0.2 % / 14–17 % / 16–18 % | 0.6–1.7 % / 17–19 % / 20–23 % |
| V1 (1/4) | 0.0–0.1 % / 16–20 % / 19–22 % | 0.9–2.1 % / 20–23 % / 23–27 % |
| V2 (1/2) | 0.0–0.2 % / 10–12 % / 12–14 % | 0.4–1.2 % / 12–14 % / 16–18 % |
| V3 (occupancy) | 11–13 % / 12–16 % / 14–17 % | r1 14 %, r2–r3 1–2 % / r1 17 %, r2–r3 3–5 % / 20–24 % |

*V0's row is the paper's §4.3 table, quoted as v3 printed it, not recomputed.*

Under scalar reparameterisation the onset stays between 0.01 and 0.02. Under V3 it moves in both directions:
- **Below 0.01 at ε = 1, and at ε = ½ on r1.** An observer unsure of the queue's occupancy faces a mixture of the 1/4
  and 1/2 coins. Such a class has withheld state, yet its law can sit within 0.01 of a pure coin.
- **Up to between 0.02 and 0.05 at ε = ½ on r2 and r3,** where the richer interfaces apparently reveal the occupancy
  more often. That the r1-to-r2 jump at ε = ½ is this large has not been checked mechanistically. Treat it as
  observed, not explained.

The precision at which "is this uncertainty random or withheld?" becomes ambiguous is therefore a property of the
world's mechanisms, not a constant of the method.

## What this means for v4

- The blind read asked whether the support finding belongs to this world. Answer: across these variants, the
  narrowness is structural (where randomness enters), and the numbers move with p while the conclusion does not.
- The precision onset is world-specific. v4 should present it as an example of what the sweep measures, not as a
  finding that transfers.
- This is the clearest instance of the reviewer's distinction: "the methodological principles may generalize
  without the numerical phenomena generalizing". The audit's verdict generalised across worlds; one of its numbers
  did not.
- Not tested: variants that add randomness in new places (e.g. per-thread dispatch weights, which change the
  binding structure). The structural conclusion is scoped to completion-probability variants.
