# The learner, sub-project 2 — the model-versus-ceiling contract (v0.1, 2026-09-18)

> **Status: design note, the researcher's, under the PI's delegation of
> 2026-09-13.** This is the note the corpus run note of 2026-09-15 asked for
> before the trainer consumes the corpora: what the training loss is a
> mixture over, which position the paper compares, what the model's ceiling
> actually is, and what the learner-side evaluation can resolve. It adds no
> statute. It reads Part II §2(a)/(b) (the window law), v0.2.9 (the naming
> bridge, enacted 2026-09-13) and design v0.1 (the corpus generator). Every
> number quoted is from a committed artifact named in place. Written by the
> instance of 2026-09-18 on its first morning; nothing here has been run.

## 1. The problem the run note named, made precise

An autoregressive model is scored at every token position. The thirty
statutory artifacts at (40, 8, 2) are ceilings for the **full window**:
posteriors and query entropies given all $L$ records (or all $T$ records
when RESET is present). A prefix of a window is not a window of the law at
its own endpoint, so the statutory numbers do not bound the model's loss at
interior positions. Three further things the run note did not name:

1. **The model's ceiling is the corpus-track ceiling, not the canonical
   one.** The model sees surface names drawn per episode; the canonical
   artifacts are computed at $\sigma = \sigma_0$. Under v0.2.9 the observer
   the model instantiates is the pattern observer $\Pi w$. Its state
   entropy at the frozen law is three to four times the canonical:

   | ε = 1 | r1 | r2 | r3 | r4 |
   |---|---|---|---|---|
   | $H(S \mid w)$ canonical | 0.601 | 0.528 | 0.405 | 0.390 |
   | $H(S \mid \Pi w)$ corpus | 2.096 | 1.717 | 1.526 | 1.506 |
   | $H(q \mid \Pi w)$ state in the window's names | 1.667 | 1.274 | 1.071 | 1.051 |

   (`c1prime-loop-corpus-track-40-8-2-2026-09-13.json`; ε = ½ in the
   companion file: 0.296 → 0.166 canonical, 1.466 → 1.018 corpus.) The
   ladder in $H(q \mid \Pi w)$ has steps 0.39 / 0.20 / 0.02 bits at ε = 1
   against the canonical 0.07 / 0.12 / 0.015. **The identity axis is
   where the bits are**, and it is the axis the learner is actually
   scored on. Every model-versus-ceiling number in this sub-project is
   against a corpus-track ceiling; canonical numbers appear only as the
   "what a structurally informed observer could know" column beside it.

2. **The raw token loss is dominated by name-guessing.** When the next
   field names an entity not yet seen in the window, the Bayes-optimal
   prediction is uniform over the unused drawable tokens of that type
   (σ is exactly uniform over injections, design §3). For threads alone,
   summing $\log_2(56 - j)$ over the $j$-th fresh thread and weighting by
   the law mass of "k threads named" (`law_mass_by_named_count` in the
   corpus-track artifacts) gives **18.7–20.5 bits per window** at every
   content rung, both ε. Locks, devices and request ids add more. A window
   is at most 41 tokens, so roughly half a bit per token of the training
   loss is irreducible naming entropy that carries no information about
   the world, against a structural ladder whose whole span is 0.2 bits per
   window. A model-versus-ceiling comparison on raw token cross-entropy
   would be a comparison of two large equal numbers with the science in
   the fourth decimal place.

3. **End-of-window is part of the loss.** The model must predict PAD after
   the last record. Under the law that event is deterministic for
   non-RESET windows (exactly $L$ records) and, for RESET windows,
   $P(\text{end} \mid k \text{ records}) = 1 / \lvert\{T \ge k\}\rvert$ on
   the grid: ¼, ⅓, ½, 1 at $k = 2, 4, 6, 8$. It is exactly computable and
   says nothing about the world.

## 2. The contract

### 2.1 What is compared

