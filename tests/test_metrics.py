from __future__ import annotations

import math

import pytest

from quantum_compare.metrics import (
    count_to_probabilities,
    expected_state_probability,
    hellinger_fidelity,
    total_variation_distance,
)


def test_count_to_probabilities_normalizes_counts() -> None:
    counts = {"00": 2, "11": 2}
    probs = count_to_probabilities(counts, shots=4)
    assert probs["00"] == 0.5
    assert probs["11"] == 0.5


def test_expected_state_probability_handles_missing_bits() -> None:
    probs = {"00": 0.5, "11": 0.5}
    assert expected_state_probability(probs, "11") == 0.5
    assert expected_state_probability(probs, "10") == 0.0


def test_total_variation_distance_known_value() -> None:
    p = {"00": 0.5, "11": 0.5}
    q = {"00": 1.0, "01": 0.0, "10": 0.0, "11": 0.0}
    assert math.isclose(total_variation_distance(p, q), 0.5, abs_tol=1e-9)


def test_hellinger_fidelity_known_value() -> None:
    p = {"00": 0.5, "11": 0.5}
    q = {"00": 1.0, "01": 0.0, "10": 0.0, "11": 0.0}
    value = hellinger_fidelity(p, q)
    assert math.isclose(value, 0.5, abs_tol=1e-9)


def test_count_to_probabilities_rejects_empty_counts() -> None:
    with pytest.raises(ValueError):
        count_to_probabilities({}, shots=4)


def test_expected_state_probability_returns_zero_when_missing() -> None:
    probs = {"00": 0.5, "11": 0.5}
    assert expected_state_probability(probs, "01") == 0.0
