# Contributing

Create a focused branch, keep logical circuits identical across architecture pipelines, add tests for code changes, and run `python scripts/validate_repository.py`, `ruff check .`, and `mypy src tests` before opening a pull request.

New evidence must state whether it is an offline model, simulator, emulator, or physical-hardware result. Record input circuits, package versions, backend/target, shots, date, and sanitized provenance. Never commit credentials or mix provider outputs into proxy tables. Provider jobs must not be submitted as part of a contribution without explicit authorization and a reviewed dry run.
