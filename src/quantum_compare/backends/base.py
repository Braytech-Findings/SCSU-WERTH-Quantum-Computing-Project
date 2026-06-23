from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from qiskit import QuantumCircuit


class BackendAdapter(ABC):
    """Common interface for ideal, IBM, and Quantinuum adapters."""

    name: str
    provider: str
    architecture: str
    execution_type: str

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the backend can be used in the current environment."""

    @abstractmethod
    def discover_devices(self) -> list[dict[str, Any]]:
        """Return discovered target devices or emulator descriptions."""

    @abstractmethod
    def compile_circuit(self, circuit: QuantumCircuit, **kwargs: Any) -> QuantumCircuit:
        """Compile a logical circuit for the backend."""

    @abstractmethod
    def execute(self, circuit: QuantumCircuit, shots: int, **kwargs: Any) -> dict[str, Any]:
        """Execute the circuit and return a normalized result payload."""

    @abstractmethod
    def get_job_status(self, job_id: str) -> str:
        """Return a status string for a submitted job if one exists."""

    @abstractmethod
    def normalize_result(self, result: Any) -> dict[str, Any]:
        """Normalize provider output to a common structure."""
