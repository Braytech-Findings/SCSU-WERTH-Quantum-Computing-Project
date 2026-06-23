from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantum_compare.architecture import IBMArchitectureModel, QuantinuumArchitectureModel
from quantum_compare.backends.ideal import IdealBackend
from quantum_compare.backends.ibm_superconducting import IBMBackend
from quantum_compare.backends.quantinuum_trapped_ion import QuantinuumBackend
from quantum_compare.circuits import (
    build_bell_state,
    build_ghz_state,
    build_grover_search,
    build_qft,
)
from quantum_compare.metrics import (
    count_to_probabilities,
    expected_state_probability,
    hellinger_fidelity,
    success_probability,
    total_variation_distance,
)
from quantum_compare.models import ExperimentConfig
from quantum_compare.visualization import generate_visualizations


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
        self._architecture_models = {
            "ibm": IBMArchitectureModel(),
            "quantinuum": QuantinuumArchitectureModel(),
        }

    def run_suite(
        self, backend_name: str | None = None, suite: str = "core"
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for family in self.config.circuit_families:
            for size in self.config.qubit_sizes.get(family, []):
                circuit = self._build_circuit(family, size)
                for repetition in range(1, self.config.repetitions + 1):
                    ideal_result = self._run_backend("ideal", circuit, shots=self.config.shots)
                    ideal_probs = self._probabilities_from_result(ideal_result)
                    rows.append(
                        self._build_row(
                            family,
                            size,
                            repetition,
                            "ideal",
                            circuit,
                            ideal_result,
                            ideal_probs,
                            ideal_probs,
                            baseline=True,
                        )
                    )
                    for provider in self._selected_backends(backend_name):
                        if provider == "ideal":
                            continue
                        try:
                            compiled_result = self._run_backend(
                                provider, circuit, shots=self.config.shots
                            )
                            compiled_circuit = compiled_result.get(
                                "compiled_circuit"
                            ) or self._backends[provider].compile_circuit(circuit)
                            compiled_probs = self._probabilities_from_result(compiled_result)
                            rows.append(
                                self._build_row(
                                    family,
                                    size,
                                    repetition,
                                    provider,
                                    circuit,
                                    compiled_result,
                                    ideal_probs,
                                    compiled_probs,
                                    baseline=False,
                                    compiled_circuit=compiled_circuit,
                                )
                            )
                        except Exception as exc:  # noqa: BLE001
                            rows.append(
                                self._build_failure_row(
                                    family, size, repetition, provider, circuit, str(exc)
                                )
                            )
        self._save_results(rows)
        self._generate_visualizations()
        return rows

    def _build_row(
        self,
        family: str,
        size: int,
        repetition: int,
        provider: str,
        logical_circuit: Any,
        result: dict[str, Any],
        reference_probs: dict[str, float] | None,
        observed_probs: dict[str, float] | None,
        *,
        baseline: bool,
        compiled_circuit: Any | None = None,
    ) -> dict[str, Any]:
        compiled_circuit = compiled_circuit or logical_circuit
        compiled_metrics = self._compiled_metrics(logical_circuit, provider)
        native_circuit = compiled_metrics.get("native_circuit") or compiled_circuit
        native_depth = compiled_metrics.get("native_compiled_depth")
        native_gate_count = compiled_metrics.get("native_compiled_gate_count")
        native_entangling_count = compiled_metrics.get("native_entangling_gate_count")
        target_metadata = compiled_metrics.get("target_metadata") or {}
        success_value = (
            success_probability(family, observed_probs, size)
            if not baseline and observed_probs is not None
            else None
        )
        total_variation = None
        fidelity = None
        if baseline:
            total_variation = 0.0
            fidelity = 1.0
        elif observed_probs is not None and reference_probs is not None:
            total_variation = total_variation_distance(reference_probs, observed_probs)
            fidelity = hellinger_fidelity(reference_probs, observed_probs)
        return {
            "experiment_id": self._make_id(family, size, provider, repetition),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "circuit_family": family,
            "qubit_count": size,
            "shots": self.config.shots,
            "repetition": repetition,
            "provider": provider,
            "backend_identifier": result.get("backend_name"),
            "architecture": self._backends[provider].architecture,
            "execution_type": result.get("execution_type"),
            "circuit_level": compiled_metrics.get("circuit_level"),
            "target_model": target_metadata.get("target_model"),
            "logical_depth": compiled_metrics.get(
                "logical_depth", self._logical_depth(logical_circuit)
            ),
            "logical_gate_count": compiled_metrics.get(
                "logical_gate_count", self._logical_gate_count(logical_circuit)
            ),
            "logical_two_qubit_gate_count": compiled_metrics.get(
                "logical_two_qubit_gate_count", self._logical_two_qubit_gate_count(logical_circuit)
            ),
            "logical_operation_counts": self._json_or_none(
                compiled_metrics.get("logical_operation_counts")
            ),
            "routed_depth": compiled_metrics.get("routed_depth"),
            "routed_gate_count": compiled_metrics.get("routed_gate_count"),
            "routed_two_qubit_gate_count": compiled_metrics.get("routed_two_qubit_gate_count"),
            "routed_operation_counts": self._json_or_none(
                compiled_metrics.get("routed_operation_counts")
            ),
            "routing_swap_count": compiled_metrics.get("routing_swap_count"),
            "native_compiled_depth": native_depth,
            "native_compiled_gate_count": native_gate_count,
            "native_one_qubit_gate_count": compiled_metrics.get("native_one_qubit_gate_count"),
            "native_entangling_gate_count": native_entangling_count,
            "native_measurement_count": compiled_metrics.get("native_measurement_count"),
            "native_operation_names": self._json_or_none(
                compiled_metrics.get("native_operation_names")
            ),
            "native_operation_counts": self._json_or_none(
                compiled_metrics.get("native_operation_counts")
            ),
            "unsupported_operation_count": compiled_metrics.get("unsupported_operation_count"),
            "estimated_native_execution_duration_ns": compiled_metrics.get(
                "estimated_native_execution_duration_ns"
            ),
            "duration_source": compiled_metrics.get("duration_source"),
            "duration_unit": compiled_metrics.get("duration_unit"),
            "estimated_success_probability_from_proxy_error_model": compiled_metrics.get(
                "estimated_success_probability_from_proxy_error_model"
            ),
            "success_probability_one_qubit_contribution": compiled_metrics.get(
                "success_probability_one_qubit_contribution"
            ),
            "success_probability_entangling_contribution": compiled_metrics.get(
                "success_probability_entangling_contribution"
            ),
            "success_probability_measurement_contribution": compiled_metrics.get(
                "success_probability_measurement_contribution"
            ),
            "error_model_source": compiled_metrics.get("error_model_source"),
            "equivalence_validation_method": compiled_metrics.get("equivalence_validation_method"),
            "equivalence_tolerance": compiled_metrics.get("equivalence_tolerance"),
            "equivalence_passed": compiled_metrics.get("equivalence_passed"),
            "architecture_connectivity": compiled_metrics.get("connectivity"),
            "target_metadata": self._json_or_none(target_metadata or None),
            "native_operation_sequence": self._operation_sequence(native_circuit),
            "routed_operation_sequence": compiled_metrics.get("routed_operation_sequence"),
            "compiler_config": self._json_or_none(target_metadata or None),
            "original_logical_depth": compiled_metrics.get(
                "logical_depth", self._logical_depth(logical_circuit)
            ),
            "original_gate_count": compiled_metrics.get(
                "logical_gate_count", self._logical_gate_count(logical_circuit)
            ),
            "original_two_qubit_gate_count": compiled_metrics.get(
                "logical_two_qubit_gate_count", self._logical_two_qubit_gate_count(logical_circuit)
            ),
            "compiled_depth": native_depth,
            "compiled_gate_count": native_gate_count,
            "compiled_two_qubit_gate_count": native_entangling_count,
            "compiled_one_qubit_gate_count": compiled_metrics.get("native_one_qubit_gate_count"),
            "compiled_swap_count": compiled_metrics.get("routing_swap_count"),
            "compiled_measurement_count": compiled_metrics.get("native_measurement_count"),
            "estimated_execution_duration_ns": compiled_metrics.get(
                "estimated_native_execution_duration_ns"
            ),
            "estimated_success_probability": compiled_metrics.get(
                "estimated_success_probability_from_proxy_error_model"
            ),
            "compiled_native_gate_count": native_gate_count,
            "compiled_native_two_qubit_gate_count": native_entangling_count,
            "compiled_operation_counts": self._json_or_none(
                compiled_metrics.get("native_operation_counts")
            ),
            "compiled_operation_sequence": self._operation_sequence(native_circuit),
            "measurement_counts": result.get("counts"),
            "probability_distribution": observed_probs,
            "reference_probability_distribution": reference_probs,
            "expected_state_probability": expected_state_probability(reference_probs, "0" * size)
            if not baseline and reference_probs is not None
            else None,
            "success_probability": success_value,
            "total_variation_distance": total_variation,
            "hellinger_fidelity": fidelity,
            "job_id": result.get("job_id"),
            "job_status": result.get("job_status"),
            "error_message": None,
            "device_metadata": result.get("metadata"),
            "is_baseline": baseline,
        }

    def _build_failure_row(
        self,
        family: str,
        size: int,
        repetition: int,
        provider: str,
        logical_circuit: Any,
        error_message: str,
    ) -> dict[str, Any]:
        return {
            "experiment_id": self._make_id(family, size, provider, repetition),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "circuit_family": family,
            "qubit_count": size,
            "shots": self.config.shots,
            "repetition": repetition,
            "provider": provider,
            "backend_identifier": None,
            "architecture": self._backends[provider].architecture,
            "execution_type": None,
            "original_logical_depth": self._logical_depth(logical_circuit),
            "original_gate_count": self._logical_gate_count(logical_circuit),
            "original_two_qubit_gate_count": self._logical_two_qubit_gate_count(logical_circuit),
            "circuit_level": None,
            "target_model": None,
            "logical_depth": self._logical_depth(logical_circuit),
            "logical_gate_count": self._logical_gate_count(logical_circuit),
            "logical_two_qubit_gate_count": self._logical_two_qubit_gate_count(logical_circuit),
            "logical_operation_counts": None,
            "routed_depth": None,
            "routed_gate_count": None,
            "routed_two_qubit_gate_count": None,
            "routed_operation_counts": None,
            "routing_swap_count": None,
            "native_compiled_depth": None,
            "native_compiled_gate_count": None,
            "native_one_qubit_gate_count": None,
            "native_entangling_gate_count": None,
            "native_measurement_count": None,
            "native_operation_names": None,
            "native_operation_counts": None,
            "unsupported_operation_count": None,
            "estimated_native_execution_duration_ns": None,
            "duration_source": None,
            "duration_unit": None,
            "estimated_success_probability_from_proxy_error_model": None,
            "success_probability_one_qubit_contribution": None,
            "success_probability_entangling_contribution": None,
            "success_probability_measurement_contribution": None,
            "error_model_source": None,
            "equivalence_validation_method": None,
            "equivalence_tolerance": None,
            "equivalence_passed": None,
            "target_metadata": None,
            "native_operation_sequence": None,
            "routed_operation_sequence": None,
            "compiled_depth": None,
            "compiled_gate_count": None,
            "compiled_two_qubit_gate_count": None,
            "compiled_one_qubit_gate_count": None,
            "compiled_swap_count": None,
            "compiled_measurement_count": None,
            "estimated_execution_duration_ns": None,
            "estimated_success_probability": None,
            "architecture_connectivity": None,
            "compiled_native_gate_count": None,
            "compiled_native_two_qubit_gate_count": None,
            "compiled_operation_counts": None,
            "compiler_config": None,
            "compiled_operation_sequence": None,
            "measurement_counts": None,
            "probability_distribution": None,
            "reference_probability_distribution": None,
            "expected_state_probability": None,
            "success_probability": None,
            "total_variation_distance": None,
            "hellinger_fidelity": None,
            "job_id": None,
            "job_status": "failed",
            "error_message": error_message,
            "device_metadata": None,
            "is_baseline": False,
        }

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

    def _probabilities_from_result(self, result: dict[str, Any]) -> dict[str, float] | None:
        counts = result.get("counts")
        if counts is None:
            return None
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
        self._latest_results_path = csv_path

    def _generate_visualizations(self) -> None:
        if not hasattr(self, "_latest_results_path"):
            return
        output_dir = self.base_dir / "results" / "figures"
        generate_visualizations(self._latest_results_path, output_dir)

    def _compiled_metrics(self, circuit: Any, provider: str) -> dict[str, Any]:
        if provider in self._architecture_models:
            model = self._architecture_models[provider]
            result = model.compile(circuit)
            summary = model.summarize(result)
            summary["native_circuit"] = result.native_compiled
            summary["routed_operation_sequence"] = self._operation_sequence(result.routed)
            return summary
        depth = self._logical_depth(circuit)
        gate_count = self._logical_gate_count(circuit)
        two_qubit_gate_count = self._logical_two_qubit_gate_count(circuit)
        return {
            "circuit_level": "logical",
            "logical_depth": depth,
            "logical_gate_count": gate_count,
            "logical_two_qubit_gate_count": two_qubit_gate_count,
            "logical_operation_counts": dict(sorted(circuit.count_ops().items())),
            "routed_depth": None,
            "routed_gate_count": None,
            "routed_two_qubit_gate_count": None,
            "routed_operation_counts": None,
            "routing_swap_count": None,
            "native_compiled_depth": None,
            "native_compiled_gate_count": None,
            "native_one_qubit_gate_count": None,
            "native_entangling_gate_count": None,
            "native_measurement_count": None,
            "native_operation_names": None,
            "native_operation_counts": None,
            "unsupported_operation_count": None,
            "estimated_native_execution_duration_ns": None,
            "duration_source": None,
            "duration_unit": None,
            "estimated_success_probability_from_proxy_error_model": None,
            "success_probability_one_qubit_contribution": None,
            "success_probability_entangling_contribution": None,
            "success_probability_measurement_contribution": None,
            "error_model_source": None,
            "equivalence_validation_method": None,
            "equivalence_tolerance": None,
            "equivalence_passed": None,
            "connectivity": None,
            "target_metadata": None,
            "native_circuit": circuit,
            "routed_operation_sequence": None,
        }

    def _logical_depth(self, circuit: Any) -> int:
        return circuit.depth()

    def _logical_gate_count(self, circuit: Any) -> int:
        return circuit.size()

    def _logical_two_qubit_gate_count(self, circuit: Any) -> int:
        return circuit.num_nonlocal_gates()

    def _make_id(self, family: str, size: int, provider: str, repetition: int) -> str:
        return f"{family}-{size}-{provider}-{repetition}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    def _json_or_none(self, value: Any) -> str | None:
        if value is None:
            return None
        return json.dumps(value, sort_keys=True)

    def _operation_sequence(self, circuit: Any) -> str:
        entries: list[str] = []
        for instruction in circuit.data:
            qubits = ",".join(str(circuit.qubits.index(qubit)) for qubit in instruction.qubits)
            entries.append(f"{instruction.operation.name}({qubits})")
        return " -> ".join(entries)
