# Limitations

- The architecture comparison tables are an offline proxy-model study, not a direct
  benchmark of physical IBM or Quantinuum hardware.
- The repository also includes real IBM Quantum hardware validation artifacts under
  `results/hardware/`. Those artifacts show what one IBM backend returned for submitted
  jobs, but they are not a broad IBM-versus-Quantinuum hardware benchmark.
- The IBM proxy is a line-coupled GenericBackendV2-style superconducting proxy, not a
  live calibrated backend snapshot.
- The Quantinuum proxy is an all-to-all H-series-style trapped-ion RZZ proxy, not an
  official hardware execution path or pytket Quantinuum compilation result.
- The Quantinuum Nexus targets reported so far are `H2-1E`, `H2-2E`, `H2-1SC`, and
  `H2-2SC`. Treat those as emulator or syntax-checker validation targets unless Nexus
  clearly shows a physical hardware target and a hardware execution is actually run.
- Estimated native execution duration depends on documented proxy timing assumptions.
  It is not experimentally measured execution time.
- Estimated success probability depends on documented proxy error-rate assumptions. It
  is not measured hardware fidelity.
- The configured circuit suite is intentionally small: Bell, GHZ, QFT, and a 2-qubit
  Grover circuit.
- Bell and the current Grover circuit are too small to support broad architecture
  conclusions.
- Repetitions are deterministic and do not sample compiler stochasticity unless future
  work varies compiler seeds.
- The results do not prove that one quantum architecture is universally superior.
- Optional qBraid simulator checks are platform sanity checks only and are not IBM or
  Quantinuum hardware measurements.
- The author-provided IBM Quantum job IDs documented in
  `docs/IBM_HARDWARE_VALIDATION.md` are separate from the proxy-model results. Their
  counts are stored under `results/hardware/`, but they should not be mixed into the
  proxy-model tables or used to claim a broad hardware benchmark.
