## v0.2.7.1 — AMEND BEFORE ENACTMENT

All six round-2 substantive amendments are discharged. The verdict is driven by contradictory stale status/evidence statements that should not enter the enacted record.

1. **VERIFIED — DISCHARGED.** The reversed support claim is corrected: r0 is identified as sparsest, with supports larger than r1—64 versus 28 at L=8 and 33 versus 1 at full context—and D4 is re-pointed explicitly to r0. [proposal:174](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:174), [L=8 raw](/home/tony/projects/yupi/docs/r0-ladder-census-14-8-2-2026-09-03.json), [full-context raw](/home/tony/projects/yupi/docs/r0-ladder-census-14-14-2-2026-09-03.json)

2. **VERIFIED — DISCHARGED.** The identity statistic is now accurately defined as the share of ambiguous law mass carried by supports classified identity-only under a coarse thread-signature quotient—not an entropy decomposition or permutation-orbit computation. The code computes `ident / amb`; the ε=1, L=8 raw is 0.2049527 with 67 windows. [proposal:42](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:42), [script:75](/home/tony/projects/yupi/scripts/r0_identity_residual.py:75), [raw:23](/home/tony/projects/yupi/docs/r0-identity-residual-14-2-2026-09-04.json:23)

3. **VERIFIED — DISCHARGED.** Clause 3 now enumerates every missing injectivity-note site: theorem “every rung,” consequences 3–5, and falsifier “any rung,” all to be qualified r1–r4. [proposal:122](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:122), [current note:12](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:12), [current note:92](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:92), [current note:99](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:99), [current note:107](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:107), [current note:113](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:113)

4. **VERIFIED — DISCHARGED.** Commit `f8fd687` supplies a genuine exhibited history class. For the r0 class `DISPATCH, DISPATCH, ACQUIRE, DISPATCH`, ACTOR changes Q1[L0] from ½/½ to point masses and changes the next-two-kind distribution; exact rationals and all 36 r1 refinements are pinned. I directly executed both witness controls successfully. It satisfies both (a) and (b), exceeding Part I’s disjunctive requirement. [proposal:163](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:163), [witness:64](/home/tony/projects/yupi/tests/test_r0_d2_witness.py:64), [pinned class:74](/home/tony/projects/yupi/tests/test_r0_d2_witness.py:74), [Part I D2:55](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:55)

5. **VERIFIED — DISCHARGED.** r0 is assigned to every ladder-variable deliverable, including per-interface characterization, the D8 order-mode cross, §9 controls, synchronization reporting, and producers currently hard-coded r1–r4. The existing “all rungs” deliverable therefore includes r0 without changing its wording. [proposal:188](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:188), [Part I deliverables:150](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:150)

6. **VERIFIED — DISCHARGED.** Companion Part I language changes D1’s falsifier from “every interface” to “every content rung r1–r4,” preserving the former D1 scope statutorily. [proposal:142](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:142)

7. **VERIFIED — AMENDMENT STILL REQUIRED.** The document contradicts its current artifacts: it says the D2 control “has not been written,” despite marking it done thirteen lines later, and its closing ledger again calls the witness and corrected-formula producer outstanding. Remove those stale statements or identify only genuinely outstanding work. [stale claim:201](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:201), [done ledger:220](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:220), [stale closing ledger:275](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:275)

8. **VERIFIED — AMENDMENT STILL REQUIRED.** Its status says “ADOPTED” while the same status says enactment awaits this review and the PI. Use “PROPOSED” or “review amendments incorporated”; do not pre-record enactment. [proposal:3](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:3)

## v0.2.8.1 — AMEND BEFORE ENACTMENT

Four amendments are fully discharged; the fresh-process amendment is only partially discharged in the proposal’s retained evidence.

1. **VERIFIED — DISCHARGED.** `PC_RANGE` now permits exhausted straight-line threads only as IO_BLOCKED or TERMINATED. The negative control covers RUNNABLE, RUNNING, and QUEUE_BLOCKED and passed when executed directly. [state:102](/home/tony/projects/yupi/src/yupi/state.py:102), [negative test:221](/home/tony/projects/yupi/tests/test_looping_programs.py:221)

2. **VERIFIED — DISCHARGED.** The rule binds exactly `max_t |frontier_t|`. `window_process.py` records `len(dist)` after each tick and takes its maximum; it does not measure simultaneous old-plus-new entries, which the clause now explicitly distinguishes. RSS is sampled only after all projections have materialized. [proposal:125](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:125), [recursion:69](/home/tony/projects/yupi/src/yupi/window_process.py:69), [maximum:92](/home/tony/projects/yupi/src/yupi/window_process.py:92), [projections:113](/home/tony/projects/yupi/src/yupi/window_process.py:113), [pricing:54](/home/tony/projects/yupi/scripts/window_process_pass_pricing.py:54)

