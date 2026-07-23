<p align="center"><img src="docs/assets/quantum_architecture_hero.svg" alt="The same circuit branching toward superconducting and trapped-ion architecture models." width="100%"></p>

# Different Roads to the Same Circuit: Quantum Architecture Comparison

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![Tests](https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project/actions/workflows/tests.yml/badge.svg)](.github/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2EA44F)](LICENSE)
[![Evidence](https://img.shields.io/badge/evidence-IBM%20QPU%20%7C%20Quantinuum%20emulator%20%7C%20offline%20proxies-5C4B8A)](EVIDENCE_STATUS.md)

> [!IMPORTANT]
> **Evidence status:** The IBM results in this repository are measurements from the physical `ibm_kingston` QPU. The Quantinuum results are from Nexus emulator targets (`H2-1LE` and `H2-Emulator`) plus compile-only workflow checks. This project is **not yet a matched physical IBM-versus-Quantinuum hardware benchmark**. A full matched physical Quantinuum QPU run remains future work.

**Navigate:** [Evidence status](EVIDENCE_STATUS.md) · [Overview](#overview) · [Results](#major-findings) · [Install](docs/INSTALLATION.md) · [Run](docs/RUNNING_THE_PROJECT.md) · [Figures](docs/FIGURE_INTERPRETATION_GUIDE.md) · [Limitations](docs/LIMITATIONS.md)

## Overview

This project asks how the same logical Bell, GHZ, Grover, and QFT circuits change when compiled for two different architecture models. One model uses nearest-neighbor superconducting-style connectivity. The other uses all-to-all trapped-ion-style connectivity. The comparison records routing SWAPs, two-qubit work, depth, model-estimated duration, and model-estimated success.

The repository also preserves provider results as separate evidence:

- **IBM:** physical `ibm_kingston` QPU measurements.
- **Quantinuum:** Nexus emulator measurements from `H2-1LE` and `H2-Emulator`, plus compile-only checks.

The project title is retained because the scientific question concerns algorithm-hardware fit. The evidence labels prevent the title from being mistaken for a completed physical IBM-versus-Quantinuum benchmark.

## Evidence Structure

| Phase | Evidence | Status | What it supports |
| --- | --- | --- | --- |
| I | Controlled offline architecture proxies | Complete | How topology and native-gate assumptions change compiled circuit cost |
| II | IBM Kingston physical QPU | Complete for saved jobs | Real IBM hardware behavior for the submitted workloads |
| III | Quantinuum Nexus emulator | Complete for the saved small suite | Provider workflow validation and emulator output for Bell-2, GHZ-3, and Grover-2 |
| IV | Matched physical Quantinuum QPU comparison | Pending | Required before any direct physical IBM-versus-Quantinuum ranking |

See [EVIDENCE_STATUS.md](EVIDENCE_STATUS.md) for the authoritative wording.

## Research Question

How do the same logical circuits change after topology routing and native-basis decomposition for superconducting-style and trapped-ion-style architecture models, and what parts of that prediction are supported by the available provider results?

## Architectures and Provider Evidence

- **IBM proxy:** line-coupled Qiskit `GenericBackendV2`-style model using `rz`, `sx`, `x`, and `cx`.
- **Quantinuum proxy:** all-to-all H-series-style model using `rz`, `rx`, and Qiskit `rzz` as an offline ZZ-type entangling proxy.
- **IBM provider evidence:** two saved physical `ibm_kingston` jobs.
- **Quantinuum provider evidence:** two saved Nexus emulator executions and two compile-only checks.

Proxy timing and error values are study assumptions. They are not live provider calibration data.

## Circuit Families

- Bell state: 2 qubits.
- GHZ states: 3, 5, and 7 qubits.
- QFT: 3 and 5 qubits.
- Grover search: 2 qubits.

## Install and Run the Offline Study

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python scripts/validate_repository.py
python -m quantum_compare.cli run --backend all --suite core
python -m quantum_compare.cli report
pytest
```

These commands do not submit provider jobs. Provider execution requires separate credentials, explicit confirmation, and quota review.

## Provider Validation Status

### IBM physical hardware

- Original GHZ stress job: `d8up2d1ropqc738b44pg`, 90 circuit results, 4,096 shots each.
- Expanded validation job: `d95vhvd2su3c739gc080`, 115 results, 4,096 shots each.
- Documentation: `docs/IBM_HARDWARE_VALIDATION.md`.

### Quantinuum Nexus emulator

- `H2-1LE`: Bell-2, GHZ-3, and Grover-2, 100 shots each.
- `H2-Emulator`: Bell-2, GHZ-3, and Grover-2, 100 shots each.
- `H2-1E` and `H2-2E`: compilation succeeded; execution was rejected for account access.
- Documentation: `docs/QUANTINUUM_HARDWARE_VALIDATION.md`.

These Quantinuum results are real provider emulator outputs, not physical trapped-ion QPU measurements.

## Major Findings

The controlled proxy comparison shows an algorithm-dependent pattern. Bell and the current two-qubit Grover circuit are too small to expose large routing differences. GHZ and QFT require substantially more routing and two-qubit work under the nearest-neighbor model than under the all-to-all model.

Under the declared proxy assumptions, the all-to-all trapped-ion-style model has lower estimated duration and higher estimated success for the tested larger GHZ and QFT circuits. This is a model result, not measured Quantinuum hardware superiority.

The physical IBM GHZ stress experiment supports the mechanism that additional compiled two-qubit work makes a fragile entangled distribution harder to preserve. The Quantinuum emulator results show that the small validation circuits compiled and executed through Nexus. Together, these evidence streams support the study workflow but do not complete a matched physical provider comparison.

## Figures and Reports

- Curated figures: `results/final_figures/`
- Expanded R figures: `results/final_figures/r_visualizations/`
- Summary report: `results/reports/summary_report.md`
- Verified proxy values: `results/reports/final_results_written_summary.md`
- Figure guide: `docs/FIGURE_INTERPRETATION_GUIDE.md`

All provider figures must retain their evidence label: IBM physical hardware or Quantinuum Nexus emulator.

## Repository Structure

- `src/quantum_compare/`: circuit construction, architecture models, metrics, and reports.
- `data/processed/`: authoritative proxy-model outputs.
- `results/hardware/`: sanitized IBM physical-hardware and Quantinuum emulator artifacts.
- `results/tables/`, `results/figures/`, `results/reports/`: generated analysis outputs.
- `docs/`: methods, evidence notes, limitations, and beginner explanations.
- `notebooks/`: qBraid validation workflow.

## Limitations

- The main architecture comparison is based on controlled offline proxy models.
- The IBM evidence is physical hardware, but it covers specific saved workloads on one backend.
- The Quantinuum evidence is emulator-only; no physical Quantinuum QPU result is stored.
- The physical IBM and Quantinuum evidence is not matched by circuit suite, shots, repetitions, compiler settings, or calibration window.
- The project therefore cannot rank IBM against Quantinuum as physical providers.
- Grover has only one supported size.

## Confidentiality

This public repository is a sanitized independent research implementation. It excludes credentials, confidential company information, and nondisclosure-agreement materials.
