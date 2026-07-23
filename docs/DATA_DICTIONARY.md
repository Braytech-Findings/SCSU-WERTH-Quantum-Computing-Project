# Data Dictionary

## Quantinuum Full-Suite Emulator Tables

`quantinuum_full_suite_raw_results.csv` contains one row per target, repetition, and
circuit. `distribution_fidelity` is the squared classical Bhattacharyya coefficient
against the exact noiseless logical-circuit probabilities. `total_variation_distance` is
half the absolute probability difference summed over all bitstrings. `counts_json`
preserves normalized Qiskit display order (highest classical-bit index at left).
`all_zero_or_all_one_probability` is populated only for Bell/GHZ; QFT receives `null`.
`marked_state_probability` is populated only for Grover. Unavailable values are null,
never fabricated zeros.

- `experiment_id`: Unique identifier for a row. It is run-specific and is ignored by
  deterministic artifact comparisons.
- `timestamp`: ISO 8601 row creation timestamp. It is run-specific and is ignored by
  deterministic artifact comparisons.
- `circuit_family`: Circuit family, such as `bell`, `ghz`, `qft`, or `grover`.
- `qubit_count`: Number of qubits in the logical circuit.
- `shots`: Number of simulator shots requested.
- `repetition`: Repetition number.
- `provider`: Pipeline key: `ideal`, `ibm`, or `quantinuum`. In architecture tables,
  `ibm` means IBM proxy and `quantinuum` means Quantinuum proxy.
- `target_model`: Offline proxy target identifier.
- `architecture`: Architecture label, such as `ideal`, `superconducting`, or
  `trapped-ion`.
- `execution_type`: Ideal simulator or dry-run adapter label. Architecture-proxy metrics
  do not require hardware execution.
- `logical_depth`: Depth of the original logical circuit.
- `routed_depth`: Depth after topology routing.
- `native_compiled_depth`: Depth after final native-basis decomposition.
- `routing_swap_count`: SWAP count inserted during routing, before SWAP decomposition.
- `native_entangling_gate_count`: Entangling-gate count after native-basis decomposition.
- `estimated_native_execution_duration_ns`: Proxy timing-model estimate in nanoseconds.
- `estimated_native_execution_duration_us`: Proxy timing-model estimate in microseconds
  in generated tables.
- `estimated_success_probability_from_proxy_error_model`: Proxy error-model estimate.
- `unsupported_operation_count`: Number of operations outside the selected native proxy
  basis and permitted non-unitary operations.
- `equivalence_passed`: Whether the native-compiled circuit matches the logical circuit
  up to global phase after removing final measurements.
- `measurement_counts`: Raw simulator measurement counts when available; `null` when not
  available.
- `probability_distribution`: Normalized simulator probabilities when available; `null`
  when not available.
- `job_id`: Provider job ID if one exists. Offline proxy rows use `null`.
- `job_status`: Job status or dry-run status.
- `error_message`: Error text when a row fails; `null` for successful rows.
- `target_metadata`: JSON metadata documenting proxy connectivity, basis gates, duration
  assumptions, error assumptions, and source/rationale.

Unavailable values are stored as `null` rather than fabricated zeroes.
