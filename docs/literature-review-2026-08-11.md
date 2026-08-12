# Focused Literature Review — August 11, 2026

**Purpose.** CLAUDE.md commits to a focused literature review before any priority claim, with particular attention to the Simplex/Astera group. This document synthesizes two parallel surveys run on the founding day: one on the Simplex/Riechers/Shai program specifically, one on the adjacent territory (synthetic-world interpretability, interface manipulation, neural belief filtering, probing methodology, information ceilings, variable binding).

**Method and epistemic status.** Web search + arXiv abstract fetches; complete date-sorted arXiv author listings for Riechers and Shai; Semantic Scholar citation graphs for the three belief-geometry anchors; the Simplex website; MATS Summer 2026 stream pages. **No full PDFs were read.** Everything post-January 2026 is reported from abstracts and snippets only. Not checked: Alignment Forum/LessWrong 2026 posts (historically where Simplex previews results), X/Twitter, OpenReview, camera-ready queues. arXiv indexing lag may hide late-July/early-August postings. The top papers below must be read in full before v0.3 is drafted.

## Headline

**The composite novelty claim stands as of today — but only as a conjunction.** Every individual ingredient now has published neighbors, most within the last nine months. What remains unclaimed:

1. **Observation-interface variation over a fixed generator** — not found anywhere, including targeted searches on observation/emission-function variation. Genuinely unclaimed.
2. **Three-way decomposition** (observation / accessible-representation / exposure-use) — not found. Two-term floor-plus-excess decompositions exist; "represented but not exposed" is claimed by no one.
3. **OS-like structured world** (threads, locks, queues, devices, entity binding) — not found. Grid worlds, Othello variants, poker, and code traces exist; nothing systems-like.

The introduction can no longer present "a world with exact posterior ceilings" or "excess loss over Bayes" as contributions — both are published. The contribution is the conjunction: **interface-as-variable × exact ceilings × three-gap decomposition × structured systems world.**

## Correction to CLAUDE.md

arXiv:2603.16689 is **not** a Simplex paper. It is Brenner, Knösche & Scherf, *Predictive Statistics Shape Emergent World Representations of Grid Walkers* (Mar 2026, v2 Jun 2026) — an independent group extending belief-geometry ideas to grid worlds. The recency marker was misattributed. Simplex itself has published nothing on arXiv since *Transformers Learn Factored Representations* (arXiv:2602.02385, Feb 2, 2026) — verified against both founders' complete author listings and the Simplex publication page.

## Threat board (most pressing first)

