# qBraid Lab Validation

This document explains how to validate the completed repository in qBraid Lab.

Development was performed in VS Code. qBraid Lab is used here for reproducibility and
platform validation: the notebook verifies imports, dependency versions, tests, the full
offline proxy-model experiment pipeline, report generation, and artifact comparison
against the verified run `20260623T223649Z`.

This validation does not require paid QPU access or private hardware credentials.

An author-provided IBM Quantum job reference is documented in
`docs/IBM_HARDWARE_VALIDATION.md`. That job reference is separate from the qBraid
offline validation workflow and is not included in the proxy-model result tables. Its
sanitized counts are stored under `results/hardware/`.

## Study Scope

The repository is an offline architecture-proxy compilation and modeling study. The IBM
and Quantinuum rows are proxy-model compilation results, not measured hardware
performance. Optional simulator output, if run in qBraid Lab, is stored separately and
must not be described as IBM or Quantinuum hardware measurement.

## qBraid Environment

Use a Python 3.11+ qBraid Lab environment with notebook support. The validation notebook
records the exact environment at runtime, including:

- Python version
- executable path
- platform string
- installed versions of `qiskit`, `qiskit-aer`, `numpy`, `pandas`, `matplotlib`,
  `pytest`, `ruff`, `mypy`, and `pyyaml`

The runtime snapshot is written by the notebook to:

`results/reports/qbraid_environment.json`

Because qBraid environments are selected at notebook launch time, this repository does
not hardcode a qBraid image name. Treat `qbraid_environment.json` as the authoritative
record of the exact qBraid environment used for validation.

## Upload or Clone Into qBraid Lab

Option A: upload the repository folder into qBraid Lab.

Option B: clone the repository in a qBraid terminal:

```bash
git clone <your-repository-url>
cd quantum-architecture-comparison
```

If dependencies are not already available in the selected qBraid environment, install
the local project dependencies:

```bash
python -m pip install -e .
```

This command installs the package from the local repository. It does not request QPU
access or submit hardware jobs.

## Run the Notebook

Open and run:

`notebooks/qbraid_validation.ipynb`

Run the cells from top to bottom.

The notebook executes these validation steps:

```bash
python -m pip install -e .
python -m quantum_compare.cli check
pytest
python scripts/generate_report.py
python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv
```

The notebook also imports the project, constructs and displays a Bell circuit and a
3-qubit GHZ circuit, and optionally runs a Bell circuit on a local qBraid-compatible
Qiskit Aer simulator when available.

## Expected Test Result

The current local validation result is:

```text
27 passed
```

qBraid should report the same tests passing if the environment has compatible package
versions.

During repository preparation, the comparison script was run locally against the
verified baseline run without rerunning the experiment, and it reported:

```text
results_match: true
passed: true
successful_architecture_rows: 42
unsupported_operation_sum: 0
equivalence_failures: 0
matched_comparison_rows: 168
sensitivity_rows: 126
```

## Artifact Comparison

After the full offline experiment pipeline is rerun in qBraid, the comparison script
checks the regenerated output against the verified baseline:

`data/processed/results_20260623T223649Z.csv`

The comparison ignores run-specific `experiment_id` and timestamp values. It compares
the deterministic scientific fields for IBM and Quantinuum proxy-model rows:

- logical depth
- routed depth
- native-compiled depth
- routing SWAP count
- native entangling-gate count
- estimated native execution duration from the proxy timing model
- estimated success probability from the proxy error model
- unsupported operation count
- logical-to-native equivalence status

The comparison output is written to:

`results/reports/qbraid_artifact_comparison.json`

Expected important checks:

- successful architecture rows: `42`
- unsupported operation sum: `0`
- equivalence failures: `0`
- matched comparison rows: `168`
- sensitivity rows: `126`
- assumptions table rows: `2`

## Optional Simulator Execution

The notebook may run a small Bell circuit on a local simulator if Qiskit Aer is
available. This is optional and is only a qBraid platform sanity check.

Simulator results are stored separately at:

`results/qbraid_validation/simulator_bell_counts.json`

These counts are not IBM or Quantinuum hardware measurements and are not part of the
proxy-model experiment.

Simulator execution was not performed as part of this documentation edit. The notebook
will record whether it ran or skipped the simulator check in
`results/qbraid_validation/simulator_bell_counts.json`.

## Final Artifacts to Inspect

Main report:

`results/reports/summary_report.md`

Verified written summary:

`results/reports/final_results_written_summary.md`

qBraid comparison report:

`results/reports/qbraid_artifact_comparison.json`

Final figures:

- `results/figures/key_metric_summary.png`
- `results/figures/logical_depth_baseline.png`
- `results/figures/routed_depth_scaling_by_family.png`
- `results/figures/native_depth_scaling_by_family.png`
- `results/figures/routing_swap_count_scaling_by_family.png`
- `results/figures/native_entangling_gate_count_scaling_by_family.png`
- `results/figures/estimated_native_duration_scaling_by_family.png`
- `results/figures/estimated_proxy_success_scaling_by_family.png`

## Remaining Limitations

- The IBM and Quantinuum targets are offline proxy models, not live calibrated hardware
  snapshots.
- Duration and success-probability values come from proxy assumptions, not provider
  calibration data.
- Quantinuum compilation uses a Qiskit `rzz` proxy rather than pytket Quantinuum passes.
- Grover currently has only one supported qubit count, so broad architecture conclusions
  for Grover remain inconclusive.
- Repetitions are deterministic unless future work varies compiler seeds.
- qBraid simulator execution, when performed, is a separate simulator sanity check and
  is not a hardware benchmark.
