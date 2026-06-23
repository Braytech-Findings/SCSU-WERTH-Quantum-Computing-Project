from __future__ import annotations

from typing import Any

from qiskit import QuantumCircuit

from quantum_compare.backends.base import BackendAdapter


class QuantinuumBackend(BackendAdapter):
    """Dry-run Quantinuum adapter that clearly distinguishes emulator and hardware expectations."""

    def __init__(self) -> None:
        self.name = "quantinuum-dry-run"
        self.provider = "quantinuum"
        self.architecture = "trapped-ion"
        self.execution_type = "emulator"

    def is_available(self) -> bool:
        return False

    def discover_devices(self) -> list[dict[str, Any]]:
        return [
            {
                "name": self.name,
                "provider": self.provider,
                "architecture": self.architecture,
                "status": "dry-run",
                "note": "Configure Quantinuum access to discover official emulator or hardware targets.",
            }
        ]

    def compile_circuit(self, circuit: QuantumCircuit, **kwargs: Any) -> QuantumCircuit:
        compiled = circuit.copy()
        compiled.metadata["target"] = "unavailable"
        compiled.metadata["target_family"] = "trapped-ion"
        return compiled

    def execute(self, circuit: QuantumCircuit, shots: int, **kwargs: Any) -> dict[str, Any]:
        return {
            "backend_name": self.name,
            "provider": self.provider,
            "architecture": self.architecture,
            "execution_type": self.execution_type,
            "counts": None,
            "job_id": None,
            "job_status": "dry_run",
            "metadata": {
                "note": "Quantinuum execution requires access to the supported emulator or hardware route.",
                "target": "unavailable",
            },
            "compiled_circuit": circuit,
        }

    def get_job_status(self, job_id: str) -> str:
        return "dry-run"

    def normalize_result(self, result: Any) -> dict[str, Any]:
        return result
