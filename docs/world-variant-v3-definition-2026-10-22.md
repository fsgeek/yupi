# World variant V3: occupancy-dependent completion (definition, 2026-10-22)

> Owning instance. This defines a versioned world *beside* the frozen one. It is not an amendment of the paper's
> world: every frozen artifact, corpus and number keeps its meaning. It exists for the world-variant gate
> (`world-variant-gate-declared-2026-10-22.md`, stamped at 707a5e2 before this code was written).

## What changes

The kernel's Part II §3.4 completion rule, in one place: when n ≥ 1 requests are pending (summed over devices), the
total completion probability is `completion_p_by_occupancy[n − 1]` instead of the scalar `completion_p`. Each pending
request still receives an equal share. The residual 1 − p still goes to the scheduling stage. V3 is
`WorldConfig.c1(p_by_occupancy=(1/4, 1/2))`: 1/4 with one request pending, 1/2 with two (queue depth 2).

Code: `kernel.completion_mass(state, cfg)`, used at both sites that previously read `cfg.completion_p`. The new
config field `completion_p_by_occupancy` defaults to `None`, which means the scalar rule, so every existing config is
unchanged.

## Checks (all before any V3 table was read)

- `tests/test_kernel.py::test_occupancy_dependent_completion_mass`: completion mass is 1/4 with one pending and 1/2
  (as 1/4 + 1/4) with two; `enabled()` sums to exactly 1.
- `tests/test_kernel.py::test_occupancy_rule_absent_matches_scalar`: `(1/3, 1/3)` gives transition-for-transition
  identical distributions to the scalar 1/3 world over six steps from reset.
- **Support unchanged** (BFS from reset, c1prime-loop programs): reachable states and (state, next state, kind)
  edges are identical sets for V0 and V3. At ε = 1 there are 1,974 states and 4,933 edges; at ε = ½, 4,236 and 10,617.
  Only probabilities differ, as the gate requires.
- **V0 regression:** `kind_uncertainty_split.py` with the new options at their defaults reproduces the pinned
  `split-v2` rows byte-for-byte (`split-v2-rows-sha256-2026-10-15.txt`), and the §3.1 ceiling gate holds.

## Why this rule

A device that completes faster under load (as with batching) is a plausible systems behaviour. More to the point,
it makes the completion coin depend on hidden state that the sparse interfaces do not always reveal: queue
occupancy. Under V3, an observer that knows the occupancy faces a pure coin of 1/4 or 1/2. An observer that does not
faces a mixture, which puts some of the device's randomness into the withheld-state term. It is the smallest change
that tests the paper's statement that the contrast's narrowness is "a consequence of design".
