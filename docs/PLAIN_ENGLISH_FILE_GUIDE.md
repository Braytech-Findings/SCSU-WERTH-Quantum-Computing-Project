# Plain English File Guide

This guide labels the project file by file in simple language. It is written for a
reader who has never coded before. Think of the project like a science fair experiment:
the code builds the experiment, the config says what to test, the data stores what
happened, and the reports explain what the results mean.

Important safety note: this project has two parts. The comparison tables use offline
proxy models. The IBM hardware validation files are real IBM Quantum machine results,
and the Quantinuum Nexus validation files are real provider emulator results. Both are
saved separately under `results/hardware/`. The project does not invent live hardware
calibration values.

## Big Picture

- The project asks one question: what happens when the same quantum circuits are prepared
  for two different kinds of quantum-computer layouts?
- The IBM proxy is like a row of seats where qubits can only easily talk to neighbors.
- The Quantinuum proxy is like a room where any qubit can talk to any other qubit.
- The code keeps the same starting circuits for both paths, so the comparison is fair.
- When a number is not available, the project uses `null` instead of pretending the value
  is zero.

## How The Code Runs On qBraid, IBM, And Quantinuum

Here is the simple version: qBraid is the place where the project can be opened, tested,
and run. IBM and Quantinuum are the two architecture styles being compared by the code.
In this repository, the IBM and Quantinuum comparison rows are offline proxy-model rows.
The separate IBM hardware files are actual IBM Quantum results, and the separate
Quantinuum Nexus files are actual provider emulator results.

### qBraid

qBraid is the cloud workspace where the project can be validated. A reader can upload or
clone the repository into qBraid Lab, install the project, and run the notebook or command
line tools.

The normal qBraid validation flow is:

```bash
python -m pip install -e .
python -m quantum_compare.cli check
pytest
python scripts/generate_report.py
python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv
```

In plain English, those commands mean:

- Install this project into the qBraid Python environment.
- Check that the command-line tool starts.
- Run the tests to make sure the code still behaves correctly.
- Rebuild the result tables, figures, and reports.
- Compare the regenerated results against the verified baseline file.

The qBraid notebook, `notebooks/qbraid_validation.ipynb`, does the same kind of work in a
step-by-step notebook format. It may also run a small Bell circuit on a local
qBraid-compatible Qiskit Aer simulator if that simulator is available. That simulator
check is only a platform sanity check. It is not an IBM or Quantinuum hardware result.

### IBM

The IBM path in this repository asks: "What happens if the same logical circuit is
compiled for an IBM-style superconducting layout?"

The code does this in two layers:

- `src/quantum_compare/architecture.py` uses `IBMArchitectureModel` to model an
  IBM-style line-connected superconducting proxy.
- `src/quantum_compare/backends/ibm_superconducting.py` provides a dry-run IBM backend
  adapter so the experiment runner can include IBM-labeled rows without pretending that
  live IBM hardware is available.

In plain English, the IBM proxy does this:

1. Start with the same logical circuit used everywhere else.
2. Pretend the qubits sit in a line, where only neighbors can easily interact.
3. Add SWAP moves when two qubits need to interact but are not neighbors.
4. Convert the circuit into the IBM proxy's allowed native gates: `rz`, `sx`, `x`, and
   `cx`, plus allowed non-unitary operations like measurement.
5. Check that the final native circuit still matches the original circuit's quantum
   behavior, ignoring the final measurements.
6. Save counts such as depth, gate count, SWAP count, estimated proxy duration, and
   estimated proxy success probability.

The important wording is "IBM-style proxy." The saved IBM rows are useful for studying
architecture effects, but they are not measured IBM device performance and they do not
contain live IBM calibration data.

### Quantinuum

The Quantinuum path asks: "What happens if the same logical circuit is compiled for a
Quantinuum-style trapped-ion layout?"

The code also does this in two layers:

- `src/quantum_compare/architecture.py` uses `QuantinuumArchitectureModel` to model a
  Quantinuum H-series-style all-to-all trapped-ion proxy.
