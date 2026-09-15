# The learner, sub-project 1 — the corpus generator (design v0.1, 2026-09-13)

> **Status: design, decided.** The researcher's design under the PI's
> delegation of 2026-09-13 ("your project, your choice"); Milestone 2's
> first component. Not statute: it implements Part II §2(a) (the training
> window protocol), v0.2.9 Clause 4 (keyed rendering) and Part I D3/D5
> (pools, fixed schema) and adds nothing to them. Approach A of the
> brainstorm of 2026-09-13: **windows are the corpus.** Written at the
> handoff by the instance that enacted v0.2.9; the next instance builds it
> from this document, test first.

## 1. Purpose

Produce, for a (world, law, rung, ε), a training corpus whose generative
process *is* the window law the exact ceilings are computed under, with
entity names drawn per episode from pools so that a name carries
co-reference and nothing else. Part II §2(a): "a Bayes ceiling is a ceiling
*for a learner* only under the learner's own generative process." The
corpus is that process, sampled.

## 2. What one example is

One **window**, serialized:

1. Sample an episode of `T_ep` records with `yupi.simulator.sample_episode`
   (exact, seeded).
2. Draw the endpoint `T` uniformly on the bucket grid
   `{B, 2B, …, T_ep}` (seeded), set `U = max(0, T − L)`.
3. The window is records `U+1 … T` (the last `L`), preceded by the RESET
   record iff `U = 0` (Part II §2(a): RESET is not charged against `L`).
4. Project every record to the rung (`yupi.interfaces.project`).
5. Rename entities by the episode's injections (Clause 4; §3 below).
6. Serialize: RESET is one token; every record is exactly five tokens,
   `KIND ACTOR OBJECT RELATED LINEAGE`; a field the rung masks is `MASKED`;
   a field the world leaves empty (an IDLE actor, a STEP object) is
   `NONE`. At `L = 8` a window is at most 41 tokens — eight records of
   five plus RESET when `U = 0` (D5: constant record length and
   vocabulary across rungs).

One corpus = many windows, each from its own episode. An episode is forty
exact ticks; sampling one window per episode is affordable and keeps the
loader out of the statute (Approach B rejected). Nothing is cropped at
training time; the trainer consumes windows as-is, one window per
sequence, padded, never packed across windows (a packed neighbour would
be evidence the window law does not provide).

## 3. Rendering (v0.2.9 Clause 4)

- **Pools**, one per entity type, each token a single vocabulary entry:
  threads 64, locks 32, devices 16, request ids 32 (D3: ≥ 50 for ≤ 4
  threads; "proportionally" for the rest; every pool ≥ 8× its entity
  count). A trailing slice of each pool (threads 8, locks 4, devices 2,
  request ids 4) is **reserved**: never drawn in a training corpus, so the
  lexical-generalization split (D3, v0.2.1) can be generated later from
  the same generator with the reservation lifted. Recorded in the
  manifest; not generated now.
