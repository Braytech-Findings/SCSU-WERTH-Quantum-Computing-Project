# Quantinuum Hardware Validation Note

This page records the safe Quantinuum Nexus workflow for this project. It is the
Quantinuum-side companion to `docs/IBM_HARDWARE_VALIDATION.md`.

## Access Reported By The Author

- Nexus account: available
- Emulator-style targets: `H2-1E`, `H2-2E`
- Syntax-checker/compiler-style targets: `H2-1SC`, `H2-2SC`
- Reported HQC balance for emulator-style targets: `20000.00`
- Reported syntax-checker balance: unlimited
- Quota reset window at the time reported: 17 days

The target names ending in `E` look like emulator targets. The target names ending in
`SC` look like syntax-checker targets. Treat both as official Quantinuum/Nexus validation
paths, but do not describe them as physical H2 hardware unless the Nexus dashboard shows
a non-emulator hardware target and an execution job is actually submitted to that target.

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
python scripts/submit_quantinuum_validation.py --target H2-1E --suite small --shots 100 --use-nexus --execute-nexus --wait --i-understand-this-may-use-hqcs-or-quota
```

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
