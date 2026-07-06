# Quantum Architecture Comparison

## Overview

In one sentence: this project asks, "If we give two different quantum-computer styles
the same small circuits, how much does each style have to rewrite those circuits before
it can run them?"

This repository is a sanitized independent research implementation comparing how the
same logical quantum circuits compile under two architecture-aware offline proxy models:
an IBM-style superconducting proxy and a Quantinuum-style trapped-ion proxy.

The study is intentionally cautious. It is not a direct benchmark of physical IBM or
Quantinuum hardware, and it does not claim measured device fidelity, measured execution
time, queue behavior, or live calibration performance. Estimated native execution
duration and estimated success probability come from documented proxy assumptions.

## Start Here

- The starting circuits are the same for every comparison.
- The IBM-style proxy acts like qubits are sitting in a line, so some qubits must be
  moved next to each other before they can interact.
- The Quantinuum-style proxy acts like any qubit can interact with any other qubit.
- The code measures how much extra work each style needs: extra moves, extra gates,
  deeper circuits, estimated time, and estimated success.
- The saved results are offline model results. They are useful for learning and
  comparison, but they are not claims about live IBM or Quantinuum hardware.

## Research Question

How do the same logical circuits change after topology routing and native-basis
decomposition for superconducting-proxy and trapped-ion-proxy architectures?

## Architectures Compared

- IBM proxy: a line-coupled GenericBackendV2-style superconducting proxy using `rz`,
  `sx`, `x`, and `cx` as native unitary operations.
- Quantinuum proxy: an all-to-all H-series-style trapped-ion proxy using `rz`, `rx`,
  and Qiskit `rzz` as an offline ZZ-type entangling proxy.

Both pipelines start from the same logical Qiskit circuits. The comparison separates
logical circuits, routed circuits, and native-compiled circuits.

## Circuit Families

- Bell state, 2 qubits.
- GHZ states, 3, 5, and 7 qubits.
- QFT circuits, 3 and 5 qubits.
- Grover search, currently a 2-qubit circuit.

## Metrics

The main metrics are:

- logical depth;
- routed depth;
- native-compiled depth;
- routing SWAP count;
- native entangling-gate count;
- estimated native execution duration;
- estimated success probability;
- unsupported native-operation count;
- logical-to-native equivalence status.

Measurement bitstring endianness follows Qiskit conventions. Measurement and unavailable
values are stored as `null` where a value is not available rather than as a fabricated
zero.

## Installation

Use Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The default workflow does not require API keys and does not submit hardware jobs.

## Running The Project

Check that the package imports and the CLI is available:

```bash
python -m quantum_compare.cli check
```

Run the full offline proxy-model experiment suite:

```bash
python -m quantum_compare.cli run --backend all --suite core
```

Generate tables, figures, and the summary report from the newest processed CSV:

```bash
python -m quantum_compare.cli report
```

Run the script form of the same full workflow:

```bash
python scripts/generate_report.py
```

Compare a regenerated run with the verified baseline:

```bash
python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv
```

Run tests:

```bash
pytest
```

Optional static checks:

```bash
ruff check .
mypy src tests
```

## Preparing A Real Hardware Test

The default project workflow is offline and credit-safe. It does not submit IBM,
Quantinuum, or other provider jobs. If you have provider access and want to try a small
real-hardware experiment, start by exporting the exact same measured logical circuit used
by the proxy comparison:

```bash
python -m quantum_compare.cli hardware-guide --provider all --export-family bell --export-size 2
```

This prints provider-specific setup notes and writes an OpenQASM 2 file under
`hardware_exports/`. The command does not submit a job.

For IBM Quantum, use the official Qiskit Runtime route after configuring an IBM Quantum
Platform account and service instance. For Quantinuum, use the official Nexus route,
convert the Qiskit circuit to TKET when needed, request a cost estimate, and submit only
after explicitly deciding to spend the required credits or quota. Keep any real hardware
or official emulator results in separate rows/files from the offline proxy-model results.

An author-provided IBM Quantum job reference is documented separately in
`docs/IBM_HARDWARE_VALIDATION.md`. It is not included in the proxy-model tables because
the measured counts and backend metadata still need to be extracted and recorded.

Official documentation checked for this section:

- IBM Qiskit installation:
  `https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit`
- IBM Cloud/Quantum setup:
  `https://quantum.cloud.ibm.com/docs/en/guides/cloud-setup`
- IBM Runtime primitives:
  `https://quantum.cloud.ibm.com/docs/en/guides/get-started-with-primitives`
