# Implicit information ι_m and the order-m exact ceiling — design v0.1 (2026-09-28)

> **Status: DESIGN, exploratory.** This implements decision D2 of
> `docs/paper1-skeleton-v0.1.md`, readiness item 1. It was written by the instance of
> 2026-09-28 before any learner number was regressed on ι. The definition is frozen at
> this version for the exploratory per-window test (readiness item 3). A confirmatory
> use needs its own stamped prediction.

## 1. The quantity

Fix a (law, rung, ε) and a prefix position k. The pattern table gives, for every pattern
class c = (flag, Πw_{≤k}), its law mass m_c and the exact next-record law P*(· | c) in
c's pattern names. Here flag is R when the window starts at reset and N otherwise.

**Suffix view.** For m < k, let s_m(c) be the last m records of Πw_{≤k}, re-keyed by
Π_all: fold `extend_binding` over them from the empty binding. Call the resulting
binding β_s. The flag is not part of the suffix view; it is history.

**Target coarsening.** An order-m observer cannot tell an entity seen before the suffix
from a fresh one. A next record ρ in c's names is therefore mapped by
φ_c(ρ) = `extend_binding`(β_s, ρ)[0]. Any entity not bound in the suffix takes the next
index of its type. Let Q_c = φ_c # P*(· | c), the push-forward.

**Order-m ceiling.** P*_m(· | s) = Σ_{c: s_m(c)=s} m_c Q_c / Σ m_c. This is the exact
next-record law of an observer who sees only the last m records at position k, on the
coarsened target.

**Implicit information.** ι_m(c) = KL(Q_c ‖ P*_m(· | s_m(c))), in bits: what the
history before the last m records adds to the ceiling for this prefix. It depends on the
prefix only, so a per-window average over any prefix-defined subset is unbiased (the
Sep 24 rule).

**Identity (the gate).** Σ_c m_c ι_m(c) / Σ_c m_c = H_m − H̄, where
H_m = mass-mean H(P*_m(· | s)) and H̄ = mass-mean H(Q_c). The script computes both sides
independently: KL per class, and entropies of the mixtures. It fails if they differ by
more than 1e-9 bits.

## 2. What it is and is not

- H_m is the **exact order-m Markov ceiling** on the coarsened target, at this position.
  No learner restricted to the last m records can do better. This is the n-gram baseline
  of readiness item 1, obtained exactly and without training.
- H̄ ≤ H* (the full ceiling on the uncoarsened target), because coarsening merges
  outcomes. The gap H* − H̄ is the entropy of the "seen earlier versus fresh"
  distinction, which is itself history information. **ι is therefore a lower bound on
  the history's contribution to the full target.** Both H* and H̄ are reported.
- ι measures information, not computational difficulty. D1's hypothesis is that it
  predicts a small transformer's excess. That hypothesis is tested, not assumed.
- The position k is implicit (one table per k). The order-m observer knows k.

## 3. Outputs

Per cell (rung, ε), per k, per m ∈ {1, 2}: n classes, n suffix groups, H*, H̄, H_m,
mean ι_m (both routes, and their difference), and the fraction of law mass with
ι_m > 0.01. Summary raw: `docs/implicit-info-40-8-2-k<k>-2026-09-28.json`. Per-class ι
goes to `~/.cache/yupi-scratch/implicit/<cell>-k<k>.jsonl` (serial key → ι_1, ι_2) for
the per-window join. Its sha256 is recorded in the raw.

## 4. Tests (written first)

1. A table whose P* depends only on the last record gives ι_1 ≡ 0 and H_1 = H̄.
2. The identity holds on a hand-built table with two classes sharing a suffix.
3. Coarsening: an entity bound before the suffix and not in it maps to the fresh index.
4. A hand-computed ι on a two-class example (one line of arithmetic, pinned to its
   value, not only to an invariant).
