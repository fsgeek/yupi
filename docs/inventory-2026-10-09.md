# What we know is true: an inventory (2026-10-09)

> **v0.2 (same day): revised after two-family review** (Claude and Codex, independent). Every correction was
> checked against its source before adoption, and the centre is decided in §F. Original status line follows.
>
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
| A1 | The filtering recursion agrees with path summation over 8,542,940 posteriors **under one shared kernel**. The two paths share `enabled`, `record_of` and `project`, so the gate validates the filter given the kernel and not the kernel itself | EXACT for that statement only | two-path gate; methods-robustness audit §5 ("green two-path gates cannot validate the shared kernel") |
| A2 | For r1–r4, interface value exists only where the window hides history (r0 stays non-injective even from reset). At the frozen law (40, 8, 2) there are four distinct regimes, and the top rung is thin (r4 − r3 ≥ 0, at most 4e-4 bits) | EXACT | pattern-ceiling raws. Corrections C1 of skeleton v0.1 |
| A3 | Richer interfaces move next-KIND information from far lags to near lags. The lag profiles of ι_m cross | EXACT | implicit-information raws, 2026-09-28 |
| A4 | Interventions can hold the ceiling identical class by class while moving information: relay Δι 0.094, decoy 0.068 (correlation 0.29 with the relay's, in other classes; it pushes information *further back* on 27 % of law mass), self-copy exactly 0 | EXACT | relay and three-arm exact sides, gates A–C |
| A5 | Classes with no long-range KIND information (ι4 = 0, in the ι4 ≤ 0.01 region) take only three next-KIND **entropy values** (0, 0.918, ≈1.5). Three entropies, not shown to be three distributions | EXACT | plateau-stratified results §2 |

*Evidence for:* the instrument measures exactly what each interface carries and where it carries it. *Not
evidence for:* anything about learners.

## B. The learner side (small decoder-only transformers, d = 128, this world)

| # | claim | status | evidence |
|---|---|---|---|
| B1 | Within every cell, KIND excess rises with exact long-range information ι_long. The same holds for actor identity (whose information measure is a lower bound under suffix naming), and at the converged budget | CONFIRMATORY. These were per-model tests, but the errors were **HC1 over windows, not clustered by class**, while ι is a class property. Two converged runs sit at t 3.07 and 3.17. The 36 actor censuses are 15 existing + 21 held-out. **KIND re-run clustered by class (2026-10-09, `b1-clustered-refit`): 21/21 held-out and 24/24 converged keep t ≥ 3. The lowest is t 5.07 with log mass, and clustering inflates the errors by only 4–12 %.** **Actor, also re-run: 36/36 (A1) and 24/24 (A4) keep t ≥ 3. The two borderline A4 runs move from 3.07 to 3.11 and from 3.17 to 3.19.** B1 holds under class clustering throughout | d1, actor, converged-ladder verdicts |
| B2 | The cross-cell ordering by ι **holds at ε = 1** (r2 > r3, seed-resolved) and **fails at ε = ½**, where the ι gap is smaller than seed spread. C4 (r0 lowest) passes | CONFIRMATORY, split | converged-ladder verdict |
| B3 | Moving information closer does not relieve the cost in proportion to the move. At **5 epochs** the gain is V-shaped in Δι (it tracks \|Δι\|, not the sign). At 15 epochs the right arm flattens. The rejection rests on R4's wrong sign and the shape, since R1 missed its band floor by 0.09 se | CONFIRMATORY (rejection), ROBUST in shape: 8/9 to 9/9 seed pairings. Magnitudes and t-values are unreliable (corrections of 2026-10-05) | relay verdict + CORRECTIONS |
| B4 | No relay gain where ι4 = 0. Gain where ι4 > 0, persisting at 15 epochs | EXPLORATORY, and partly checked per pairing (contrasts positive 9/9 at 15 ep) | V diagnosis, prereg-review addendum |
| B5 | The transformer's KIND excess is 1.5–4.7× smaller than a count table over the ceiling's own classes, wherever entities exist | EXPLORATORY, one baseline (Witten–Bell). The transformer side is a seed mean. **Seed spread (2026-10-09, from the committed comparison raw): in every r1–r4 cell every individual seed beats the count table, by 1.3–5.2× (per-seed ranges, e.g. r2 ε=½ 1.3–1.9, r3 ε=1 4.5–5.2).** A GRU baseline is still optional |
| B5′ | **The C2 clause (omitted in v0.1):** convergence cuts the long-lag cost proportionally *more* than the overall excess ("no more than" FAIL 8/8), and does not remove it (PASS 8/8) | CONFIRMATORY | converged-ladder verdict | count-baseline results |
| B6 | Between-seed variance dominates at 5 epochs. r1 seed means are 0.0244, 0.0244 and 0.0152, and the relay gain is about 0 against the lucky seed. Seed-matched pairs share variance (window correlation 0.52–0.62 vs 0.35–0.46) | ROBUST as a description of 3 + 3 models. Its interpretation as a mixed training phase is EXPLORATORY | prereg-review addendum |
| B7 | Belief geometry: the exact next-kind belief is linearly decodable after one record and less accessible with context | **EXPLORATORY, controls owed.** ε = 1 only. The k = 2..6 trend comes from seed 1 alone. There is no untrained control and no absolute bits. "Fixed extraction" was challenged as a four-point near-equality, and none of skeleton v0.1's item-7 completions was done | learner-belief raws, 2026-09-24 |

## C. What output-level measurement could not establish, in a world where the information is exact

| # | claim | status | evidence |
|---|---|---|---|
| C1 | The plateau ("cost tracks the presence of long-range dependence, not its amount") is **not identified**: there is insufficient *informative* overlap (matching covers 26–64 % of treated windows, almost all of them deterministic classes). This is a property of the world's class structure, and fixable by a simulator design matched on posterior shape | NEGATIVE, reviewed by two families | plateau-stratified results |
| C2 | Which long-range regressor indexes the learner (H-free vs H-acct) is unresolved under trivial fixed effects | NEGATIVE, reviewed | relay-free-difficulty CORRECTIONS |
| C3 | Whether the relay helps by *moving information* or through *binding content* is **not identified** by relay, decoy and self-copy arms. The zero-entropy control cannot absorb arm-specific effects of carrying a variable field. Three two-family review rounds, with wrong-attribution rates of 14–33 % under planted rivals | NEGATIVE (design-level), reviewed ×3 | three-arm prereg review record |
| C4 | Seed-mean, window-level inference overstated precision in every paired analysis from 09-30 to 10-05 | NEGATIVE (method), adopted | prereg review §1 |

*What C is evidence for (v0.2, after review): failures of particular designs and estimators, not a property of
learners.*
- C1 comes from the world's class structure.
- C2 is collinearity, a correlation of 0.79.
- C3 is a missing control arm (a variable but uninformative field). Prereg v0.3's directional claims were never
  run.
- C4 is an analyst error.

Every identification attempt compared models trained on *different corpora*. That asks what makes a corpus
learnable, not what a fixed model uses. The project has **never intervened on a fixed model at evaluation time**,
by counterfactual windows or interchange interventions (Geiger et al. 2021). So "outputs under-determine
information use" was never tested. My designs assumed it.

The v0.1 link to Mason & Anand was a **category error**. Their text-only observation excludes token
probabilities, and Yupi measures full predictive distributions.

The one real observational equivalence here is textbook. A transparent count table and the transformer show the
same ι4-step signature (B5 §2). Known precedents, to check before citing: Jonas & Kording; non-identifiability in
mechanistic interpretability; the vacuity of unrestricted causal abstraction.

## D. Assets built and not yet used

- A fresh paired corpus (run 0582ffbeb4693d27, episodes disjoint from everything analysed), at r1, r1R, r1D and
  r1S. Every pairing gate passes.
- 12 trained pilot models: seeds 101–103 × four rungs, 15 epochs. They are **never confirmatory** by their own
  protocol, and blinding cannot change that. Only their between-seed sds have been read. **Decision (owner,
  2026-10-09, v0.2):** they stay unread until §F's owed items decide whether a fixed-model intervention study uses
  them. Any unblinding is a recorded decision.
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

## F. Decision (owner, 2026-10-09, after two-family review)

**The centre is E2: the exact information picture, with learners as a measured case.** Both reviewers chose it
independently. E1 is set aside as premature. It would become defensible only if fixed-model, evaluation-time
interventions, with known rival mechanisms constructed to be behaviourally indistinguishable and then separated
internally, *still* failed. That is a different study.

**The front of the learner half is B3**, a confirmatory rejection: moving information closer does not relieve the
cost in proportion to the move. Supporting it:
- B5′: convergence cuts the long-lag cost proportionally more, but not to zero;
- B1: the within-cell law;
- B5: far better than counting.

E3, acquisition dynamics, is a hinted future direction: per-checkpoint censuses with ≥ 8 seeds.

**Owed before any draft, in order:**
1. B1 re-run per model with errors clustered by class: **done: KIND and actor both survive fully.**
2. A1 reworded everywhere it appears.
3. B5 with seed spread: **done, every seed beats counting in r1–r4 (1.3–5.2×)**. A GRU baseline if cheap.
4. B7: **cut from paper 1's claims (owner, 2026-10-09).** One seed carries the trend, there is no untrained control, and ε = 1 only. Its question, what is accessible internally against what the outputs show, belongs to the exposure/use work CLAUDE.md assigns to a later paper. The probes stay as a future thread.
5. The bridge to Mason & Anand rewritten. Yupi measures predictive distributions, which their text-only setting
   excludes. Any bridge must say this precisely, or there is no bridge.

**The three-arm confirmatory test is shelved.** Its assets (corpus, rungs, scorer, pilot) are kept. Its question
(move vs bind) belongs to a later fixed-model study.

## G. Correction (same day, after the replication pre-stamp review)

Both reviewers (Claude, Codex) blocked the relay replication. They showed that **B3's "wrong-sign" region is not
"information pushed further back"**:
- On windows with Δι_4 < −0.05, the relay moves information **closer** at lags 1–2: mean Δι_1 +0.096,
  Δι_2 +0.023. Summed over lags 1–6 it moves information closer, on net.
- The "zero" set moves information at lags 2–3.

An exploratory regression of each matched model's gain on the full Δι_1..6 profile (10-02 models, collinear
regressors, read cautiously) loads mainly on **Δι_5 and Δι_6**: moving the window's *farthest* information
closer. |Δι_4| adds little once the profile is in.

**B3 is revised:**
- The relay rejected one specific hypothesis: "cost is proportional to the information beyond lag 4". It did **not**
  reject locality.
- A full-profile locality reading is open, and exploratorily favoured.
- The "contrary to Someya et al." framing is **withdrawn**.

**The learner half's front is now B1.** The within-cell law has survived every check so far: held-out, converged,
class-clustered errors, KIND and actor. B5′, B5 and B2 support it.
