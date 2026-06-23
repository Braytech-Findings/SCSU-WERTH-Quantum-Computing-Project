#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from quantum_compare.config import load_config
from quantum_compare.experiment import ExperimentRunner


if __name__ == "__main__":
    config = load_config(Path("config/experiments.yaml"))
    runner = ExperimentRunner(config, base_dir=Path.cwd())
    rows = runner.run_suite(backend_name="ideal")
    print(f"Completed {len(rows)} rows")
