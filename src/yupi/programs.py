from typing import Tuple

COMPUTE = ("COMPUTE",)


def acquire(l: int) -> Tuple[str, int]:
    """Create an ACQUIRE instruction for lock l."""
    return ("ACQUIRE", l)


def release(l: int) -> Tuple[str, int]:
    """Create a RELEASE instruction for lock l."""
    return ("RELEASE", l)


def io(d: int) -> Tuple[str, int]:
    """Create an IO instruction for device d."""
    return ("IO", d)


Program = Tuple[Tuple, ...]


def validate_lock_order(programs: Tuple[Program, ...]) -> bool:
    """Validate lock order discipline (I6) for all programs.

    Returns True iff in every program, ACQUIRE lock indices between paired
    ACQUIRE/RELEASE are strictly increasing while held, and every acquired
    lock is released before program end. This ensures no deadlock cycle can
    occur and no TERMINATED thread retains ownership (I3).

    For each program, tracks the stack of held locks. When an ACQUIRE occurs,
    the lock index must be strictly greater than the maximum held lock index.
    When a RELEASE occurs, the lock must be the top of the held-locks stack.
    """
    for program in programs:
        held_locks = []

        for instruction in program:
            if instruction[0] == "ACQUIRE":
                lock_idx = instruction[1]
                if held_locks and lock_idx <= max(held_locks):
                    return False
                held_locks.append(lock_idx)
            elif instruction[0] == "RELEASE":
                lock_idx = instruction[1]
                if not held_locks or held_locks[-1] != lock_idx:
                    return False
                held_locks.pop()

        # 2026-08-20 audit (finding 10): a program ending while holding a lock
        # leaves a TERMINATED owner (violating I3) — outside the declared machine.
        if held_locks:
            return False

    return True


def c0b_programs() -> Tuple[Program, Program]:
    """Return the canonical C0b program pair.

    Thread 0: (io(0),)
    Thread 1: (io(0),)

    The minimal workload placing two requests in flight (Part I,
    Configurations): with one CPU, thread 0 issues and blocks, thread 1 is
    dispatched and issues, and the depth-2 queue holds both requests. No
    locks, no compute: every record kind this world can emit concerns the
    device.
    """
    thread_0 = (io(0),)
    thread_1 = (io(0),)
    return (thread_0, thread_1)


def c0c_programs() -> Tuple[Program, Program, Program]:
    """Return the canonical C0c program triple.

    Thread 0: (io(0),)
    Thread 1: (COMPUTE,)
    Thread 2: (COMPUTE,)

    The minimal workload for the 2-CPU scheduling witnesses: threads 1-2
    supply the pure-compute pair whose dispatch and execution ordering the
    scheduler must choose between; thread 0's single IO puts a request in
    flight so Stage A completion can fire while both CPU slots are busy.
    """
    thread_0 = (io(0),)
    thread_1 = (COMPUTE,)
    thread_2 = (COMPUTE,)
    return (thread_0, thread_1, thread_2)


def c1_programs() -> Tuple[Program, Program, Program, Program]:
    """Return the canonical C1 program quadruple.

    Thread 0: (acquire(0), COMPUTE, release(0), io(0))
    Thread 1: (acquire(0), acquire(1), release(1), release(0))
    Thread 2: (COMPUTE, acquire(0), release(0), io(0))
    Thread 3: (io(0), acquire(1), release(1), io(0))

    Design arguments (implementation-time choice per Part I line 169,
    recorded here per the C0c precedent):

    - Multi-waiter wake: threads 1 and 2 both contend for lock 0 while
      thread 0 can hold it; thread 2's leading COMPUTE staggers its
      arrival so BOTH wait-queue orders (1,2) and (2,1) are reachable —
      the ambiguity a windowed observer inherits when the BLOCK events
      fall before its window (full-context observers lose nothing, per
      the injectivity theorem).
    - Nested hold: thread 1 acquires lock 0 then lock 1 (I6
      strictly-increasing), witnessing two-lock machinery; thread 3
      contends on lock 1 so nested ownership meets a waiter.
    - QUEUE_BLOCKED: three IO issuers (0, 2, 3) against queue depth 2 —
      the queue-full BLOCK branch has been sound-but-unwitnessed in every
      C0 config (two issuers can never fill a depth-2 queue before
      issuing); C1 is the first world where it must fire.
    - D6 hazard audit: no instruction computes over identities; all
      structure is relational (who owns, who waits, who wakes); no
      permutation-composition state tracking is embedded.
    """
    thread_0 = (acquire(0), COMPUTE, release(0), io(0))
    thread_1 = (acquire(0), acquire(1), release(1), release(0))
    thread_2 = (COMPUTE, acquire(0), release(0), io(0))
    thread_3 = (io(0), acquire(1), release(1), io(0))
    return (thread_0, thread_1, thread_2, thread_3)


def c0a_programs() -> Tuple[Program, Program]:
    """Return the canonical C0a program pair.

    Thread 0: (acquire(0), COMPUTE, release(0), io(0))
    Thread 1: (COMPUTE, acquire(0), release(0))

    Short enough that exhaustive tree stays small; exercises lock contention,
    blocking, and I/O.
    """
    thread_0 = (acquire(0), COMPUTE, release(0), io(0))
    thread_1 = (COMPUTE, acquire(0), release(0))
    return (thread_0, thread_1)
