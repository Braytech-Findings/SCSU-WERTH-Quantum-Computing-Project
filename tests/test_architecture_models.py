from __future__ import annotations

from quantum_compare.architecture import IBMArchitectureModel, QuantinuumArchitectureModel
from quantum_compare.circuits import build_ghz_state, build_grover_search


def test_ibm_final_circuits_contain_only_target_operations() -> None:
    model = IBMArchitectureModel()
    result = model.compile(build_ghz_state(5))
    summary = model.summarize(result)
    assert summary["unsupported_operation_count"] == 0
    assert set(summary["native_operation_names"]).issubset(model.allowed_operations)
    assert "swap" not in summary["native_operation_names"]


def test_quantinuum_final_circuits_contain_only_selected_target_operations() -> None:
    model = QuantinuumArchitectureModel()
    result = model.compile(build_grover_search(2))
    summary = model.summarize(result)
    assert summary["unsupported_operation_count"] == 0
    assert set(summary["native_operation_names"]).issubset(model.allowed_operations)
    assert not {"h", "x", "cx", "cz", "swap"} & set(summary["native_operation_names"])


def test_grover_is_genuinely_decomposed_for_both_targets() -> None:
    circuit = build_grover_search(2)
    ibm_summary = IBMArchitectureModel().summarize(IBMArchitectureModel().compile(circuit))
    quantinuum_summary = QuantinuumArchitectureModel().summarize(
        QuantinuumArchitectureModel().compile(circuit)
    )
    assert "cz" not in ibm_summary["native_operation_names"]
    assert "h" not in quantinuum_summary["native_operation_names"]
    assert "x" not in quantinuum_summary["native_operation_names"]
    assert ibm_summary["native_entangling_gate_count"] > 0
    assert quantinuum_summary["native_entangling_gate_count"] > 0


def test_swap_routing_is_separate_from_native_entangling_count() -> None:
    model = IBMArchitectureModel()
    summary = model.summarize(model.compile(build_ghz_state(5)))
    assert summary["routing_swap_count"] > 0
    assert summary["native_entangling_gate_count"] > summary["routing_swap_count"]
    assert summary["native_operation_counts"].get("swap") is None


def test_logical_routed_and_native_depths_are_separate_fields() -> None:
    model = IBMArchitectureModel()
    summary = model.summarize(model.compile(build_ghz_state(5)))
    assert "logical_depth" in summary
    assert "routed_depth" in summary
    assert "native_compiled_depth" in summary
    assert summary["native_compiled_depth"] != summary["logical_depth"]


def test_native_depth_cannot_silently_substitute_logical_depth() -> None:
    model = QuantinuumArchitectureModel()
    summary = model.summarize(model.compile(build_grover_search(2)))
    assert summary["logical_depth"] == 8
    assert summary["native_compiled_depth"] == 10


def test_logical_native_equivalence_is_validated() -> None:
    for model in (IBMArchitectureModel(), QuantinuumArchitectureModel()):
        summary = model.summarize(model.compile(build_grover_search(2)))
        assert summary["equivalence_passed"] is True
        assert summary["equivalence_tolerance"] == 1e-8
