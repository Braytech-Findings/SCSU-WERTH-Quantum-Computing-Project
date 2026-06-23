from __future__ import annotations

from quantum_compare.cli import main
from quantum_compare.config import load_config
from quantum_compare.experiment import ExperimentRunner


def test_cli_check_returns_zero(monkeypatch) -> None:
    import sys

    monkeypatch.setattr(sys, "argv", ["quantum_compare.cli", "check"])
    assert main() == 0


def test_ideal_runner_smoke() -> None:
    config = load_config("config/experiments.yaml")
    runner = ExperimentRunner(config, base_dir=".")
    rows = runner.run_suite(backend_name="ideal")
    assert len(rows) >= 1


def test_runner_respects_repetitions_and_unique_ids() -> None:
    config = load_config("config/experiments.yaml")
    runner = ExperimentRunner(config, base_dir=".")
    rows = runner.run_suite(backend_name="ideal")
    experiment_ids = [row["experiment_id"] for row in rows]
    assert len(experiment_ids) == len(set(experiment_ids))
    rows_for_bell = [row for row in rows if row["circuit_family"] == "bell"]
    assert len(rows_for_bell) == config.repetitions * 1
