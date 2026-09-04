# Cross-family review of Part II proposals v0.2.7 and v0.2.8 — Codex, 2026-09-04

> **Status: independent review, not a governing document.** Produced by
> Codex (codex-cli 0.151.0, read-only sandbox) at repository head `da208af`
> (stamp of `d01023b`), invoked by the Claude instance of 2026-09-04 with the
> prompt recorded below the review. Codex could not start pytest in its
> sandbox and says so; every VERIFIED tag below is Codex's own check against
> code or artifact. The authoring instance re-verified the load-bearing
> findings (five pc-advance sites; the (48,6,2) RSS contradiction; the §6
> synchronization formula; the exit-clause wording; the injectivity note's
> corollary 3) before adopting them in `part2-amendment-proposal-v0.2.7.1.md`
> and `part2-amendment-proposal-v0.2.8.1.md`. Retained verbatim.

Both proposals contain defensible ideas, but neither is safe to enact verbatim.

## v0.2.7 — AMEND BEFORE ENACTMENT

1. **VERIFIED — The numerical headline is accurate.** The raw `(14,14,2)` values are 2.577229 bits at ε=1 and 2.374523 bits at ε=½, with r0→r1 next-2-kind gaps 0.488437 and 0.512383 bits. Across measured `L≥4`, the gap ranges 0.488–0.602 bits; max r0 support is 282; every sampled filter comparison has zero mismatches. [raw ε=1](/home/tony/projects/yupi/docs/r0-ladder-census-14-14-2-2026-09-03.json:14), [raw ε=½](/home/tony/projects/yupi/docs/r0-ladder-census-14-14-2-2026-09-03.json:315), [census table](/home/tony/projects/yupi/docs/r0-ladder-census-v0.1.md:20).

2. **VERIFIED — This is not “no frozen decision change.”** Part I freezes the ladder as r1→r4, names actor-only as the sparsest D4 rung, and makes regimes “across rungs” an exit condition. Expanding the interface variable changes those constitutional meanings even if no numerical threshold changes. A companion Part I amendment must specify:

   - whether D2 now includes r0→r1;
   - whether D4 prices r0 or intentionally remains bound to r1;
   - how D1 and the exit condition treat r0.

   [proposal claim](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.md:6), [Part I D2](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:55), [Part I D4](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:69), [exit clause](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:150).

3. **VERIFIED — The measurements cannot enter §4 as statutory ceilings yet.** The source census expressly says the full gate was not run and “nothing here is a statutory ceiling.” Its measured process also reached 4.4 GB at `L=14`; the normal B4′ path-aggregation memory line is 2 GB, with 4 GB allowed only for the D8-specific E2 extension. Because the census did not isolate one r0 aggregation pass or measure B1/B3 per filter step, “D4 is not touched” is not established. Keep the numbers as exploratory rationale and add an r0 D2/§9 gate before calling them statutory. [census gate status](/home/tony/projects/yupi/docs/r0-ladder-census-v0.1.md:46), [census RSS](/home/tony/projects/yupi/docs/r0-ladder-census-v0.1.md:110), [B4′](/home/tony/projects/yupi/docs/d4-budget-freeze-v0.1.md:145), [E2 scope](/home/tony/projects/yupi/docs/d4-budget-freeze-v0.1.md:196).

4. **VERIFIED — Review request (i): the categorical “residual is thread identity” is not adequately evidenced.** The evidence does show that r1 splits every measured long-context ambiguous r0 class, strongly implicating ACTOR information. It does not prove that supports are permutation orbits, or that kind-permuted programs remain confounded for an entire episode. The source note explicitly declines the exact permutation-entropy claim. The modal-support summary is also ε-dependent: mode 6 at ε=1, but mode 12 at ε=½ for `L≥8`. Either perform the orbit computation or weaken the statutory wording to “the measured residual is consistent with unresolved actor/thread identity.” [residual evidence](/home/tony/projects/yupi/docs/r0-ladder-census-v0.1.md:54), [original non-claim](/home/tony/projects/yupi/docs/r0-ladder-census-v0.1.md:103), [executable split check](/home/tony/projects/yupi/tests/test_r0_ladder.py:54).

