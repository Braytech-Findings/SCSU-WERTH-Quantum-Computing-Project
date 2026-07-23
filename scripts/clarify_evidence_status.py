#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STATUS_BLOCK = """> [!IMPORTANT]\n> **Evidence status:** The IBM results in this repository are measurements from the physical `ibm_kingston` QPU. The Quantinuum results are from Nexus emulator targets (`H2-1LE` and `H2-Emulator`) plus compile-only workflow checks. This project is **not yet a matched physical IBM-versus-Quantinuum hardware benchmark**. A full matched physical Quantinuum QPU run remains future work.\n"""

SHORT_STATUS = (
    "IBM evidence: physical `ibm_kingston` QPU. Quantinuum evidence: Nexus emulator "
    "execution and compile-only checks. No matched physical IBM-versus-Quantinuum QPU "
    "benchmark has been completed."
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")


def replace(path: str, old: str, new: str, *, required: bool = True) -> None:
    text = read(path)
    if old not in text:
        if required and new not in text:
            raise RuntimeError(f"Expected text not found in {path}: {old!r}")
        return
    write(path, text.replace(old, new))


def insert_after_heading(path: str, block: str) -> None:
    text = read(path)
    if block.strip() in text:
        return
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            lines[index + 1:index + 1] = ["", block.rstrip()]
            write(path, "\n".join(lines))
            return
    raise RuntimeError(f"No top-level heading found in {path}")


# Authoritative evidence statement.
write(
    "EVIDENCE_STATUS.md",
    """# Evidence Status\n\n"
    + STATUS_BLOCK
    + """\n## What is complete\n\n"
      "- The controlled offline architecture-proxy comparison is complete for Bell, GHZ, Grover, and QFT circuits.\n"
      "- IBM physical-hardware evidence is complete for the saved `ibm_kingston` jobs, including the original 90-circuit GHZ stress study and the later 115-result validation package.\n"
      "- Quantinuum Nexus emulator validation is complete for the saved small suite on `H2-1LE` and `H2-Emulator`.\n"
      "- Quantinuum `H2-1E` and `H2-2E` compile-only checks are preserved as workflow evidence; direct execution was not authorized for the account at the time of testing.\n\n"
      "## What is not complete\n\n"
      "- No physical Quantinuum QPU result is stored in this repository.\n"
      "- The full standardized suite has not been run as a matched physical IBM-versus-Quantinuum QPU experiment.\n"
      "- Provider-level claims about which company or physical platform is better are therefore unsupported.\n\n"
      "## Correct public description\n\n"
      "This is a controlled algorithm-hardware-fit study with offline architecture proxies, real IBM Kingston hardware evidence, and Quantinuum Nexus emulator validation. It is not yet a complete matched physical multi-provider hardware benchmark.\n\n"
      "## Future completion rule\n\n"
      "A matched physical comparison requires the same logical circuits, circuit sizes, compiler objective, shot counts, repetitions, scoring rules, and documented calibration windows on both physical platforms. Until those data exist, IBM hardware and Quantinuum emulator results must remain separate evidence categories.\n""",
)

# Rewrite the public landing page so the distinction is impossible to miss.
write(
    "README.md",
    """<p align=\"center\"><img src=\"docs/assets/quantum_architecture_hero.svg\" alt=\"The same circuit branching toward superconducting and trapped-ion architecture models.\" width=\"100%\"></p>\n\n"
    "# Different Roads to the Same Circuit: Quantum Architecture Comparison\n\n"
    "[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)\n"
    "[![Tests](https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project/actions/workflows/tests.yml/badge.svg)](.github/workflows/tests.yml)\n"
    "[![License: MIT](https://img.shields.io/badge/License-MIT-2EA44F)](LICENSE)\n"
    "[![Evidence](https://img.shields.io/badge/evidence-IBM%20QPU%20%7C%20Quantinuum%20emulator%20%7C%20offline%20proxies-5C4B8A)](EVIDENCE_STATUS.md)\n\n"
    + STATUS_BLOCK
    + "\n**Navigate:** [Evidence status](EVIDENCE_STATUS.md) · [Overview](#overview) · [Results](#major-findings) · [Install](docs/INSTALLATION.md) · [Run](docs/RUNNING_THE_PROJECT.md) · [Figures](docs/FIGURE_INTERPRETATION_GUIDE.md) · [Limitations](docs/LIMITATIONS.md)\n\n"
      "## Overview\n\n"
      "This project asks how the same logical Bell, GHZ, Grover, and QFT circuits change when compiled for two different architecture models. One model uses nearest-neighbor superconducting-style connectivity. The other uses all-to-all trapped-ion-style connectivity. The comparison records routing SWAPs, two-qubit work, depth, model-estimated duration, and model-estimated success.\n\n"
      "The repository also preserves provider results as separate evidence:\n\n"
      "- **IBM:** physical `ibm_kingston` QPU measurements.\n"
      "- **Quantinuum:** Nexus emulator measurements from `H2-1LE` and `H2-Emulator`, plus compile-only checks.\n\n"
      "The project title is retained because the scientific question concerns algorithm-hardware fit. The evidence labels prevent the title from being mistaken for a completed physical IBM-versus-Quantinuum benchmark.\n\n"
      "## Evidence Structure\n\n"
      "| Phase | Evidence | Status | What it supports |\n"
      "| --- | --- | --- | --- |\n"
      "| I | Controlled offline architecture proxies | Complete | How topology and native-gate assumptions change compiled circuit cost |\n"
      "| II | IBM Kingston physical QPU | Complete for saved jobs | Real IBM hardware behavior for the submitted workloads |\n"
      "| III | Quantinuum Nexus emulator | Complete for the saved small suite | Provider workflow validation and emulator output for Bell-2, GHZ-3, and Grover-2 |\n"
      "| IV | Matched physical Quantinuum QPU comparison | Pending | Required before any direct physical IBM-versus-Quantinuum ranking |\n\n"
      "See [EVIDENCE_STATUS.md](EVIDENCE_STATUS.md) for the authoritative wording.\n\n"
      "## Research Question\n\n"
      "How do the same logical circuits change after topology routing and native-basis decomposition for superconducting-style and trapped-ion-style architecture models, and what parts of that prediction are supported by the available provider results?\n\n"
      "## Architectures and Provider Evidence\n\n"
      "- **IBM proxy:** line-coupled Qiskit `GenericBackendV2`-style model using `rz`, `sx`, `x`, and `cx`.\n"
      "- **Quantinuum proxy:** all-to-all H-series-style model using `rz`, `rx`, and Qiskit `rzz` as an offline ZZ-type entangling proxy.\n"
      "- **IBM provider evidence:** two saved physical `ibm_kingston` jobs.\n"
      "- **Quantinuum provider evidence:** two saved Nexus emulator executions and two compile-only checks.\n\n"
      "Proxy timing and error values are study assumptions. They are not live provider calibration data.\n\n"
      "## Circuit Families\n\n"
      "- Bell state: 2 qubits.\n"
      "- GHZ states: 3, 5, and 7 qubits.\n"
      "- QFT: 3 and 5 qubits.\n"
      "- Grover search: 2 qubits.\n\n"
      "## Install and Run the Offline Study\n\n"
      "```bash\n"
      "python -m venv .venv\n"
      "source .venv/bin/activate\n"
      "python -m pip install --upgrade pip\n"
      "python -m pip install -e .\n"
      "python scripts/validate_repository.py\n"
      "python -m quantum_compare.cli run --backend all --suite core\n"
      "python -m quantum_compare.cli report\n"
      "pytest\n"
      "```\n\n"
      "These commands do not submit provider jobs. Provider execution requires separate credentials, explicit confirmation, and quota review.\n\n"
      "## Provider Validation Status\n\n"
      "### IBM physical hardware\n\n"
      "- Original GHZ stress job: `d8up2d1ropqc738b44pg`, 90 circuit results, 4,096 shots each.\n"
      "- Expanded validation job: `d95vhvd2su3c739gc080`, 115 results, 4,096 shots each.\n"
      "- Documentation: `docs/IBM_HARDWARE_VALIDATION.md`.\n\n"
      "### Quantinuum Nexus emulator\n\n"
      "- `H2-1LE`: Bell-2, GHZ-3, and Grover-2, 100 shots each.\n"
      "- `H2-Emulator`: Bell-2, GHZ-3, and Grover-2, 100 shots each.\n"
      "- `H2-1E` and `H2-2E`: compilation succeeded; execution was rejected for account access.\n"
      "- Documentation: `docs/QUANTINUUM_HARDWARE_VALIDATION.md`.\n\n"
      "These Quantinuum results are real provider emulator outputs, not physical trapped-ion QPU measurements.\n\n"
      "## Major Findings\n\n"
      "The controlled proxy comparison shows an algorithm-dependent pattern. Bell and the current two-qubit Grover circuit are too small to expose large routing differences. GHZ and QFT require substantially more routing and two-qubit work under the nearest-neighbor model than under the all-to-all model.\n\n"
      "Under the declared proxy assumptions, the all-to-all trapped-ion-style model has lower estimated duration and higher estimated success for the tested larger GHZ and QFT circuits. This is a model result, not measured Quantinuum hardware superiority.\n\n"
      "The physical IBM GHZ stress experiment supports the mechanism that additional compiled two-qubit work makes a fragile entangled distribution harder to preserve. The Quantinuum emulator results show that the small validation circuits compiled and executed through Nexus. Together, these evidence streams support the study workflow but do not complete a matched physical provider comparison.\n\n"
      "## Figures and Reports\n\n"
      "- Curated figures: `results/final_figures/`\n"
      "- Expanded R figures: `results/final_figures/r_visualizations/`\n"
      "- Summary report: `results/reports/summary_report.md`\n"
      "- Verified proxy values: `results/reports/final_results_written_summary.md`\n"
      "- Figure guide: `docs/FIGURE_INTERPRETATION_GUIDE.md`\n\n"
      "All provider figures must retain their evidence label: IBM physical hardware or Quantinuum Nexus emulator.\n\n"
      "## Repository Structure\n\n"
      "- `src/quantum_compare/`: circuit construction, architecture models, metrics, and reports.\n"
      "- `data/processed/`: authoritative proxy-model outputs.\n"
      "- `results/hardware/`: sanitized IBM physical-hardware and Quantinuum emulator artifacts.\n"
      "- `results/tables/`, `results/figures/`, `results/reports/`: generated analysis outputs.\n"
      "- `docs/`: methods, evidence notes, limitations, and beginner explanations.\n"
      "- `notebooks/`: qBraid validation workflow.\n\n"
      "## Limitations\n\n"
      "- The main architecture comparison is based on controlled offline proxy models.\n"
      "- The IBM evidence is physical hardware, but it covers specific saved workloads on one backend.\n"
      "- The Quantinuum evidence is emulator-only; no physical Quantinuum QPU result is stored.\n"
      "- The physical IBM and Quantinuum evidence is not matched by circuit suite, shots, repetitions, compiler settings, or calibration window.\n"
      "- The project therefore cannot rank IBM against Quantinuum as physical providers.\n"
      "- Grover has only one supported size.\n\n"
      "## Confidentiality\n\n"
      "This public repository is a sanitized independent research implementation. It excludes credentials, confidential company information, and nondisclosure-agreement materials.\n""",
)

# Public overview: retain the project name but state the evidence categories precisely.
write(
    "PROJECT_OVERVIEW.md",
    """# Project Overview\n\n"
    + STATUS_BLOCK
    + "\n## What Was Built\n\n"
      "This project contains a reproducible comparison of the same logical quantum circuits across two controlled architecture proxy models, plus separate provider evidence. The proxy study compares a nearest-neighbor superconducting-style model with an all-to-all trapped-ion-style model. The provider evidence contains physical IBM Kingston QPU measurements and Quantinuum Nexus emulator measurements.\n\n"
      "## Evidence Categories\n\n"
      "1. **Offline proxy comparison:** Bell, GHZ, Grover, and QFT compilation and model metrics.\n"
      "2. **IBM physical hardware:** saved results from `ibm_kingston`.\n"
      "3. **Quantinuum emulator:** saved results from `H2-1LE` and `H2-Emulator`, plus compile-only checks for `H2-1E` and `H2-2E`.\n"
      "4. **Pending future work:** a matched execution of the full standardized suite on a physical Quantinuum QPU.\n\n"
      "## How the Comparison Works\n\n"
      "Every configured circuit begins as the same logical recipe. The workflow measures logical depth, routed depth, routing SWAPs, native-compiled depth, native two-qubit work, model-estimated duration, and model-estimated success. The provider artifacts are stored separately and are never substituted for the proxy rows.\n\n"
      "## What the Results Suggest\n\n"
      "For the tested GHZ and QFT circuits, nearest-neighbor connectivity creates substantial routing overhead. The all-to-all model avoids routing SWAPs for those circuits under the selected assumptions. The IBM physical experiment separately shows that extra compiled two-qubit work is associated with lower GHZ distribution fidelity. The Quantinuum emulator runs confirm that the small validation suite can be compiled and executed through Nexus.\n\n"
      "## What the Results Do Not Prove\n\n"
      "The project does not yet compare physical IBM and physical Quantinuum QPUs under matched conditions. The Quantinuum results are emulator outputs, not physical trapped-ion hardware measurements. The evidence therefore does not prove that one provider, architecture, or qubit technology is universally superior.\n\n"
      "## Independent Student Contribution\n\n"
      "The student independently implemented the circuit suite, architecture-aware compilation, metrics, validation tables, figures, reports, tests, provider-result packaging, and qBraid validation workflow. The public repository is sanitized and excludes credentials and protected materials.\n""",
)

# Add the authoritative block to status and reports.
for public_file in [
    "FINAL_STATUS.md",
    "docs/MANUSCRIPT_REPOSITORY_ALIGNMENT.md",
    "docs/QUANTINUUM_HARDWARE_VALIDATION.md",
    "docs/LIMITATIONS.md",
    "docs/RUNNING_THE_PROJECT.md",
    "docs/EXPERIMENT_PROTOCOL.md",
    "results/reports/summary_report.md",
    "results/reports/final_results_written_summary.md",
    "results/final_figures/README.md",
    "docs/FIGURE_INTERPRETATION_GUIDE.md",
    "reports/R_VISUAL_ANALYSIS.md",
    "CODEX_UPGRADE_REPORT.md",
]:
    if (ROOT / public_file).exists():
        insert_after_heading(public_file, STATUS_BLOCK)

# Rename visible Quantinuum documentation without breaking existing file paths.
replace(
    "docs/QUANTINUUM_HARDWARE_VALIDATION.md",
    "# Quantinuum Hardware Validation Note",
    "# Quantinuum Nexus Emulator Validation Note",
)
replace(
    "docs/QUANTINUUM_HARDWARE_VALIDATION.md",
    "This page records the safe Quantinuum Nexus workflow for this project. It is the\nQuantinuum-side companion to `docs/IBM_HARDWARE_VALIDATION.md`.",
    "This page records the safe Quantinuum Nexus emulator and compile-only workflow for this project. It complements `docs/IBM_HARDWARE_VALIDATION.md`, but it is not a physical-hardware counterpart to the IBM results.",
)

# Clarify limitations and execution table wording.
replace(
    "docs/LIMITATIONS.md",
    "- The Quantinuum Nexus targets reported so far are `H2-1E`, `H2-2E`, `H2-1SC`, and\n  `H2-2SC`. Treat those as emulator or syntax-checker validation targets unless Nexus\n  clearly shows a physical hardware target and a hardware execution is actually run.",
    "- The completed Quantinuum executions in this repository used the Nexus-hosted `H2-1LE` and `H2-Emulator` emulator targets. `H2-1E` and `H2-2E` accepted compilation but did not authorize execution for the account. No physical Quantinuum QPU result is stored."
)
replace(
    "docs/RUNNING_THE_PROJECT.md",
    "| Nexus emulator/hardware | Execute on selected H-Series target | **HQCs or quota may apply** | Authorized Nexus project | Add `--estimate-cost --confirm-submit --i-understand-this-may-use-hqcs-or-quota --wait` only after reviewing the dry run | Sanitized submission/result JSON in `results/hardware/` |",
    "| Nexus emulator or future hardware target | Execute on a selected Nexus target; current saved evidence is emulator-only | **HQCs or quota may apply** | Authorized Nexus project | Add `--estimate-cost --confirm-submit --i-understand-this-may-use-hqcs-or-quota --wait` only after reviewing the dry run and target type | Sanitized submission/result JSON in `results/hardware/`; label emulator and physical QPU results separately |",
)

# Citation metadata keeps the project title but makes the evidence classification explicit.
replace(
    "CITATION.cff",
    'abstract: "An independent research implementation comparing superconducting and trapped-ion quantum computing architectures through compilation behavior, offline proxy models, IBM hardware validation, and Quantinuum Nexus emulator validation."',
    'abstract: "A controlled quantum algorithm-hardware-fit study using offline superconducting-style and trapped-ion-style proxy models, physical IBM Kingston QPU evidence, and Quantinuum Nexus emulator validation. It is not yet a matched physical IBM-versus-Quantinuum QPU benchmark."',
)

# The matched future Quantinuum suite must include every configured proxy-study size.
replace(
    "scripts/submit_quantinuum_validation.py",
    "            build_ghz_state(5),\n            build_qft(3),",
    "            build_ghz_state(5),\n            build_ghz_state(7),\n            build_qft(3),",
)

# Make graph language explicitly emulator-only where visible.
for path in [
    "scripts/plot_quantinuum_validation.py",
    "scripts/generate_final_figures.R",
    "analysis/generate_final_figures_r.R",
    "src/quantum_compare/visualization.py",
]:
    if not (ROOT / path).exists():
        continue
    text = read(path)
    text = text.replace("Quantinuum Nexus validation", "Quantinuum Nexus emulator validation")
    text = text.replace("Quantinuum Validation", "Quantinuum Emulator Validation")
    write(path, text)

# Add a regression test for the complete matched dry-run plan.
write(
    "tests/test_quantinuum_matched_suite.py",
    """from __future__ import annotations\n\n"
    "import json\n"
    "import subprocess\n"
    "import sys\n"
    "from pathlib import Path\n\n\n"
    "def test_quantinuum_matched_plan_contains_full_standardized_suite(tmp_path: Path) -> None:\n"
    "    result = subprocess.run(\n"
    "        [\n"
    "            sys.executable,\n"
    "            \"scripts/submit_quantinuum_validation.py\",\n"
    "            \"--target\",\n"
    "            \"H2-Emulator\",\n"
    "            \"--suite\",\n"
    "            \"matched\",\n"
    "            \"--shots\",\n"
    "            \"100\",\n"
    "            \"--output-dir\",\n"
    "            str(tmp_path),\n"
    "        ],\n"
    "        check=False,\n"
    "        capture_output=True,\n"
    "        text=True,\n"
    "    )\n\n"
    "    assert result.returncode == 0, result.stderr\n"
    "    plan = json.loads((tmp_path / \"quantinuum_validation_plan.json\").read_text(encoding=\"utf-8\"))\n"
    "    assert plan[\"circuit_count\"] == 7\n"
    "    assert plan[\"total_requested_shots\"] == 700\n"
    "    assert [circuit[\"qubits\"] for circuit in plan[\"circuits\"]] == [2, 3, 5, 7, 3, 5, 2]\n"
    "    assert plan[\"execute_requested\"] is False\n"
    "    assert \"Dry run only\" in result.stdout\n""",
)

# Remove the temporary migration files from the final branch commit.
for temporary in [
    ROOT / "scripts/clarify_evidence_status.py",
    ROOT / ".github/workflows/clarify-evidence-status.yml",
]:
    if temporary.exists():
        temporary.unlink()

print(SHORT_STATUS)
