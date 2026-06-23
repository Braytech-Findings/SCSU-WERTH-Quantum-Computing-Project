# Architecture Overview

The project is organized around a shared logical-circuit layer, a backend abstraction, and a runner that preserves the same logical circuits for each backend pipeline.

- Circuits: reusable circuit builders and validation.
- Backends: adapter classes for ideal, IBM, and Quantinuum execution.
- Experiment runner: orchestration, metrics, and result saving.
- CLI: simple commands for environment checks, device discovery, runs, and reporting.
