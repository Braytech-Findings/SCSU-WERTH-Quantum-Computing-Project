from __future__ import annotations

from collections.abc import Mapping
import math


def count_to_probabilities(counts: Mapping[str, int], shots: int | None = None) -> dict[str, float]:
    """Convert counts to probabilities, validating the shot count and normalizing safely."""
    if not counts:
        raise ValueError("Counts cannot be empty.")
    if shots is None:
        shots = sum(int(value) for value in counts.values())
    if shots <= 0:
        raise ValueError("Shots must be positive.")
    total = sum(int(value) for value in counts.values())
    if total <= 0:
        raise ValueError("Counts must sum to a positive total.")
    if total != shots:
        if total > shots:
            raise ValueError("Counts cannot exceed the provided shot count.")
    probabilities: dict[str, float] = {}
    for bitstring, count in counts.items():
        probabilities[str(bitstring)] = float(int(count)) / float(total)
    return probabilities


def expected_state_probability(probabilities: Mapping[str, float], state: str) -> float:
    """Return the probability assigned to the requested bitstring, or 0.0 if absent."""
    if not state:
        raise ValueError("State cannot be empty.")
    return float(probabilities.get(state, 0.0))


def total_variation_distance(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    """Compute the TVD between two probability distributions."""
    all_states = sorted(set(p) | set(q))
    total = 0.0
    for state in all_states:
        total += abs(float(p.get(state, 0.0)) - float(q.get(state, 0.0)))
    return total / 2.0


def hellinger_fidelity(p: Mapping[str, float], q: Mapping[str, float]) -> float:
    """Compute the Hellinger fidelity between two probability distributions."""
    all_states = sorted(set(p) | set(q))
    sum_term = 0.0
    for state in all_states:
        p_value = float(p.get(state, 0.0))
        q_value = float(q.get(state, 0.0))
        sum_term += math.sqrt(p_value * q_value)
    return sum_term**2


def logical_to_compiled_ratio(logical_value: float, compiled_value: float) -> float:
    """Return the ratio of logical to compiled value, or None when the denominator is zero."""
    if compiled_value == 0:
        return float("nan")
    return logical_value / compiled_value


def successful_shot_percentage(successful: int, total: int) -> float:
    """Return the percentage of successful shots; smaller values are worse."""
    if total <= 0:
        raise ValueError("Total shots must be positive.")
    return successful / total * 100.0
