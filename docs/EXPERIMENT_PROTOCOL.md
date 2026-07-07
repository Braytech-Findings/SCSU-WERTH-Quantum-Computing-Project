# Experiment Protocol

1. Create and activate the Python virtual environment.
2. Install the package and dependencies.
3. Review `config/experiments.yaml`.
4. Run the environment check with `python -m quantum_compare.cli check`.
5. Run the full proxy-model suite with
   `python -m quantum_compare.cli run --backend all --suite core`.
6. Generate tables, figures, and the written report with
   `python -m quantum_compare.cli report`.
7. Review processed CSV and JSON outputs in `data/processed`.
8. Review generated tables in `results/tables`, figures in `results/figures`, and
   reports in `results/reports`.
9. Compare a regenerated run against the verified baseline with
   `python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv`.

The same logical circuits must be used for every architecture-proxy pipeline. The goal
is to compare logical, routed, and native-compiled circuit structure under documented
offline proxy assumptions. The separate IBM hardware validation artifacts under
`results/hardware/` are real IBM Quantum machine results, but they must not be mixed into
the proxy-model tables or described as a broad IBM-versus-Quantinuum hardware benchmark.
