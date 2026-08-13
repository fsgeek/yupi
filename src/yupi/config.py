from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class WorldConfig:
    """Configuration for the Yupana simulator world.

    All numeric fields must use exact arithmetic (Fraction).
    Represents a fixed system configuration: thread count, CPU cores, locks,
    devices, queue depth, request pool size, device completion probability,
    epsilon for tracing, and scheduling discipline.
    """
    n_threads: int
    n_cpus: int
    n_locks: int
    n_devices: int
    queue_depth: int
    req_pool: int
    completion_p: Fraction
    epsilon: Fraction
    discipline: str

    @classmethod
    def c0a(cls) -> "WorldConfig":
        """Canonical minimal config: 2 threads, 1 CPU, 1 lock, 1 device,
        depth 1, pool 2, completion_p = 2/3, epsilon = 1, fifo discipline.
        """
        return cls(
            n_threads=2,
            n_cpus=1,
            n_locks=1,
            n_devices=1,
            queue_depth=1,
            req_pool=2,
            completion_p=Fraction(2, 3),
            epsilon=Fraction(1),
            discipline="fifo"
        )
