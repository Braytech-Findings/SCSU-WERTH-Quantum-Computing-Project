# Running the Project

> [!IMPORTANT]
> The saved IBM provider results are physical `ibm_kingston` QPU measurements. The saved Quantinuum provider results are emulator outputs. Selecting a Nexus target in a command does not by itself prove that the target is physical hardware.

Run commands from the repository root. Offline commands are the default and do not use provider credentials.

## Environment Matrix

| Environment | Purpose | Cost risk | Credentials | Verified command | Output or success check |
| --- | --- | ---: | --- | --- | --- |
| Local proxy models | Compare compilation overhead | None | No | `python -m quantum_compare.cli run --backend all --suite core` | Timestamped files in `data/processed/` |
| Local report | Build tables and figures | None | No | `python -m quantum_compare.cli report` | Files in `results/tables/`, `results/figures/`, and `results/reports/` |
| qBraid | Independent rerun environment | Usually none | qBraid account | Run `notebooks/qbraid_validation.ipynb` | See `QBRAID_VALIDATION.md` |
| IBM hardware preview | Inspect a physical-QPU plan | None | No | `python scripts/submit_ibm_extended_validation.py --dry-run` | Writes a plan; no job |
| IBM physical hardware | Execute on an IBM QPU | Quota or credits may apply | IBM token and instance | Add the script's explicit submit and credit-awareness flags after reviewing the plan | Backend, shots, job ID, and sanitized submission record |
| Quantinuum local preview | Inspect circuits, target, project, and shots | None | No | `python scripts/submit_quantinuum_validation.py --target H2-Emulator --suite small --shots 100` | Writes a plan; no Nexus job |
| Nexus compile-only check | Validate provider compilation | Provider policy applies | Nexus access | Add `--use-nexus --wait` without execution flags | Compiled references and sanitized submission metadata |
| Nexus emulator execution | Reproduce the current Quantinuum evidence type | HQCs or quota may apply | Authorized Nexus project | Use the explicit estimate, submit, quota-awareness, and wait flags only after confirming the target is an emulator | Sanitized emulator result JSON and CSV |
| Future physical Quantinuum QPU | Complete the matched hardware comparison | Provider cost or quota may apply | Authorized physical-QPU access | Use the same suite, shots, repetitions, compiler objective, and scoring rules as the matched IBM run | Separate physical-hardware artifacts clearly labeled as QPU results |
| InQuanto | Not part of this repository | Not applicable | Not applicable | No command | See the separate DHFR repository |

## Complete Offline Workflow

```bash
python scripts/validate_repository.py
python -m quantum_compare.cli run --backend all --suite core
python -m quantum_compare.cli report
python scripts/compare_run_artifacts.py \
  --baseline data/processed/results_20260623T223649Z.csv
pytest
```

## Quantinuum Safety Rules

- Confirm the exact Nexus target type before execution.
- Treat `H2-1LE` and `H2-Emulator` results as emulator evidence.
- Do not call emulator output physical trapped-ion hardware data.
- Do not accept a monetary charge or paid overage without explicit approval.
- Save target name, project, compile job, execute job, shots, counts, target type, and any reported cost.
- Store physical QPU results separately from emulator and proxy results.

Hardware measurements can vary with calibration, mapping, scheduling, and shot noise. Exact count equality is not expected across repeated provider runs.
