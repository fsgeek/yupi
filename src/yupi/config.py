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
    def c0a(cls, p: Fraction = Fraction(1, 3)) -> "WorldConfig":
        """Canonical minimal config: 2 threads, 1 CPU, 1 lock, 1 device,
        depth 1, pool 2, completion_p = p (default 1/3), epsilon = 1, fifo discipline.

        Args:
            p: Device completion probability (default Fraction(1, 3))
        """
        return cls(
            n_threads=2,
            n_cpus=1,
            n_locks=1,
            n_devices=1,
            queue_depth=1,
            req_pool=2,
            completion_p=p,
            epsilon=Fraction(1),
            discipline="fifo"
        )
