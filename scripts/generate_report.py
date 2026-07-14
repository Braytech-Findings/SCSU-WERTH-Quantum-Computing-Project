#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the full offline proxy workflow and regenerate report artifacts. "
            "This command does not submit provider hardware jobs."
        )
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parse_args(argv)
    from quantum_compare.config import load_config
    from quantum_compare.experiment import ExperimentRunner

    config = load_config(Path("config/experiments.yaml"))
    runner = ExperimentRunner(config, base_dir=Path.cwd())
    runner.run_suite(backend_name="all")
    print("Report generation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
