# Limitations

- This is an architecture-aware offline proxy-model study, not a direct benchmark of
  physical IBM or Quantinuum hardware.
- The IBM proxy is a line-coupled GenericBackendV2-style superconducting proxy, not a
  live calibrated backend snapshot.
- The Quantinuum proxy is an all-to-all H-series-style trapped-ion RZZ proxy, not an
  official hardware execution path or pytket Quantinuum compilation result.
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
