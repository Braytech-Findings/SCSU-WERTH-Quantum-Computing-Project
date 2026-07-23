.DEFAULT_GOAL := help
.PHONY: help setup test validate run report figures publication-figures final-check
help:
	@echo "Credit-safe targets: setup, test, validate, run, report, figures, publication-figures, final-check"
setup:
	python -m pip install -e .
test:
	python -m pytest -q
validate:
	python scripts/validate_repository.py
run:
	python -m quantum_compare.cli run --backend all --suite core
report figures:
	python -m quantum_compare.cli report
publication-figures:
	Rscript scripts/generate_publication_figures.R
final-check:
	ruff check .
	mypy src tests scripts
	pytest -q
	python scripts/validate_repository.py
	Rscript scripts/generate_publication_figures.R