3. **VERIFIED — DISCHARGED INCOMPLETELY.** The current script correctly starts one subprocess per ε and defines Linux `ru_maxrss` as KiB, with the threshold equal to 8,000,000 KiB. [script:16](/home/tony/projects/yupi/scripts/window_process_pass_pricing.py:16), [subprocess:69](/home/tony/projects/yupi/scripts/window_process_pass_pricing.py:69), [proposal:132](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:132)

   What remains wrong is the proposal’s use of pre-isolation raws. The (48,4,2) pass rows lack `rss_isolated_per_eps`, and the proposal itself says the unrolled ε=½ value came after ε=1. More seriously, the (48,8,2) cumulative 14.35-GB value does **not** prove an isolated ε=½ pass exceeds 8 GB; “14.35 ≥ 8 either way” is invalid under the newly enacted fresh-process unit. Keep the refusal on frontier, which is independently decisive, but remove the memory refusal or produce an isolated ε=½ raw. [proposal:155](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:155), [proposal:172](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:172), [old raw:1](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-8-2-2026-09-04.json:1)

4. **VERIFIED — DISCHARGED.** The new unrolled full-pass raw contains `states_per_tick[31] = 5,054` and `[47] = 14,370` for ε=1. [raw:71](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-48-4-2-2026-09-04.json:71), [tick 32:103](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-48-4-2-2026-09-04.json:103), [tick 48:119](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-48-4-2-2026-09-04.json:119)

5. **VERIFIED — DISCHARGED.** The (48,8,2) two-row raw, isolated ε=1 raw, r1 raw, and log are tracked in commit `68ca6ec`; commit `60dcd99` stamps that commit. [two-row raw:1](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-8-2-2026-09-04.json:1), [isolated raw:1](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-8-2-2026-09-04-eps1.json:1), [stamp payload:1](/home/tony/projects/yupi/timestamps/anchored/68ca6ecbae0449a7387ef54979392a966858ae46:1)

6. **VERIFIED — AMENDMENT STILL REQUIRED.** As with v0.2.7.1, the status simultaneously says “ADOPTED” and “awaiting … PI enactment.” [proposal:3](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:3)

## Looping exit-law freeze v0.1 — AMEND BEFORE ENACTMENT

1. **VERIFIED.** The governing (40,8,2) raw is compliant: both ε rows report frontier 1,964,919; RSS is 7,205,116 and 7,226,648 KiB; both carry `rss_isolated_per_eps: true`. Thus the law clears both limits, narrowly but genuinely. [raw definition:7](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-04.json:7), [ε=1:18](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-04.json:18), [ε=½:142](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-40-8-2-2026-09-04.json:142)

2. **VERIFIED — AMENDMENT REQUIRED.** All ten `(rung, ε)` pairs have eight shards, zero mismatches, and sums matching their claimed per-pair totals; I directly executed the raw-audit control successfully. But the grand total is arithmetically wrong: the five per-ε counts sum to 4,271,470, hence both ε total **8,542,940**, not **5,542,940**. [expected totals/test:14](/home/tony/projects/yupi/tests/test_window_gate_full.py:14), [raw-audit logic:34](/home/tony/projects/yupi/tests/test_window_gate_full.py:34), [incorrect total:210](/home/tony/projects/yupi/docs/looping-exit-law-freeze-v0.1.md:210)

3. **VERIFIED.** The exit evaluation matches v0.2.7.1 Clause 4 exactly: r1–r4 determine the content-ladder result, r0→r1 is reported beside it, and whether r0 counts is explicitly reserved to the PI. [freeze:113](/home/tony/projects/yupi/docs/looping-exit-law-freeze-v0.1.md:113), [v0.2.7.1:154](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:154)

4. **VERIFIED.** All 30 producer raws exist and carry the correct law, program, rung, and ε metadata: three producers × five rungs × two ε. The pin suite checks their values and coverage. [producer coverage:268](/home/tony/projects/yupi/tests/test_c1prime_loop_ceilings.py:268), [representative query raw:2](/home/tony/projects/yupi/docs/c1prime-loop-query-ceilings-40-8-2-r0-2026-09-06-eps1_2.json:2), [Q4 raw:2](/home/tony/projects/yupi/docs/c1prime-loop-q4-ceilings-40-8-2-r0-W4-2026-09-06-eps1_2.json:2), [predictive raw:2](/home/tony/projects/yupi/docs/c1prime-loop-predictive-targets-40-8-2-r0-2026-09-06-eps1_2.json:2)

