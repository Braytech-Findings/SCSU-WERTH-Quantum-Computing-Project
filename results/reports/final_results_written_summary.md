# Verified Final Results Written Summary

This written version was verified against the authoritative completed full architecture
proxy run:
`20260623T223649Z`.

The authoritative verified processed run is:
`data/processed/results_20260623T223649Z.csv`.

The tables below use proxy-model labels:

- IBM proxy model: `qiskit-generic-backend-v2-line-proxy`
- Quantinuum proxy model: `quantinuum-h-series-rzz-offline-proxy`

The CSV schema stores the proxy-model key in a column named `provider`; this report
displays it as a proxy model rather than as a hardware provider.

No values below are real-hardware measurements. This is an offline architecture-proxy
compilation and modeling study.

## Verification Result

Every numeric value in this written summary was checked against the latest generated
CSV/table artifacts. No value was found to come from an older run. No manually typed
figure value was retained without checking it against the source tables.

One presentation correction was made: the written sensitivity sections include the
actual aggregate values from `results/tables/model_sensitivity_analysis.csv`; the
earlier written version stated only the ordering conclusion.

## Figure 1: Logical Depth Baseline

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=logical_depth`, `circuit_family`, `qubit_count`, `mean`  
Proxy-model note: logical circuits are architecture-independent, so each logical value
is listed once per circuit family and qubit count.

| Circuit family | Qubits | Logical depth |
| --- | ---: | ---: |
| Bell | 2 | 3 |
| GHZ | 3 | 4 |
| GHZ | 5 | 6 |
| GHZ | 7 | 8 |
| Grover | 2 | 8 |
| QFT | 3 | 7 |
| QFT | 5 | 11 |

Interpretation: both proxy-model pipelines begin from the same logical circuit for
each circuit family and qubit count.

## Figure 2: Routed Depth by Family

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=routed_depth`, `circuit_family`, `qubit_count`, `provider`,
`target_model`, `mean`

| Circuit family | Qubits | IBM proxy routed depth | Quantinuum proxy routed depth |
| --- | ---: | ---: | ---: |
| Bell | 2 | 3 | 3 |
| GHZ | 3 | 8 | 4 |
| GHZ | 5 | 18 | 6 |
| GHZ | 7 | 28 | 8 |
| Grover | 2 | 8 | 8 |
| QFT | 3 | 14 | 7 |
| QFT | 5 | 33 | 11 |

Interpretation: Bell and the current two-qubit Grover circuit do not expose routing
differences. GHZ and QFT show routing-depth growth under the IBM line-connectivity
proxy model, while the Quantinuum all-to-all proxy model avoids routing SWAP insertion.

## Figure 3: Native-Compiled Depth by Family

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=native_compiled_depth`, `circuit_family`, `qubit_count`,
`provider`, `target_model`, `mean`

| Circuit family | Qubits | IBM proxy native-compiled depth | Quantinuum proxy native-compiled depth |
| --- | ---: | ---: | ---: |
| Bell | 2 | 5 | 7 |
| GHZ | 3 | 16 | 9 |
| GHZ | 5 | 38 | 13 |
| GHZ | 7 | 60 | 17 |
| Grover | 2 | 12 | 10 |
| QFT | 3 | 42 | 21 |
| QFT | 5 | 106 | 29 |

Interpretation: native-compiled depth includes native-basis decomposition. IBM proxy
depth grows sharply for GHZ and QFT because routed SWAPs are decomposed into native
operations. Quantinuum proxy circuits also have native-basis overhead, but avoid
topology-routing SWAPs.

## Figure 4: Routing SWAP Count by Family

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=routing_swap_count`, `circuit_family`, `qubit_count`,
`provider`, `target_model`, `mean`

| Circuit family | Qubits | IBM proxy routing SWAP count | Quantinuum proxy routing SWAP count |
| --- | ---: | ---: | ---: |
| Bell | 2 | 0 | 0 |
| GHZ | 3 | 4 | 0 |
| GHZ | 5 | 12 | 0 |
| GHZ | 7 | 20 | 0 |
| Grover | 2 | 0 | 0 |
| QFT | 3 | 6 | 0 |
| QFT | 5 | 30 | 0 |

