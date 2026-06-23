from __future__ import annotations

import pytest

from quantum_compare.circuits import build_bell_state, build_ghz_state, build_qft, build_grover_search


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
