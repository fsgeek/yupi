# Direct-Handoff Self-Deadlock — Reproduction Record

**Status:** verified defect artifact, not a repair.

**Date:** 2026-08-20

**Audited repository state:** `d19ef25cba54be463990ddbcd7040162c02e3843`

## Command

```bash
uv run python scripts/reproduce_direct_handoff_self_deadlock.py
```

## Captured output

```json
{
  "bad_path_count": 1,
  "bad_path_mass": "1/8",
  "configuration": "C0a",
  "horizon": 10,
  "witnesses": [
    {
      "lock_owner": [
        0
      ],
      "lock_wait_queues": [
        [
          0
        ]
      ],
      "path_probability": "1/8",
      "record_tail": [
        {
          "actor": 1,
          "kind": "RELEASE",
          "related": 0
        },
        {
          "actor": 0,
          "kind": "DISPATCH",
          "related": null
        },
        {
          "actor": 0,
          "kind": "BLOCK",
          "related": 0
        }
      ],
      "reported_invariant_violations": [],
      "status": [
        [
          "LOCK_BLOCKED",
          0
        ],
        [
          "TERMINATED"
        ]
      ]
    }
  ]
}
```

The final state has thread 0 both owning lock 0 and waiting in lock 0's
queue. `check_invariants` reports no violation.

## Independent verification performed in the originating review

The same checkout produced:

```text
sampled_c0b_records_at_h40 11
101 passed in 27.35s
```

The first line independently verifies that `sample_episode` stops early for
`WorldConfig.c0b("fifo")`, `c0b_programs()`, horizon 40, seed 0, contrary to
the fixed-horizon absorbing-IDLE episode law. The green suite demonstrates
that the existing tests did not detect either semantic mismatch; it is not
evidence that the findings are harmless.
