# Literature check: transition randomness vs. observation gap in activations

2026-10-15. Uncommitted working note. The candidate question: the observer's next-event entropy splits exactly as H(next | h) = R + G, where R = E[H(next | S) | h] is transition randomness and G = I(next; S | h) is the observation gap. Do small transformers represent R and G differently? Does the output distribution expose the split? Does post-training change it? This note complements `literature-exposure-2026-10-15.md`, which covers entropy calibration and post-training, and does not repeat it. Every arXiv id below was checked against the arXiv API today. Unless a line says otherwise, I read the abstract only.

## 0. A constraint on the output-side question

**Bergna, Depeweg & Hernández-Lobato, "Decoupled PFNs: Identifiable Epistemic-Aleatoric Decomposition via Structured Synthetic Priors"**, arXiv:2605.06413, May 2026. They state that the epistemic/aleatoric split "is not identifiable in general from the posterior predictive distribution alone, even when that distribution is known exactly." For Yupana this follows directly: P(next | h) = Σ_s b(s) P(next | s) is a mixture, and many pairs (belief, kernel) yield the same marginal. So "does the next-event output expose R vs. G?" has the answer *no, by construction*, for any single-step readout. The question only has content relative to a query class: multi-step continuations, where G shows up as dependence between successive future events, or interventional queries. That is the same move CLAUDE.md already asks for in the exposure-gap definition. The representation-side question is not affected, because activations can carry b(h), and b(h) determines both R and G given the known kernel. Bergna et al. get the split by **supervising separate heads** with generator labels, in regression (PFNs), not by probing an unsupervised sequence model. **They pre-empt the identifiability observation. They do not pre-empt the Yupi question.** Cite them for the observation.

## 1. Belief-state geometry (Simplex and allied work)

- **Shai et al., "Transformers represent belief state geometry…"**, arXiv:2405.15943; also Piotrowski et al. 2502.01954, Levinson 2604.02685, Farrugia-Roberts 2606.01302. Linear regression from activations to the exact mixed-state belief, on HMMs (Mess3, RRXOR). Belief is the object that determines both R and G, but the paper does not split predictive uncertainty into components. Does not pre-empt.
- **Riechers, Bigelow, Alt & Shai, "Next-token pretraining implies in-context learning"**, arXiv:2505.18373. Gives exact information-theoretic predictions of how context-dependent loss converges toward the entropy rate. This is the nearest aggregate, output-side analogue of the split. In computational-mechanics terms the asymptote is h_μ and the excess is synchronization. My inference, not theirs: h_μ = H(next | causal state) does not depend on the presentation, while R = E[H(next | S)] is tied to Yupana's physical state S. For a non-synchronizing presentation, G stays positive asymptotically, and that is the gap Yupi cares about. They do not probe activations for the components. Partial overlap, not pre-emption.
- **Shai et al., "Transformers learn factored representations"**, arXiv:2602.02385. The authors list on arXiv is Shai, Amdahl-Culleton, Christensen, Bigelow, Rosas, Boyd, Alt, Ray, …. This closes the `[check: authors]` in paper1-references. The paper is about factor subspaces. It includes noise that breaks conditional independence, but it does not decompose uncertainty.
- **Balcells, Lee, Rastogi, Riechers, Shai & Poncini, "LLMs Develop Belief State Geometry In-Context"**, arXiv:2609.17376. Belief probes in pretrained LLMs, R² 0.83–0.99, with patching and steering. No split. The base-vs-instruct question flagged in the exposure note is still open.

## 2. The entropy axis (Misra/Dalal line)

- **Agarwal, Dalal & Misra, arXiv:2512.22471.** The value manifold is "parameterized by posterior entropy". The exposure note (full read) records no aleatoric/epistemic decomposition. Its two wind tunnels sit at opposite poles: bijection elimination is essentially pure G, and HMM filtering is mixed. Nobody has asked whether the entropy coordinate is the same across those two regimes.
- **Agarwal, Dalal & Misra, "Geometric Scaling of Bayesian Inference in LLMs"**, arXiv:2512.23752. In Pythia, Phi-2, Llama-3 and Mistral, a single dominant last-layer value axis correlates with **total predictive entropy**. Ablating it disrupts the uncertainty geometry, though not proportionally to Bayesian behaviour ("a privileged readout of uncertainty"). **This is the closest representation-side precedent.** It finds one entropy axis and does not test whether that axis encodes R + G jointly or only one of them. A direct Yupi test: regress activations on R and on G separately, and ask whether the 2512.23752 axis aligns with their sum.
- **Dalal, Misra & Parekh, "Bayesian Wind Tunnels for Model Selection"**, arXiv:2607.19379. Class-posterior entropy against the exact optimum. No split.
- **Stolfo et al., "Confidence Regulation Neurons"**, arXiv:2406.16254. Entropy neurons scale logits through a null space of the unembedding. This is a mechanism for total output entropy. Two follow-up questions for Yupi: do entropy neurons respond to G, to R, or to both, and does post-training retune them?

