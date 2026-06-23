from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment run."""

    circuit_families: list[str] = field(default_factory=lambda: ["bell", "ghz", "qft", "grover"])
    qubit_sizes: dict[str, list[int]] = field(
        default_factory=lambda: {
            "bell": [2],
            "ghz": [3, 5, 7],
            "qft": [3, 5],
            "grover": [2],
        }
    )
    shots: int = 1000
    repetitions: int = 3
    seed: int = 42
    backends: list[str] = field(default_factory=lambda: ["ideal", "ibm", "quantinuum"])
    optimization_level: int = 1
    output_dirs: dict[str, str] = field(default_factory=lambda: {
        "raw": "data/raw",
        "processed": "data/processed",
        "figures": "results/figures",
        "tables": "results/tables",
        "reports": "results/reports",
    })
    timeout_seconds: int = 60
    allow_physical_hardware: bool = False
    provider_permissions: dict[str, bool] = field(
        default_factory=lambda: {"ibm": False, "quantinuum": False}
    )

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "ExperimentConfig":
        return cls(**values)