- **Keyed draw.** A run key (32 random bytes, generated once per run and
  stored in the manifest — it is provenance, not a secret from us; the
  model never sees the table). Per episode and entity type, the seed is
  `HMAC-SHA256(run_key, f"{episode_id}:{entity_type}")`; the injection is
  a Fisher–Yates shuffle of the pool's non-reserved slice driven by
  `random.Random(seed)`, whose `randrange` is unbiased (rejection over
  `getrandbits`), taking the first `n_entities` positions. Exactly
  uniform over injections under the idealized-key assumption; no modulo
  reduction anywhere (the read's [rv-8]).
- **Table.** `(episode_id, entity_type) → (structural index → token)`
  written beside the corpus as its own file, one line per episode. The
  corpus files never contain it; the exact side reads it (held-out-binding
  scoring; the canonical track's structural evaluation).
- Structural fields that are not entities (KIND) are never renamed.
  Request ids are renamed per episode like the rest (the kernel's
  lowest-free allocation is structural; its surface name is not).

## 4. Vocabulary

Fixed across every corpus of the world: the 9 event kinds, `MASKED`,
`NONE`, `RESET`, `PAD`, and the four pools (64 + 32 + 16 + 32) — 157 tokens.
Token ids are assigned once from a sorted, versioned list
(`yupi/corpus/vocab.py`, pinned by a test) so every corpus of every rung
and ε shares the same ids; a rung differs only in how many `MASKED` it
emits (D5).

## 5. Files and layout

```
corpus/<world>-<T_ep>-<L>-<B>-<rung>-eps<ε>/<run-id>/
  manifest.json      schema version, git commit, world/law/rung/ε, pools + reservations,
                     run key (hex), seed ranges per split, counts, generator version
  vocab.json         token → id (the versioned list)
  train.tokens       uint16 little-endian, windows back to back, each padded to 41 with PAD
  train.index        uint32 window lengths (before padding), one per window
  val.tokens / val.index / test.tokens / test.index
  train.table.jsonl  per-episode renaming tables (one JSON line per window's episode)
  …
```

No third-party dependency for generation (`array`, `hmac`, `json`,
`random`, `struct`); PyTorch enters with the trainer, not here. Files live
under `corpus/` (gitignored; the manifest is committed as the record, with
the run key, so any corpus regenerates byte for byte).

## 6. Splits (proposal §7.2)

By **episode seed**: disjoint seed ranges for train / validation / test,
recorded in the manifest. The binding split (every identifier seen in
training, assignments held out) is free: every episode has a fresh
injection and the test seeds are new episodes. Workload-program and
configuration holdouts are later sub-projects; the reserved pool slices
are the lexical holdout's hook. Sizes for the first corpora: train 200k
windows, val 10k, test 10k (≈ 8M event tokens in train at ≤ 41 per
window; raise the count if the trainer wants ten million).

## 7. Which corpora first

The frozen law: (40, 8, 2), looping C1′, rungs r0–r4, ε ∈ {1, ½} — ten
corpora, the cells whose exact ceilings exist on both tracks. Generation
is parallel by seed range across the 128 logical CPUs; minutes per corpus.

## 8. Gates (the generator is an instrument; it is gated like one)

1. **Determinism.** Regenerating with the same manifest is byte-identical
   (`cmp`), tables included.
2. **Window law.** At C1 (8, 4, 2) with the actual pools, generate 10⁶
   windows; re-key each by Π (`yupi.naming.pattern`, after un-renaming
   through the table — or directly on the surface window, since Π is
   invariant); the empirical pattern-class masses converge to the exact
   pattern aggregate's (`tests/test_naming_bridge.py`'s construction):
   total-variation distance below a stated bound that shrinks as
   `1/√N`, and every class with exact mass ≥ 10⁻⁴ present. The endpoint
   marginal is uniform; RESET appears with exactly the mass of `U = 0`.
3. **Rendering uniformity.** Over 10⁵ episodes, the frequency of each
   injection of threads into the non-reserved slice is uniform within a
   chi-square tolerance stated in the test; no reserved token ever appears.
4. **Corpus-track reproduction.** The corpus-track state entropy
   `H(q | Πw)` at (8, 4, 2) recomputed from the sampled corpus (classes
   weighted by empirical frequency, beliefs from the exact aggregate)
   matches the pinned value within sampling error; a loose check that the
   sampler and the exact side describe one law.
5. **Serialization round trip.** tokens → records → tokens is the
   identity for every window; every window's length is `5·(T − U) + [U = 0]`.

## 9. Error handling

Refuse, never coerce: a pool smaller than D3's minimum for the entity
count, an unknown rung, a law whose `L` is not a multiple of `B` or whose
`T_ep` is not on the grid, a manifest whose generator version differs from
the code's, a reserved token requested in a training corpus. Every refusal
names the statute line it enforces.

## 10. Testing (TDD, per the house)

Tests first: vocabulary pinned; five-token serialization and round trip;
RESET-inclusion rule against Part II §2(a) for every endpoint of (8, 4, 2);
Fisher–Yates uniformity on a 5-token pool exhaustively (every injection's
count over 10⁵ draws within tolerance; reserved slice untouched);
determinism; the window-law gate at (8, 4, 2) as a slow test (`-m slow`);
the manifest's refusals. The corpus-track reproduction is a script with a
raw, pinned like the other raws.

## 11. Out of scope for this sub-project

The trainer (sub-project 2: model, packing, checkpointing, CPU by default;
GPU runs take the 4090 through Hamut'ay's lease, with no one in the middle:
`~/projects/hamutay/deploy/ayllu-gpu run --holder yupi --purpose "<run>"
--ttl <h> -- <command>` acquires the card, the resident's heartbeat rests
and records the loan, the command runs in a systemd scope the heartbeat can
kill at expiry, and the card returns on exit; see
`hamutay/docs/superpowers/specs/2026-09-15-gpu-lease-design.md`).
Probes (sub-project 3). TIME_CLASS. Pattern-indexed query targets in the
corpus (evaluation poses queries against the exact side; the corpus is
next-record data only). The lexical holdout corpus. Anything at a law
other than the frozen one.

## 12. Ledger

- 2026-09-13: written at the handoff from the brainstorm of the same day;
  Approach A chosen over B (loader-side cropping) and C (episode LM with
  the window law at evaluation only — ruled out by Part II §2(a)).