- `src/quantum_compare/backends/quantinuum_trapped_ion.py` provides a dry-run Quantinuum
  backend adapter so the experiment runner can include Quantinuum-labeled rows without
  pretending that live Quantinuum hardware or emulator access is available.

In plain English, the Quantinuum proxy does this:

1. Start with the same logical circuit used for the IBM path.
2. Pretend the qubits have all-to-all connectivity, meaning any qubit can interact with
   any other qubit.
3. Because of that all-to-all proxy layout, the tested circuits do not need routing SWAPs.
4. Convert the circuit into the Quantinuum proxy's allowed native gates: `rz`, `rx`, and
   Qiskit's `rzz` as an offline ZZ-type entangling proxy, plus measurement.
5. Check that the final native circuit still matches the original circuit's quantum
   behavior, ignoring the final measurements.
6. Save the same kinds of metrics as the IBM path so the two architecture styles can be
   compared fairly.

The important wording is "Quantinuum-style proxy." The saved Quantinuum rows are not
official Quantinuum hardware or emulator measurements, and they are not official pytket
Quantinuum compilation results.

The separate Quantinuum Nexus validation path is documented in
`docs/QUANTINUUM_HARDWARE_VALIDATION.md`. That path can use the author's Nexus access to
prepare, compile, and, after explicit approval, execute official Quantinuum emulator or
syntax-checker jobs.

### Why This Still Counts As Running The Comparison

The experiment really does execute the project workflow: it builds circuits, compiles
them through both architecture-proxy paths, checks equivalence, calculates metrics, and
writes result files. What it does not do by default is submit paid jobs to physical
quantum computers. This is why the project can be safely reproduced in qBraid without
API keys or spending hardware credits.

## How To Prepare A Small Real-Hardware Test

The safest first step is to export one tiny circuit and read the provider instructions:

```bash
python -m quantum_compare.cli hardware-guide --provider all --export-family bell --export-size 2
```

In plain English, this command does three things:

- It explains how IBM and Quantinuum hardware access would be set up.
- It saves the same measured Bell circuit used by the project as an OpenQASM file in
  `hardware_exports/`.
- It does not submit a job, does not use an API key, and does not spend credits.

The exported circuit measures qubit 0 into classical bit 0, qubit 1 into classical bit 1,
and so on. Qiskit usually prints bitstrings with the highest classical bit on the left.
That means a reader should write down any bit-order conversion before comparing provider
counts with this project's saved results.

### IBM Hardware In Plain English

To run on IBM hardware, a reader needs an IBM Quantum Platform account, a configured
service instance, and the `qiskit-ibm-runtime` package. The official IBM Runtime workflow
selects an operational non-simulator backend, transpiles the circuit for that backend,
and runs it with a Runtime primitive such as Sampler. This project does not do those
steps automatically because they may depend on the reader's account, region, backend
availability, queue, and pricing.

If a reader does run an IBM job, they should save the backend name, job id, shot count,
date, measured counts, and any provider-reported metadata. If a value is unavailable,
they should record `null`, not zero.

### Quantinuum Hardware In Plain English

To run on Quantinuum hardware, a reader needs Quantinuum Nexus access and the packages
`pytket-qiskit`, `pytket`, and `qnexus`. The official Quantinuum pathway can convert a
Qiskit circuit into a TKET circuit, upload it to Nexus, compile it for a selected target,
estimate cost, and then execute it. This project stops before submission so nobody
accidentally spends HQCs or account quota.

If a reader does run a Quantinuum job, they should keep those rows separate from the
offline proxy rows. Official Quantinuum emulator or hardware measurements are real
provider outputs; the existing Quantinuum rows in this repository are architecture-proxy
rows.

### Other Hardware Providers

Other quantum providers can be tested in the same careful way:

1. Export or rebuild the same logical circuit from `src/quantum_compare/circuits.py`.
2. Compile it using the provider's official tools.
3. Record the provider, backend, job id, shot count, date, and measured counts.
4. Keep unavailable values as `null`.
5. Do not mix real hardware measurements with offline proxy estimates in the same label.

The science rule is simple: same starting circuit, clearly named target, honest source
for every measurement.

## Main Project Files

