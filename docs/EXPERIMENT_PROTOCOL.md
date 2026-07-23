# Experiment Protocol

> [!IMPORTANT]
> The controlled comparison, IBM physical-hardware experiments, and Quantinuum emulator validation are separate evidence streams. They must not be merged into one physical provider benchmark.

## Offline Architecture-Proxy Protocol

1. Create and activate the Python virtual environment.
2. Install the package and dependencies.
3. Review `config/experiments.yaml`.
4. Run `python -m quantum_compare.cli check`.
5. Run `python -m quantum_compare.cli run --backend all --suite core`.
6. Generate tables, figures, and reports with `python -m quantum_compare.cli report`.
7. Review processed CSV and JSON outputs in `data/processed/`.
8. Review generated tables, figures, and reports.
9. Compare a regenerated run against the verified baseline:

```bash
python scripts/compare_run_artifacts.py \
  --baseline data/processed/results_20260623T223649Z.csv
```

The same logical circuits must be used for every architecture-proxy pipeline. Proxy duration and success values are model outputs, not provider measurements.

## Provider-Evidence Protocol

For every provider job, save:

- exact backend or target name;
- physical QPU, emulator, or compile-only classification;
- circuit family and qubit count;
- compiler objective and relevant settings;
- shot count and repetitions;
- job identifier and date;
- measured counts or distributions;
- provider-reported cost or quota information;
- unavailable values as `null`, never invented zeroes.

## Current Provider Classification

- IBM `ibm_kingston`: physical QPU evidence.
- Quantinuum `H2-1LE` and `H2-Emulator`: emulator evidence.
- Quantinuum `H2-1E` and `H2-2E`: compile-only evidence for this account during the saved runs.

## Requirement for a Matched Physical Benchmark

A direct physical IBM-versus-Quantinuum comparison requires the same logical circuits, sizes, shots, repetitions, compiler objective, scoring rules, and documented calibration windows on both physical platforms. That experiment is not yet complete.