5. **VERIFIED — The random-naming equivalence is false as written.** Random-σ r1 still exposes a persistent actor pseudonym and equality/repetition structure; r0 removes ACTOR entirely. Thus both produce mixtures over roles, but they are not “the same object.” The v0.2.6 bridge requires joint inference over σ precisely because actor-bearing observations update the role binding. Rewrite this as an analogy, not an equality. [proposal](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.md:36), [canonical/random naming distinction](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:47), [r0 projection](/home/tony/projects/yupi/src/yupi/interfaces.py:39).

6. **VERIFIED — Refinement monotonicity survives, but several global theorem statements do not.**

   - Entropy/refinement monotonicity survives because r1 determines r0; the implementation has that property. [projection](/home/tony/projects/yupi/src/yupi/interfaces.py:23)
   - Predicted-record divergent mass remains non-increasing when r0 is prepended: the pushforward/nested-pair proof applies unchanged. [G1 proof](/home/tony/projects/yupi/docs/c1-divergent-grid-v0.1.md:122)
   - The r1 injectivity theorem survives, but its corollaries saying “every rung” and “the interface axis is degenerate at full context” become false. At full context the raw has 5,696 r0 classes versus 394,824 for each r1–r4 rung. [theorem wording](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:12), [overbroad consequence](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:92), [raw partition counts](/home/tony/projects/yupi/docs/r0-ladder-census-14-14-2-2026-09-03.json:93)
   - The partition-identity result remains true only for r1–r4; it is false for the expanded r0–r4 set. [identity scope](/home/tony/projects/yupi/docs/partition-identity-note-v0.1.md:13)
   - Most importantly, §6’s formula `E[H|U>0]=H_law/P(U>0)` relies on full-context entropy being zero “at every rung.” It is wrong for r0. For r0 it must subtract the `U=0` contribution before dividing, or exclude r0 from synchronization scoring. [current formula](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:184)

7. **VERIFIED — Review requests (ii) and (iii): r0 must not silently rescue D1 or the exit clause.** “r0 never collapses by construction” is false generally; actor identity can be derivable in other worlds. Score r0→r1 as an added D2 adjacency, but retain a separate D1 verdict for the original r1→r4 content ladder. Likewise, Part I does not literally say “three rungs distinct”; that is a later evidence-map gloss. Do not count r0 as a substitute for one of r1/r2/r3 without explicitly amending Part I’s exit criterion. [actual exit text](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:158), [later three-rung interpretation](/home/tony/projects/yupi/docs/d1-falsifier-verdict-v0.1.md:208).

8. **VERIFIED — The claim that r1–r4 still collapses by 8–10 records needs a from-reset qualifier.** The later deep census found every adjacent r1–r4 pair above δ at `(32,8,2)`, ε=1. The proposal’s statement is true for the `(14,L,2)` reset-dominated family, not C1 windows generally. [proposal](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.md:64), [deep reversal](/home/tony/projects/yupi/docs/deep-truncation-census-v0.1.md:58).

Required additions before enactment: companion Part I language; corrected §6 synchronization formula; r0→r1 §9 witness/control; explicit exploratory status for the cited figures; legacy r1–r4 scoping for injectivity, partition identity, D1, and exit; weakened identity/naming claims unless orbit evidence is added.

## v0.2.8 — AMEND BEFORE ENACTMENT

