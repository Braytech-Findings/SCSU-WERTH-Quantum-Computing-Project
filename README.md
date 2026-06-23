# Comparing Superconducting and Trapped-Ion Quantum Computing Architectures Using qBraid

## Purpose
This repository is a one-week coding sprint project for a Southern Connecticut nanotechnology and quantum internship. It compares how the same logical quantum circuits behave when they are executed in three settings:

1. An ideal simulator that serves as a mathematical reference.
2. An IBM-style superconducting backend adapter.
3. A Quantinuum-style trapped-ion backend adapter.

The project uses Qiskit as a shared logical-circuit representation and keeps the code scientifically accurate while remaining understandable to an advanced high-school student.

## Research question
How do the same logical circuits change when they are compiled and executed for superconducting versus trapped-ion architectures?

## Hypothesis
The same logical circuit may require different compiled forms and may show different output distributions when run on superconducting versus trapped-ion hardware or emulators, because the two technologies have different native gate sets, connectivity, and noise behavior.

## What are these qubit technologies?
- Superconducting qubits are microscopic circuits that behave quantum mechanically at very low temperatures. They are widely used in IBM-style devices and often use microwave-based control.
- Trapped-ion qubits use ions confined and controlled by electromagnetic fields. They are often associated with long coherence times and all-to-all connectivity in software, though the exact hardware layout depends on the system.

## Why an ideal control is required
The ideal simulator gives a baseline probability distribution. That baseline is the reference for judging how compilation and execution change the circuit in the other environments.

## Installation
```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Authentication setup
This repository does not require real credentials for the default ideal workflow. If you later want to use IBM or Quantinuum access through qBraid, create a local `.env` file from the example and fill in the provider-specific names only if you have real access.

## Checking available devices
```bash
python -m quantum_compare.cli devices
```

## Running the simulations
```bash
python -m quantum_compare.cli check
python -m quantum_compare.cli run --backend ideal --suite core
python -m quantum_compare.cli run --backend ibm --suite core
python -m quantum_compare.cli run --backend quantinuum --suite core
python -m quantum_compare.cli run --backend all --suite core
```

## Generating a report
```bash
python -m quantum_compare.cli report
```

## Interpreting the outputs
- The ideal run gives the clean mathematical behavior.
- IBM and Quantinuum adapters currently run in dry-run mode unless you configure real access.
- The processed CSV file is the main place to compare the logical and compiled circuit statistics.

## Running tests
```bash
pytest -q
ruff check .
mypy src
```

## Known limitations
- No paid hardware jobs are submitted in this repository.
- IBM and Quantinuum provider access requires credentials and supported permissions that are not assumed here.
- The adapters are intentionally explicit about dry-run behavior so they do not misrepresent a simulator as a real hardware run.
