.DEFAULT_GOAL := help
.PHONY: help setup test validate run report figures
help:
	@echo "Credit-safe targets: setup, test, validate, run, report, figures"
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
