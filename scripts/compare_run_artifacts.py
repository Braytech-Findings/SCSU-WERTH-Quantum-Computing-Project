#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.testing import assert_frame_equal


DEFAULT_BASELINE = Path("data/processed/results_20260623T223649Z.csv")
KEY_COLUMNS = ["circuit_family", "qubit_count", "repetition", "provider"]
RESULT_COLUMNS = [
    *KEY_COLUMNS,
    "target_model",
    "logical_depth",
    "routed_depth",
    "native_compiled_depth",
    "routing_swap_count",
    "native_entangling_gate_count",
    "estimated_native_execution_duration_ns",
    "estimated_success_probability_from_proxy_error_model",
    "unsupported_operation_count",
    "equivalence_passed",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare regenerated qBraid artifacts with the verified baseline run."
    )
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--candidate", type=Path, default=None)
    parser.add_argument("--tables-dir", type=Path, default=Path("results/tables"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/reports/qbraid_artifact_comparison.json"),
    )
    return parser.parse_args()


def latest_results_csv() -> Path:
    candidates = sorted(Path("data/processed").glob("results_*.csv"))
    if not candidates:
        raise FileNotFoundError("No processed results CSV files found.")
    for candidate in reversed(candidates):
        dataframe = pd.read_csv(candidate, usecols=["provider"])
        providers = set(dataframe["provider"].dropna().astype(str))
        if {"ibm", "quantinuum"}.issubset(providers):
            return candidate
    raise FileNotFoundError(
        "No full architecture-proxy results CSV found with both IBM and Quantinuum proxy rows."
    )


def normalized_results(path: Path) -> pd.DataFrame:
    dataframe = pd.read_csv(path)
    filtered = dataframe[dataframe["provider"].isin(["ibm", "quantinuum"])].copy()
    filtered = filtered[RESULT_COLUMNS]
    filtered = filtered.sort_values(KEY_COLUMNS).reset_index(drop=True)
    return filtered


def compare_frames(baseline: pd.DataFrame, candidate: pd.DataFrame) -> tuple[bool, str | None]:
    try:
        assert_frame_equal(baseline, candidate, check_dtype=False, atol=1e-12, rtol=1e-12)
    except AssertionError as exc:
        return False, str(exc)
    return True, None


def table_checks(tables_dir: Path) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    validation_path = tables_dir / "architecture_validation_table.csv"
    grouped_path = tables_dir / "qubit_grouped_statistics.csv"
    matched_path = tables_dir / "matched_size_architecture_comparison.csv"
    sensitivity_path = tables_dir / "model_sensitivity_analysis.csv"
    ordering_path = tables_dir / "model_sensitivity_ordering.csv"
    assumptions_path = tables_dir / "proxy_assumptions_table.csv"

    required = [
        validation_path,
        grouped_path,
        matched_path,
        sensitivity_path,
        ordering_path,
        assumptions_path,
    ]
    checks["required_tables_exist"] = all(path.exists() for path in required)
    checks["missing_tables"] = [str(path) for path in required if not path.exists()]
    if checks["missing_tables"]:
        return checks

    validation = pd.read_csv(validation_path)
    grouped = pd.read_csv(grouped_path)
    matched = pd.read_csv(matched_path)
    sensitivity = pd.read_csv(sensitivity_path)
    ordering = pd.read_csv(ordering_path)
    assumptions = pd.read_csv(assumptions_path)

    checks["successful_architecture_rows"] = int(len(validation))
    checks["unsupported_operation_sum"] = int(
        validation["unsupported_operation_count"].fillna(0).sum()
    )
    checks["equivalence_failures"] = int((validation["equivalence_passed"] != True).sum())  # noqa: E712
    checks["grouped_statistics_rows"] = int(len(grouped))
    checks["matched_comparison_rows"] = int(len(matched))
    checks["sensitivity_rows"] = int(len(sensitivity))
    checks["duration_ordering_stable"] = bool(ordering["duration_ordering_stable"].all())
    checks["success_ordering_stable"] = bool(ordering["success_ordering_stable"].all())
    checks["assumption_rows"] = int(len(assumptions))
    checks["assumptions_not_live_calibration"] = bool(
        assumptions["not_live_device_calibration"].all()
    )
    checks["important_numeric_values_match_expected_shape"] = all(
        [
            checks["successful_architecture_rows"] == 42,
            checks["unsupported_operation_sum"] == 0,
            checks["equivalence_failures"] == 0,
            checks["matched_comparison_rows"] == 168,
            checks["sensitivity_rows"] == 126,
            checks["assumption_rows"] == 2,
        ]
    )
    return checks


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd()))
    except ValueError:
        return str(resolved)


def main() -> int:
    args = parse_args()
    baseline_path = args.baseline
    candidate_path = args.candidate or latest_results_csv()
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline CSV not found: {baseline_path}")
    if not candidate_path.exists():
        raise FileNotFoundError(f"Candidate CSV not found: {candidate_path}")

    baseline = normalized_results(baseline_path)
    candidate = normalized_results(candidate_path)
    results_match, mismatch = compare_frames(baseline, candidate)
    checks = table_checks(args.tables_dir)
    passed = bool(results_match and checks.get("important_numeric_values_match_expected_shape"))

    report = {
        "baseline_csv": display_path(baseline_path),
        "candidate_csv": display_path(candidate_path),
        "results_match": results_match,
        "mismatch": mismatch,
        "table_checks": checks,
        "passed": passed,
        "note": (
            "Comparison ignores experiment_id and timestamp columns and checks deterministic "
            "scientific fields for IBM and Quantinuum proxy-model rows."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
