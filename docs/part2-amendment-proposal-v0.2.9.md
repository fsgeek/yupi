# Part II amendment proposal — v0.2.9 (the naming bridge: observation on equality patterns, the corpus track, and keyed rendering)

> **Status (2026-09-12): PROPOSAL, researcher's brief to the PI. Not enacted.**
> Discharges the bridge requirement of Part II v0.2.6 Clause 2′ by
> route (b) in its strongest form: instead of a per-metric equivariance
> proof, the corpus-facing observation is *defined* on equality patterns,
> so every corpus-facing quantity is invariant under renaming by
> construction, and the claim is executable
> (`tests/test_naming_bridge.py`, exhaustive over every injection into a
> pool at C1 (8,4,2), r1 and r3, both statutory ε). No existing number
> changes; the canonical track keeps its meaning and its thirty gated
> artifacts. Written by the instance of 2026-09-12; the form of the bridge
> is the one found in the 2026-09-04 session ("the requirement is
> co-reference only, so the observation process should be defined on
> equality patterns"); the rendering clause is the PI's Pukara shape
> (2026-09-12). Cross-family read requested before this reaches the desk.

## 0. Why now

Every exact number in the instrument is a **structural-characterization
quantity under the canonical injection σ₀** (Clause 2′): thread 0 is always
called by the same name, so a name tells the observer which program its
bearer runs. The corpus a transformer will train on draws names per
episode from a pool (D3). Until a bridge exists, no canonical number is a
ceiling for that corpus. The r0 census and v0.2.7.1 put identity on the
interface axis and found the r0 → r1 step an order of magnitude larger
than any content step; the exit-clause note kept that step *beside* the
ladder because the bridge was about to separate the who-axis from the
what-axis. This proposal is that separation.

## 1. Clause 1 — the pattern projection Π

For a rung-projected window $w = (o_1, \ldots, o_m)$, **Π(w)** relabels
every thread-valued field (ACTOR; RELATED at r3–r4) by **first appearance
within the window**, in record order and actor-before-related within a
record: the first distinct thread becomes 0, the next 1, and so on. MASKED
and absent fields are untouched. The same construction applies, per
entity type, to lock and device names in OBJECT and to request identifiers
in LINEAGE when those are drawn from pools (D3 says "proportionally"); the
executable lemma covers threads, which is where the counterexample lives.
Π commutes with the rung projections (the coarse pattern is a function of
the fine window), so the pattern partition at r_{i+1} refines the one at
r_i (`test_pattern_partition_refines_down_the_ladder`).

**Binding.** For a structural window, Π also yields the *binding*
$\beta$: the list whose $k$-th entry is the structural thread that became
pattern index $k$. The pair (Π(w), β) determines w.

## 2. Clause 2 — the corpus track

**Corpus process.** Per episode, σ is a uniform injection from structural
threads into the D3 pool, independent of the dynamics; the observer sees
σ applied to the thread fields of the rung-projected window.

**Lemma (executable).** Because σ is uniform and independent of the
kernel, for any surface window $w_\sigma$:

1. the posterior over the structural state depends on $w_\sigma$ only
   through Π($w_\sigma$), and equals the state marginal of the
   **pattern aggregate** — the rung aggregate the instrument already
   computes, re-keyed by (RESET-observed, Π(window)) with the binding kept
   in the value: $\{(\text{state}, \beta) \mapsto \text{law mass}\}$;
2. the law mass of $w_\sigma$ is its pattern class's mass split uniformly
   over the $|P|!/(|P|-k)!$ token assignments of its $k$ named threads;
3. a query about **the thread named x** has, under the corpus process, the
   answer distribution of the pattern-side pushforward of
   $\text{query}(\text{state}, \beta[k_x])$, where $k_x$ is x's pattern
   index — the mixture over bindings consistent with what x has done in
   the window, which is what the 1.208-bit counterexample computed by hand.

Checked Fraction for Fraction over all 120 injections into a 5-token pool
at C1 (8,4,2), r1 and r3, both ε: 10,250 / 15,375 surface windows against
207 / 282 pattern classes and 690 / 758 canonical windows
(`test_surface_posterior_is_the_pattern_posterior`). The surface partition
is strictly finer than the pattern partition and carries no more
information — tokens are inert; equality is everything.

**Corpus-track quantities.** On the pattern partition, with beliefs over
(state, β):

- **Statutory queries take pattern-indexed arguments**: Q2[k] "status of
  the k-th named thread", Q1[ℓ] "owner of lock ℓ, as a pattern index or
  UNSEEN", Q5[k, k′], and so on. A query about a token the window never
  named is a query about the UNSEEN class (the mixture over unnamed
  threads). Every query mean is a law-mass mean over pattern classes
  exactly as today.
- **The corpus-track state ceiling** is $H(\text{quotient} \mid \Pi(w))$,
  where the **quotient** re-expresses the state in the window's names:
  named threads keep their fields under their pattern index, unnamed
  threads form an unordered multiset, and every thread reference (running
  set, lock owners, wait queues, device queue, cursor) is mapped to a
  pattern index or UNSEEN. It is the finest description of the state an
  observer of the surface trace could state in its own terms. The chain
  rule $H(S, \beta \mid w) = H(q \mid w) + H(S, \beta \mid q, w)$ is
  asserted exactly (`test_corpus_track_state_entropy_and_chain_rule`).
- **The who-axis quantity**: $H(\beta \mid \Pi(w))$, the binding entropy,
  reported per rung beside the ladder. Its reduction below the prior over
  consistent bindings is the identity leak — at ε = 1 the round-robin
  cursor reveals the cyclic order of the named threads' structural indices
  through dispatch order. This is a measurable, not a defect (PI,
  2026-09-12: "we need the data to decide").

**What the lemma's by-product already says** (C1 (8,4,2), law-mass means,
bits, exploratory, pinned documentary in the test):