Interpretation: routing SWAP count is measured before SWAP decomposition. The IBM line
proxy model inserts routing SWAPs for larger GHZ and QFT circuits. The Quantinuum
all-to-all proxy model inserts none for these circuits.

## Figure 5: Native Entangling-Gate Count by Family

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=native_entangling_gate_count`, `circuit_family`,
`qubit_count`, `provider`, `target_model`, `mean`

| Circuit family | Qubits | IBM proxy native entangling gates | Quantinuum proxy native entangling gates |
| --- | ---: | ---: | ---: |
| Bell | 2 | 1 | 1 |
| GHZ | 3 | 12 | 2 |
| GHZ | 5 | 34 | 4 |
| GHZ | 7 | 56 | 6 |
| Grover | 2 | 2 | 2 |
| QFT | 3 | 27 | 6 |
| QFT | 5 | 116 | 16 |

Interpretation: native entangling-gate count is measured after native-basis
decomposition. IBM proxy counts increase substantially for GHZ and QFT because routing
SWAPs are decomposed into native entangling operations.

## Figure 6: Estimated Native Duration by Family

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=estimated_native_execution_duration_us`, `circuit_family`,
`qubit_count`, `provider`, `target_model`, `mean`

These are proxy timing estimates in microseconds. Raw nanosecond values remain in the
CSV artifacts.

| Circuit family | Qubits | IBM proxy duration, us | Quantinuum proxy duration, us |
| --- | ---: | ---: | ---: |
| Bell | 2 | 0.62 | 0.45 |
| GHZ | 3 | 4.04 | 0.77 |
| GHZ | 5 | 10.88 | 1.41 |
| GHZ | 7 | 17.72 | 2.05 |
| Grover | 2 | 1.16 | 0.72 |
| QFT | 3 | 8.70 | 1.53 |
| QFT | 5 | 35.80 | 3.53 |

Interpretation: under the selected proxy timing model, Quantinuum proxy duration is
lower for every matched circuit size. These are not experimentally measured execution
times.

## Figure 7: Estimated Proxy Success Probability by Family

Source: `results/tables/qubit_grouped_statistics.csv`  
Source columns: `metric=estimated_success_probability_from_proxy_error_model`,
`circuit_family`, `qubit_count`, `provider`, `target_model`, `mean`

These are proxy error-model estimates. They are not physical fidelity measurements.

| Circuit family | Qubits | IBM proxy estimated success probability | Quantinuum proxy estimated success probability |
| --- | ---: | ---: | ---: |
| Bell | 2 | 0.949845 | 0.973737 |
| GHZ | 3 | 0.833424 | 0.958221 |
| GHZ | 5 | 0.641642 | 0.927926 |
| GHZ | 7 | 0.493991 | 0.898589 |
| Grover | 2 | 0.937529 | 0.967416 |
| QFT | 3 | 0.715360 | 0.937323 |
| QFT | 5 | 0.280311 | 0.870268 |

Interpretation: under the selected proxy error model, Quantinuum proxy estimated success
probability is higher for every tested matched circuit size.

## Written Sensitivity Section: Duration

Source: `results/tables/model_sensitivity_analysis.csv`  
Source columns: `scenario`, `provider`, `target_model`,
`estimated_native_execution_duration_from_proxy_timing_model_us`

The figure values are means across the tested circuit-family, qubit-count, and
repetition rows within each scenario and proxy model. Circuits were not recompiled for
this sensitivity analysis.

| Scenario | IBM proxy mean duration, us | Quantinuum proxy mean duration, us |
| --- | ---: | ---: |
| Optimistic | 8.455714 | 1.120714 |
| Baseline | 11.274286 | 1.494286 |
| Pessimistic | 14.092857 | 1.867857 |

Ordering check source: `results/tables/model_sensitivity_ordering.csv`  
Ordering source columns: `scenario`, `circuit_family`, `qubit_count`, `repetition`,
`faster_duration_provider`, `duration_ordering_stable`

Ordering result: Quantinuum proxy has the lower duration estimate in every tested
scenario, circuit family, qubit count, and repetition. Duration ordering is stable
across optimistic, baseline, and pessimistic proxy timing assumptions.

## Written Sensitivity Section: Success Probability

