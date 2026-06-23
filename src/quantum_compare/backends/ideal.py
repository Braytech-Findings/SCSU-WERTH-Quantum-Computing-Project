from __future__ import annotations

from typing import Any

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from quantum_compare.backends.base import BackendAdapter


class IdealBackend(BackendAdapter):
    """Noiseless reference backend implemented with Qiskit Aer."""

    def __init__(self) -> None:
        self.name = "aer_simulator"
        self.provider = "qiskit-aer"
        self.architecture = "ideal"
        self.execution_type = "ideal simulator"

    def is_available(self) -> bool:
        return True

    def discover_devices(self) -> list[dict[str, Any]]:
        return [{"name": self.name, "provider": self.provider, "architecture": self.architecture}]

    def compile_circuit(self, circuit: QuantumCircuit, **kwargs: Any) -> QuantumCircuit:
        return circuit

    def execute(self, circuit: QuantumCircuit, shots: int, **kwargs: Any) -> dict[str, Any]:
        simulator = AerSimulator(method="automatic")
        result = simulator.run(circuit, shots=shots, seed_simulator=kwargs.get("seed", 42)).result()
        counts = result.get_counts(circuit)
        return {
            "backend_name": self.name,
            "provider": self.provider,
            "architecture": self.architecture,
            "execution_type": self.execution_type,
            "counts": counts,
            "job_id": None,
            "job_status": "finished",
            "metadata": {"method": "aer"},
        }

    def get_job_status(self, job_id: str) -> str:
        return "finished"

    def normalize_result(self, result: Any) -> dict[str, Any]:
        return result
