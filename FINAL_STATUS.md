# Final Status

## Expanded Quantinuum Emulator Package (July 23, 2026)

Complete: seven standardized circuits, 1,000 shots per circuit, and three repetitions
on each of the live-catalog-confirmed `H2-1LE` and `H2-Emulator` emulator targets.
All 42,000 requested shots were retrieved. Distribution fidelity and TVD are in
`results/tables/quantinuum_full_suite_aggregate.csv`. Physical Quantinuum execution and
a matched physical IBM-versus-Quantinuum benchmark remain pending.

Quantinuum Nexus emulator execution validates the standardized workflow and output
distributions on emulator targets. It does not constitute physical Quantinuum
trapped-ion QPU evidence and does not complete a matched physical IBM-versus-Quantinuum
benchmark.

## Release

- Release preparation version: `1.0.0`
- Public title: `Different Roads to the Same Circuit: Quantum Architecture Comparison`
- Release date in citation metadata: `2026-07-14`

## Current Study Framing

This repository contains three clearly separated evidence categories:

- `offline_proxy`: the main architecture comparison using controlled proxy models.
- `physical_hardware`: saved IBM `ibm_kingston` hardware validation counts.
- `emulator`: saved Quantinuum Nexus emulator validation counts.
- `syntax_checker`: Quantinuum/Nexus compile-only workflow checks, when present.

The project is no longer described as offline-only. The proxy comparison remains the
main controlled architecture study, while IBM hardware and Quantinuum emulator artifacts
are preserved separately because they answer different questions.

## Offline Proxy Architecture Comparison

- Authoritative processed CSV: `data/processed/results_20260623T223649Z.csv`
- Authoritative processed JSON: `data/processed/results_20260623T223649Z.json`
- Authoritative manifest: `data/processed/manifest_20260623T223649Z.json`
- Total processed rows: `63`
- Architecture-proxy rows: `42`
- Ideal baseline rows: `21`
- Circuit families: Bell, GHZ, QFT, and Grover.
- Configured circuit sizes:
  - Bell: 2 qubits
  - GHZ: 3, 5, and 7 qubits
  - QFT: 3 and 5 qubits
  - Grover: 2 qubits
- Repetitions per configured backend/circuit-size row: `3`

Architecture models:

- IBM-style superconducting proxy:
  `qiskit-generic-backend-v2-line-proxy`
- Quantinuum-style trapped-ion proxy:
  `quantinuum-h-series-rzz-offline-proxy`

Pipeline status:

- Logical, routed, and native-compiled circuit levels are separated in result rows.
- Routing SWAP count is measured before SWAP decomposition.
- Native entangling-gate count is measured after final native-basis decomposition.
- Estimated duration comes from documented proxy timing assumptions.
- Estimated success probability comes from documented proxy error assumptions.
- Unsupported native-operation count across successful architecture rows: `0`.
- Logical-to-native equivalence failures: `0`.

## IBM Physical-Hardware Validation

The repository preserves two sanitized IBM hardware retrieval records under
`results/hardware/`. They are separate experimental packages and must not be merged into
one statistical analysis.

### IBM Experiment A - Original GHZ Stress Study

This is the IBM experiment used in the July 2026 manuscript's GHZ stress curves,
heatmap, fidelity analysis, and correlation/regression discussion.

- Backend: `ibm_kingston`
- IBM Runtime job ID: `d8up2d1ropqc738b44pg`
- Pub results retrieved: `90`
- GHZ sizes: 2, 4, 6, 8, 12, and 16 qubits
- Stress layers: 0, 1, 2, 4, and 8
- Repetitions per condition: `3` transpiler-seed mappings
- Aggregate conditions: `30`
- Shots per pub result: `4096`
- Total retrieved shots: `368640`
- Counts artifact: `results/hardware/ibm_job_d8up2d1ropqc738b44pg.json`
- Summary artifact: `results/hardware/ibm_job_d8up2d1ropqc738b44pg_summary.csv`

The manuscript statistics, including the reported Pearson `r = -0.911`, Spearman
`rho = -0.876`, slope, and `R^2`, belong to this original 30-condition GHZ analysis.

### IBM Experiment B - Expanded Hardware Validation

This later package is the main source for the repository's supplemental IBM final
figure. It is not the same dataset as the original manuscript analysis.

