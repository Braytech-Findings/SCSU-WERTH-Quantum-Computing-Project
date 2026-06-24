# Architecture Overview

The project is organized around one shared logical-circuit layer and two
architecture-aware offline proxy compilation models.

- Circuits: reusable Qiskit logical circuit builders for Bell, GHZ, QFT, and Grover.
- Architecture models: IBM proxy and Quantinuum proxy compilation, routing, native-basis
  conversion, proxy duration estimates, proxy success estimates, and equivalence checks.
- Backends: an ideal simulator plus dry-run provider adapters that do not fabricate
  hardware availability.
- Experiment runner: orchestration, result rows, processed CSV/JSON files, tables,
  figures, and reports.
- CLI: commands for environment checks, experiment runs, and report generation.

The IBM proxy represents line-coupled superconducting-proxy compilation behavior. The
Quantinuum proxy represents all-to-all trapped-ion-proxy compilation behavior using a
Qiskit RZZ entangling proxy. Neither proxy is a live calibrated hardware backend.
