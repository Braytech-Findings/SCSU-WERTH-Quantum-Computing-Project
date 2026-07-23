# Quantinuum Nexus Emulator Validation Note

> [!IMPORTANT]
> The completed Quantinuum executions stored in this repository are **emulator results**, not physical Quantinuum QPU measurements. They do not complete a matched physical IBM-versus-Quantinuum hardware benchmark.

This file path is retained for compatibility with existing links. Its contents document the Quantinuum Nexus emulator and compile-only workflow.

## Evidence Classification

| Target | Saved evidence | Classification |
| --- | --- | --- |
| `H2-1E` | Compilation succeeded; execution returned a machine-access error | Compile-only workflow check |
| `H2-2E` | Compilation succeeded; execution returned a machine-access error | Compile-only workflow check |
| `H2-1LE` | Compilation and 3-circuit execution completed | Nexus emulator |
| `H2-Emulator` | Compilation and 3-circuit execution completed | Nexus emulator |

No physical Quantinuum trapped-ion QPU result is stored in this repository.

## Account and Target Information Recorded During Validation

- Nexus account: available
- Emulator-style targets observed: `H2-1E`, `H2-2E`, `H2-1LE`, and `H2-Emulator`
- Syntax-checker targets observed: `H2-1SC` and `H2-2SC`
- Reported HQC balance at the time: `20000.00`
- Reported syntax-checker balance: unlimited
- Reported quota reset window: 17 days

Target names alone are not proof of physical hardware. The Nexus dashboard, job metadata, and completed execution target must all identify a physical QPU before a result can be described as physical Quantinuum hardware evidence.

## Completed Emulator Results

### `H2-1LE`

- Date: July 14, 2026
- Suite: small
- Circuits: Bell-2, GHZ-3, and Grover-2
- Shots per circuit: 100
- Compile job: `compile-H2-1LE-20260714T173914Z`
- Execute job: `execute-H2-1LE-20260714T173914Z`
- Submission artifact: `results/hardware/quantinuum_submission_H2-1LE_20260714T173914Z.json`
- Counts artifact: `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z.json`
- Summary artifact: `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z_summary.csv`

| Circuit | Saved counts |
| --- | --- |
| Bell-2 | `00`: 43, `11`: 57 |
| GHZ-3 | `000`: 54, `111`: 46 |
| Grover-2 | `11`: 100 |

### `H2-Emulator`

- Date: July 14, 2026
- Suite: small
- Circuits: Bell-2, GHZ-3, and Grover-2
- Shots per circuit: 100
- Compile job: `compile-H2-Emulator-20260714T175518Z`
- Execute job: `execute-H2-Emulator-20260714T175518Z`
- Submission artifact: `results/hardware/quantinuum_submission_H2-Emulator_20260714T175518Z.json`
- Counts artifact: `results/hardware/quantinuum_job_H2-Emulator_20260714T175518Z.json`
- Summary artifact: `results/hardware/quantinuum_job_H2-Emulator_20260714T175518Z_summary.csv`

| Circuit | Saved counts |
| --- | --- |
| Bell-2 | `00`: 52, `11`: 48 |
| GHZ-3 | `000`: 52, `111`: 47, `101`: 1 |
| Grover-2 | `11`: 99, `10`: 1 |

These counts are real provider emulator outputs. They are not offline proxy estimates and are not physical trapped-ion QPU measurements.

## Compile-Only Checks

### `H2-1E`

- Compile job: `compile-H2-1E-20260714T173701Z`
- Circuits: 3
- Requested shots per circuit: 100
- Execution result: machine-access error
- Artifact: `results/hardware/quantinuum_submission_H2-1E_20260714T173701Z.json`

### `H2-2E`

- Compile job: `compile-H2-2E-20260714T174745Z`
- Circuits: 3
- Requested shots per circuit: 100
- Execution result: machine-access error
- Artifact: `results/hardware/quantinuum_submission_H2-2E_20260714T174745Z.json`

A successful compilation is useful workflow evidence, but it is not an execution result.

## Validation Figure

- Figure: `results/figures/quantinuum_validation_expected_state_probability.png`
- Source table: `results/tables/quantinuum_validation_plot_rows.csv`

The figure must be labeled **Quantinuum Nexus emulator validation**. It must not be labeled as physical Quantinuum hardware performance.

## Safe Workflow

Create a local plan without contacting Nexus:

```bash
python scripts/submit_quantinuum_validation.py \
  --target H2-Emulator \
  --suite small \
  --shots 100
```

Compile through Nexus without execution:

```bash
python scripts/submit_quantinuum_validation.py \
  --target H2-Emulator \
  --suite small \
  --shots 100 \
  --use-nexus \
  --wait
```

Execution requires explicit quota awareness:

```bash
python scripts/submit_quantinuum_validation.py \
  --target H2-Emulator \
  --suite small \
  --shots 100 \
  --use-nexus \
  --estimate-cost \
  --confirm-submit \
  --wait \
  --i-understand-this-may-use-hqcs-or-quota
```

Before any execution, confirm the exact target type and reject monetary charges or paid-overage requirements that were not explicitly approved.

## What Remains for a Full Hardware Benchmark

A full matched physical comparison still requires:

- a physical Quantinuum QPU target;
- the complete standardized circuit suite;
- matched circuit sizes, shots, repetitions, compiler objectives, and scoring rules;
- documented calibration windows;
- separate physical-hardware artifacts and analysis.

Until those requirements are met, the correct description is: **IBM physical hardware evidence plus Quantinuum Nexus emulator validation**.