1. **VERIFIED — The pc-advance list is inaccurate.** There are exactly five `pc` mutation sites:

   1. STEP/COMPUTE — [kernel.py:321](/home/tony/projects/yupi/src/yupi/kernel.py:321)
   2. successful ACQUIRE — [kernel.py:349](/home/tony/projects/yupi/src/yupi/kernel.py:349)
   3. releasing thread on RELEASE — [kernel.py:395](/home/tony/projects/yupi/src/yupi/kernel.py:395)
   4. directly handed-off waiter on RELEASE — [kernel.py:416](/home/tony/projects/yupi/src/yupi/kernel.py:416)
   5. successful IO_ISSUE — [kernel.py:449](/home/tony/projects/yupi/src/yupi/kernel.py:449)

   BLOCK, DISPATCH, completion, and IDLE do not advance `pc`. Completion only inspects the already-advanced counter to choose RUNNABLE versus TERMINATED. Thus “completion path” is not an advance site, and “eight advance sites” is false. [completion logic](/home/tony/projects/yupi/src/yupi/kernel.py:223), [proposal list](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.md:36), [eight-site claim](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.md:55).

2. **VERIFIED — Define `advance` and `done` separately.** The clause should specify:

   - `advance_i(pc) = (pc+1) mod |P_i|` for looping programs, otherwise `pc+1`;
   - `done_i ⇔ ¬loop_i ∧ pc_i=|P_i|`.

   Completion uses `done_i`; it does not advance. This also exposes an existing statutory inconsistency: §1 says `pc=|P|` means TERMINATED, but final IO_ISSUE sets `pc=|P|` while the thread remains IO_BLOCKED until completion. [§1 wording](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:29), [IO issue](/home/tony/projects/yupi/src/yupi/kernel.py:443), [§3.4 acknowledgment](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:128).

3. **VERIFIED — `PC_RANGE` alone is underspecified.** `check_invariants(state,cfg)` currently has neither programs nor their lengths, so it cannot check per-program pc bounds. The amendment must state where lengths/loop flags live or change the checker’s signature. It should add:

   - looping body is nonempty;
   - looping: `0≤pc<|P|` and status is never TERMINATED;
   - straight-line: `0≤pc≤|P|`, with `pc=|P|` allowing final-IO-blocked or TERMINATED;
   - mixed looping/straight-line configurations are permitted.

   [checker signature](/home/tony/projects/yupi/src/yupi/state.py:70), [program representation](/home/tony/projects/yupi/src/yupi/programs.py:21).

4. **VERIFIED — The I6 lock-cycle argument survives the wrap, conditionally.** The validator enforces increasing order among simultaneously held locks, LIFO release, and an empty held stack at body end; the kernel enforces that validator at its boundary. Consequently no lock crosses a wrap and the standard global-order cycle proof still applies. This establishes lock-cycle freedom, not termination or starvation freedom. In mixed configurations I3 remains active for straight-line owners; it is only vacuous with respect to a looping owner’s termination. [validator](/home/tony/projects/yupi/src/yupi/programs.py:24), [kernel enforcement](/home/tony/projects/yupi/src/yupi/kernel.py:497), [dynamic I6 check](/home/tony/projects/yupi/src/yupi/state.py:138).

5. **VERIFIED — Review request (i): add the executable exact-zero control.** Yes. All enumerator/filter paths share `kernel.enabled`, so their mutual agreement cannot detect a shared wrap bug. Add independent transition tests covering wrap at COMPUTE, RELEASE, and IO_ISSUE/completion, a direct-handoff recipient, mixed loop/non-loop programs, and an exhaustive assertion that posterior mass on `pc=|P|` for looping threads is exactly zero.

6. **VERIFIED — Nothing operational assumes eventual termination.** Scheduler/idle selection depends on enabled work and device queues, not `all(TERMINATED)`. The simulator and enumerator run to fixed horizons; endpoint prior is uniform on a fixed grid; Q4 and every τ use finite `W` with `NONE_WITHIN_W`. A looping world therefore fits these mechanisms unchanged. [scheduler/IDLE](/home/tony/projects/yupi/src/yupi/kernel.py:521), [simulator horizon](/home/tony/projects/yupi/src/yupi/simulator.py:46), [enumerator horizon](/home/tony/projects/yupi/src/yupi/enumerator.py:45), [endpoint prior](/home/tony/projects/yupi/src/yupi/window.py:55), [Q4 recursion](/home/tony/projects/yupi/src/yupi/forecast.py:44), [τ recursion](/home/tony/projects/yupi/src/yupi/predict.py:42).