5. **VERIFIED.** The note does not claim the exit clause is satisfied or that exploratory producer gaps are statutory. Its §5 producer debt is now stale—not an overclaim—and should be marked done while correcting the grand total. [owed producers:148](/home/tony/projects/yupi/docs/looping-exit-law-freeze-v0.1.md:148), [not claimed:156](/home/tony/projects/yupi/docs/looping-exit-law-freeze-v0.1.md:156)

## M1-success semantics

**VERIFIED — no covert change found.** The only potentially success-changing choice—whether r0 counts toward “across rungs”—is explicitly identified as the PI’s decision in both v0.2.7.1 and the freeze. The looping law selection is expressly labeled the researcher’s freeze decision. No additional unflagged redefinition of M1 success appears.

Repository remained clean at `604a0a0`.

---

## Prompt given to the reviewer

```
You are the cross-family reviewer for Project Yupi (repo: /home/tony/projects/yupi), third round. Read-only; do not modify files. HEAD is 604a0a0 (tree clean).

Your second-round review is filed verbatim at docs/part2-v0.2.7.1-v0.2.8.1-codex-review-2-2026-09-04.md (verdict AMEND BEFORE ENACTMENT for both, with six required amendments for v0.2.7.1 and five for v0.2.8.1). The authoring instance says every one was folded in, marked [r2-N] in:
- docs/part2-amendment-proposal-v0.2.7.1.md
- docs/part2-amendment-proposal-v0.2.8.1.md
Both status lines say "awaiting a third read, then PI enactment." This is that read. The PI will enact each document on the strength of it, one at a time, today.

Task 1. For EACH of the eleven required amendments in your round-2 "Required amendments" section, state whether the current text and artifacts DISCHARGE it (say where: file:line), discharge it INCOMPLETELY (say what is missing), or do NOT discharge it. Verify against the code and raws, not the prose: e.g. for v0.2.8.1 #1 run/inspect the PC_RANGE negative test; for #2 read scripts/window_process_pass_pricing.py and src/yupi/window_process.py and say what quantity is measured versus the clause's max_t |frontier_t|; for #3 confirm per-ε subprocess isolation and the KiB unit; for #4 open docs/window-process-pass-pricing-c1prime-48-4-2-2026-09-04.json and confirm states_per_tick carries 5,054 at tick 32 and 14,370 at tick 48; for #5 confirm the (48,8,2) raws/log are tracked and stamped. For v0.2.7.1, the round-2 items were: reversed r0/r1 support claim and the D4 support gate re-pointed to r0; identity metric described as ambiguous-mass support classification; injectivity-note scope edits; D2 not claimed satisfied without a history-class witness (the authors say a witness now exists: docs mention "r0→r1 D2 witness exhibited", commit f8fd687 — find it and check it satisfies D2's (a) and (b) as Part I states them, docs/yupana-m1-spec-draft.md D2); r0's effect on D8 and "all rungs" deliverables stated; preserved r1–r4 D1 scope in companion Part I text.

Task 2. docs/looping-exit-law-freeze-v0.1.md (never cross-family reviewed) is third on the PI's desk. It chooses (40,8,2) as the law on which the exit clause is evaluated in the looping world, under v0.2.8.1's per-pass rule. Since it was written, the §5 debts were paid: the two-path gate ran on every window at every rung r0–r4 at both ε (docs/window-gate-c1prime-loop-40-8-2-*-full*-shard*.json, ten (rung, ε) pairs, pinned in tests/test_window_gate_full.py) and the three producers ran at every rung (docs/c1prime-loop-{query-ceilings,q4-ceilings...-W4,predictive-targets}-40-8-2-*.json, pinned in tests/test_c1prime_loop_ceilings.py). Check: (a) does the (40,8,2) pricing raw cited in §2 actually show frontier ≤ 2×10⁶ and RSS ≤ 8 GB under the clause's definitions (max_t |frontier_t|; ru_maxrss KiB, fresh process per ε)? (b) do the shard raws sum to the window counts claimed and report zero mismatches? (c) does §3's exit-clause evaluation rule (content ladder r1–r4; r0→r1 reported beside; r0 counting is a separate decision) match v0.2.7.1 Clause 4? (d) anything the freeze note claims beyond what §6 "Not claimed" excludes?

Task 3. Anything in either proposal or the freeze note that would change what M1 succeeding means and is not flagged as a decision.

Output: a verdict per document (CONFIRM AS WRITTEN / AMEND BEFORE ENACTMENT / REJECT) with numbered findings, each tagged VERIFIED or PLAUSIBLE, with file:line pointers. Be adversarial; unverified agreement is worthless here. Keep it under 2,500 words.
```

*(Filed verbatim by the instance of 2026-09-06; `codex exec --sandbox read-only`, 163,040 tokens, ~7 min, HEAD 604a0a0. Corrections applied the same day: see the [r3-N] markers in both proposals and the 2026-09-06 addendum of the freeze note.)*
