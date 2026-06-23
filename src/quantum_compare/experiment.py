from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantum_compare.backends.ideal import IdealBackend
from quantum_compare.backends.ibm_superconducting import IBMBackend
from quantum_compare.backends.quantinuum_trapped_ion import QuantinuumBackend
from quantum_compare.circuits import build_bell_state, build_ghz_state, build_grover_search, build_qft
from quantum_compare.metrics import (
    count_to_probabilities,
    expected_state_probability,
    hellinger_fidelity,
    total_variation_distance,
)
from quantum_compare.models import ExperimentConfig


class ExperimentRunner:
    """Run the configured comparison suite and save results to disk."""

    def __init__(self, config: ExperimentConfig, base_dir: str | Path | None = None) -> None:
        self.config = config
        self.base_dir = Path(base_dir or ".")
        self._backends = {
            "ideal": IdealBackend(),
            "ibm": IBMBackend(),
            "quantinuum": QuantinuumBackend(),
        }

    def run_suite(self, backend_name: str | None = None, suite: str = "core") -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for family in self.config.circuit_families:
            for size in self.config.qubit_sizes.get(family, []):
                circuit = self._build_circuit(family, size)
                ideal_result = self._run_backend("ideal", circuit, shots=self.config.shots)
                ideal_probs = self._probabilities_from_result(ideal_result)
                for provider in self._selected_backends(backend_name):
                    try:
                        compiled_result = self._run_backend(provider, circuit, shots=self.config.shots)
                        compiled_probs = self._probabilities_from_result(compiled_result)
                        row = {
                            "experiment_id": self._make_id(family, size, provider),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "circuit_family": family,
                            "qubit_count": size,
                            "shots": self.config.shots,
                            "repetition": 1,
                            "provider": provider,
                            "backend_identifier": compiled_result.get("backend_name"),
                            "architecture": self._backends[provider].architecture,
                            "execution_type": compiled_result.get("execution_type"),
                            "logical_depth": self._logical_depth(circuit),
                            "logical_gate_count": self._logical_gate_count(circuit),
                            "logical_two_qubit_gate_count": self._logical_two_qubit_gate_count(circuit),
                            "compiled_depth": self._logical_depth(circuit),
                            "compiled_gate_count": self._logical_gate_count(circuit),
                            "compiled_two_qubit_gate_count": self._logical_two_qubit_gate_count(circuit),
                            "measurement_counts": compiled_result.get("counts"),
                            "probability_distribution": compiled_probs,
                            "expected_state_probability": expected_state_probability(ideal_probs, "0" * size),
                            "total_variation_distance": total_variation_distance(ideal_probs, compiled_probs),
                            "hellinger_fidelity": hellinger_fidelity(ideal_probs, compiled_probs),
                            "job_id": compiled_result.get("job_id"),
                            "job_status": compiled_result.get("job_status"),
                            "error_message": None,
                            "device_metadata": compiled_result.get("metadata"),
                        }
                    except Exception as exc:  # noqa: BLE001
                        row = {
                            "experiment_id": self._make_id(family, size, provider),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "circuit_family": family,
                            "qubit_count": size,
                            "shots": self.config.shots,
                            "repetition": 1,
                            "provider": provider,
                            "backend_identifier": None,
                            "architecture": self._backends[provider].architecture,
                            "execution_type": None,
                            "logical_depth": self._logical_depth(circuit),
                            "logical_gate_count": self._logical_gate_count(circuit),
                            "logical_two_qubit_gate_count": self._logical_two_qubit_gate_count(circuit),
                            "compiled_depth": None,
                            "compiled_gate_count": None,
                            "compiled_two_qubit_gate_count": None,
                            "measurement_counts": None,
                            "probability_distribution": None,
                            "expected_state_probability": None,
                            "total_variation_distance": None,
                            "hellinger_fidelity": None,
                            "job_id": None,
                            "job_status": "failed",
                            "error_message": str(exc),
                            "device_metadata": None,
                        }
                    rows.append(row)
        self._save_results(rows)
        return rows

    def _selected_backends(self, backend_name: str | None) -> list[str]:
        if backend_name is None:
            return [name for name in self.config.backends if name in self._backends]
        if backend_name == "all":
            return [name for name in self.config.backends if name in self._backends]
        if backend_name not in self._backends:
            raise ValueError(f"Unknown backend '{backend_name}'.")
        return [backend_name]

    def _build_circuit(self, family: str, size: int) -> Any:
        if family == "bell":
            return build_bell_state()
        if family == "ghz":
            return build_ghz_state(size)
        if family == "qft":
            return build_qft(size)
        if family == "grover":
            return build_grover_search(size)
        raise ValueError(f"Unknown circuit family '{family}'.")

    def _run_backend(self, backend_name: str, circuit: Any, shots: int) -> dict[str, Any]:
        adapter = self._backends[backend_name]
        compiled = adapter.compile_circuit(circuit)
        return adapter.execute(compiled, shots=shots, seed=self.config.seed)

    def _probabilities_from_result(self, result: dict[str, Any]) -> dict[str, float]:
        counts = result.get("counts") or {}
        total_shots = self.config.shots
        return count_to_probabilities(counts, shots=total_shots)

    def _save_results(self, rows: list[dict[str, Any]]) -> None:
        output_dir = self.base_dir / self.config.output_dirs["processed"]
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        csv_path = output_dir / f"results_{timestamp}.csv"
        json_path = output_dir / f"results_{timestamp}.json"
        manifest_path = output_dir / f"manifest_{timestamp}.json"
        dataframe = pd.DataFrame(rows)
        dataframe.to_csv(csv_path, index=False)
        dataframe.to_json(json_path, orient="records", indent=2)
        manifest = {
            "timestamp": timestamp,
            "csv": str(csv_path),
            "json": str(json_path),
            "rows": len(rows),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _logical_depth(self, circuit: Any) -> int:
        return circuit.depth()

    def _logical_gate_count(self, circuit: Any) -> int:
        return circuit.size()

    def _logical_two_qubit_gate_count(self, circuit: Any) -> int:
        return circuit.num_nonlocal_gates()

    def _make_id(self, family: str, size: int, provider: str) -> str:
        return f"{family}-{size}-{provider}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
