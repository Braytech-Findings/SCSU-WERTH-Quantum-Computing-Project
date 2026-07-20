.DEFAULT_GOAL := help
.PHONY: help install check test run report reproduce reproduce-r baseline export-bell

help:
	@echo "Different Roads to the Same Circuit — safe public commands"
	@echo ""
	@echo "  make install       Install the project in the active Python environment"
	@echo "  make check         Confirm that the command-line interface imports"
	@echo "  make test          Run tests, Ruff, and mypy"
	@echo "  make run           Regenerate the controlled offline experiment suite"
	@echo "  make report        Regenerate Python figures and reports"
	@echo "  make baseline      Compare the newest run with the verified baseline"
	@echo "  make reproduce     Run the complete public offline workflow"
	@echo "  make reproduce-r   Run the public workflow and optional R figures"
	@echo "  make export-bell   Export a Bell circuit without submitting a provider job"
	@echo ""
	@echo "No target submits IBM or Quantinuum jobs."

install:
	python -m pip install --upgrade pip
	python -m pip install -e .

check:
	python -m quantum_compare.cli check

test:
	pytest -q
	ruff check .
	mypy src tests

run:
	python -m quantum_compare.cli run --backend all --suite core

report:
	python -m quantum_compare.cli report

baseline:
	python scripts/compare_run_artifacts.py --baseline data/processed/results_20260623T223649Z.csv

reproduce:
	python scripts/reproduce_everything.py

reproduce-r:
	python scripts/reproduce_everything.py --include-r

export-bell:
	python -m quantum_compare.cli hardware-guide --provider all --export-family bell --export-size 2