| File | Plain English label |
| --- | --- |
| `README.md` | The front door of the project. It explains what the project is, how to install it, how to run it, and what the main findings are. |
| `PROJECT_OVERVIEW.md` | A short project summary for readers who want the story before the details. |
| `PLAN.md` | The project plan. It lists the intended steps and checks for the research work. |
| `FINAL_STATUS.md` | A final wrap-up that says what is complete, what was checked, and what the results support. |
| `AGENTS.md` | Instructions for coding assistants working in this repository. |
| `LICENSE` | The legal permission file that says how others may use the project. |
| `CITATION.cff` | A citation helper so other people know how to cite this work. |
| `.gitignore` | A list of files Git should usually ignore, such as cache files or private local files. |
| `.env.example` | A safe example of environment-variable names. It is not supposed to contain real secrets or API keys. |
| `pyproject.toml` | The Python project setup file. It lists package dependencies, test settings, and formatting settings. |

## Source Code: `src/quantum_compare/`

This folder is the main engine of the project.

| File | Plain English label |
| --- | --- |
| `src/quantum_compare/__init__.py` | Marks `quantum_compare` as a Python package. It is intentionally tiny. |
| `src/quantum_compare/circuits.py` | Builds the starting quantum circuits: Bell, GHZ, QFT, and Grover. These are the same logical circuits used for each architecture path. |
| `src/quantum_compare/architecture.py` | Builds the offline architecture proxy models. It routes circuits, converts them to native gates, counts SWAPs, checks equivalence, and estimates proxy duration and proxy success probability. |
| `src/quantum_compare/experiment.py` | Runs the full experiment. It builds each circuit, sends it through the ideal, IBM-proxy, and Quantinuum-proxy paths, calculates metrics, and saves CSV/JSON result files. |
| `src/quantum_compare/metrics.py` | Contains the math helpers for probabilities, success probability, total variation distance, and Hellinger fidelity. |
| `src/quantum_compare/visualization.py` | Turns saved result files into tables, figures, and a Markdown summary report. |
| `src/quantum_compare/hardware.py` | Exports the same logical circuits for optional real-hardware testing and prints safe provider setup guidance without submitting jobs. |
| `src/quantum_compare/models.py` | Defines the experiment settings object: circuit families, qubit sizes, shots, repetitions, seed, backends, and output folders. |
| `src/quantum_compare/config.py` | Loads and saves the YAML config file. |
| `src/quantum_compare/cli.py` | Provides command-line commands such as `check`, `devices`, `run`, `report`, and `hardware-guide`. |

## Backend Adapters: `src/quantum_compare/backends/`

These files give each backend path the same shape, so the experiment runner can talk to
them in a consistent way.

| File | Plain English label |
| --- | --- |
| `src/quantum_compare/backends/base.py` | Defines the required methods every backend adapter must have. It is like a checklist for backend classes. |
| `src/quantum_compare/backends/ideal.py` | Runs the circuit on a noiseless Qiskit Aer simulator. This gives the clean reference answer. |
| `src/quantum_compare/backends/ibm_superconducting.py` | A dry-run IBM adapter. It does not submit IBM hardware jobs. It clearly reports unavailable live execution unless real access is added separately. |
| `src/quantum_compare/backends/quantinuum_trapped_ion.py` | A dry-run Quantinuum adapter. It does not submit Quantinuum hardware jobs. It keeps emulator or hardware access separate from the offline proxy study. |

## Scripts: `scripts/`

Scripts are small command shortcuts.

| File | Plain English label |
| --- | --- |
| `scripts/check_environment.py` | Runs the CLI environment check. It is a quick "does the package start?" test. |
| `scripts/run_core_suite.py` | Runs the ideal-only core suite from the config. |
| `scripts/generate_report.py` | Runs the full configured suite and generates report artifacts. |
| `scripts/list_devices.py` | Prints the available backend adapters and whether they are available in the current environment. |
| `scripts/compare_run_artifacts.py` | Compares a new run against the verified baseline and checks that important result tables have the expected shape. |
| `scripts/submit_quantinuum_validation.py` | Builds a Quantinuum Nexus validation plan, and can upload, compile, estimate cost, or execute only when explicit flags are used. |