| # | Work | What it takes off the table | What it leaves |
|---|------|------------------------------|----------------|
| 1 | **"Bayesian wind tunnels"** — Misra/Dalal group, Columbia: arXiv:2512.22471 (v5 May 2026), arXiv:2607.19379 (**Jul 2026**), arXiv:2512.23752 | Exact-posterior-ceiling environments as a named, actively published method brand; transformers shown to reproduce exact posteriors to 10⁻³–10⁻⁴ bits | No interface variation; no gap decomposition; abstract math worlds, not systems |
| 2 | **Predictive Monte Carlo** — Aswadi, Ma, Wei: arXiv:2607.17060 (**Jul 19, 2026**) | Recovering a transformer's implicit prior/posterior **from output behavior alone** — the conceptual core of the exposure/use gap's query-class framing | No exact ceilings, no known-world comparison, toy exchangeable families. **But this is gap-3 territory, three weeks old — the gap-3 formalization is the piece under real time pressure** |
| 3 | **Markovian circuit tracing** — arXiv:2605.20824 (May 2026; authorship unverified) | Excess-loss-over-Bayes measurement + belief probing + counterfactual patching validated against exact HMM counterfactuals | Flat HMMs; no interfaces; no three-way decomposition |
| 4 | **Grid walkers** — Brenner et al., arXiv:2603.16689 | Belief geometry in a structured-ish world; architecture (transformer vs RNN) as variable, with differing geometry at matched accuracy | No interface axis, no ceilings-as-decomposition |
| 5 | **State reveals in code traces** — Siems et al., arXiv:2602.14814 | Nearest neighbor to interface variation: "state reveal" density varied in training data; capability degrades as reveals sparsen | One-dimensional, no ceilings, aimed at architecture comparison. Cite prominently |
| 6 | **Excess-loss decomposition** — Dalla Riva, arXiv:2604.05469 | Cross-entropy = irreducible entropy floor + JS excess term, in small "laboratory organism" LMs | Two terms only; no posteriors over a simulator; no interface axis |
| 7 | **Transducer decomposition cluster** — Boyd, Rosas et al.: arXiv:2512.02193, arXiv:2504.04608 | Composition/decomposition theory for world models (Simplex's social network) | Threatens **Paper 2** (factorization/coupling), not Paper 1. Engage when Paper 2 is framed |
| 8 | **MetaOthello** — arXiv:2602.23164 (v2 Jul 2026) | Multiple generators, shared syntax, causal transfer | Varies the *generator* — the inverse of our move. Contrast citation |

Lower relevance, checked and dismissed: SAE belief-subspace discovery in Gemma-2 (2604.02685), poker world beliefs (2512.23722), next-latent-prediction training objectives (2511.05963), simplicial scaling (2606.01302), neural-Bayesian-filter architectures (2512.18489, 2510.03614, 2602.10743), program-trace execution models (2603.09951, 2602.07672, 2509.25073), Atari world-model probing (2603.21546), PGN-vs-FEN input-format contrasts (2510.27009).

## Simplex trajectory

Quiet on arXiv since February. The MATS Summer 2026 stream (Riechers & Shai) lists scholar projects — SAE benchmarking, ICL, OOD generalization, representation compression — **none on interface variation or loss-gap decomposition**. A fall-2026 wave of Simplex-branded workshop papers is plausible. Citation note: 2405.15943 has ~68 citations; 2602.02385 has only 2 — the factored-representations thread is not yet crowded. The unchecked Alignment Forum is the most likely place a recent result hides.

## Implications for the project

1. **Reposition the contribution statement** (v0.3): from ingredients to the conjunction. Cite wind tunnels, Markovian circuit tracing, grid walkers, and state-reveals from day one and differentiate explicitly.
2. **Gap-3 formalization is time-critical.** Wei's group is one conceptual step from the query-class definition of the exposure gap. Holding the paper cut (exposure/use experiments remain Paper 3) is compatible with writing and OTS-stamping a short formal note *defining* the gap relative to a query class now. Decision owner: Tony.
3. **Ground gap 2 in V-information** (Xu et al., ICLR 2020, arXiv:2002.10689) — the existing formal language for "accessible under computational constraints." The accessible-representation gap should be stated in these terms rather than reinvented.
4. **Adopt current probing best practice**: tuned linear/MLP baselines alongside any SAE analysis (arXiv:2502.16681); report completeness *and* selectivity for causal interventions (arXiv:2408.15510); mean-projection/LEACE for concept removal (ACL Findings 2025).
5. **Representation–performance dissociation precedent**: Kuo et al., NeurIPS 2025 (arXiv:2510.22039) show equal task performance with different belief fidelity in meta-RL — a cousin of the accessible-representation gap worth citing in motivation.
6. **Variable-binding mechanism analysis** reusable from Wu, Geiger, Millière (arXiv:2505.20896); nobody evaluates held-out binding against exact posteriors — Yupana's entity-pool design keeps that claim.

## Before v0.3 is drafted

- Read in full: 2512.22471, 2607.19379, 2607.17060, 2605.20824, 2602.14814, 2604.05469.
- Check Alignment Forum for Simplex 2026 posts.
- Verify authorship/venue of 2605.20824 and 2604.05469.
- Re-run this survey immediately before preregistration of any confirmatory test (standing CLAUDE.md requirement).
