# Do learners err toward hidden state? Declared before computing (2026-10-26)

> Owning instance. Ledger item 3, now load-bearing. After the size of errors is accounted for, about 0.25 of the
> two-step certification floor's gap remains (`prospective-certification-v2-result-2026-10-26.md`), and error
> *direction* is the candidate. 22 models (12 cell models, 10 ladder learners), k = 6 test dumps, pure-truth windows
> only.

**Measure.** For a pure window with true law P_c and model output q, at one and at two steps:
- err = q − P_c;
- u_W = P_W − P_c, where P_W is the nearest substantially withheld law to P_c (exact, TV);
- u_P = P_P − P_c, where P_P is the nearest *other pure* law to P_c. This is the baseline: is the error pointed at
  hidden-state alternatives in particular, or at nearby alternatives in general?
- cos_W = cosine(err, u_W) and cos_P = cosine(err, u_P), in Euclidean coordinates on the KIND (or KIND-pair) vector.
- Per model, report the mean and median over pure windows.

## Predictions

- **W1 (toward hidden state).** At two steps, mean cos_W > 0 for at least 18 of 22 models.
- **W2 (specifically, not just toward neighbours).** At two steps, mean cos_W > mean cos_P for at least 18 of 22 models.
- **W3 (one step too).** W1 holds at one step for at least 18 of 22.

**Basis.** Cross-entropy rewards hedging, and a hedge is a mixture, which is what withheld-state laws are. So I
expect errors to lean toward mixtures. If W2 fails while W1 holds, learners err toward nearby alternatives without
favouring hidden state, and the PACMI-shaped reading ("models over-attribute uncertainty to what they cannot see")
is not supported here.
