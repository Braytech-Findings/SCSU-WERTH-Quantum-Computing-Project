# Code Walkthrough

This page explains the main code in everyday language. It is not a full programming
lesson. It is a map for readers who want to understand what the project is doing.

## The Short Story

1. Build the same starting quantum circuits.
2. Run an ideal simulator to get the clean reference answer.
3. Prepare the same circuits for an IBM-style proxy.
4. Prepare the same circuits for a Quantinuum-style proxy.
5. Save the numbers, tables, figures, and reports.
6. Keep real hardware testing separate unless someone chooses to run it on purpose.

## The Main Code Files

| File | What it does |
| --- | --- |
| `src/quantum_compare/circuits.py` | Builds the Bell, GHZ, QFT, and Grover starting circuits. |
| `src/quantum_compare/architecture.py` | Rewrites circuits for each architecture proxy and checks that the rewrite did not change the intended circuit behavior. |
| `src/quantum_compare/experiment.py` | Runs the configured experiment and writes the raw results. |
| `src/quantum_compare/metrics.py` | Turns counts into probabilities and compares probability distributions. |
| `src/quantum_compare/visualization.py` | Turns saved results into tables, figures, and the summary report. |
| `src/quantum_compare/hardware.py` | Exports a small circuit and prints safe real-hardware preparation notes without submitting jobs. |
| `src/quantum_compare/cli.py` | Gives the project command-line commands such as `check`, `run`, `report`, and `hardware-guide`. |

## How A Circuit Moves Through The Project

The project starts in `circuits.py`. For example, the Bell circuit creates two qubits,
connects them, and measures them. That same starting circuit is used for every backend
path.

Then `experiment.py` sends the circuit through three paths:

- `ideal`: a clean simulator reference.
- `ibm`: an IBM-style offline proxy.
- `quantinuum`: a Quantinuum-style offline proxy.

The proxy paths use `architecture.py`. That file does three big things:

- Routing: add movement when qubits need to be neighbors.
- Native compilation: rewrite the circuit into the gate set for that proxy.
- Equivalence check: confirm the rewritten circuit still represents the same quantum
  operation before measurement.

Finally, `visualization.py` reads the saved results and makes the tables, figures, and
Markdown report.

## The Most Important Safety Rules

- The same logical circuit must be used for every comparison path.
- Real provider results must not be mixed with offline proxy rows.
- If a value is not available, write `null`, not zero.
- Do not submit paid hardware jobs unless the user clearly approves it.
- Do not claim live IBM or Quantinuum hardware performance unless a real provider job
  was actually run and recorded.

## Reading The Results

The most useful first files are:

- `results/reports/summary_report.md`
- `results/tables/architecture_validation_table.csv`
- `results/figures/key_metric_summary.png`

The report gives the main explanation. The table gives the detailed numbers. The figure
shows the big picture quickly.
