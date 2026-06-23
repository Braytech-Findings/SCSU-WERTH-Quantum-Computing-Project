from __future__ import annotations

from quantum_compare.models import ExperimentConfig


def test_config_defaults_are_sensible() -> None:
    config = ExperimentConfig()
    assert config.shots == 1000
    assert config.repetitions == 3
    assert config.allow_physical_hardware is False