## 3. Aleatoric vs. epistemic probes in LLMs (no ground truth)

- **Ahdritz, Qin, Vyas, Barak & Edelman**, arXiv:2402.03563. Linear probes predict when a larger proxy model is confident, which serves as a proxy for "knowable" uncertainty. Conceptually this is the closest work, and its limitation is that it has no exact ground truth. Note that its "epistemic" means the *model's* ignorance (a gap in learner capacity), which corresponds to Yupi's representation gap, not to G. Yupi's G is a property of the interface and is irreducible for any learner. The distinction deserves a sentence in any paper.
- **Kossen et al., "Semantic Entropy Probes"**, arXiv:2406.15927. Hidden states predict semantic entropy, i.e. total uncertainty. No split.
- **Tomov, Fuchsgruber, Wollschläger & Günnemann, "The Illusion of Certainty"**, arXiv:2511.04418. Ground-truth answer distributions are estimated from co-occurrence data. Uncertainty estimators, including probes on internal representations, collapse to near chance once aleatoric uncertainty is nonzero. The authors give a theoretical explanation for predictive and ensemble estimators. This supports the claim that existing probes conflate R and G, and it is a negative-result precedent worth citing.
- **Jayasekera et al., "Variational Uncertainty Decomposition for ICL"**, arXiv:2509.02327 (NeurIPS 2025). Bounds aleatoric and epistemic uncertainty through auxiliary queries, output-side only. **Chung et al.**, arXiv:2606.19353: "self-function vectors" for estimating aleatoric uncertainty in ICL, with a controlled synthetic protocol. **Qchohi & Rossi**, arXiv:2604.12434: epistemic uncertainty collapses at grokking, using approximate posteriors. **Dakhmouche et al.**, arXiv:2510.04108: Bayesian linear probes for total uncertainty. None of these has an exact ceiling, a hidden *dynamical* state, or an interface manipulation.

## 4. Bayesian ICL with a known latent variable

- **Xie, Raghunathan, Liang & Ma**, arXiv:2111.02080 (GINC, a mixture of HMMs). The latent concept plays the role of S. The paper measures behavioural ICL accuracy, not activations, and does not split uncertainty.
- **Falck et al.**, arXiv:2406.00793, and **Müller et al. (PFNs)**, arXiv:2112.10510: already covered in the exposure note.
- **Dai et al.**, arXiv:2506.07298 and arXiv:2607.22646. LLMs on synthetic HMMs approach the optimum, and a "Principal Activations Probe" tracks how representations shift across HMM regimes. That makes the HMM, not the view of a fixed HMM, the manipulated variable. No split.

## 5. Varying the observation channel of a fixed hidden process

I found no work that holds the hidden process fixed and varies the observation channel to separate R from G. The near misses vary something else:
- Siems et al., arXiv:2602.14814: the density of state-reveals in a PFSA. This is interface-like, but it has no exact entropy decomposition and no probe split.
- arXiv:2605.20824 (the exposure note): an "ambiguous-emission" HMM family. This varies the HMM itself.
- Qchohi & Rossi vary context noise. Bergna et al. vary the noise function. Both are regression priors, not views of a dynamical system.

This agrees with the 2026-10-09 Q3 verdict.

## Verdict

**Is the R/G split in activations already studied?** Not as posed. Three neighbouring results are established: (a) belief states are linearly decodable, which makes the split *recoverable in principle* from activations (Shai; Balcells); (b) there is an axis aligned with total entropy (2512.22471, 2512.23752; entropy neurons); (c) aleatoric/epistemic probes exist, but without ground truth, and on ambiguous data they fail (Ahdritz; Tomov). I found no paper that regresses activations separately on exact R and exact G, or that asks whether the entropy axis carries their sum or a single component.

**Is the output-side question done?** It has a known answer for single-step readouts: R and G are not identifiable (Bergna et al.; in an HMM this follows from the mixture structure). Frame Yupi's output question as exposure relative to a multi-step query class, or it reduces to that fact.

**Is the vary-the-interface design done?** No. That has held through three passes. **Post-training effects on the split:** nothing found. The exposure note's open items apply: the full text of 2609.17376 (base vs. instruct), and the Misra Paper III, still unlocated.

**Re-check before any priority claim:** 2512.23752's full text (whether they condition the entropy axis on wind-tunnel type) and 2605.06413's full text.
