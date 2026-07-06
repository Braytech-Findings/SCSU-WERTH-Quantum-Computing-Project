# Ownership And Citation

This repository is written as an independent public research implementation. The code,
documentation, generated tables, and generated figures in this repository should be
treated as the author's work unless a file explicitly says otherwise.

## Before Sharing Widely

- Confirm that the author name in `CITATION.cff` is the preferred public citation name.
- Confirm that the repository URL in `CITATION.cff` points to the public GitHub
  repository: `https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project`.
- Confirm that the local `origin` remote points to the same public repository before
  pushing release updates.
- Keep `LICENSE` and `CITATION.cff` in the repository root so readers know how to reuse
  and cite the project.
- Keep generated results tied to the exact code and configuration used to make them.

## How Others Should Credit This Project

Readers who use this repository should cite the project using `CITATION.cff`. If they
reuse figures or tables, they should also mention that the results come from offline
architecture-aware proxy models, not direct IBM or Quantinuum hardware benchmarks.

## What This Project Does Not Claim

This project does not claim ownership of IBM, Quantinuum, Qiskit, TKET, qBraid, or any
provider-specific hardware platform. It uses public software interfaces and independent
proxy models to compare how the same logical circuits change under different architecture
assumptions.