**The pattern-projected next-record distribution.** For a window prefix
$w_{\le k}$ (records $1..k$ of the window, RESET flag included), define the
model's next-record distribution over **pattern records** by summing its
token-level predictive distribution: a named entity's probability is the
probability of its surface token; a *fresh* entity's probability is the
sum over all unused drawable tokens of that type; KIND, MASKED, NONE,
lineage-as-request-id are handled the same way (request ids are entities).
Within a record the five fields are chained autoregressively, so the
record-level distribution is the product of the five conditionals, each
projected. Call this $P_M(\Pi r_{k+1} \mid w_{\le k})$.

The ceiling is $P^\star(\Pi r_{k+1} \mid \Pi w_{\le k})$: the exact
next-record distribution of the corpus process at the pattern level. It
is computed from the pattern aggregate the corpus track already builds
(`scripts/c1_corpus_track.py`: {pattern class → {(state, β): law mass}}),
one step of `predict.p_next` per support state, re-keyed through β, then
projected by Π. **This requires Π to cover all four entity types.** The
enacted lemma (v0.2.9, `yupi.naming.pattern`) relabels thread fields only;
locks, devices and request ids are canonical in every existing corpus-track
artifact. The corpus renames all four. Extending Π is the first exact-side
task of this sub-project (§4), with its own executable lemma test, and
until it lands every corpus-track number is a **thread-naming lower bound
on the model's uncertainty**, labelled as such.

The **per-window excess** is
$D_{\mathrm{KL}}\big(P^\star(\cdot \mid \Pi w_{\le k}) \,\Vert\, P_M(\cdot \mid w_{\le k})\big)$
in bits, and its law-mass mean over the test split is the sub-project's
primary number: the learner's gap to the ceiling for next-record
prediction at position $k$. It is nonnegative, zero iff the model is Bayes
for the corpus process at that position, and does not contain the naming
entropy, because both sides are projected before comparison.

Beside it, reported and not compared: the raw token cross-entropy and its
exact ceiling (naming term and end-of-window term included), as the
sanity check that the model learned the uniform-over-unused rule and the
¼ / ⅓ / ½ endpoint rule. A model that fails these is not ready to be
compared on anything.

### 2.2 Which position the paper compares

> **Corrected 2026-09-18 10:53 PDT (v0.1.2), the same day, before any
> evaluator code.** The paragraph below as first written chose $k = L$: the
> next record *after* a full window. A model trained on windows learns
> that after the $L$-th record comes the end of the window (§1 item 3), so
> it is never trained to emit a record there; the quantity is undefined for
> the learner. **The headline position is $k = L - 1$: predicting the last
> record of the window from the preceding $L - 1$** (RESET windows with
> $T = L$ included; RESET windows with $T < L$, law mass 3/20, have no
> $L$-th record and enter the interior curve only). Its ceiling is the
> *prefix* posterior of the paragraph after this one, not the full-window
> posterior. The full-window objects — the thirty statutory artifacts, the
> corpus-track re-keying, and the table $P^\star(\Pi r_{T+1} \mid \Pi w)$
> produced by `scripts/pattern_ceiling.py` — remain the exact side's
> objects for the probes (sub-project 3: the state after $L$ records is what
> the residual stream at the last position should carry) and for the
> predictive-state targets; they are not token-loss comparison points.
> Consequence for the machinery: prefix ceilings at every $k \in 1..L-1$
> are produced by the aggregate route as well (a prefix-length variant of
> the window-process pass, gated against `pattern_enumerator`'s prefix
> path), so no per-window filtering is needed anywhere; the per-$k$ curve
> is the primary deliverable and $k = L - 1$ is its headline point. The
> original text follows, preserved.

