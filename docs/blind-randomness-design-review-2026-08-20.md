# Blind Review — Randomness and Reproducibility Design

**Status:** non-governing review artifact. No finding in this document is an
enacted fact merely because the reviewer stated it.

**Date:** 2026-08-20

**Reviewed artifact:**
`docs/superpowers/specs/2026-08-20-randomness-reproducibility-threat-model-design.md`
(commit `4ce102d`, stamped by `d19ef25`).

## Provenance and blinding

Tony proposed asking an agent for an undirected review so that the review
would not inherit the authors' focus on the seed-inference problem. Codex
spawned a context-isolated subagent with no conversation history. Its complete
prompt was:

> Please review
> docs/superpowers/specs/2026-08-20-randomness-reproducibility-threat-model-design.md
> and let us know what you find.

The subagent made no file changes. Its complete report follows.

## Reviewer report

I found four issues:

- **[P1] The design conflates computational pseudorandomness with the exact
  enacted law.** A uniformly chosen 256-bit root permits only probabilities
  that are multiples of $2^{-256}$; it cannot even realize the enacted $1/3$
  device probability literally exactly. Derived streams are pseudorandom, not
  statistically independent, and rejection sampling is unbiased only under
  an ideal random-bit source. Therefore the seed-marginal corpus law is not
  exactly the law enumerated by the “exact truth oracle.” Lines 60–70 and
  especially 92–94 of the reviewed design should explicitly declare a
  computational-indistinguishability idealization and qualify “exact,” or
  adopt a recorded true-entropy-tape design.

- **[P1] The public provenance does not bind the generated corpus.** The
  public manifest commits only to the private manifest at lines 100–105.
  Without canonical content hashes or a Merkle root for the records and other
  public artifacts, a corpus can be replaced after generation and later seed
  disclosure cannot establish which corpus was actually evaluated.

- **[P2] KDF domain separation lacks an injective encoding contract.** The
  fields listed at lines 60–67 can collide under naive concatenation,
  normalization differences, or overlapping free-form labels. The design
  should require a canonical length-prefixed or fixed-schema encoding, a
  registered label namespace, exact KDF parameter placement, and
  key/nonce/counter derivation. Reference vectors alone do not prove domain
  injectivity.

- **[P2] The replay requirement understates its inputs.** Verification item 1
  says private manifest plus configuration is sufficient at lines 137–140,
  while the public metadata itself depends on source commit and dependency
  versions. Byte-identical replay also requires canonical serialization,
  deterministic ordering/concurrency, runtime/platform constraints, and the
  complete public/private manifest pair. Those inputs should be stated
  explicitly.

Overall, the threat separation is sound, but I would not adopt the design
until the exact-law versus computational-sampler distinction is resolved.

## Disposition at capture time

Codex assessed all four findings as technically applicable to the reviewed
design. They have not yet been remediated. In particular, the design remains
explicitly non-enacted; no corpus generator was changed under it.
