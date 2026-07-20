# Reproduce Everything

This guide recreates every **public, offline, credit-safe** result that can be regenerated from the repository. It also explains which saved provider artifacts are historical evidence and therefore cannot be recreated without separate accounts, permissions, credits, and an explicit decision to submit jobs.

> [!IMPORTANT]
> The default reproduction workflow never contacts IBM Quantum or Quantinuum Nexus. It does not use API keys, submit jobs, or spend credits.

## What a complete public reproduction creates

| Stage | Command | Main outputs |
|---|---|---|
| Environment check | `python -m quantum_compare.cli check` | Import and CLI confirmation |
| Automated validation | `pytest -q`, `ruff check .`, `mypy src tests` | Test, lint, and type-check results |
| Controlled experiment | `python -m quantum_compare.cli run --backend all --suite core` | Timestamped CSV/JSON files under `data/processed/` |
| Python report package | `python -m quantum_compare.cli report` | Tables, figures, Markdown, and JSON under `results/` |
| Baseline comparison | `python scripts/compare_run_artifacts.py ...` | Comparison with the verified 2026-06-23 baseline |
| Optional R package | `Rscript analysis/generate_final_figures_r.R` | Expanded figures under `results/final_figures/r_visualizations/` |

## Fastest route: one command

From the repository root, create and activate a Python 3.11+ environment, then run:

```bash
python scripts/reproduce_everything.py --install
```

To preview every command without changing anything:

```bash
python scripts/reproduce_everything.py --dry-run --install --include-r
```

To include the optional R visualization package:

```bash
python scripts/reproduce_everything.py --install --include-r
```

The runner stops immediately when a required step fails and prints the exact command that failed.

## Fresh-clone instructions

### macOS or Linux

```bash
git clone https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project.git
cd SCSU-WERTH-Quantum-Computing-Project
python3.11 -m venv .venv
source .venv/bin/activate
python scripts/reproduce_everything.py --install
```

### Windows PowerShell

```powershell
git clone https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project.git
Set-Location SCSU-WERTH-Quantum-Computing-Project
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python scripts/reproduce_everything.py --install
```

## Manual route

Use this route when you want to see each stage separately.

### 1. Install the package

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

### 2. Check the environment

```bash
python -m quantum_compare.cli check
```

Expected message:

```text
Environment check passed.
```

### 3. Validate the code

```bash
pytest -q
ruff check .
mypy src tests
```

These checks do not contact a quantum provider.

### 4. Regenerate the controlled proxy study

```bash
python -m quantum_compare.cli run --backend all --suite core
```

This runs the same logical Bell, GHZ, QFT, and Grover circuit families through:

1. the ideal baseline;
2. the IBM-style superconducting proxy; and
3. the Quantinuum-style trapped-ion proxy.

New processed files are written under `data/processed/`. The timestamp identifies the new run; it does not replace the verified public baseline.

### 5. Regenerate Python figures and reports

```bash
python -m quantum_compare.cli report
```

Primary locations:

```text
results/figures/     Generated Python figures
results/tables/      Generated analysis tables
results/reports/     Generated Markdown and JSON summaries
```

### 6. Compare against the verified baseline

```bash
python scripts/compare_run_artifacts.py \
  --baseline data/processed/results_20260623T223649Z.csv
```

The comparison checks the regenerated scientific fields against the stored baseline while allowing harmless differences such as timestamps or dictionary ordering where documented.

### 7. Regenerate the optional R figures

Install R and the packages listed in the main README, then run:

```bash
Rscript analysis/generate_final_figures_r.R
```

Outputs are written to:

```text
results/final_figures/r_visualizations/
```

## Use the command-line interface directly

| Goal | Command |
|---|---|
| Check installation | `quantum-compare check` |
| List available adapters | `quantum-compare devices` |
| Run all controlled backends | `quantum-compare run --backend all --suite core` |
| Run only the ideal baseline | `quantum-compare run --backend ideal --suite core` |
| Run only the IBM proxy | `quantum-compare run --backend ibm --suite core` |
| Run only the Quantinuum proxy | `quantum-compare run --backend quantinuum --suite core` |
| Rebuild figures and reports | `quantum-compare report` |
| Export a circuit without submitting | `quantum-compare hardware-guide --provider all --export-family bell --export-size 2` |

`python -m quantum_compare.cli ...` remains equivalent when the installed command is unavailable.

## What the public workflow does not recreate

The following files are saved evidence records from earlier provider activity:

- IBM Kingston physical-hardware job artifacts under `results/hardware/`;
- Quantinuum Nexus emulator result artifacts under `results/hardware/`; and
- syntax-checker or provider submission metadata under `results/hardware/`.

A new provider run would be a **new experiment**, not a deterministic recreation of the old hardware conditions. Queue state, calibrations, compiler versions, access permissions, and provider configuration can change.

To prepare a provider test without submitting anything:

```bash
python -m quantum_compare.cli hardware-guide \
  --provider all \
  --export-family bell \
  --export-size 2
```

Read these documents before any provider work:

- [IBM hardware validation](IBM_HARDWARE_VALIDATION.md)
- [Quantinuum Nexus validation](QUANTINUUM_HARDWARE_VALIDATION.md)
- [Limitations](LIMITATIONS.md)

## qBraid reproduction

The qBraid notebook and validation notes are under `notebooks/` and [QBRAID_VALIDATION.md](QBRAID_VALIDATION.md). The same core sequence applies:

```bash
python -m pip install -e .
pytest -q
python -m quantum_compare.cli run --backend all --suite core
python -m quantum_compare.cli report
python scripts/compare_run_artifacts.py \
  --baseline data/processed/results_20260623T223649Z.csv
```

## Reproduction checklist

A successful public reproduction should confirm all of the following:

- [ ] Python 3.11 or newer is active.
- [ ] The environment check passes.
- [ ] Tests, Ruff, and mypy pass.
- [ ] A new timestamped processed run is created.
- [ ] Figures and reports are regenerated.
- [ ] The new run agrees with the verified baseline under the documented comparison rules.
- [ ] Proxy, emulator, and physical-hardware evidence remain separately labeled.
- [ ] No credentials or provider tokens are committed.

## Common problems

### `ModuleNotFoundError: quantum_compare`

Run:

```bash
python -m pip install -e .
```

### Python version is too old

Create a Python 3.11 or newer environment and rerun the installation.

### `Rscript` is not found

R is optional. Rerun without `--include-r`, or install R and the required packages first.

### Baseline file is missing

Confirm that this file exists:

```text
data/processed/results_20260623T223649Z.csv
```

### A regenerated timestamp is different

That is expected. Compare scientific fields using `scripts/compare_run_artifacts.py`; do not compare filenames alone.

## Scientific interpretation rule

Reproducing the code confirms that the public workflow can regenerate the stored proxy-model analysis. It does **not** prove that one hardware architecture is universally better, and it does not transform emulator or proxy output into physical-QPU evidence.
