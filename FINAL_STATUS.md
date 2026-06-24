# Final Status

## Current study framing

This project is currently an offline architecture-proxy compilation and modeling study.
It is not real-hardware benchmarking and does not report measured IBM hardware
performance, measured Quantinuum hardware performance, physical fidelity, or
experimentally measured execution time.

## Pipeline status

- Logical, routed, and native-compiled circuit levels are separated in result rows.
- IBM uses the `qiskit-generic-backend-v2-line-proxy` target model with `rz`, `sx`, `x`,
  and `cx` native unitary operations.
- Quantinuum uses the `quantinuum-h-series-rzz-offline-proxy` target model with `rz`,
  `rx`, and `rzz` native unitary operations.
- Routing SWAP count is measured before SWAP decomposition.
- Native entangling-gate count is measured after final native-basis decomposition.
- Estimated duration is reported as
  `estimated_native_execution_duration_from_proxy_timing_model` in analysis tables.
- Estimated success probability is reported as
  `estimated_success_probability_from_proxy_error_model`.

## Validation evidence

- Successful architecture result rows: 42.
- Unsupported native-operation count across successful architecture rows: 0.
- Logical-to-native equivalence failures: 0.
- Equivalence method: unitary comparison up to global phase after removing final
  measurements.
- Equivalence tolerance: `1e-8`.
- IBM final circuits contain only the IBM proxy basis plus permitted non-unitary
  operations.
- Quantinuum final circuits contain only the H-series RZZ proxy basis plus permitted
  non-unitary operations.

## Statistical and reporting outputs

- Matched-size architecture comparison:
  `results/tables/matched_size_architecture_comparison.csv`
- Per-family/qubit grouped statistics:
  `results/tables/qubit_grouped_statistics.csv`
- Proxy assumptions table:
  `results/tables/proxy_assumptions_table.csv`
- Model sensitivity rows:
  `results/tables/model_sensitivity_analysis.csv`
- Model sensitivity ordering:
  `results/tables/model_sensitivity_ordering.csv`
- Plain-language interpretation table:
  `results/tables/results_interpretation_table.csv`
- Final report:
  `results/reports/summary_report.md`

## Sensitivity-analysis result

- Sensitivity rows: 126.
- Duration ordering stable across optimistic, baseline, and pessimistic scenarios: true.
- Success-probability ordering stable across optimistic, baseline, and pessimistic
  scenarios: true.
- Circuits were not recompiled for sensitivity analysis; timing and error estimates were
  recomputed from final native operation counts.

## Final figures

- `results/figures/key_metric_summary.png`
- `results/figures/logical_depth_baseline.png`
- `results/figures/routed_depth_scaling_by_family.png`
- `results/figures/native_depth_scaling_by_family.png`
- `results/figures/routing_swap_count_scaling_by_family.png`
- `results/figures/native_entangling_gate_count_scaling_by_family.png`
- `results/figures/estimated_native_duration_scaling_by_family.png`
- `results/figures/estimated_proxy_success_scaling_by_family.png`

## Commands run

- `ruff check .`
- `pytest`
- warning-producing test count via an in-process pytest warning hook
- `mypy src tests`
- `python -m quantum_compare.cli report`
- isolated reproduction run in a temporary directory
- `python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv`

## Test results

- `ruff check .`: passed.
- `mypy src tests`: passed.
- `pytest`: 26 passed, 0 failed, 0 skipped, 1496 warnings.
- Warning-producing tests: 11 distinct tests.
- Isolated full experiment/report generation: completed and matched the verified
  baseline scientific fields.

## Authoritative verified data

- Processed CSV: `data/processed/results_20260623T223649Z.csv`
- Processed JSON: `data/processed/results_20260623T223649Z.json`
- Manifest: `data/processed/manifest_20260623T223649Z.json`
- Later local `ideal`-only processed runs may exist in an ignored workspace, but they
  are not the verified full architecture-proxy baseline used for the public reports.

## Remaining scientific limitations

- Targets are offline proxies, not current calibrated hardware snapshots.
- Quantinuum compilation uses a Qiskit `rzz` proxy rather than pytket Quantinuum passes.
- Duration and error values are proxy assumptions, not live-device calibration values.
- Grover has only one supported qubit count, so its architecture conclusion remains
  inconclusive.
- Repetitions are deterministic and do not sample compiler stochasticity unless future
  runs vary compilation seeds.
