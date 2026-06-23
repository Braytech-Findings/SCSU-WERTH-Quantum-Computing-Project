from __future__ import annotations

import pytest
from qiskit_aer import AerSimulator

from quantum_compare.circuits import (
    build_bell_state,
    build_ghz_state,
    build_qft,
    build_grover_search,
)


def test_bell_state_has_expected_distribution() -> None:
    circuit = build_bell_state()
    assert circuit.num_qubits == 2
    assert circuit.num_clbits == 2


def test_ghz_state_rejects_invalid_size() -> None:
    with pytest.raises(ValueError):
        build_ghz_state(2)


def test_qft_rejects_invalid_size() -> None:
    with pytest.raises(ValueError):
        build_qft(2)


def test_grover_search_rejects_invalid_size() -> None:
    with pytest.raises(ValueError):
        build_grover_search(1)


def test_grover_search_amplifies_marked_state() -> None:
    circuit = build_grover_search(2)
    simulator = AerSimulator(method="automatic")
    result = simulator.run(circuit, shots=1000, seed_simulator=1234).result()
    counts = result.get_counts(circuit)
    assert counts.get("11", 0) > counts.get("00", 0)
    assert counts.get("11", 0) > counts.get("01", 0)
    assert counts.get("11", 0) > counts.get("10", 0)


def test_qft_measurement_order_is_preserved() -> None:
    circuit = build_qft(3)
    assert circuit.num_qubits == 3
    assert circuit.num_clbits == 3
    assert circuit.cregs[0].size == 3