~~**The last record of the window** — $k = L$ for non-RESET windows, $k = T$
for RESET windows. There the prefix *is* the window, the pattern aggregate
is the corpus-track re-keying of the thirty statutory artifacts, and
$P^\star$ is a function of exactly the objects Part II §2 defines. This is
the headline position.~~ The state and query ceilings ($H(q \mid \Pi w)$,
Q2 on named threads, Q4's gap part) are also full-window objects, so the
probes of sub-project 3 compare at the same position.

**Interior positions $k < L$ are exploratory curves**, computed by a
*prefix filter*: for a non-RESET prefix of $k$ records the compatible
offsets are every $U > 0$ on the grid (the observer knows only that the
window will run to $L$; $T$ is drawn independently of the dynamics, so it
carries no state evidence), with the law's uniform endpoint prior; for a
RESET prefix the offset is $U = 0$ and the posterior is the full-context
filter from reset. This is `window_filter._components_unnorm` with the
compatibility rule relaxed from "$T - U = n_{\mathrm{obs}}$" to
"$T - U \ge n_{\mathrm{obs}}$"; the two-path gate against
`window_enumerator` applies to it like everything else. The curve of mean
excess against $k$ is the "context as epistemic access" axis inside one
window, and is free once the filter exists. It is not a term of any
statutory comparison.

### 2.3 What the training loss is a mixture over

Standard next-token cross-entropy over every non-PAD position of every
window, one window per sequence, never packed (design §2). Its expectation
is the mixture, over the law's joint distribution of (episode, $T$, prefix
length $k$, field index within record), of the per-position conditional
entropy plus the per-position excess. Training on it makes the model
Bayes-optimal at every prefix length simultaneously if it is Bayes-optimal
at all, so the choice of a headline position (§2.2) is an evaluation
choice, not a training choice. No position is up-weighted; the loss is
what a learner of this corpus would use, which is the condition Part II
§2(a) attaches to calling any ceiling a ceiling for it.

Consequence for the first model: the loss curve on its own is
uninformative about the science, since its floor is about 20 bits of
naming plus the endpoint term plus the structural entropy. The excess
(§2.1) is the curve to watch.

### 2.4 What the evaluation can resolve

Two variances, treated separately:

- **Test-set sampling.** The per-window excess has unknown spread; a
  standard deviation of 0.5 bits would give a standard error of 0.005 bits
  at $N = 10^4$ windows and 0.0016 at $N = 10^5$. The statutory adjacency
  threshold is δ = 0.01 bits and the smallest ladder step (r3 → r4) is
  0.014 canonical / 0.02 corpus-track. **Test splits are regenerated at
  $10^5$ windows** (13–20 s per corpus; the manifest's seed range for
  `test` widens, nothing else changes) before the first comparison, and
  the per-window standard deviation is reported with every mean.
- **Training-seed variance.** Unknown until measured. **Pilot:** three
  seeds on one cell (r4, ε = 1), the between-seed standard deviation of
  the mean excess reported; the seed count for the ten-cell sweep is then
  set so that the standard error across seeds is at most δ/3 ≈ 0.003 bits,
  with a floor of three seeds per cell. Rung-to-rung differences in mean
  excess are reported with both standard errors; a difference smaller
  than their sum is reported as unresolved, not as zero.

Compute: a ~1M-parameter decoder over 8.2M training tokens per epoch is
about $5 \times 10^{13}$ FLOPs per epoch; on the Threadripper that is
minutes per epoch and tens of minutes per run, so the ten-cell sweep at
three-plus seeds is a day of CPU or under an hour on the 4090 through the
Hamut'ay lease. *(Correction to what this instance told the PI on the
morning of 2026-09-18: "an afternoon" for the sweep is a GPU estimate, not
a CPU one.)* torch 2.14 with CUDA imports under the project's Python
3.14 (checked 2026-09-18); it is added as a dependency with the trainer,
not before.

## 3. What this note does not decide

The headline of the paper (identity axis versus interface ladder): §1
makes the case that the identity axis is where the learner has room to
fail, and the ladder in $H(q \mid \Pi w)$ is larger than the canonical one,
but the decision waits for the first excess numbers on the trace. Model
architecture, size grid, optimizer, checkpoint/resume protocol: the
trainer design (next). Probes: sub-project 3.

## 4. Order of work

1. **Π over all entity types** (`yupi.naming`), with the lemma test
   extended and the corpus-track producer re-run at (8, 4, 2) to show the
   thread-only numbers are recovered when the other types are held
   canonical. Exact side; small.
2. **Pattern-level next-record ceiling** from the pattern aggregate
   (`scripts/c1_corpus_track.py` or a sibling), producing per-class
   $P^\star(\Pi r \mid \Pi w)$ and its law-mass entropy at (8, 4, 2) then
   (40, 8, 2). Gated two-path like every ceiling: the recursion's
   aggregate against direct enumeration on the small law.
