# Running the Project

## Full Quantinuum Emulator Suite

```bash
python scripts/submit_quantinuum_validation.py --dry-run --target H2-1LE \
  --suite matched --shots 1000 --repetitions 3
```

The matched suite has exactly seven circuits and writes timestamped immutable manifests.
Execution is restricted to live-catalog-confirmed `H2-1LE` and `H2-Emulator` emulator
targets and requires explicit quota acknowledgement. QFT uses exact-distribution scoring,
not all-zero/all-one support.

Run commands from the repository root. Offline commands are the default and do not use provider credentials.

## Environment matrix

| Environment | Purpose | Cost risk | Credentials | Verified command | Output / success check |
|---|---|---:|---|---|---|
| Local proxy models | Compare compilation overhead | None | No | `python -m quantum_compare.cli run --backend all --suite core` | Timestamped files in `data/processed/` |
| Local report | Build tables and figures | None | No | `python -m quantum_compare.cli report` | Files in `results/tables/`, `results/figures/`, and `results/reports/` |
| qBraid | Independent rerun environment | Usually none | qBraid account | Open `notebooks/qbraid_validation.ipynb` and run its cells | See [QBRAID_VALIDATION.md](QBRAID_VALIDATION.md); no CLI submission path is claimed |
| IBM hardware preview | Inspect a real-QPU plan | None | No | `python scripts/submit_ibm_extended_validation.py --dry-run` | Writes `results/hardware/ibm_extended_validation_plan.json`; no job |
| IBM hardware | Real superconducting QPU | **Quota/credits may apply** | IBM token and instance | Same command with `--confirm-submit --i-understand-this-may-use-credits` | Prints backend, shots, job ID, and sanitized submission record |
| Quantinuum local preview | Inspect circuits, target, project, and shots | None | No | `python scripts/submit_quantinuum_validation.py --dry-run` | Writes a plan; no Nexus object or job |
| Nexus compile/syntax check | Provider validation | Provider policy applies | Nexus access | `python scripts/submit_quantinuum_validation.py --target H2-1SC --use-nexus --wait` | Compiled circuit references; no execution unless confirmed |
| Nexus emulator/hardware | Execute on selected H-Series target | **HQCs or quota may apply** | Authorized Nexus project | Add `--estimate-cost --confirm-submit --i-understand-this-may-use-hqcs-or-quota --wait` only after reviewing the dry run | Sanitized submission/result JSON in `results/hardware/` |
| InQuanto | Not part of this project | — | — | No command | See the separate DHFR repository |

**Credit warning:** provider submission is never part of installation, tests, reports, figure generation, or validation. `--confirm-submit` is deliberately insufficient by itself: each provider also requires its explicit credit-awareness flag. Cost estimates depend on provider support and are not invented when unavailable.

## Complete safe workflow

```bash
python scripts/validate_repository.py
python -m quantum_compare.cli run --backend all --suite core
python -m quantum_compare.cli report
python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv
```

The last command compares a new offline run to the committed verified baseline. Hardware measurements can vary with calibration, queue time, mapping, and shot noise; do not expect exact count equality.