- Quantinuum documentation home:
  `https://docs.quantinuum.com/`
- Quantinuum Nexus getting started:
  `https://docs.quantinuum.com/nexus/trainings/getting_started.html`
- Quantinuum Qiskit-to-Nexus pathway:
  `https://docs.quantinuum.com/systems/trainings/alternate_pathways/qiskit_h2.html`

## Repository Structure

- `config/experiments.yaml`: circuit families, qubit sizes, repetitions, and output
  locations.
- `src/quantum_compare/`: source package for circuits, architecture models, metrics,
  experiment execution, CLI commands, and visualization/report generation.
- `tests/`: unit and smoke tests for circuits, metrics, backend modes, architecture
  compilation, and visualization generation.
- `scripts/`: reproducibility, environment, device-listing, report, and artifact
  comparison helpers.
- `docs/`: architecture notes, metrics, limitations, experiment protocol, beginner
  guide, ownership/citation notes, IBM hardware validation notes, and qBraid validation
  notes.
- `data/processed/`: timestamped processed experiment outputs. The verified public
  baseline is `results_20260623T223649Z`.
- `results/tables/`: generated CSV tables used by the report.
- `results/figures/`: generated PNG figures for presentation and review.
- `results/reports/`: generated Markdown and JSON reports.
- `notebooks/`: qBraid validation notebook.

For a file-by-file explanation written for non-coders, see
`docs/PLAIN_ENGLISH_FILE_GUIDE.md`.

For a simple walkthrough of the code path, see `docs/CODE_WALKTHROUGH.md`.

For public authorship and citation notes, see `docs/OWNERSHIP_AND_CITATION.md`.

## Major Findings

The verified baseline run is `data/processed/results_20260623T223649Z.csv`. It contains
63 rows: 21 ideal baseline rows and 42 architecture-proxy rows.

The main result is structural rather than a universal hardware ranking. Bell and the
current 2-qubit Grover circuit are too small to expose meaningful routing differences.
For GHZ and QFT, the IBM proxy's line connectivity introduces routing SWAPs as qubit
count grows. Those SWAPs are decomposed into native entangling operations, increasing
native-compiled depth and native entangling-gate count. The Quantinuum proxy avoids
routing SWAP insertion for these tested circuits because its proxy connectivity is
all-to-all, although it still has native-basis decomposition overhead.

Under the selected proxy timing and proxy error assumptions, the Quantinuum proxy has
lower estimated native execution duration and higher estimated success probability for
the tested matched circuit sizes. These estimates depend on model assumptions and do
not prove that one architecture is universally superior.

## Figures And Reports

Primary figures:

- `results/figures/key_metric_summary.png`
- `results/figures/logical_depth_baseline.png`
- `results/figures/routed_depth_scaling_by_family.png`
- `results/figures/native_depth_scaling_by_family.png`
- `results/figures/routing_swap_count_scaling_by_family.png`
- `results/figures/native_entangling_gate_count_scaling_by_family.png`
- `results/figures/estimated_native_duration_scaling_by_family.png`
- `results/figures/estimated_proxy_success_scaling_by_family.png`

Primary reports:

- `results/reports/summary_report.md`
- `results/reports/final_results_written_summary.md`
- `results/reports/qbraid_artifact_comparison.json`

## qBraid Validation Status

The qBraid validation path is documented in `docs/QBRAID_VALIDATION.md` and
`notebooks/qbraid_validation.ipynb`. It validates imports, package versions, tests, the
offline proxy-model experiment pipeline, report generation, and artifact comparison
against `data/processed/results_20260623T223649Z.csv`.

This validation does not require paid QPU access. Optional local simulator output in
qBraid is a platform sanity check only and must not be described as IBM or Quantinuum
hardware measurement.

## Limitations

- The study uses architecture-aware offline proxy models, not live calibrated hardware.
- Results are not direct benchmarks of physical IBM or Quantinuum hardware.
- Estimated native execution duration depends on proxy timing assumptions.
- Estimated success probability depends on proxy error-rate assumptions.
- The Quantinuum proxy uses Qiskit `rzz` as an offline ZZ-type entangling proxy rather
  than official pytket Quantinuum compilation passes.
- The configured circuit set is small; Grover currently has only one supported qubit
  count.
- Repetitions are deterministic unless future work varies compiler seeds.
- The findings do not prove that one architecture is universally superior.

## Confidentiality Statement

This public repository contains a sanitized independent research implementation. It
excludes confidential company information and materials protected under a nondisclosure
agreement.
