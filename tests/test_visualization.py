from __future__ import annotations

from pathlib import Path

import pandas as pd

from quantum_compare.visualization import generate_visualizations


def test_generate_visualizations_creates_png_files(tmp_path: Path) -> None:
    results_path = tmp_path / "results.csv"
    base_row = {
        "is_baseline": False,
        "target_model": "test-target",
        "logical_depth": 3,
        "logical_gate_count": 4,
        "logical_two_qubit_gate_count": 1,
        "logical_operation_counts": "{}",
        "routed_depth": 3,
        "routed_gate_count": 4,
        "routed_two_qubit_gate_count": 1,
        "routed_operation_counts": "{}",
        "routing_swap_count": 0,
        "native_compiled_depth": 3,
        "native_compiled_gate_count": 4,
        "native_one_qubit_gate_count": 3,
        "native_entangling_gate_count": 1,
        "native_measurement_count": 2,
        "native_operation_counts": "{}",
        "native_operation_sequence": "rz(0) -> cx(0,1) -> measure(0) -> measure(1)",
        "routed_operation_sequence": "h(0) -> cx(0,1) -> measure(0) -> measure(1)",
        "unsupported_operation_count": 0,
        "estimated_native_execution_duration_ns": 500,
        "estimated_success_probability_from_proxy_error_model": 0.99,
        "success_probability_one_qubit_contribution": 0.99,
        "success_probability_entangling_contribution": 0.99,
        "success_probability_measurement_contribution": 0.99,
        "equivalence_passed": True,
        "equivalence_validation_method": "unitary",
        "equivalence_tolerance": 1e-8,
        "duration_source": "test",
        "error_model_source": "test",
        "target_metadata": "{}",
        "original_logical_depth": 3,
        "original_two_qubit_gate_count": 1,
        "compiled_gate_count": 4,
        "compiled_one_qubit_gate_count": 3,
        "compiled_two_qubit_gate_count": 1,
        "compiled_swap_count": 0,
        "compiled_measurement_count": 2,
        "estimated_execution_duration_ns": 500,
        "estimated_success_probability": 0.99,
        "compiler_config": "{}",
        "compiled_operation_counts": "{}",
        "compiled_operation_sequence": "h(0) -> cx(0,1) -> measure(0) -> measure(1)",
        "error_message": None,
    }
    pd.DataFrame(
        [
            {
                **base_row,
                "provider": "ideal",
                "circuit_family": "bell",
                "qubit_count": 2,
                "repetition": 1,
                "compiled_depth": 3,
                "hellinger_fidelity": 1.0,
                "total_variation_distance": 0.0,
                "is_baseline": True,
            },
            {
                **base_row,
                "provider": "ibm",
                "circuit_family": "bell",
                "qubit_count": 2,
                "repetition": 1,
                "compiled_depth": 3,
                "hellinger_fidelity": 0.8,
                "total_variation_distance": 0.3,
            },
            {
                **base_row,
                "provider": "quantinuum",
                "circuit_family": "ghz",
                "qubit_count": 3,
                "repetition": 1,
                "original_logical_depth": 4,
                "logical_depth": 4,
                "routed_depth": 4,
                "native_compiled_depth": 4,
                "compiled_depth": 4,
                "compiled_measurement_count": 3,
                "hellinger_fidelity": 0.75,
                "total_variation_distance": 0.35,
            },
        ]
    ).to_csv(results_path, index=False)

    output_dir = tmp_path / "figures"
    created_files = generate_visualizations(results_path, output_dir)

    assert len(created_files) >= 2
    assert all(path.exists() for path in created_files)
    suffixes = {path.suffix for path in created_files}
    assert ".png" in suffixes
    assert ".csv" in suffixes
    assert ".md" in suffixes
