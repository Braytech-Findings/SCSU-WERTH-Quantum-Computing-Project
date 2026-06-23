from __future__ import annotations

from typing import Any

from qiskit import QuantumCircuit

from quantum_compare.backends.base import BackendAdapter


class IBMBackend(BackendAdapter):
    """Dry-run IBM adapter that uses current qBraid-style naming without fabricating hardware access."""

    def __init__(self) -> None:
        self.name = "ibm-dry-run"
        self.provider = "ibm"
        self.architecture = "superconducting"
        self.execution_type = "simulator"

    def is_available(self) -> bool:
        return False

    def discover_devices(self) -> list[dict[str, Any]]:
        return [{
            "name": self.name,
            "provider": self.provider,
            "architecture": self.architecture,
            "status": "dry-run",
            "note": "Configure qBraid IBM access to discover real targets.",
        }]

    def compile_circuit(self, circuit: QuantumCircuit, **kwargs: Any) -> QuantumCircuit:
        return circuit

    def execute(self, circuit: QuantumCircuit, shots: int, **kwargs: Any) -> dict[str, Any]:
        return {
            "backend_name": self.name,
            "provider": self.provider,
            "architecture": self.architecture,
            "execution_type": self.execution_type,
            "counts": {},
            "job_id": None,
            "job_status": "dry-run",
            "metadata": {"note": "IBM execution requires real qBraid/IBM credentials or a supported local simulator."},
        }

    def get_job_status(self, job_id: str) -> str:
        return "dry-run"

    def normalize_result(self, result: Any) -> dict[str, Any]:
        return result
