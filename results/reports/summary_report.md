# Quantum Architecture Comparison Report

This is an offline architecture-proxy compilation and modeling study. It separates
algorithmic logical circuits, topology-routed circuits, and final native-basis circuits.
It is not real-hardware benchmarking and does not report measured IBM or Quantinuum
hardware performance, physical fidelity, or experimentally measured execution time.

## Targets and Assumptions

- IBM proxy: Qiskit GenericBackendV2-compatible line-coupled proxy with `rz`, `sx`, `x`, and `cx`.
- Quantinuum proxy: H-series-style all-to-all proxy with `rz`, `rx`, and Qiskit `rzz` as the ZZ-type entangling proxy.

Assumption table: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/proxy_assumptions_table.csv`. These values are not live-device calibration values.

Duration metric name: `estimated_native_execution_duration_from_proxy_timing_model`.
Success metric name: `estimated_success_probability_from_proxy_error_model`.

## Statistical Handling

Uncertainty is calculated only within matched circuit family, architecture, and qubit-count
groups across repetitions. Variation across qubit counts is shown as scaling, not as an
experimental error bar.

Grouped statistics table: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/qubit_grouped_statistics.csv`
Matched-size comparison table: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/matched_size_architecture_comparison.csv`

## Native-Basis Validation

Unsupported-operation count across successful native circuits: `0`.
Logical/native equivalence failures: `0`.
Routing SWAPs are recorded on the routed circuit before SWAP decomposition. Native
entangling-gate counts are recorded after final native-basis decomposition.

## Main Figures

- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/routed_depth_scaling_by_family.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/native_depth_scaling_by_family.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/routing_swap_count_scaling_by_family.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/native_entangling_gate_count_scaling_by_family.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/estimated_native_duration_scaling_by_family.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/estimated_proxy_success_scaling_by_family.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/logical_depth_baseline.png`

## Plain-Language Interpretation

| Circuit family | Connectivity demand | IBM proxy behavior | Quantinuum proxy behavior | Supported conclusion | Important limitation |
| --- | --- | --- | --- | --- | --- |
| bell | Two-qubit nearest-neighbor-sized circuit. | No routing SWAPs; native decomposition adds basis-gate layers. | No routing SWAPs; all-to-all connectivity is not meaningfully exercised. | Too small to expose meaningful topology differences. | Only a two-qubit case is present. |
| ghz | Fan-out from one qubit to many others. | Line connectivity creates routing SWAPs and more native CX operations as qubit count grows. | All-to-all routing avoids SWAP insertion; native RZZ decomposition still adds basis layers. | Restricted connectivity creates routing and native-gate overhead as qubit count grows. | Targets are proxies, not calibrated devices. |
| grover | Current implementation is only the two-qubit search circuit. | No routing SWAPs; CZ/H/X are decomposed into RZ/SX/CX basis. | No routing SWAPs; CZ/H/X are decomposed into RZ/RX/RZZ proxy basis. | Current small-size evidence is insufficient for a broad architecture conclusion. | No 3-5 qubit Grover circuits are implemented here. |
| qft | Many long-range controlled-phase interactions. | Line connectivity and SWAP decomposition produce large native-depth and entangling-gate overhead. | All-to-all routing avoids SWAP insertion; native decomposition still increases depth. | Long-range interactions strongly expose the difference between line connectivity and all-to-all connectivity. | Only 3- and 5-qubit QFT cases are configured. |

## Sensitivity Analysis

Duration and success probability were recomputed from the final native operation counts
under optimistic, baseline, and pessimistic proxy assumptions without recompiling circuits.

Sensitivity rows: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/model_sensitivity_analysis.csv`
Sensitivity ordering: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/model_sensitivity_ordering.csv`
Duration ordering stable across scenarios: `True`.
Success-probability ordering stable across scenarios: `True`.

## Appendix Figures

Family-wide mean charts are appendix-only because circuit families use different qubit-count coverage.
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/appendix_family_mean_native_depth.png`
- `/Users/abdellahaly/quantum-architecture-comparison/results/figures/appendix_family_mean_native_depth_ratio.png`

## Provenance

Raw processed results: `/Users/abdellahaly/quantum-architecture-comparison/data/processed/results_20260623T223649Z.csv`
Validation table: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/architecture_validation_table.csv`
Native-depth raw rows: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/native_depth_bar_raw_rows.csv`
Grover diagnostics: `/Users/abdellahaly/quantum-architecture-comparison/results/tables/grover_diagnostic_report.csv`

## Remaining Scientific Limitations

- Targets are offline proxies, not current calibrated hardware snapshots.
- Quantinuum compilation uses a Qiskit RZZ proxy rather than pytket Quantinuum passes.
- Duration and error values are proxy assumptions; they are not hardware metadata.
- Grover has only one supported qubit count, so its ordering remains inconclusive.
- Repetitions are deterministic and do not sample compiler stochasticity unless seeds are varied in future runs.