| ε | rung | canonical $H(S \mid w)$ | corpus $H(q \mid \Pi w)$ | $H(\beta \mid \Pi w)$ |
|---|---|---:|---:|---:|
| 1 | r1 | 0.5230 | 1.8216 | 2.4238 |
| 1 | r3 | 0.4452 | 1.6567 | 2.3343 |
| ½ | r1 | 0.2597 | 1.2709 | 2.0093 |
| ½ | r3 | 0.2316 | 1.0941 | 1.8583 |

The canonical track understates the corpus observation gap by more than a
bit at this law, and the reason is role: a canonical name says which
program its bearer runs; a pattern name does not, so the observer must
infer the program from behaviour. At the frozen law (40,8,2) the corpus
figures are not yet computed; they are a re-keying of the existing
aggregates (§5) and are expected to move the ladder, because in the
corpus track OBJECT and RELATED carry role information that the canonical
actor index made redundant.

**Canonical track unchanged.** Every existing artifact keeps its meaning
as a structural-characterization quantity under σ₀. The exit clause was
read on the canonical track (exit-clause note §1); this clause does not
reopen it. Which track paper 1's headline ceilings cite is a scope
decision for the PI at the time of writing; the researcher's
recommendation is: both, labelled, with the corpus track as the ceiling
against which a trained model is compared.

## 3. Clause 3 — the gate

Before any corpus-track number at a law is cited: (i) the executable lemma
passes at that world's smallest law admitting every rung (as
`tests/test_naming_bridge.py` does at (8,4,2)); (ii) the pattern aggregate
at the law is produced by re-keying the gated rung aggregate (the window
gate of the freeze note is inherited — every window's posterior was exact
before re-keying, and re-keying is a sum); (iii) the chain rule holds
exactly on every pattern class. No new enumerator, no new filter, no
change to E3's unit or line.

## 4. Clause 4 — rendering (the corpus layer; the PI's Pukara shape)

Corpus generation draws σ per episode by a **keyed generator**: a key
recorded with the run, a base value per (episode, entity type, structural
index), a keyed pseudorandom function over them (AES over the base value
with the run key, or an equivalent keyed PRF), 4–8 bytes of output reduced
modulo the pool size, first unique taken. The pool is the vocabulary:
fixed across the corpus, one token per name, sized per D3 (≥ 50 for ≤ 4
threads; locks, devices and request ids proportionally). The
**translation table** (structural entity → token, per episode) is stored
with the run for interpretability and for the exact side (held-out-binding
evaluation needs it; the corpus-track filter does not, since Π discards
it) and is **never in the model's context**. Reproducibility: the run key
regenerates every binding; without the key the tokens are opaque. The
held-out-binding split (D3, v0.2.2) is a constraint on which (episode,
σ) pairs are drawn, not on Π.

This clause is implementation, not semantics: nothing in §1–§3 depends
on how σ is drawn beyond uniformity and independence.

## 5. Cost

A re-keying of the aggregates the pass already returns: for each rung,
iterate the (RESET, window) keys once, compute Π and β, and merge into
the pattern aggregate keyed by (RESET, Π(window)) with values over (state,
β). Memory is bounded by the rung aggregate's own size (the pattern
partition is coarser; the value key grows by a ≤ 4-tuple). Under E3 the
unit is unchanged; the re-keying runs after the pass, like the producers'
evaluation phase. Wall time: seconds per rung at (40,8,2). The producers
gain a `--track corpus` switch; the pattern-indexed queries are a second
`all_queries` table.

## 6. What this proposal does not do

It does not change the exit clause, D1's falsifier, δ, any committed
number, or the thirty (40,8,2) artifacts. It does not address lexical
generalization (untrained embeddings), which D3 already separates. It does
not remove the cursor's structural-index leak; it measures it. It does not
claim the corpus-track ladder at (40,8,2) — that is the first measurement
after enactment, and the by-product table above is the reason to expect
it to differ from the canonical one.

## 7. Decision requested

Enact §1–§4 as Part II v0.2.9 (§4 may be enacted as an implementation
note if the PI prefers the statute to stay silent on rendering). On
enactment the researcher produces the corpus-track counterparts of the
(40,8,2) artifacts under Clause 3 and reports the corpus ladder beside the
canonical one.

## 8. Ledger

- 2026-09-12: drafted with the executable lemma
  (`tests/test_naming_bridge.py`, 10 tests). Codex read requested.
