# Randomness, Reproducibility, and Seed-Secrecy Design

**Status:** approved in dialogue with Tony, 2026-08-20. This document is a
design note, not an enacted amendment to either M1 statute and not an
implementation claim.

## Purpose

Yupana needs sampled episodes that are reproducible by an auditor without
letting a learned observer predict future stochastic choices by recovering the
sampler's internal state. The simulator implementation must not silently turn
the intended experiment into one about recovering a non-cryptographic PRNG.

The solution separates three concerns:

1. the enacted transition kernel defines the scientific probability law;
2. an entropy-seeded cryptographic generator selects one realization of that
   law; and
3. a private provenance record permits exact replay of that realization.

## Actors and threat model

### Exact truth oracle

The exact filter and independent path enumerator know the declared stochastic
law and compute exact posteriors over the finite Yupana state and horizon. They
do not enumerate sampler seeds, and sampler state is not added to the latent
Yupana state tuple. Their computational bounds remain the enacted support,
transition, memory, and horizon budgets.

### Learned observer

The learned observer may know the complete simulator source, generator
algorithm, transition law, and experimental protocol. It receives only the
records exposed by its interface. It does not receive the run seed, derived
keys, private replay manifest, generator memory, or side-channel access to the
generation process. It has the finite computation, context, and training
budget of the model under study.

### Reproduction auditor

An authorized auditor may receive the private replay manifest and reproduce a
run exactly. Evaluation seeds remain secret until the corresponding evaluation
is retired. Revealing a seed closes that seed for future blinded evaluation.

### Out of scope

This design does not defend against compromise of the generation host, access
to process memory or private manifests, malicious generator dependencies,
unbounded brute-force search, or seed disclosure. Those are security-system
threats rather than Yupana observation-interface conditions.

## Randomness architecture

At the start of each corpus-generation run, obtain a 256-bit root seed from the
operating system's initialized cryptographic randomness interface. Failure to
obtain entropy is fatal; there is no timestamp, process-id, constant, or silent
fallback seed.

Derive independent subkeys from the root using a specified cryptographic key
derivation function. The derivation input includes at least:

- format and derivation version;
- run identifier and dataset split;
- episode index; and
- mechanism label: scheduler, device, D8 channel, workload, or another enacted
  stochastic mechanism.

The resulting separation prevents observations of one mechanism from exposing
the stream used by another and prevents an implementation change in one stream
from shifting every later random choice. Episode boundaries provide the normal
rekey boundary. Random reseeding intervals are excluded from the baseline: they
would add a hidden stochastic process without serving the current research
question.

The stream generator must be a publicly specified, cryptographically secure,
deterministic construction supplied by a maintained cryptographic library.
AES-256 in a defined counter/DRBG construction and ChaCha20 are acceptable
families; "AES-256 RNG" alone is not a complete algorithm specification. The
implementation plan will select one based on library quality, stable reference
vectors, deterministic cross-platform replay, and simple unbiased integer
sampling. Yupana will not implement a cryptographic primitive itself.

## Sampling exact transition weights

The kernel continues to return exact `Fraction` probabilities. The sampler
maps cryptographic stream bytes to an integer in the required finite range
using rejection sampling or an equivalent unbiased construction, then selects
from cumulative integer weights. Modulo reduction with a biased remainder and
floating-point conversion are prohibited.

The seed chooses a realized path; it does not alter transition probabilities.
The exact filter and enumerator continue to branch over the enacted kernel and
remain independent of the sampling implementation.

## Provenance and disclosure

Each run produces two manifests:

- A public manifest records the source commit, configuration, algorithm and
  derivation versions, split and episode ranges, dependency versions, and a
  cryptographic commitment to the private manifest.
- A private manifest records the root seed and everything needed for exact
  replay. It must not appear in model inputs, ordinary logs, filenames,
  exceptions, public artifacts, or source control.

Training and evaluation use different run seeds and derived key domains.
Published training seeds may support open reproduction. A held-out evaluation
seed is disclosed only after that evaluation is no longer used as a blind
test; subsequent evaluations receive new entropy-generated seeds.

## Relationship to D8 and the D1 contingency

Seed secrecy prevents accidental prediction of future sampled choices. It does
not prevent an observation history from revealing the current latent state.
Consequently it complements rather than replaces the experimental levers:

- D8 tests how much causal history the observation channel exposes;
- scheduler and device entropy define stochastic branching in the world; and
- cryptographic sampling ensures that the implementation does not expose a
  shortcut through PRNG-state recovery.

No claim that D8 restores rung separation, and no Part C contingency choice,
is made by this design.

## Failure behavior

Generation stops rather than falling back when entropy acquisition, key
derivation, manifest protection, or deterministic replay checks fail. A seed
collision or duplicate run identifier is reported and requires a new run. A
private-manifest leak retires every evaluation derived from that root seed.

## Verification requirements

Before adoption, the implementation must demonstrate:

1. identical private manifest and configuration produce byte-identical random
   draws, trajectories, records, and public metadata;
2. published reference vectors fix the generator, derivation, and integer-draw
   behavior across supported platforms;
3. episode and mechanism domain labels produce isolated streams;
4. transition selection preserves exact integer weights without floats or
   modulo bias;
5. seeds and derived keys are absent from emitted observations and public logs;
6. train and evaluation domains cannot reuse a subkey accidentally; and
7. existing exact filter-versus-enumerator gates remain unchanged and green.

Statistical randomness tests may detect gross implementation defects but are
not evidence of cryptographic security and are not substitutes for reference
vectors or use of a vetted construction.

## Explicit non-decisions

This design freezes the threat model and architecture, not the cryptographic
library or choice between an approved AES- or ChaCha-family construction. It
does not change the enacted stochastic kernel, D8 semantics, corpus size,
episode horizon, or seed-disclosure policy for a future public benchmark; those
must be chosen in their respective plans or governance documents.