- Backend: `ibm_kingston`
- IBM Runtime job ID: `d95vhvd2su3c739gc080`
- Pub results retrieved: `115`
- Shots per pub result: `4096`
- Total retrieved shots: `471040`
- Counts artifact: `results/hardware/ibm_job_d95vhvd2su3c739gc080.json`
- Summary artifact: `results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv`

The IBM all-zero/all-one probability is most meaningful for Bell/GHZ-style circuits. It
is not a universal success metric for every algorithm family.

## Quantinuum Nexus Validation

Quantinuum Nexus validation artifacts are saved separately from the offline proxy rows:

- `H2-1E`: compile-only check succeeded; direct execution returned a machine-access
  error for this account.
- `H2-2E`: compile-only check succeeded; direct execution returned a machine-access
  error for this account.
- `H2-1LE`: Nexus emulator execution completed for 3 small circuits with 100 shots per
  circuit.
- `H2-Emulator`: Nexus emulator execution completed for 3 small circuits with 100 shots
  per circuit.

Targets labeled `H2-1LE`, `H2-1E`, `H2-2E`, and similarly named emulator or
syntax-checker targets are emulator-based or workflow-validation evidence in this
repository. They are not physical Quantinuum QPU results.

## Figure Packages

Original curated final figures:

- `results/final_figures/01_simulated_success_probability.png`
- `results/final_figures/02_simulated_routing_swap_cost.png`
- `results/final_figures/03_simulated_time_reliability_tradeoff.png`
- `results/final_figures/04_ibm_hardware_expected_state_probability.png`
- `results/final_figures/05_quantinuum_nexus_emulator_validation.png`

Expanded R visualization package:

- Folder: `results/final_figures/r_visualizations/`
- Generator: `analysis/generate_final_figures_r.R`
- Manifest: `results/final_figures/r_visualizations/r_visualizations_manifest.csv`
- Interpretation guide: `docs/FIGURE_INTERPRETATION_GUIDE.md`
- R analysis report: `reports/R_VISUAL_ANALYSIS.md`

## Validation Status For This Release-Preparation Pass

The following local checks were run during the v1.0.0 cleanup pass:

- `Rscript scripts/generate_final_figures.R`: passed.
- `Rscript analysis/generate_final_figures_r.R`: passed.
- `ruff check .`: passed.
- `ruff format --check .`: passed after running `ruff format .`.
- `mypy src tests scripts/fetch_ibm_hardware_job.py scripts/submit_ibm_extended_validation.py scripts/submit_quantinuum_validation.py scripts/plot_quantinuum_validation.py`:
  passed.
- `pytest`: passed with 28 tests.
- `python -m quantum_compare.cli check`: passed.
- `python -m quantum_compare.cli report`: passed and generated report artifacts.
- `python scripts/generate_report.py`: passed.
- `python scripts/generate_report.py --help`: passed and printed usage without running
  the workflow.
- `python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv --candidate data/processed/results_20260623T223649Z.csv --output results/reports/qbraid_artifact_comparison.json`:
  passed.
- Local secret scan for IBM, Quantinuum, and Nexus token/account patterns: no matches.

Warning cleanup:

- The repository-owned QFT deprecation warning was fixed by replacing deprecated
  `QFT(...)` circuit construction with `QFTGate`.
- Python report generation no longer reports Matplotlib/font-cache warnings after
  configuring temporary writable cache directories before importing Matplotlib.
- A narrow pytest warning filter documents and hides the dependency-originating
  `IBMFractionalTranslationPlugin` deprecation warning from `stevedore.extension`.

## Final Supported Conclusion

Connectivity and native-gate structure affect circuit families differently. The tested
results do not establish that one hardware architecture is universally superior.

## Remaining Scientific Limitations

- The main architecture comparison uses offline proxy models, not live calibrated
  hardware snapshots.
- Quantinuum compilation uses a Qiskit `rzz` proxy rather than official pytket
  Quantinuum compilation passes in the offline comparison.
- Duration and error values in the proxy tables are assumptions, not live-device
  calibration values.
- Grover has only one supported qubit count, so its architecture conclusion remains
  inconclusive.
- IBM hardware validation and Quantinuum emulator validation are separate evidence
  categories and should not be merged into one direct hardware ranking.
