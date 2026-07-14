# Quantinuum Hardware Validation Note

This page records the safe Quantinuum Nexus workflow for this project. It is the
Quantinuum-side companion to `docs/IBM_HARDWARE_VALIDATION.md`.

## Access Reported By The Author

- Nexus account: available
- Emulator-style targets: `H2-1E`, `H2-2E`
- Syntax-checker/compiler-style targets: `H2-1SC`, `H2-2SC`
- Nexus-hosted local emulator target discovered during validation: `H2-1LE`
- Reported HQC balance for emulator-style targets: `20000.00`
- Reported syntax-checker balance: unlimited
- Quota reset window at the time reported: 17 days

The target names ending in `E` look like emulator targets. The target names ending in
`SC` look like syntax-checker targets. Treat both as official Quantinuum/Nexus validation
paths, but do not describe them as physical H2 hardware unless the Nexus dashboard shows
a non-emulator hardware target and an execution job is actually submitted to that target.
During validation, `H2-1E` and `H2-2E` accepted compilation but rejected execution for
this account with a machine-access error. The Nexus-hosted `H2-1LE` emulator target
accepted both compilation and execution.

## Safe First Run

Start with a local plan. This writes a public, sanitized plan and does not contact Nexus:

```bash
python scripts/submit_quantinuum_validation.py --target H2-1E --suite small --shots 100
```

Then install the Nexus tools in the environment where you will run the job:

```bash
python -m pip install pytket-qiskit pytket qnexus
```

Authenticate with Nexus using the official Quantinuum login flow. Do not put passwords,
tokens, or recovery codes into this repository.

Compile through Nexus without execution:

```bash
python scripts/submit_quantinuum_validation.py --target H2-1E --suite small --shots 100 --use-nexus --wait
```

If that succeeds, execute on the emulator-style target only after reviewing quota use:

```bash
python scripts/submit_quantinuum_validation.py --target H2-1LE --suite small --shots 100 --use-nexus --execute-nexus --wait --i-understand-this-may-use-hqcs-or-quota
```

## Completed Nexus Validation

The first Quantinuum Nexus validation was completed on July 14, 2026.

### H2-1E Compile-Only Check

- Target: `H2-1E`
- Suite: `small`
- Shots requested per circuit: `100`
- Circuits: `3`
- Compile job name: `compile-H2-1E-20260714T173701Z`
- Execution status: not used for the saved result; direct `H2-1E` execution returned a
  machine-access error for this account.
- Submission artifact:
  `results/hardware/quantinuum_submission_H2-1E_20260714T173701Z.json`

### H2-2E Compile-Only Check

- Target: `H2-2E`
- Suite: `small`
- Shots requested per circuit: `100`
- Circuits: `3`
- Compile job name: `compile-H2-2E-20260714T174745Z`
- Execution status: direct `H2-2E` execution returned a machine-access error for this
  account.
- Submission artifact:
  `results/hardware/quantinuum_submission_H2-2E_20260714T174745Z.json`

### H2-1LE Emulator Execution

- Target: `H2-1LE`
- Suite: `small`
- Shots per circuit: `100`
- Circuits: `3`
- Compile job name: `compile-H2-1LE-20260714T173914Z`
- Execute job name: `execute-H2-1LE-20260714T173914Z`
- Submission artifact:
  `results/hardware/quantinuum_submission_H2-1LE_20260714T173914Z.json`
- Counts artifact:
  `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z.json`
- Summary artifact:
  `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z_summary.csv`

Compact result summary:

| Result index | Circuit | Bit width | Shots | Dominant/expected result summary |
| ---: | --- | ---: | ---: | --- |
| 0 | Bell state | 2 | 100 | `00`: 43, `11`: 57 |
| 1 | GHZ-3 | 3 | 100 | `000`: 54, `111`: 46 |
| 2 | Grover-2 | 2 | 100 | `11`: 100 |

These are real Quantinuum Nexus emulator results, not offline proxy estimates and not
physical H2 hardware measurements.

## What The Script Saves

The script writes sanitized files under `results/hardware/`.

| File | Meaning |
| --- | --- |
| `results/hardware/quantinuum_validation_plan.json` | Local plan showing target, circuit names, qubits, shots, and safety notes. |
| `results/hardware/quantinuum_submission_<target>_<timestamp>.json` | Nexus compile/execute job names and safe metadata. It intentionally excludes secrets. |
| `results/hardware/quantinuum_job_<target>_<timestamp>.json` | Downloaded counts and distributions when `--execute-nexus --wait` finishes. |
| `results/hardware/quantinuum_job_<target>_<timestamp>_summary.csv` | Compact result summary by result index, bit-width, shots, and all-zero/all-one probability. |

## What To Save Before Drawing Conclusions

Save these fields before describing a Quantinuum result:

- exact Nexus target name
- whether the target is syntax checker, emulator, or physical hardware
- project name
- compile job name
- execute job name, if execution was requested
- shot count
- circuit family and qubit count
- measured counts or probability distribution
- any provider-reported cost estimate
- any unavailable value as `null`, not zero

## Scope

Quantinuum emulator or syntax-checker results are real provider workflow outputs, but
they are not the same as physical H2 hardware measurements. Keep them separate from the
offline proxy-model tables and label them by target name.

Official Quantinuum docs used for this workflow:

- `https://docs.quantinuum.com/nexus/trainings/getting_started.html`
- `https://docs.quantinuum.com/systems/trainings/alternate_pathways/qiskit_h2.html`
