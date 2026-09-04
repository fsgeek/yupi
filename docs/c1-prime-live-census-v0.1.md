# C1′ live-world census at (48, 4, 2) — the ladder in a running, contended world, and what it costs to look

**v0.1 — 2026-09-04 (runs 2026-09-03 19:14 → 09-04 00:24 PDT).** Exploratory,
enumerator side (window-process recursion, single r4 recursion with keys
projected down — `yupi.window_process.window_law_aggregates`, gated), C1′
programs (`c1-prime-pilot-note-v0.1.md`), corrected kernel, canonical track,
both statutory ε. Raws `c1prime-r0-ladder-census-48-4-2-2026-09-03.json`,
`c1prime-residual-ambiguity-census-{48,64}-4-2-2026-09-03.json`,
`window-process-pricing-c1prime-{32-4,48-4,48-6}-2-r1-2026-09-03.json`; pins
`tests/test_c1_prime_live.py`. Numbers copied from the raws in-session.

## 1. Where this law sits

C1′ at horizon 48: no thread has terminated; 98 % of episodes have at least
one thread that has re-acquired a lock; 14370 reachable states (C1: ≤ 456).
Context 4 is the only context affordable in the unrolled world (§4). So this
is the ladder measured in a live, contended world, at short context; the
long-context live-world ladder waits on v0.2.8.

## 2. The ladder, three worlds at context 4 (law-mass means, bits)

| world, law | ε | H(S) r0 / r1 / r2 / r3 / r4 | kinds2 gap r1 − r4 | Q1[L0] r1 / r2 / r3 | Q3[D0] r3 / r4 | Q4@4 gap r1 / r4 |
|---|---|---|---|---|---|---|
| C1 from reset (14, 4, 2) | 1 | 4.132 / 1.344 / 1.211 / 1.100 / 1.098 | 0.076 | 0.247 / 0.224 / 0.115 | 0.066 / 0.065 | 0.183 / 0.149 |
| C1 half-dead (32, 4, 2) | 1 | 4.854 / 2.012 / 1.894 / 1.661 / 1.614 | 0.139 | 0.414 / 0.361 / 0.149 | 0.174 / 0.128 | 0.373 / 0.306 |
| **C1′ live (48, 4, 2)** | 1 | **7.551 / 4.235 / 4.027 / 3.692 / 3.646** | **0.141** | **0.628 / 0.501 / 0.208** | **0.176 / 0.134** | **0.451 / 0.334** |
| C1 from reset (14, 4, 2) | ½ | 3.631 / 0.798 / 0.726 / 0.679 / 0.679 | 0.041 | 0.140 / 0.131 / 0.084 | 0.041 / 0.041 | 0.133 / 0.114 |
| C1 half-dead (32, 4, 2) | ½ | 3.951 / 1.139 / 1.064 / 0.931 / 0.896 | 0.087 | 0.228 / 0.187 / 0.071 | 0.118 / 0.083 | 0.267 / 0.213 |
| **C1′ live (48, 4, 2)** | ½ | **6.354 / 2.757 / 2.569 / 2.312 / 2.271** | **0.143** | **0.459 / 0.338 / 0.122** | **0.149 / 0.113** | **0.398 / 0.282** |

Adjacent-pair gaps in the live world, ε = 1, against δ = 0.01: r1 → r2
Q1[L0] 0.127; r2 → r3 Q1[L0] 0.293; r3 → r4 Q3[D0] 0.042 — every pair an
order of magnitude or more above δ, the lineage rung included. At ε = ½:
0.121 / 0.216 / 0.036.

**Reading.**

1. **The ladder has range in a live world.** The three interface steps the
   proposal designed — object, owner, lineage — each carry tens to hundreds
   of millibits at context 4 when threads keep contending. From reset the
   same steps carried 23, 109 and 1 millibits.
2. **Horizon 32 on C1 was already most of the way there.** The
   exposure-side interface share (kinds2 r1 − r4) is 0.141 live against
   0.139 half-dead; the lineage step is 0.042 against 0.046. The half-dead
   caveat on the horizon-32 census was real but small at context 4: what
   changed between reset and mid-episode is the prior over states at the
   window's start, and that change is already complete by the time a third
   of the world's instructions have run.