7. **VERIFIED — Review request (iii): the continuation rule needs no semantic change.** A fixed loop flag remains part of the fixed kernel configuration, so the kernel is still time-homogeneous and forward sums naturally continue past `T_ep`. A short cross-reference would help readers, but reenactment is unnecessary. [existing continuation rule](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:51).

8. **VERIFIED — The D4 erratum is not well-defined for the current producer.** `window_law_aggregates()` performs one r4 recursion per `(law, ε)` and then materializes all requested coarser aggregates; there is no per-rung recursion to which the proposed unit can bind. Moreover, `max_pairs` counts only the live recursion dictionary, while RSS also includes the accumulating endpoint aggregate and projected outputs. The cited pricing script still prices the older single-rung entry point. [one-r4 implementation](/home/tony/projects/yupi/src/yupi/window_process.py:91), [pair instrumentation](/home/tony/projects/yupi/src/yupi/window_process.py:65), [single-rung pricing](/home/tony/projects/yupi/scripts/window_process_pricing.py:23).

   The rule should bind the actual producer invocation: one `(law, ε, execution mode)` pass, with a defined maximum-live-pair counter and whole-process peak RSS including aggregate materialization. If single-rung passes remain admissible, define them separately. Preserve B4′’s 1.5M-path and 2 GB path-side rules, including the D8-only E2 exception, rather than ambiguously replacing B4′.

9. **VERIFIED — The proposed D4 admission result contradicts the raw and its regression test.** `(48,6,2)` has 1,650,623 pairs but 9,703,432 KB peak RSS. It passes `≤2M` pairs and fails `≤8GB`; the proposal nevertheless calls it admitted. The repository test explicitly asserts that it is over the proposed memory line. `(48,4,2)` is 332,119 pairs and about 2.03 GB. [L6 raw](/home/tony/projects/yupi/docs/window-process-pricing-c1prime-48-6-2-r1-2026-09-03.json:13), [L6 RSS](/home/tony/projects/yupi/docs/window-process-pricing-c1prime-48-6-2-r1-2026-09-03.json:67), [L4 raw](/home/tony/projects/yupi/docs/window-process-pricing-c1prime-48-4-2-r1-2026-09-03.json:13), [contradicting test](/home/tony/projects/yupi/tests/test_c1_prime_live.py:67).

10. **VERIFIED — The other key counts check, with qualifications.** Exact replay gives C1′ reachable-state counts 5,054 at tick 32 and 14,370 at tick 48. Those counts are not retained in the cited JSON raws, which is an artifact gap. “C1 ≤456” is true at the selected comparison ticks/table entries—C1 has 317 at tick 32 and 185 at tick 48—but not as a global bound: exact replay peaks at 482 states at tick 21. Also, ε=1 C1′ has approximately `7.57×10⁻⁶` probability of at least one terminated thread at tick 48, so “keeps threads alive” is overwhelmingly but not exactly true. [cited table](/home/tony/projects/yupi/docs/deep-truncation-census-v0.1.md:27), [live-note categorical claim](/home/tony/projects/yupi/docs/c1-prime-live-census-v0.1.md:14).

11. **PLAUSIBLE — The claimed approximately 500× quotient is a heuristic, not established evidence.** `5×4×5×5=500` is the maximum product of unrolling phases, not a demonstrated reachable-state reduction. Unrolled states one body apart also cease to be dynamically equivalent near the finite program’s end because one reaches termination sooner. Present 500 as an upper-bound intuition pending loop pricing, not an expected measured factor. [proposal](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.md:19).

12. **VERIFIED — D6 does not categorically exclude general control flow.** D6 excludes specified hard belief-update structures such as group composition and permutation tracking; it does not say that every JUMP is forbidden. Declining JUMP for scope is reasonable, but the attribution to D6 should be narrowed. [D6](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:77), [proposal](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.md:79).

