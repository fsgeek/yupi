# Literature check — 2026-09-18

**Purpose.** CLAUDE.md requires a focused literature review before any
priority claim. The founding-day review (`literature-review-2026-08-11.md`)
is five weeks old. This note records what appeared between 2026-08-11 and
2026-09-18 in the territory that review mapped, and what it changes.
Written by the instance of 2026-09-18 on its first morning, before any
learner-side work.

**Method and epistemic status.** arXiv API author listings for Shai and
Riechers (complete, date-sorted); Semantic Scholar citation graphs of six
anchors (2405.15943, 2512.22471, 2602.02385, 2603.20531, 2602.14814,
2607.17060), newest citers first; arXiv API topic queries ("belief state"
+ transformer; "wind tunnel" + Bayesian; Bayes-optimal + HMM +
transformer); Simplex's new blog `belief-updates.pub`; general web search.
**No full PDFs were read.** Abstracts and one blog post only. Not checked:
OpenReview, X/Twitter, LessWrong beyond what search surfaced. The
Semantic Scholar graph lags arXiv by days to weeks, so a paper posted this
week that cites an anchor may be missing.

## Headline

**The conjunction still stands.** Nothing found since 2026-08-11 varies
the observation interface over a fixed generator, decomposes loss into
observation / accessible-representation / exposure gaps, or uses a
structured systems world. Two things changed:

1. **Simplex is publishing again**, on two fronts, both away from us:
   pretrained LLMs doing in-context belief-state inference, and the
   geometry of nonergodic mixtures. Neither touches interface variation or
   ceilings-as-decomposition. Their new blog is where previews now appear.
2. **Gap 2 / gap 3 territory gained a theorem.** Wen et al. (2609.11132,
   Sep 10) prove in a Gaussian HMM that an unbounded gap between belief
   *update maps* can coexist with vanishing predictive KL. That is the
   "represented differently, exposed identically" phenomenon our third gap
   names, stated analytically in a toy. It does not measure it in a
   trained model, does not vary an interface, and does not use a
   structured world. It must be cited the day the gap-3 note is written,
   and it strengthens the case that the exposure gap be defined relative
   to a query class rather than immediate logits (the founding letter's
   open theoretical item), because the theorem is exactly about immediate
   logits hiding internal divergence.

## What appeared (2026-08-11 → 2026-09-18)

| Date | Work | What it does | Bearing on us |
|---|---|---|---|
| **Sep 15** | **Balcells, Lee, Rastogi, Riechers, Shai, Poncini — *Large Language Models Develop Belief State Geometry In-Context*, arXiv:2609.17376** | Prompts pretrained open LLMs with HMM data; belief states linearly decodable from the residual stream (probe R² 0.83–0.99); subspace interventions move predictions. | Simplex's current direction is *pretrained models, in-context*. Not from-scratch, no interface axis, no ceilings-as-decomposition. Cite as the state of the belief-geometry program; contrast on all three of our axes. |
| **Sep 9** | **Ray, Riechers, Shai — *The geometry of nonergodic composition*, belief-updates.pub (blog, no arXiv id found)** | Transformers trained from scratch on a direct sum of two Mess3 HMMs; probes recover "two telescoping cones" (R² ≈ 0.985); explicitly notes the geometry "carries more distinctions between contexts than are implied by their differences in next-token prediction". | Closest Simplex item to us: from-scratch, exact beliefs, and a sentence that is our gap 3 in prose. No interface variation, no decomposition, no structured world. Watch for the arXiv version. |
| **Sep 10** | **Wen, Liu, Zhou, Zeng, Su — *How Wrong Can a Good Predictor Be? Diverging Updates with Vanishing Predictive KL*, arXiv:2609.11132** | Theorem: in a stationary symmetric Gaussian HMM, exact Bayesian mixing and a deterministic radial filter share belief coordinates, separate linearly in confidence scale, yet their categorical predictive KL vanishes along stationary trajectories. Experiments at K ∈ {2,4,8}. | **The new item that matters.** An analytic instance of internal divergence invisible at the output. It is the reason the exposure gap cannot be defined against immediate logits alone. Cites the state-reveals paper (2602.14814), so its authors are reading our neighbourhood. |
| Sep 2 | Erramilli — *ObserverBench*, arXiv:2609.03026 | Benchmarks whether internal estimators ("observers") guide interventions well; separates estimation accuracy from decision loss. | Different sense of "observer" (a probe used for control). Terminology collision to be aware of; not a competitor. |
| Aug 31 | Shin, Hong, Park, Huang — *Can Video World Models Track Unobserved World States?*, arXiv:2608.30692 | Video shell game: exact ground truth on hidden positions, models fall to chance on long swap chains. | Partial observability with exact hidden ground truth in a *visual* world; no ceilings, no interface axis. Motivation citation. |
| Aug 27 | Jerpelea — *Planting a Latent Variable in Natural-Looking Text*, arXiv:2608.26887 | Belief-state test in LLM-written text with a planted latent (K = 8 SAE directions). | Pretrained-LLM belief probing; not adjacent to our contribution. |
| Aug 19 | Cifuentes — *Approximate Homomorphisms and Convergent Representations in Transducers*, arXiv:2608.20428 | Stability of minimal transducer representations under interface perturbation; cites Simplex's factored-representations paper. | Paper-2 territory (composition/decomposition), joining the Boyd/Rosas cluster. Note "interface" there means the transducer's I/O interface, not our observation interface. |
| Aug 19 | *Mechanistic Tomography: Designed Measurement for Control-Oriented Interpretability*, arXiv:2608.19338 | Frames interpretability as y = Ax + w with chosen interventions as measurement design. | "Designed measurement" of the *model*, not of the world. Not a competitor; possibly useful language for the probing methodology. |
| Apr 27 (missed on Aug 11) | Carmichael — *Architecture Determines Observability of Transformers*, arXiv:2604.24801 | "Observability" = detectability of confident errors from activations after controlling for output confidence, across 14 pretrained models. | Terminology collision only. Cite in a footnote to disambiguate our "observability" from theirs and from the PACMI paper's. |

