# What we know is true: an inventory (2026-10-09)

> **Status: INVENTORY, not a paper plan.** Written by the owning instance after Tony's observation of 2026-10-09:
> *"we are trying to fit the truth to the paper, rather than finding something true and making that the center of
> the paper."* Each item gives the claim, its evidential status, what it is evidence *for*, and what it is not.
> No section structure is implied. The paper's centre is chosen from this list after review, not before. Items
> the instance did not re-audit this session are marked as such.

Status labels:
- **EXACT:** a computed identity, gated.
- **CONFIRMATORY:** a stamped prediction, passed on held-out models.
- **ROBUST:** survives the model-as-unit check, but was not pre-registered.
- **EXPLORATORY.**
- **NEGATIVE:** something we tried to establish and could not.

## A. The information side (what each trace interface makes knowable)

| # | claim | status | evidence |
|---|---|---|---|
| A1 | Exact Bayes ceilings per observer, cross-validated by two independent paths over 8,542,940 posteriors | EXACT | two-path gate (skeleton v0.1 §2). Not re-audited this session |
| A2 | Interface value exists only where the window hides history. At the frozen law (40, 8, 2) there are four distinct regimes, and the top rung is thin (r4 − r3 ≥ 0, at most 4e-4 bits) | EXACT | pattern-ceiling raws. Corrections C1 of skeleton v0.1 |
| A3 | Richer interfaces move next-KIND information from far lags to near lags. The lag profiles of ι_m cross | EXACT | implicit-information raws, 2026-09-28 |
| A4 | Interventions can hold the ceiling identical class by class while moving information: relay Δι 0.094, decoy 0.068 (correlation 0.29 with the relay's, in other classes), self-copy exactly 0 | EXACT | relay and three-arm exact sides, gates A–C |
| A5 | Classes with no long-range KIND information (ι4 = 0, in the ι4 ≤ 0.01 region) have only three next-KIND posterior shapes (H ∈ {0, 0.918, ≈1.5}) | EXACT | plateau-stratified results §2 |

*Evidence for:* the instrument measures exactly what each interface carries and where it carries it. *Not
evidence for:* anything about learners.

## B. The learner side (small decoder-only transformers, d = 128, this world)

| # | claim | status | evidence |
|---|---|---|---|
| B1 | Within every cell, KIND excess rises with exact long-range information ι_long. The same holds for actor identity, and at the converged budget | CONFIRMATORY (21/21, 36/36, 24/24, 24/24 held-out runs). *These were per-model tests, so they do not inherit the seed-mean precision problem* | d1, actor, converged-ladder verdicts |
| B2 | The cross-cell ordering of interfaces by ι fails (C3) | CONFIRMATORY, NEGATIVE | converged-ladder verdict |
| B3 | Moving information closer does not relieve the cost in proportion to the move. The gain is V-shaped in Δι (it tracks \|Δι\|, not the sign) | CONFIRMATORY (rejection), ROBUST in shape: 8/9 to 9/9 seed pairings. Magnitudes and t-values are unreliable (corrections of 2026-10-05) | relay verdict + CORRECTIONS |
| B4 | No relay gain where ι4 = 0. Gain where ι4 > 0, persisting at 15 epochs | EXPLORATORY, and partly checked per pairing (contrasts positive 9/9 at 15 ep) | V diagnosis, prereg-review addendum |
| B5 | The transformer's KIND excess is 1.5–4.7× smaller than a count table over the ceiling's own classes, wherever entities exist | EXPLORATORY, one baseline (Witten–Bell). The transformer side is a seed mean | count-baseline results |
| B6 | Between-seed variance dominates at 5 epochs. r1 seed means are 0.0244, 0.0244 and 0.0152, and the relay gain is about 0 against the lucky seed. Seed-matched pairs share variance (window correlation 0.52–0.62 vs 0.35–0.46) | ROBUST as a description of 3 + 3 models. Its interpretation as a mixed training phase is EXPLORATORY | prereg-review addendum |
| B7 | Belief geometry: the exact next-kind belief is linearly decodable after one record and less accessible with context. The first block extracts a roughly fixed amount whatever the interface | per skeleton v0.1 §5. **Not re-audited this session.** Its probes may need the model-as-unit check too | learner-belief raws, 2026-09-24 |

## C. What output-level measurement could not establish, in a world where the information is exact

| # | claim | status | evidence |
|---|---|---|---|
| C1 | The plateau ("cost tracks the presence of long-range dependence, not its amount") is **not identified**: the classes being compared have no common support in posterior shape | NEGATIVE, reviewed by two families | plateau-stratified results |
| C2 | Which long-range regressor indexes the learner (H-free vs H-acct) is unresolved under trivial fixed effects | NEGATIVE, reviewed | relay-free-difficulty CORRECTIONS |
| C3 | Whether the relay helps by *moving information* or through *binding content* is **not identified** by relay, decoy and self-copy arms. The zero-entropy control cannot absorb arm-specific effects of carrying a variable field. Three two-family review rounds, with wrong-attribution rates of 14–33 % under planted rivals | NEGATIVE (design-level), reviewed ×3 | three-arm prereg review record |
| C4 | Seed-mean, window-level inference overstated precision in every paired analysis from 09-30 to 10-05 | NEGATIVE (method), adopted | prereg review §1 |

*What C is evidence for (a candidate, not adopted):* even with exact posteriors, exact ceilings and interventions
whose ceilings are identical, a learner's **outputs** under-determine **which information it used**. Every attempt
to read mechanism off excess needed an intervention, and each intervention brought confounds of its own. This is
the ayllu's impossibility result (Mason & Anand) at small scale, in the most favourable setting available.

*What C is not:* a theorem, or evidence about large models. It is also possibly a property of *these analyses*,
not of learners in general. Separating the two is the first thing a reviewer of this inventory should attack.

## D. Assets built and not yet used

- A fresh paired corpus (run 0582ffbeb4693d27, episodes disjoint from everything analysed), at r1, r1R, r1D and
  r1S. Every pairing gate passes.
- 12 trained pilot models: seeds 101–103 × four rungs, 15 epochs. They are **blind**. Only their between-seed sds
  have been read. **Decision (owner, 2026-10-09):** they stay blind until the centre is chosen from this
  inventory. If that centre does not need them confirmatory-clean, they are unblinded as exploratory data by a
  recorded decision.
- Scorer v3 with strict provenance gates, and severity simulations v1–v4. The machinery is reusable.

## E. Candidate centres, for discussion and not decided

1. **Learner observability (C plus B1–B3).** The information side is exact. The learner's shortfall tracks it
   within cells, but the outputs cannot say *why*. Each identification attempt fails in an instructive, exactly
   measurable way. This connects directly to the impossibility result and to the exposure/use gap. Risk: it can
   read as a list of failures unless C is shown to be about learners and not about analysts.
2. **The exact information picture (A), with learners as a measured case (B1, B5).** The original framing. It is
   solid. Risk: B1's lesson ("small models lose long-range information") is something readers already believe.
3. **Acquisition dynamics (B6).** When does a learner acquire long-range structure, class by class, against exact
   ceilings? Least developed, and possibly the most novel. It needs new data: per-checkpoint censuses across
   seeds.
