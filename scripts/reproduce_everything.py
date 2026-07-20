#!/usr/bin/env python3
"""Reproduce the public architecture-comparison workflow from the repository root.

This runner is intentionally offline and credit-safe. It never submits IBM Quantum,
Quantinuum Nexus, or other provider jobs. It only installs the public package when
requested, validates the code, regenerates the controlled proxy experiment, rebuilds
figures/reports, and compares the newest output with the verified public baseline.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "data" / "processed" / "results_20260623T223649Z.csv"


@dataclass(frozen=True)
class Step:
    name: str
    command: tuple[str, ...]
    optional: bool = False


def run(step: Step, *, dry_run: bool) -> float:
    printable = " ".join(step.command)
    print(f"\n{'=' * 78}\n{step.name}\n$ {printable}\n{'=' * 78}")
    if dry_run:
        return 0.0
    started = time.perf_counter()
    subprocess.run(step.command, cwd=ROOT, check=True)
    elapsed = time.perf_counter() - started
    print(f"✓ {step.name} completed in {elapsed:.1f} seconds")
    return elapsed


def build_steps(args: argparse.Namespace) -> list[Step]:
    python = sys.executable
    steps: list[Step] = []

    if args.install:
        steps.extend(
            [
                Step("Upgrade pip", (python, "-m", "pip", "install", "--upgrade", "pip")),
                Step("Install the project", (python, "-m", "pip", "install", "-e", ".")),
            ]
        )

    steps.append(Step("Check the project environment", (python, "-m", "quantum_compare.cli", "check")))

    if not args.skip_tests:
        steps.extend(
            [
                Step("Run automated tests", (python, "-m", "pytest", "-q")),
                Step("Run Ruff linting", (python, "-m", "ruff", "check", ".")),
                Step("Run static type checks", (python, "-m", "mypy", "src", "tests")),
            ]
        )

    if not args.skip_experiment:
        steps.append(
            Step(
                "Regenerate the controlled offline experiment suite",
                (python, "-m", "quantum_compare.cli", "run", "--backend", "all", "--suite", "core"),
            )
        )

    if not args.skip_report:
        steps.append(
            Step(
                "Regenerate Python figures and reports",
                (python, "-m", "quantum_compare.cli", "report"),
            )
        )

    if not args.skip_baseline_check:
        steps.append(
            Step(
                "Compare the regenerated run with the verified baseline",
                (
                    python,
                    "scripts/compare_run_artifacts.py",
                    "--baseline",
                    str(args.baseline),
                ),
            )
        )

    if args.include_r:
        rscript = shutil.which("Rscript")
        if rscript is None and not args.dry_run:
            raise SystemExit(
                "Rscript was not found. Install R and the packages listed in README.md, "
                "or rerun without --include-r."
            )
        steps.append(
            Step(
                "Regenerate the expanded R visualization package",
                ((rscript or "Rscript"), "analysis/generate_final_figures_r.R"),
                optional=True,
            )
        )

    return steps


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Safely reproduce the public, offline quantum-architecture study."
    )
    command.add_argument(
        "--install",
        action="store_true",
        help="Install the package and public dependencies into the active Python environment.",
    )
    command.add_argument(
        "--include-r",
        action="store_true",
        help="Also regenerate the optional R visualization package.",
    )
    command.add_argument("--skip-tests", action="store_true")
    command.add_argument("--skip-experiment", action="store_true")
    command.add_argument("--skip-report", action="store_true")
    command.add_argument("--skip-baseline-check", action="store_true")
    command.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Verified processed CSV used for the reproducibility comparison.",
    )
    command.add_argument(
        "--dry-run",
        action="store_true",
        help="Print every command without executing it.",
    )
    return command


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if sys.version_info < (3, 11):
        raise SystemExit("Python 3.11 or newer is required.")
    args.baseline = args.baseline.resolve()
    if not args.baseline.exists() and not args.skip_baseline_check:
        raise SystemExit(f"Baseline file not found: {args.baseline}")

    print("Different Roads to the Same Circuit — public reproduction runner")
    print(f"Repository: {ROOT}")
    print("Safety boundary: offline only; no provider job submission or credit use.")

    steps = build_steps(args)
    total = 0.0
    completed: list[str] = []
    try:
        for step in steps:
            total += run(step, dry_run=args.dry_run)
            completed.append(step.name)
    except subprocess.CalledProcessError as error:
        print(f"\n✗ Reproduction stopped during: {step.name}", file=sys.stderr)
        print(f"  Exit code: {error.returncode}", file=sys.stderr)
        return error.returncode or 1

    print("\n" + "=" * 78)
    print("REPRODUCTION COMPLETE" if not args.dry_run else "DRY RUN COMPLETE")
    print("=" * 78)
    for name in completed:
        print(f"✓ {name}")
    if not args.dry_run:
        print(f"Total command time: {total:.1f} seconds")
    print("Generated outputs are stored under data/processed/ and results/.")
    print("Provider artifacts already committed under results/hardware/ are evidence records;")
    print("this script does not recreate paid or authenticated provider jobs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