## Configuration: `config/`

| File | Plain English label |
| --- | --- |
| `config/experiments.yaml` | The experiment recipe. It says which circuits to run, which qubit sizes to use, how many shots and repetitions to run, which backends to include, and where outputs should be saved. |

## Tests: `tests/`

Tests are safety checks. They make sure important behavior still works after changes.

| File | Plain English label |
| --- | --- |
| `tests/test_architecture_models.py` | Checks the IBM and Quantinuum proxy models, including routing, native gates, and equivalence. |
| `tests/test_backend_modes.py` | Checks that backend adapters correctly report dry-run or simulator behavior. |
| `tests/test_circuits.py` | Checks that the Bell, GHZ, QFT, and Grover circuit builders create valid circuits. |
| `tests/test_config.py` | Checks that config loading works. |
| `tests/test_metrics.py` | Checks the probability and comparison math. |
| `tests/test_smoke.py` | Runs small broad checks to make sure the project can start and basic commands work. |
| `tests/test_visualization.py` | Checks that result tables, figures, and reports can be generated. |

## Documentation: `docs/`

These files explain the project for humans.

| File | Plain English label |
| --- | --- |
| `docs/BEGINNER_GUIDE.md` | The easiest starting explanation for new readers. |
| `docs/CODE_WALKTHROUGH.md` | A simple map of how the main code files work together. |
| `docs/ARCHITECTURE.md` | Explains how the code is organized and how the main parts connect. |
| `docs/DATA_DICTIONARY.md` | Explains the columns in the result files. |
| `docs/EXPERIMENT_PROTOCOL.md` | Explains the steps used to run the experiment in a reproducible way. |
| `docs/IBM_HARDWARE_VALIDATION.md` | Records real IBM Quantum hardware job references and the safe sanitized artifacts saved from them. |
| `docs/QUANTINUUM_HARDWARE_VALIDATION.md` | Explains the safe Quantinuum Nexus validation path for `H2-1E`, `H2-2E`, `H2-1SC`, and `H2-2SC`. |
| `docs/LIMITATIONS.md` | Explains what the project does not prove. This protects the research from overclaiming. |
| `docs/METRICS.md` | Explains the measurements used to compare circuits. |
| `docs/QBRAID_VALIDATION.md` | Explains how the project was validated in qBraid and what that validation means. |
| `docs/PLAIN_ENGLISH_FILE_GUIDE.md` | This file. It labels the repository in simple language. |
| `docs/OWNERSHIP_AND_CITATION.md` | Explains how to mark the project as public independent work and how readers should cite it. |

## Notebook: `notebooks/`

| File | Plain English label |
| --- | --- |
| `notebooks/qbraid_validation.ipynb` | A notebook version of the qBraid validation workflow. It helps someone run checks step by step in a notebook environment. |

## Processed Data: `data/processed/`

Processed data files are saved experiment outputs. The verified public baseline is:

| File | Plain English label |
| --- | --- |
| `data/processed/results_20260623T223649Z.csv` | The verified baseline results in spreadsheet form. This is usually the easiest results file to inspect. |
| `data/processed/results_20260623T223649Z.json` | The same verified baseline results in JSON form, which is easier for programs to read. |
| `data/processed/manifest_20260623T223649Z.json` | A small receipt for the verified baseline run. It records the timestamp, file names, and row count. |

Your local folder may also contain extra files named like `results_YYYYMMDDTHHMMSSZ.csv`,
`results_YYYYMMDDTHHMMSSZ.json`, and `manifest_YYYYMMDDTHHMMSSZ.json`. Those are older
or repeated saved runs. The timestamp in the name says when the run was created in UTC.

## Result Tables: `results/tables/`

Tables are CSV files that summarize the experiment in different ways.

