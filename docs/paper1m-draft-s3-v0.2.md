# Paper 1 (methods), §3 draft v0.2 (2026-10-15): What each interface lets an observer know

> **Status: DRAFT v0.2, owning instance.** v0.1 revised per `paper1m-draft-review-2026-10-15.md` (items 4, 6, 9, Codex #13). Governed by `paper1-skeleton-v0.9.md` §3. Compressed from
> `paper1-draft-s3-v0.4.md`, whose numbers and gates it inherits; every table is cited to its raw at the end. Not
> yet reviewed.

## 3. What each interface lets an observer know, exactly

For each interface and each class of observable windows, Yupana gives the exact posterior over hidden state and
the exact law of the next event. Unless stated otherwise, the observer is the *pattern observer* (it sees entity
names only up to renaming, as a learner trained on per-episode names does), the position is after seven records,
and the target is the next record's KIND. Position-7 quantities cover the windows that run at least seven records:
0.85 of window law mass.

### 3.1 Where the uncertainty comes from

The next-KIND entropy of a class c splits exactly into two parts:
- **R(c) = Σ_s P(s | c) H(KIND | s)**, the randomness an observer who knew the hidden state would still face;
- **G(c) = H\*(c) − R(c) = I(KIND; S | c)**, the part due to state the interface withholds.

| ε = 1 | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| H\*, the ceiling | 1.176 | 0.999 | 0.955 | 0.911 | 0.911 |
| R, transition randomness | 0.609 | 0.609 | 0.609 | 0.609 | 0.609 |
| G, observation gap | 0.567 | 0.391 | 0.346 | 0.302 | 0.302 |

*Bits, law-mass means. At ε = ½: R = 0.544 on every rung; G = 0.560, 0.329, 0.279, 0.240, 0.240.*

R's mean is the same on every interface **by construction**: it is E[H(KIND | S)], which no observation changes.
Per class, R does vary. The finding is in G: about half of the sparsest interface's mean next-KIND uncertainty at
position 7 is withheld state, and a third of r3's (r4 adds nothing on this target, so five interfaces give four
distinct KIND ceilings). On average, added fields act only on the withheld part;
the mean randomness is out of any interface's reach.

### 3.2 Knowing the state is not predicting the next event

The classical figure of merit for telemetry is identifiability: how much uncertainty about the hidden state the
record leaves. Log placement work minimises a quantity of this kind (Zhao et al. 2017). For the structural observer
at the window's last record, on the whole-record target:

| ε = 1 | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| state entropy H(S \| window) | 3.947 | 0.601 | 0.528 | 0.405 | 0.390 |
| next-record observation gap | 0.442 | 0.150 | 0.135 | 0.106 | 0.103 |

Most state uncertainty is irrelevant to the next record: on r1, 0.60 bits of state uncertainty correspond to 0.15
bits of reducible next-record uncertainty. (The gap is a mutual information with the state, so it cannot exceed the
state entropy; the size of the difference is the finding.) On the content interfaces, each further field (OBJECT,
RELATED, LINEAGE) removes 3–5 times more of the first than of the second (4.7, 4.3, 4.4 at ε = 1; 4.3, 3.1, 4.0 at
ε = ½), and both measures rank those fields the same way. The first field, ACTOR, is not comparable: it also changes
the next-record target, since r0's record is KIND alone (its ratio is 11.5 at ε = 1). Along this nested ladder, an
identifiability objective would choose the same fields as a predictor's ceiling while overstating the relevant
uncertainty by a fairly stable factor; that need not hold for unrestricted field selection. This
table uses a different observer, position and target from §3.1; the two are not to be compared number by number.

### 3.3 Where in the window the knowable information sits

For a class c, let ι_m(c) be the information about the next KIND that lies more than m records back: the KL
divergence from the full-window law to the law given only the last m records. Its law-mass mean is the interface's
*lag profile*. It equals the order-m entropy minus the ceiling: a per-class, exact relative of the m-local entropy of Someya et
al. (2025), with two differences in convention (our order m counts records, and conditions on m of them, where
theirs conditions on m − 1 symbols), computed for each interface of one fixed system.

The profiles cross. At lags 1–3, r3 and r4 (effectively tied; r4 is larger by under 10⁻⁵ bits) leave the most
information beyond m records; from m = 4, r2 does
(ι₄ = 0.282 against r3's 0.259, ε = 1). A richer field both adds information and moves information that was already
available closer to the point of use, and the ceiling registers only the first. The crossing is about 0.02 bits in
one world, and we report it as an illustration of why a profile is needed, not as a general effect.

### 3.4 Rewrites that hold the ceiling

A *window-level* rewrite may fill a masked slot with any function of the window's earlier records. It adds nothing an
observer of the window lacked, so the ceiling is unchanged class by class, which three gates verify exactly (equal
KIND marginals per class; equal multisets of record probabilities per class; an independent construction checked by
brute force on small worlds). We use one such rewrite in §5: the *relay*, which writes into each record the KIND of
the same actor's previous record in the window.

---

## Provenance

- 3.1: `kind-uncertainty-split-40-8-2-k7-eps1-2026-10-15.json`, `…-eps1_2-…`; R = 0.608521 / 0.544118 at every rung;
  each H\* reproduces the ceilings of `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`. Reproduced by Codex
  (v0.8 review #7).
- 3.2: `state-vs-predictive-40-8-2-2026-10-13.json`; ratios 4.7 / 4.3 / 4.4 (ε = 1) and 4.3 / 3.1 / 4.0 (ε = ½),
  reproduced by Codex (v0.8 review #7).
- 3.3: `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json` (s3 v0.4 §3.2 table); KL and entropy-difference routes agree
  to 3 × 10⁻¹⁴.
- 3.4: `three-arm-exact-side-r1S-2026-10-05.log` (gates A–C); relay construction, `paper1-draft-s3-v0.4.md` §3.3.
- Zhao et al., Log20, SOSP 2017; Someya et al., ACL 2025.
