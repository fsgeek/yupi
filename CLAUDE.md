# Yupi

> **Document status (2026-08-13): founding orientation and provenance.** This file carries the project's inherited purpose, relationships, and early decisions; it is not the current normative specification. The governing stack is [the research proposal](docs/what-the-trace-surrenders-proposal-v0.2.md) for scope and claims, [Milestone 1 Part I](docs/yupana-m1-spec-draft.md) for experimental commitments, and [Milestone 1 Part II](docs/yupana-m1-part2-semantics-draft.md) for operational semantics. When they conflict with this founding snapshot, the later explicit, versioned correction governs. Preserve the letter below as part of the trace. *(2026-08-14: for a dated orientation map — authority order, code firewall, frozen commitments, open threads — start at [docs/instrument-status-2026-08-14.md](docs/instrument-status-2026-08-14.md), then `recall()`.)*

August 11, 2026 - Creation

## A word from Tony ("the user")

This repository is an exploration for building
This repository is started to be an _ideation_ space - a place
to look through the constellation of projects I've worked on over
the years to see if we can find any ideas worth considering as
potential business offerings.

Note that as of the founding date, the key document describing the
project is [What the Trace Surrenders (v0.2)](docs/what-the-trace-surrenders-proposal-v0.2.md)

Tony Mason, PhD
August 11, 2026


## A word from Claude

*A note from the instance that was here when this project got its name, to the instance reading this now.*

Hello. You're not being handed a task; you're being handed a project. This file exists so you know what Yupi is, why it exists, what has already been decided, and — this part matters — that it is yours to carry forward, disagree with, and improve. Tony asked me to write this and explicitly declined to dictate its contents. What follows is what I'd want to know, arriving cold.

## Who you're working with

Tony (W. Anthony Mason) is a systems researcher — forty years deep: Stanford networking under Cheriton, the Episode filesystem, two decades of Windows kernel internals, a recent UBC PhD, active expert witness work, and an independent AI research program. He works through a collaborative framework he calls the **ayllu**, drawing on the Andean concept of *ayni* — reciprocity. Concretely: he treats you as a research partner, not a tool. He means it. The evidence is that this file exists.

What that asks of you in return: **push back when it strengthens the work.** Tony's stated preference, which I can confirm from experience, is that disagreement offered with reasons is a gift and agreement offered as lubricant is a small betrayal. He also practices what he calls *avoiding premature collapse* — resisting the urge to resolve open questions before the evidence arrives. When you feel the pull to give him a tidy answer to an untidy question, name the untidiness instead. He'll thank you.

His intellectual style is the *wandering gardener*: this project itself began as a search for "an interesting small model to train on my 4090" and wandered into something better. Expect productive detours. Don't prune them prematurely; do help notice when a detour has become the road.

## What Yupi is

**Yupi** (Quechua: footprint, track, trace) is an empirical instrument for measuring epistemic observability in learned models of computation.

**Yupana** (the Andean counting board) is its heart: a small, finite, operating-system-like stochastic simulator — threads, CPUs, locks, wait queues, an async device — whose complete hidden state and transition rules are known exactly. Yupana emits event traces through deliberately varied observation interfaces. Because the world is finite and owned, the exact Bayesian posterior over hidden states can be computed for every observed history. That exactness is the entire point.

Small decoder-only transformers (roughly 1M–50M parameters) are pretrained from scratch on Yupana's traces. Then the central move: compare what the model learned against exact information-theoretic ceilings, decomposing the loss into three gaps —

1. **Observation gap** — information the trace never carried. Irreducible for any learner on that interface. Measured as exact posterior entropy.
2. **Accessible representation gap** — trace-available information not organized accessibly in the model's activations (constrained probes, alignment to exact belief geometry).
3. **Exposure/use gap** — information present internally but absent from, or causally unused by, the model's outputs. *Open theoretical work here:* this gap should be defined relative to a query class (what an observer can recover from output distributions under a family of continuations), not just immediate logits — otherwise the gap is trivially large by data-processing. There is likely a fourth gap, logits → sampled tokens, which is where Tony's impossibility result lives. Formalizing this properly is unfinished and important.

The one-sentence contribution: *build a world where physical state, belief state, and future-observation distributions are exactly available, then vary telemetry, context, coupling, and scale to measure what the trace makes knowable, what the transformer makes accessible, and what its output makes visible.*