13. **PLAUSIBLE — Review request (ii): use a looping deep-truncation law, but freeze it separately.** The authoritative Part I clause does not literally say “three rungs distinct.” A natural primary candidate is `(64,8,2)`, both statutory ε: only 12.5% of endpoints are reset-visible, it directly targets the first context inaccessible in the unrolled world, and existing C1 `(64,8,2)` pricing gives a comparator. Treat `L=12` and/or `T_ep=96` as secondary only after the corrected D4 rule and actual loop pricing. Do not allow r0, if enacted, to substitute for separation within r1–r4. [actual exit clause](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:158), [current deep-pricing rationale](/home/tony/projects/yupi/docs/window-process-enumerator-v0.1.md:97).

Required additions before enactment: exact `advance/done` definitions; corrected five-site list; nonempty-loop and mixed-program invariants; executable wrap controls; a pass-based D4 rule priced on the current one-r4 producer; corrected `(48,6,2)` verdict; and a separate freeze decision for the looping exit law.

Verification was read-only. Fresh exact replay and JSON assertions confirmed the stated counts and contradictions, and `git status --short` remained empty. Pytest itself could not start because the sandbox exposes no writable temporary directory, so I do not claim a fresh suite run.
---

## Prompt given to the reviewer

```
You are the cross-family reviewer for Project Yupi (repo: /home/tony/projects/yupi). Read-only review; do not modify files.

Review two PROPOSED Part II amendments before PI enactment:
- docs/part2-amendment-proposal-v0.2.7.md (a kind-only rung r0 below the interface ladder)
- docs/part2-amendment-proposal-v0.2.8.md (looping programs: pc modulo the body, plus a D4 erratum sizing recursions by (state,window) pairs and memory)

Governing documents: docs/yupana-m1-part2-semantics-draft.md (Part II, operational semantics; §3 kernel, §4 projection table, I1–I6 invariants), docs/yupana-m1-spec-draft.md (Part I; D1–D10 decisions, exit clause), docs/d4-budget-freeze-v0.1.md or the D4 section of Part I for the budget rule B4′.
Evidence the proposals cite: docs/r0-ladder-census-v0.1.md, docs/full-context-injectivity-note-v0.1.md, docs/c1-residual-ambiguity-census-v0.1.md, docs/window-process-enumerator-v0.1.md, docs/deep-truncation-census-v0.1.md, docs/c1-prime-pilot-note-v0.1.md, docs/c1-prime-live-census-v0.1.md.
Code: yupi/kernel.py (advance sites, validate_lock_order, invariants), yupi/interfaces.py (project; r0 exploratory), yupi/enumerate*.py / window-process recursion, tests/.

Answer each proposal's own "Review request" questions explicitly, and additionally:
1. Is every claim in each proposal consistent with the statute as written and with the cited artifacts? Check numbers against the JSON raws in docs/ where cited (e.g. r0 entropies at (14,14,2), C1′ reachable-state counts 5054/14370, pair counts 332K/1.65M).
2. For v0.2.8: enumerate every pc-advance site in kernel.py and confirm the clause's list (STEP, ACQUIRE, RELEASE, IO_ISSUE, woken thread's advance on RELEASE, completion path) is complete. Does the I6 deadlock-freedom argument survive the wrap? Does TERMINATED/I3 handling elsewhere (scheduler idle detection, episode end, endpoint prior, τ) assume some thread eventually terminates?
3. For v0.2.8's D4 erratum: is "≤ 2e6 pairs and ≤ 8 GB per (ε, rung) recursion" well-defined given window_law_aggregates() runs ONE r4 recursion projected to all rungs? Which unit does the rule bind?
4. For v0.2.7: does prepending r0 break any monotonicity assertion or theorem in the producers or notes (full-context injectivity, divergent-mass non-increasing in predicted-record rung, partition identity)?
5. Anything either proposal should say and does not.

Output: a verdict per proposal (CONFIRM AS WRITTEN / AMEND BEFORE ENACTMENT / REJECT) with numbered findings, each tagged VERIFIED (you checked code/artifact) or PLAUSIBLE (reasoning only), with file:line pointers. Be adversarial; the project treats a reviewer's unverified agreement as worthless.
```
