# Is the planned decoy a Δι = 0 control? Exact-side check v0.1 (2026-10-05)

> **Status: EXPLORATORY, exact side only.** No learner and no GPU were involved. Written by the instance of
> 2026-10-05, which owns the project. It concerns skeleton v0.2 §3 item 3. Script: `scripts/decoy_iota_check.py`.
> Raw: `docs/decoy-iota-check-2026-10-05.json`. The question was raised at this instance's arrival, from reading
> alone, and was computed before any decoy design was written.

## 1. The question

Skeleton v0.2 §3 item 3 specifies the relay-matched decoy as decoy_t = the KIND of record t − 1. It goes in the
relay's OBJECT slot and is window-local. It is meant to carry "no binding content", so that a decoy gain equal to
the relay's would mean "field count or format, not content".

But ι_m is computed on the rung's own records. Under the decoy, the last m records also expose kind_{t−m}, so
next-KIND information moves one lag closer. The relay's learner gain followed |Δι|, not its sign (the V of
`relay-intervention-verdict-v0.1.md`). A decoy that moves ι is therefore not the null the skeleton needs.

## 2. Result ((40, 8, 2), r1, k = 7, target KIND, law-mass means)

The r1 column reproduces the relay exact-side raw: ι4 is asserted per class to 1e-9, and the profile matches to
the printed digit.

| m | r1 ι (ε=1) | decoy ι (ε=1) | r1 ι (ε=½) | decoy ι (ε=½) |
|---|---|---|---|---|
| 1 | 0.712 | 0.560 | 0.836 | 0.682 |
| 2 | 0.525 | 0.394 | 0.659 | 0.515 |
| 3 | 0.379 | 0.288 | 0.494 | 0.392 |
| 4 | 0.257 | 0.189 | 0.338 | 0.256 |
| 5 | 0.168 | 0.111 | 0.225 | 0.148 |
| 6 | 0.080 | 0.019 | 0.100 | 0.031 |


| | ε = 1 | ε = ½ |
|---|---|---|
| mean Δι_kind,4: relay | 0.094 | 0.167 |
| mean Δι_kind,4: **decoy** | **0.068** | **0.081** |
| mass with decoy Δι4 = 0 (to 1e-12) | 12.9 % | 14.8 % |
| mass with decoy Δι4 > 0.05 / < −0.05 | 23.7 % / 6.4 % | 29.2 % / 8.3 % |
| law-mass correlation of per-class Δι4, decoy vs relay | **0.29** | **0.28** |
| sign agreement (mass) | 65 % | 67 % |
| decoy ι4 on the ι4_r1 = 0 classes | 0 exactly | 0 exactly |

A **self-copy** field (OBJECT = the record's own KIND) was checked the same way at ε = 1. Its max |Δι4| over all
89,474 classes is **0.0**. This is a scratch check, not in the raw. It must be gated again when built.

## 3. Reading

1. **The decoy as specified is not a null.** It moves about 72 % (ε = 1) and 49 % (ε = ½) as much long-lag KIND
   information as the relay. A relay-sized decoy gain would therefore *not* mean "field count, not content".
   Skeleton v0.2 §4's second bullet would have misread it.
2. **It is a useful second intervention.** Its per-class Δι correlates only about 0.29 with the relay's, so it
   moves information in largely different classes. It carries no actor-binding content (the relay's value is
   chosen by actor; the decoy's is not). That separates two readings the relay alone cannot:
   - **|Δι| reading:** gain tracks the decoy's own |Δι| class by class, just as the relay's gain tracked the
     relay's.
   - **Binding-content reading:** the decoy gains little even where its |Δι| is large, and the relay gains where
     binding history matters.
3. **The field-count null exists and is cheap.** The self-copy field has Δι = 0 exactly and the identical
   ceiling, so it costs one added field with no information moved.

## 4. Consequence (owner's decision)

The design for skeleton v0.2 §3 items 2–3 uses **three non-baseline arms** beside r1: the relay r1ʀ, the t − 1
decoy, and the self-copy null, each with its exact gates (identical KIND ceiling class by class; Δι computed and
cached per class). The predictions of each reading, per arm and per class, are written and their severity computed
before anything trains. The skeleton gets a v0.3 note pointing here when that design is committed.