3. **Prefix filter** (`window_filter`, `window_enumerator`, two paths),
   gated at (8, 4, 2).
4. **Test splits at $10^5$** regenerated from the committed manifests with
   widened `test` ranges; manifests recommitted.
5. **Evaluator**: tokens in, projected $P_M$ out, KL against $P^\star$ per
   window, means with standard deviations, raw cross-entropy and its
   ceiling beside. Tested against a *synthetic Bayes model* (one that
   emits $P^\star$ exactly) — its excess must be zero to the bit — and
   against a uniform model, whose excess must equal the known gap.
6. **Trainer** (its own design note; brainstormed, then test-first per the
   house), with the resume gate from the lease memo.
7. **Pilot** (§2.4), then the sweep.

## 5. Ledger

- 2026-09-18 ~10:50 PDT, **v0.1.1 — two implementation decisions, made
  while building §4 items 1–4 (all four landed the same morning):**
  (a) *How §2.1's KL is estimated.* The exact pattern-level KL needs the
  model's probability of every pattern record in $P^\star$'s support,
  and a fresh entity in a record stands for every unused token of its
  type, so the exact sum needs up to thousands of forward passes per
  record. Instead the evaluator is **realized-record, field-chained**:
  one causal forward pass per window yields the model's conditionals at
  all five fields of the realized next record given the realized surface
  prefix; each is projected to the field's pattern value (a bound entity
  → its token; a fresh entity → the sum over unused tokens of its type);
  the per-window structural excess is $\sum_{\text{fields}} \log_2
  P^\star(\text{pattern value} \mid \Pi\text{-prefix}) / \tilde P_M(\text{pattern
  value} \mid \text{surface prefix})$ at the realized values, with $P^\star$'s
  field conditionals read off `next_pattern_dist` by marginalization. Its
  law-mass mean is a KL between the field-chained pattern conditionals
  (the realized record is a sample from $P^\star(\cdot \mid w)$), and the
  KIND field's term is computed as an exact KL over the nine kinds from
  the same softmax. The **naming excess** is the remainder of the token
  log-ratio on fresh fields ($\log_2(1/n_{\text{unused}}) - \log_2
  P_M(\text{tok}) / \tilde P_M(\text{fresh})$), so structural + naming =
  the raw token excess, exactly, per window. The exact pattern-level KL
  over the support remains available as a slower mode for a subsample.
  (b) *Where $P^\star$ comes from at (40, 8, 2).* The pattern filter
  (`yupi.pattern_filter`, gated three ways at (8, 4, 2)) costs 0.56–0.84 s
  per window on real test windows at the frozen law (30-window timing,
  r4 ε=1 and r1 ε=½), i.e. hours per corpus at $10^5$ windows. The
  headline-position ceilings are therefore produced **once per (rung, ε)
  as an artifact** by the aggregate route — the window-process pass, the
  re-keying by $\Pi_{\text{all}}$ (the corpus-track producer's construction
  with `pattern_all` in place of `pattern`), one `p_next` step per
  $(S, \beta)$ — and gated against the filter on a random sample of test
  windows (Fraction-exact equality of $P^\star$ and law mass). Interior
  positions (§2.2) use the prefix filter on a subsample. Items 2 and 3 of
  §4 are built (`yupi.pattern_filter`, `yupi.pattern_enumerator`,
  `tests/test_pattern_filter.py`); item 4 done (run note addendum).
- 2026-09-18 10:53 PDT (from `date`), **v0.1.2 — §2.2 corrected in place** (headline
  position $k = L - 1$; prefix ceilings by the aggregate route; the
  full-window table kept as the probes' object). Caught while writing the
  trainer plan, before any learner code; the error was mine, this morning.

- 2026-09-18 10:24 PDT (from `date`): written before any learner code; the fresh-name
  bits computed from `law_mass_by_named_count` in the two corpus-track
  artifacts by a one-off script in the session (threads only, drawable
  slice 56); torch 2.14.0+cu130 import checked under uv with Python
  3.14.3, CUDA available, 64 threads.