Source: `results/tables/model_sensitivity_analysis.csv`  
Source columns: `scenario`, `provider`, `target_model`,
`estimated_success_probability_from_proxy_error_model`

The figure values are means across the tested circuit-family, qubit-count, and
repetition rows within each scenario and proxy model. Circuits were not recompiled for
this sensitivity analysis.

| Scenario | IBM proxy mean estimated success probability | Quantinuum proxy mean estimated success probability |
| --- | ---: | ---: |
| Optimistic | 0.819718 | 0.965992 |
| Baseline | 0.693157 | 0.933354 |
| Pessimistic | 0.530117 | 0.871940 |

Ordering check source: `results/tables/model_sensitivity_ordering.csv`  
Ordering source columns: `scenario`, `circuit_family`, `qubit_count`, `repetition`,
`higher_success_provider`, `success_ordering_stable`

Ordering result: Quantinuum proxy has the higher estimated success probability in
every tested scenario, circuit family, qubit count, and repetition. Success-probability
ordering is stable across optimistic, baseline, and pessimistic proxy error assumptions.

## Overall Verified Conclusion

Both proxy-model pipelines begin from the same logical circuits. Differences appear
after topology routing and native-basis decomposition. The IBM proxy model uses line
connectivity, so GHZ and QFT require routing SWAPs as qubit count grows. Those SWAPs
are then decomposed into native entangling operations, increasing native-compiled depth
and native entangling-gate count. The Quantinuum proxy model uses all-to-all
connectivity, so it avoids routing SWAP insertion in these circuits, although it still
has native-basis decomposition overhead.

Bell is too small to expose meaningful topology differences. GHZ shows increasing IBM
proxy routing and native-gate overhead as qubit count grows. QFT strongly exposes the
difference between line connectivity and all-to-all connectivity because it contains
many long-range interactions. Grover remains inconclusive as a broad architecture
comparison because only the two-qubit version is implemented.

Under the selected proxy timing and proxy error assumptions, the Quantinuum proxy model
has lower estimated native duration and higher estimated success probability for every
tested matched circuit size. These estimates are model-based and must not be described
as measured execution time or hardware fidelity.

## Source-Trace Appendix

Run timestamp: `20260623T223649Z`  
Authoritative manifest: `data/processed/manifest_20260623T223649Z.json`  
Authoritative processed CSV: `data/processed/results_20260623T223649Z.csv`  
Authoritative processed JSON: `data/processed/results_20260623T223649Z.json`

CSV/table artifacts used:

| Artifact | Use in this written summary |
| --- | --- |
| `results/tables/qubit_grouped_statistics.csv` | Figures 1-7 numeric values; grouped by metric, circuit family, proxy-model key, target model, and qubit count. |
| `results/tables/model_sensitivity_analysis.csv` | Figures 8-9 aggregate scenario values. |
| `results/tables/model_sensitivity_ordering.csv` | Figures 8-9 ordering stability checks. |
| `results/tables/architecture_validation_table.csv` | Cross-check for logical, routed, native-compiled, duration, success-probability, unsupported-operation, and equivalence fields. |
| `results/tables/proxy_assumptions_table.csv` | Confirms proxy timing/error assumptions are not live-device calibration values. |
| `results/tables/matched_size_architecture_comparison.csv` | Cross-checks matched circuit-family, qubit-count, and repetition comparisons. |

Verification checks:

- Newest completed run timestamp: `20260623T223649Z`.
- Processed run rows: `63`.
- Successful architecture rows in `architecture_validation_table.csv`: `42`.
- Unsupported native-operation count across architecture rows: `0`.
- Logical-to-native equivalence failures: `0`.
- No figure value in this written summary was taken from the older open tab
  `data/processed/results_20260623T222801Z.csv`.

## Correction Log

- Figures 1-7: values matched the latest grouped statistics table.
- Figure 8: added the exact scenario mean duration values from
  `model_sensitivity_analysis.csv`; the prior written version only stated the ordering.
- Figure 9: added the exact scenario mean success-probability values from
  `model_sensitivity_analysis.csv`; the prior written version only stated the ordering.
- Terminology: replaced hardware/provider-style wording with proxy-model wording while
  preserving exact CSV source-column names where needed for traceability.