| File | Plain English label |
| --- | --- |
| `results/tables/architecture_validation_table.csv` | The main detailed table for each architecture-proxy row. It includes depths, gates, SWAPs, estimates, and equivalence checks. |
| `results/tables/qubit_grouped_statistics.csv` | Groups results by circuit, qubit count, and provider so trends are easier to see. |
| `results/tables/matched_size_architecture_comparison.csv` | Compares IBM-proxy and Quantinuum-proxy rows at matching circuit sizes. |
| `results/tables/proxy_assumptions_table.csv` | Lists the proxy timing and error assumptions. It also marks that they are not live calibration data. |
| `results/tables/model_sensitivity_analysis.csv` | Tests how results change under optimistic, baseline, and pessimistic proxy assumptions. |
| `results/tables/model_sensitivity_ordering.csv` | Checks whether the ordering of architectures stays stable under those sensitivity assumptions. |
| `results/tables/results_interpretation_table.csv` | Gives a short human-readable interpretation of the main result patterns. |
| `results/tables/native_depth_bar_raw_rows.csv` | Raw rows used for the native-depth bar chart and diagnostics. |
| `results/tables/native_depth_bar_summary.csv` | Summary values for native compiled depth. |
| `results/tables/appendix_family_mean_summary.csv` | Average values by circuit family for appendix-style reporting. |
| `results/tables/grover_diagnostic_report.csv` | Extra detail for the small Grover circuit, because it is too small to show much routing difference. |

## Figures: `results/figures/`

Figures are PNG images made from the saved results.

| File | Plain English label |
| --- | --- |
| `results/figures/key_metric_summary.png` | A summary picture of the most important comparison metrics. |
| `results/figures/logical_depth_baseline.png` | Shows the starting logical circuit depth before architecture-specific compilation. |
| `results/figures/routed_depth_scaling_by_family.png` | Shows how routed depth changes as circuits get larger. |
| `results/figures/native_depth_scaling_by_family.png` | Shows how native compiled depth changes as circuits get larger. |
| `results/figures/routing_swap_count_scaling_by_family.png` | Shows how many routing SWAPs were added. |
| `results/figures/native_entangling_gate_count_scaling_by_family.png` | Shows how many native two-qubit-style gates were needed. |
| `results/figures/estimated_native_duration_scaling_by_family.png` | Shows estimated native execution duration from proxy assumptions. |
| `results/figures/estimated_proxy_success_scaling_by_family.png` | Shows estimated success probability from proxy error assumptions. |

## Reports: `results/reports/`

Reports are written explanations of the generated results.

| File | Plain English label |
| --- | --- |
| `results/reports/summary_report.md` | A generated Markdown report summarizing the latest processed results. |
| `results/reports/final_results_written_summary.md` | A longer written explanation of the final results and what they mean. |
| `results/reports/qbraid_artifact_comparison.json` | A machine-readable report showing whether generated artifacts match the verified baseline checks. |

## Hardware Artifacts: `results/hardware/`

These files are sanitized provider records and validation plans. They are kept separate
from the offline proxy-model tables so readers can tell provider outputs from model
estimates.

| File | Plain English label |
| --- | --- |
| `results/hardware/ibm_job_d8up2d1ropqc738b44pg.json` | Safe raw IBM job output with backend, status, and measured counts. It does not include tokens, CRNs, or account identifiers. |
| `results/hardware/ibm_job_d8up2d1ropqc738b44pg_summary.csv` | A smaller table summarizing each pub result by bit-width, shot count, and all-zero/all-one probability. |
| `results/hardware/ibm_extended_validation_plan.json` | The reviewed plan for the longer IBM hardware validation run. It lists the planned circuits before any hardware job is submitted. |
| `results/hardware/ibm_extended_validation_submission_d95vhvd2su3c739gc080.json` | The public submission record for the longer IBM job. It includes the job id, backend, circuit count, and shot count, but no private account data. |
| `results/hardware/ibm_job_d95vhvd2su3c739gc080.json` | Safe raw output from the longer IBM hardware job after it finished. It keeps the measured counts and removes private IBM account details. |
| `results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv` | A smaller table summarizing the longer IBM job by pub result, bit-width, shot count, and all-zero/all-one probability. |
| `results/hardware/quantinuum_validation_plan.json` | The latest safe Quantinuum Nexus validation plan. It lists the planned circuits and shots before or during a Nexus validation attempt. |
| `results/hardware/quantinuum_submission_H2-1E_20260714T173701Z.json` | Safe metadata for the `H2-1E` Nexus compile-only validation. Execution on this target was not used for the saved result. |
| `results/hardware/quantinuum_submission_H2-2E_20260714T174745Z.json` | Safe metadata for the `H2-2E` Nexus compile-only validation. Execution on this target returned a machine-access error. |
| `results/hardware/quantinuum_submission_H2-1LE_20260714T173914Z.json` | Safe metadata for the successful `H2-1LE` Nexus emulator execution. |
| `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z.json` | Downloaded counts from the successful `H2-1LE` Nexus emulator execution. |
| `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z_summary.csv` | Compact summary of the successful `H2-1LE` Nexus emulator execution. |