3. **What the live world adds is mass, not shape.** H(S) at r1 is 4.2 bits
   live against 2.0 half-dead and 1.3 from reset; every query's entropy
   roughly doubles; the r0 → r1 identity step is 3.3 bits (against 2.8 and
   2.8). The rung *differences* on the exposure side barely move; the fact
   queries' differences grow with the mass. A world that never stops
   contending is a world with a lot to know and the same relative amount
   surrendered per rung.
4. **The residual census agrees** (`c1prime-residual-ambiguity-census-{48,64}-4-2`):
   ambiguous mass 0.917 (48) and 0.937 (64) at r1; reachable by some rung
   0.69–0.72; unreachable 25 % (48) and 24 % (64) — against 31 % half-dead and 48 % from reset.
   Lock ownership dominates the residual and the related rung splits most of
   it.

## 3. Filter check

The r0 census's timed two-path sample at (48, 4, 2): the 20 largest r0
supports per ε (20455 → ~19000 states at ε = 1; 30234 → ~28000 at ε = ½)
through `filter_window` against the recursion — **40 of 40 exact**, in 615 s
and 1721 s. This is the largest-support exactness check the instrument has
run; it is also why the census took 1 h 40 min (§4).

## 4. Cost, and why context 4 is the ceiling in the unrolled world

| law (C1′) | rung | pairs (max) | windows | max support | wall | RSS |
|---|---|---|---|---|---|---|
| (32, 4, 2) | r1 | 102950, still growing | 7041 | 1518 | 36 s | 0.46 GB |
| (48, 4, 2) | r1 | 332119 | ~7300 | 7337 | 3.5 min | 2.0 GB |
| (48, 6, 2) | r1 | 1650623 | 94679 | 5043 | 15.5 min | 9.7 GB |
| (40, 8, 2) | r1 | — | — | — | **> 30 min, killed at 21.6 GB** | — |
| (64, 4, 2) residual census, 4 rungs × 2 ε | | | 7586 | | 2 h 48 min | 37.5 GB |
| (48, 4, 2) residual census (per-rung recursions) | | | 7289 | | 41 min | 14.2 GB |
| (48, 4, 2) ladder census (one r4 recursion; 39 min of it the filter sample) | | | 7289 | 30234 (r0) | 1 h 41 min | 8.6 GB |

The state space of an unrolled nonterminating world grows with the horizon
(5054 states at tick 32, 14370 at 48) for no dynamical reason, and the
recursion pays states × windows. The proposed D4 line (≤ 2 × 10⁶ pairs, ≤ 8
GB per (ε, rung)) admits (48, 4, 2) and (48, 6, 2) and refuses (40, 8, 2).
The looping kernel of `part2-amendment-proposal-v0.2.8.md` folds the counter
(≈ 500× fewer states for C1′) and is the prerequisite for the live-world
ladder at L ≥ 8. The one-recursion-for-all-rungs change made in this commit
cuts the ladder census by ~4× on the recursion side; the filter sample on
20 000–30 000-state supports is now the dominant cost and should be sized
by support, not by count.

## 5. Two process failures of the evening, recorded

- The horizon-64 census was launched before C1′ had been priced, against
  the enumerator note's own instruction; it ran 2 h 48 min at 37.5 GB.
- The watcher meant to stop that chain after one step used `pkill -f` on an
  environment string shared by two chains; it killed itself, both chains'
  parents, and left the horizon-48 ladder census unlaunched for 2.5 h
  while I reported it running. Both are in the memory store as rules:
  price the world first; kill by recorded PID, never by pattern.

## 6. What this changes

- The Part C recommendation stands as revised in
  `deep-truncation-census-v0.1.md`: the ladder's range is a property of
  where the window sits in the episode, not of the workload; the
  intervention needed is episode *length* (a looping kernel, v0.2.8), not
  workload redesign for separation.
- The r0 identity step is 3.3 bits in a live world: the naming bridge is
  no longer a paper-gating item but the largest single term on the
  interface axis.
- Order: v0.2.8 review → looping C1′ priced at L ∈ {8, 12} → statutory
  producers on the recursion with a support-sized gate → live-world
  ceilings at (48–96, ≤ 12, 2) → then the PI's Part C decision, which by
  then may be a decision about which world to freeze rather than which
  intervention to make.

## 7. Not claimed

Statutory status for any number here (ungated beyond the 40-window sample);
anything at L ≥ 6 in a live world; that the from-reset / mid-episode
contrast holds at L ≥ 8 for C1′ (unmeasured); that the looping kernel's
numbers will match the unrolled ones (they should, dynamically; to be
gated).
