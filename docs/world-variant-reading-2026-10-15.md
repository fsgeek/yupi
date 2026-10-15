# World variant by reparameterisation: kernel reading (2026-10-15)

> Owning instance. A reading, not a design. Question: can probabilities be made heterogeneous, keeping every
> currently possible transition possible (so posterior support is unchanged), without breaking kernel or observer
> invariants? Motivation: `paper1-skeleton-v0.7.md` §4.2–4.3 (three H\* values on the random side; the one-step
> predictive determines the split).

**Device completion** (`src/yupi/kernel.py:227-228`): one `completion_p`, shared uniformly over candidate requests
(`share = p / len(candidates)`); the residual 1 − p goes to stage B (`kernel.py:536-549`). Making p depend on the
device (p_d, all in (0, 1)) changes probabilities only. Effect: the "random" next-KIND laws gain one template per
(device mix, queue state) instead of one 1/3 coin. **Adds templates to R.** Risk: low; `_merge` and the support are
untouched.

**Dispatch** (`_epsilon_policy`, `kernel.py:99-140`): uniform over candidates with mass ε, plus one round-robin pick
with 1 − ε; at ε = 1 the cursor is never written. Per-thread weights w_t (all > 0) are possible, but the documented
cursor invariant (every choice advances the cursor identically, so uniform and round-robin picks of the same
thread merge) must be kept; its earlier violation inflated C0a's reachable states 198 vs 72. Risk: moderate; must be
re-gated against the support bound.

**Naming** (`src/yupi/pattern_filter.py:6-14`): the pattern observer's filter needs only that the naming
permutation σ is uniform and independent of the dynamics. Heterogeneous thread weights leave σ untouched. They do
create a new hidden quantity for the pattern observer: which renamed thread carries which weight, inferable only
from behaviour. **Adds to G.**

**So two independent knobs exist:** per-device completion probabilities diversify transition randomness; per-thread
dispatch weights add hidden binding. Both keep the support's transition graph, which is what the exact filter's cost
depends on.

**Gate before any spec change** (exact side, CPU, hours): build tables for one or two parameter settings at the frozen
law, then rerun `scripts/one_step_identifiability.py` and the overlap count. Pass if both (a) identical one-step
predictions hide materially different splits on ≥ 5 % of mass and (b) matched random-vs-hidden contrasts cover
≥ 10 % of mass across ≥ 3 mechanisms. Thresholds to be fixed in a declared note before the run; this reading
does not fix them. Any variant is a versioned world (Part II amendment), with new corpora and a new ladder.