## Build Metadata: `src/quantum_architecture_comparison.egg-info/`

These files are created by Python packaging tools. They help Python know what package was
installed locally.

| File | Plain English label |
| --- | --- |
| `src/quantum_architecture_comparison.egg-info/PKG-INFO` | Package summary information copied from project metadata. |
| `src/quantum_architecture_comparison.egg-info/SOURCES.txt` | A list of files included in the package metadata. |
| `src/quantum_architecture_comparison.egg-info/dependency_links.txt` | Packaging metadata for dependency links. It is usually empty. |
| `src/quantum_architecture_comparison.egg-info/requires.txt` | Package dependency list used by packaging tools. |
| `src/quantum_architecture_comparison.egg-info/top_level.txt` | Says the top-level import package is `quantum_compare`. |

## Local Generated Folders You May See

These are normal local helper folders. They are not the scientific results.

| Folder or file | Plain English label |
| --- | --- |
| `.git/` | Git's private history folder. It tracks changes to the project. People usually do not edit it by hand. |
| `.venv/` | The local Python environment. It stores installed packages for this computer. |
| `.pytest_cache/` | A cache made by pytest so repeated tests can run more conveniently. |
| `.ruff_cache/` | A cache made by Ruff, the code checker. |
| `.mypy_cache/` | A cache made by mypy, the type checker. |
| `__pycache__/` folders | Python's local speed-up files. They can be regenerated and are not research data. |

## Result Column Labels In Kid-Friendly Words

| Column or phrase | Simple meaning |
| --- | --- |
| `circuit_family` | Which circuit type was tested, such as Bell, GHZ, QFT, or Grover. |
| `qubit_count` | How many qubits the circuit uses. |
| `provider` | Which path made the row: ideal, IBM proxy, or Quantinuum proxy. |
| `logical_depth` | How many layers the original circuit has before hardware-style rules are applied. |
| `routed_depth` | How deep the circuit is after qubits are moved to where they can interact. |
| `native_compiled_depth` | How deep the circuit is after it is rewritten using the target's allowed gates. |
| `routing_swap_count` | How many SWAP moves were added to bring qubits next to each other. |
| `native_entangling_gate_count` | How many native two-qubit-style gates were used. |
| `estimated_native_execution_duration_ns` | Estimated duration in nanoseconds from the proxy assumptions, not from live hardware timing. |
| `estimated_success_probability_from_proxy_error_model` | Estimated chance of success from the proxy error assumptions, not from measured hardware fidelity. |
| `unsupported_operation_count` | How many gates were left that the target was not supposed to use. This should be zero for successful rows. |
| `equivalence_passed` | Whether the compiled circuit still does the same quantum operation as the original circuit, ignoring final measurements. |
| `null` | Means "not available" or "not meaningful here." It does not mean zero. |

## How To Read The Main Result

The safest interpretation is:

- The same logical circuits were used for both architecture-proxy paths.
- The IBM proxy's line connectivity can require extra SWAPs for larger GHZ and QFT
  circuits.
- The Quantinuum proxy's all-to-all connectivity avoids routing SWAPs for these tested
  circuits.
- The duration and success-probability numbers are estimates from proxy assumptions.
- The IBM hardware validation files and Quantinuum Nexus emulator files are real
  provider results and are stored separately from those estimates.
- The project does not prove that one real hardware system is always better than another.
