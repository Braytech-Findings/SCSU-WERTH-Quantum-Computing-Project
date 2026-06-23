# Experiment Protocol

1. Create and activate the Python virtual environment.
2. Install the package and dependencies.
3. Review the configuration file in config/experiments.yaml.
4. Run the environment check and list devices.
5. Execute the ideal core suite.
6. Execute the IBM and Quantinuum adapter runs in dry-run mode unless real access is configured.
7. Review the generated CSV and JSON results in data/processed.
8. Compare the logical and compiled circuit statistics as well as the fidelity metrics.

The same logical circuits should be used for every environment. The goal is to compare how the architecture-specific compilation and execution path changes the results, not to pretend that the dry-run adapters are real hardware results.