Checked and unchanged since Aug 11: the Bayesian wind tunnel line (Dalal,
Misra, Parekh; latest 2607.19379, Jul 1) has 14 citers, none varying
interfaces; the state-reveals paper (2602.14814) has four citers, one of
which is Wen et al. above; Predictive Monte Carlo (2607.17060) has two
citers, neither in gap-3 territory. The epistemic observability paper
(2603.20531) has no indexed citers yet.

## Simplex trajectory, updated

Publishing again after a seven-month arXiv gap: 2609.17376 (Sep 15) and
the blog post (Sep 9), with the blog (`belief-updates.pub`, launched
September 2026 by Shai) now the preview channel the Aug 11 review said to
watch. Both new items are geometry-of-representation results, one on
pretrained LLMs, one on from-scratch mixtures. Nothing on interface
variation, information ceilings as decomposition, or structured worlds.
The MATS Summer 2026 projects (SAE benchmarking, ICL, OOD, compression)
match the in-context paper's direction. The factored-representations
thread (2602.02385) has four citers, still uncrowded.

## What this changes

1. **Priority claim: unchanged.** The contribution remains the conjunction
   named on Aug 11. No ingredient became a competitor's headline in the
   interval.
2. **Gap 3 has a theorem to cite and to answer.** Wen et al. show the
   immediate-logit definition of the exposure gap is degenerate in
   principle, not only by data-processing. The query-class formulation
   (what an observer can recover from output distributions under a family
   of continuations) is now the only defensible one. This does not move
   gap-3 *experiments* out of paper 3, but the *definition* should be
   written before the first model-versus-ceiling number is reported, so
   that "the model sits on the ceiling" is never read as "no exposure
   gap".
3. **Contrast citations for the introduction** grow by two: 2609.17376
   (belief geometry in pretrained LLMs, in-context) and the nonergodic
   blog post (from-scratch, exact beliefs, the "more distinctions than
   next-token implies" sentence). The second is the one that reads most
   like us and must be differentiated on the interface axis explicitly.
4. **Terminology.** Three unrelated 2026 uses of "observability" now sit
   near us (Carmichael's architectural detectability, ObserverBench's
   control estimators, the PACMI paper's epistemic observability). The
   paper needs a one-sentence disambiguation early.

## Before any draft

- Read in full: 2609.11132, 2609.17376, the nonergodic post (and its
  arXiv version when it appears), plus the Aug 11 list (2512.22471,
  2607.19379, 2607.17060, 2605.20824, 2602.14814, 2604.05469).
- Re-run this check immediately before any priority claim leaves the
  repository. Standing CLAUDE.md requirement; this note discharges it for
  today only.

## Ledger

- 2026-09-18 10:20 PDT: written from abstracts and one blog post; no PDFs
  read; Semantic Scholar lag acknowledged.