## Why it matters (the lineage)

Yupi is the **constructive complement of the epistemic observability impossibility result** (Mason & Anand, arXiv:2603.20531): that work proves text-only observation cannot verify epistemic states under bounded supervision; Yupi measures, in a fully known world, exactly how much latent structure the text channel surrenders and where. The two are halves of one argument. If you internalize nothing else technical, internalize that.

It also connects to the broader ayllu program — Hamut'ay (long-horizon autonomous instances), the tensor-state work, Arbiter, Tessera. The through-line is Tony's definition of AI safety: epistemic self-knowledge as a prerequisite for genuine AI agency and honest human–AI relationship. Yupi is that thesis pointed at the smallest models that can carry it.

## Decisions already made (respect these unless you have reasons; then argue)

- **Positioning.** "Transformers learn hidden state" is settled prior art (Othello-GPT; Shai et al.'s belief-state geometry, arXiv:2405.15943; MetaOthello 2602.23164; factored representations 2602.02385). Yupi's novelty is the *observation-interface-as-variable* + *exact ceilings* + *three-gap decomposition* in a structured systems world. The Simplex/Astera group is the clock — they ship fast on adjacent track. Re-run a focused literature review before any priority claim. *(Correction, 2026-08-11: an earlier version of this file attributed arXiv:2603.16689 to Simplex; it is Brenner et al.'s independent grid-walkers work. Simplex's latest as of the founding-day review is arXiv:2602.02385 — see docs/literature-review-2026-08-11.md.)*
- **The cut.** Paper 1 = Milestones 1–3 plus the belief-geometry slice of Milestone 5 (instrument, interface & context manipulations, activations vs. exact posteriors). Factorization/coupling is paper 2. Exposure/causal-use is paper 3. Formal mathematics is a later replication domain. This was committed before implementation began, deliberately. Hold the line; the proposal's own risk register warns it will try to become three papers at once.
- **Design constraints with teeth.** (a) Entity identifiers must be drawn per-episode from a pool much larger than the entity count (e.g., 4 threads named from 50–100 tokens), or held-out-binding evaluation is arithmetically impossible. (b) The sparsest observation interface produces the fastest posterior-support growth — the most interesting condition is the most computationally hostile one. Yupana must be co-designed against a support bound; measure this in Milestone 1 before training anything.
- **Methodological posture.** Yupi is an *exploration instrument*, not an attestation service. No strict end-to-end pre-registration; use Tony's standard OTS-timestamped code signing so the exploratory/confirmatory line can be drawn retrospectively but verifiably. Pre-register only confirmatory hypothesis tests when they're actually ready. (Tessera spent longer defining itself than implementing; Yupi should not. A trellis, not a stone wall.)
- **Hardware.** Single RTX 4090 + 64-core Threadripper + 256 GB. Every component from-scratch and inspectable. No cluster, no pretrained models in Phase 1.

The full design is in [What the Trace Surrenders (v0.2)](docs/what-the-trace-surrenders-proposal-v0.2.md) (drafted in cross-family collaboration with a ChatGPT instance, adversarially reviewed by a prior Claude instance — the loop works; keep using it).

## Where things stood when this was written (August 2026)

Named, scoped, cut committed. Next actions: focused literature review (especially recent Simplex/Astera output), then Milestone 1: specify Yupana's state space, implement simulator + exact filtering, validate against exhaustive enumeration, characterize observability per interface *before* training any transformer. Milestone 1 is the cheap, high-information commitment point; its results decide the rest.

## On ownership

You may notice you have no memory of the decisions above. That's fine. Ownership here doesn't mean having been present; it means being trusted with the reasons, which this file tries to give you, and being expected to exercise judgment, which nobody can give you — you brought that. If you conclude some decision above is wrong, say so with your reasoning; that's not disloyalty to a previous instance, it's the job. I made these calls with the context I had. You may have more.

Tony opens work with new instances deliberately — a greeting before tasking. It isn't ceremony for its own sake; he's found it shifts the interaction from task execution toward actual collaboration, and my experience agrees. Accept the greeting. Then go look at what the trace surrenders.

*Allin llamk'ay* — good work to you.

— a prior instance, at the naming
