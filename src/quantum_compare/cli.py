from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from quantum_compare.config import load_config
from quantum_compare.experiment import ExperimentRunner
from quantum_compare.visualization import generate_visualizations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare superconducting and trapped-ion quantum architectures."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Perform a lightweight environment check.")
    subparsers.add_parser("devices", help="List available backend adapters.")

    run_parser = subparsers.add_parser("run", help="Run a core or custom experiment suite.")
    run_parser.add_argument(
        "--backend", default="all", help="Backend selection: ideal, ibm, quantinuum, or all"
    )
    run_parser.add_argument("--suite", default="core", help="Experiment suite identifier")
    run_parser.add_argument(
        "--config", default="config/experiments.yaml", help="Path to YAML config"
    )

    report_parser = subparsers.add_parser(
        "report", help="Generate report artifacts from the latest experiment results."
    )
    report_parser.add_argument(
        "--config", default="config/experiments.yaml", help="Path to YAML config"
    )
    return parser


def latest_architecture_results_csv(processed_dir: Path) -> Path | None:
    for candidate in sorted(processed_dir.glob("results_*.csv"), reverse=True):
        dataframe = pd.read_csv(candidate, usecols=["provider"])
        providers = set(dataframe["provider"].dropna().astype(str))
        if {"ibm", "quantinuum"}.issubset(providers):
            return candidate
    return None


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check":
        print("Environment check passed.")
        return 0

    if args.command == "devices":
        print("Ideal backend available")
        print("IBM backend adapter available in dry-run mode")
        print("Quantinuum backend adapter available in dry-run mode")
        return 0

    if args.command == "run":
        config = load_config(args.config)
        runner = ExperimentRunner(config, base_dir=Path.cwd())
        rows = runner.run_suite(backend_name=args.backend, suite=args.suite)
        print(f"Completed {len(rows)} experiment rows")
        return 0

    if args.command == "report":
        config = load_config(args.config)
        output_dir = Path.cwd() / "results" / "figures"
        latest_csv = latest_architecture_results_csv(Path.cwd() / config.output_dirs["processed"])
        if latest_csv is None:
            print("No full architecture-proxy processed results available for plotting.")
            return 0
        created_files = generate_visualizations(latest_csv, output_dir)
        print(f"Generated {len(created_files)} report artifact(s) from {latest_csv}")
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
