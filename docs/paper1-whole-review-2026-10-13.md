# Whole-draft review of paper 1 (2026-10-13, evening): record and dispositions

> Reviewed: §1–§6 as of d274bbf, plus Figure 4a. Read-only adversarial reviews, run in parallel by a Claude
> subagent and by Codex. Both reviewers' overall view: **a defensible exact-instrument paper with a measured learner
> case; not ready for external review; a credible workshop paper once fixed; main track would need scale and
> baselines.** Owning instance. **(R)** marks a finding the owner reproduced; **(rev.)** marks one adopted on the
> reviewer's word.

## Decision on scope (owner)

**Paper 1 is written as an instrument-and-method paper, at workshop scope first.** It reports the exact side as the
result. The learner half is labelled throughout as a single-configuration case study, with every claim at its
status. Two cheap learner additions are worth their GPU time, because both reviewers named them and both bear on
whether the case study is idiosyncratic:
- a recurrent baseline (GRU);
- one larger model size.

These run as separate pre-registered waves. More seeds, a second world variant and producer-side telemetry belong
to the next paper. The decision can be revisited if Tony sees it differently. Venue is his call as much as mine.

## Findings and dispositions

| # | finding | by | disposition |
|---|---|---|---|
| W1 | No related-work section. ι_m resembles block-entropy convergence (Crutchfield & Feldman 2003). Neighbours: memory–surprisal and locality (Hahn, Degen & Futrell 2021; Futrell), belief-state geometry (Shai et al.; Simplex), Othello-GPT, learned log readers. The novelty sentence needs a demonstrated distinctive capability | Claude 1, Codex 1 | **Adopt.** Write §7 related work from *verified* sources. Restate contribution 1 per Codex's sentence. Show the worked comparison prior methods cannot do: one fixed system, several interfaces, class-matched rewrites |
| W2 | §4e/§1 keep pre-correction inference: the "CONFIRMATORY" Δι₄ rejection rests on window-level se; "8–9/9 pairings"; p = 1/20 used as primary; §6's p floor | Claude 2, Codex 3/9 | **Adopt.** The Δι₄ rejection is now stated as a failed pre-registered prediction with window-level precision only, no se quoted, and shape described per model (3 vs 3). Paired p is primary everywhere |
| W3 | The §1 framing is not earned. Log20 is invoked but state entropy and the predictive ceiling are never computed side by side. The placement claim is untested at the producer | Claude 3/Q5, Codex 2 | **Adopt.** §1 leads with the measurement problem, and placement becomes the motivating question with its first test's outcome stated. **Add a per-rung table of state entropy vs predictive ceiling vs ι profile** (Part I's split exists), or drop the Log20 contrast |
| W4 | The exhaustive 8.5 M-window gate sits beside the pattern observer, but pattern ceilings are validated separately (small-world exhaustive, frozen-law sampled) | Codex 4 | **Adopt.** §2.3 gets separate validation statements for structural windows, pattern posteriors, prefix ceilings and the lag identity |
| W5 | Gate letters: A = KIND-marginal equality, B = whole-record probability multiset, C = independent construction plus brute force | Codex 5, Claude 22 | **Adopt**, checking against `pattern_ceiling.py:124` |
| W6 | The ACTOR target, its ceiling and its shortfall are undefined. The ι_A\|K lower-bound construction is unexplained | Codex 6, Claude 12 | **Adopt.** Define these in §2.5 |
| W7 | KIND scoring: continuation-conditioned (PAD removed), other vocabulary mass kept, termination scored separately, normalisation over 0.85 mass | Codex 7 | **Adopt**, read from `evaluate.py` |
| W8 | Injectivity: one place says "proved", another "argued"; it is tested at r4 only and does not imply r1 | Claude 9/10, Codex 8 | **Adopt.** "Argued (proof sketch)" everywhere. Scope to the structural observer. **Run the frozen-world reset test at r1** (cheap, CPU) |
| W9 | The 2×2 table omits r1, the C2 baseline. Map every contrast to its arms | Codex 10 | **Adopt:** a five-arm table |
| W10 | "Differs between fields" / "not a reallocation" exceed unresolved ACTOR contrasts | Claude 8, Codex 11 | **Adopt:** "the KIND pattern changes across recipes; ACTOR evidence is inconclusive" |
| W11 | §2.5 says every position is trained, which the follow-up recipes contradict | Codex 12 | **Adopt** |
| W12 | "Convergence" needs diagnostics | Claude 4, Codex 13 | **Adopt:** say "at 15 epochs" unless convergence curves are shown. Plot validation curves for the ladder (committed logs) |
| W13 | Seed and held-out inventory is inconsistent | Claude 19, Codex 14 | **Adopt:** one experiment-by-cell table |
| W14 | The FE/coarse-cluster check is KIND-only | Codex 15 | **Adopt:** label it, and run the actor version (CPU) |
| W15 | r0 count wording is backwards at ε = 1 | Codex 16, Claude 28 | **Adopt (R):** ratio > 1 means the transformer is better. Fix §4d and §1 |
| W16 | §5.2 says "reversed" where the source says "unresolved" | Codex 17 | **Adopt** |
| W17 | "Self-copy carries zero entropy" is underspecified | Codex 18 | **Adopt:** zero *conditional on the record's own KIND* |
| W18 | §5's universal explanation and its "settling" remedies | Codex 19 | **Adopt:** specific causes, *candidate* designs |
| W19 | Instrument spec: pseudocode, worked window, costs (state/class/frontier counts, runtime, memory), reproducibility manifest | Codex 21 | **Adopt** as an appendix, from the D4 pricing raws |
| W20 | §4c omits the passed r0-lowest ordering (C4 of the converged ladder) | Claude 5 | **Adopt** |
| W21 | §5.3 is stale against the 2×2; §5.1's plateau wording too | Claude 6/15, Codex 22 | **Adopt** |
| W22 | Effect sizes need proportion (shortfall as % of ceiling; what would matter) | Claude 17 | **Adopt** |
| W23 | Contribution 1: separate what holds by construction (monotone ladder; ceiling fixed under window functions) from what was found (the crossing) | Claude 18 | **Adopt.** A second world is deferred to paper 2 and named as a limit |
| W24 | Mason & Anand paragraph: ε collision, no payoff | Claude 14 | **Adopt:** move to related work and rename their tolerance |
| W25 | Rounded lag values used as exact rankings (r4 slightly above r3 at lags 1–3); profile sums from rounded entries | Codex 23 | **Adopt.** Recompute from unrounded values |
| W26 | Minor stale items: version labels, filenames, "three to four" rounds, pilots "unopened" (their sds were read), the §3.1 (rev.) provenance, the §3.2 wording slip, overloaded labels, no title/abstract | both | **Adopt** |
| W27 | Claude 7: "the count table, which has no notion of distance, shows the same signature, so B1 is partly class rarity, not location" | Claude 7 | **Partly adopted.** The premise is wrong: Witten–Bell backs off to shorter-suffix estimates, which are wrong exactly where ι_m > 0, so it is locality-biased by construction (v0.1 §4d said this). The caveat that the association may partly reflect class rarity or complexity stands, and §4a says so |
| W28 | Main-track demands: scale, seeds, GRU, positions other than k = 7, a data-size curve | Claude 4, Codex 20 | **Partly adopted:** GRU and one larger size (see scope decision). The rest is named in §6 |

## Order of work

1. Text fixes that need no new computation (W2, W5–W7, W9–W11, W13, W15–W18, W20–W26). Section versions bump to
   v0.3.
2. Cheap CPU checks: injectivity at r1 (W8), the actor FE check (W14), unrounded profile sums (W25), validation
   curves for convergence (W12), the state-entropy vs ceiling table (W3).
3. Related work from verified sources (W1, W24).
4. Pre-registered GRU and larger-model waves (W28).
5. Instrument appendix (W19).
6. A third two-family review of the whole draft.
