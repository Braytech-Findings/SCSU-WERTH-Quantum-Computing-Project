#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / "results/hardware"
TABLES = ROOT / "results/tables"
REPORTS = ROOT / "results/reports"
STAMP = "20260723T163500Z"
TARGETS = ("H2-1LE", "H2-Emulator")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    raw = []
    aggregate = []
    for target in TARGETS:
        raw.extend(read_rows(HARDWARE / f"quantinuum_full_suite_{target}_{STAMP}_raw.csv"))
        aggregate.extend(
            read_rows(HARDWARE / f"quantinuum_full_suite_{target}_{STAMP}_aggregate.csv")
        )
    if len(raw) != 42 or sum(int(row["shots_retrieved"]) for row in raw) != 42000:
        raise ValueError("Full-suite row or shot total validation failed.")
    write_rows(TABLES / "quantinuum_full_suite_raw_results.csv", raw)
    write_rows(TABLES / "quantinuum_full_suite_aggregate.csv", aggregate)
    write_rows(TABLES / "quantinuum_full_suite_statistical_summary.csv", aggregate)
    manifest = {
        "evidence_type": "Quantinuum Nexus emulator validation",
        "source_stamp": STAMP,
        "targets": list(TARGETS),
        "target_classification": "emulator",
        "circuits_per_target": 7,
        "shots_per_circuit": 1000,
        "repetitions": 3,
        "requested_shots": 42000,
        "retrieved_shots": 42000,
        "raw_rows": 42,
        "aggregate_rows": 14,
        "reported_cost": None,
        "quota_message": "Nexus simulation CPU quota: No quota set for user.",
        "source_files": [
            f"results/hardware/quantinuum_full_suite_{target}_{STAMP}_raw.csv"
            for target in TARGETS
        ],
    }
    (TABLES / "quantinuum_full_suite_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    best = max(aggregate, key=lambda row: float(row["mean_distribution_fidelity"]))
    worst = min(aggregate, key=lambda row: float(row["mean_distribution_fidelity"]))
    report = f"""# Quantinuum Nexus Full-Suite Emulator Validation

## Run Summary

- Evidence: Quantinuum Nexus emulator validation, not physical QPU evidence.
- Targets: `H2-1LE` and `H2-Emulator`, live-catalog-confirmed local H2 emulators.
- Suite: Bell-2, GHZ-3, GHZ-5, GHZ-7, Grover-2, QFT-3, and QFT-5.
- Design: 1,000 shots per circuit, 3 independent repetitions, 42,000 requested and
  42,000 retrieved shots.
- Provider-reported execution cost: `null` for all six jobs.
- Quota: Nexus reported simulation CPU usage with `No quota set for user`; no monetary
  charge or paid-overage prompt appeared.

## Main Result

All 42 circuit results passed shot-total validation. Mean classical distribution fidelity
ranged from {float(worst['mean_distribution_fidelity']):.4f} ({worst['target']},
{worst['display_name']}) to {float(best['mean_distribution_fidelity']):.4f}
({best['target']}, {best['display_name']}). QFT-5 had the largest mean TVD on both targets:
0.0761 on H2-1LE and 0.0661 on H2-Emulator. Three repetitions show run-to-run spread but
are not enough to claim statistical significance.

Classical distribution fidelity compares measured output probabilities with the exact
noiseless logical-circuit distribution. QFT measurement fidelity does not validate the
complete quantum phase state.

## Claim Boundary

Quantinuum Nexus emulator execution validates the standardized workflow and output
distributions on emulator targets. It does not constitute physical Quantinuum trapped-ion
QPU evidence and does not complete a matched physical IBM-versus-Quantinuum benchmark.
"""
    (REPORTS / "quantinuum_full_suite_emulator_report.md").write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
