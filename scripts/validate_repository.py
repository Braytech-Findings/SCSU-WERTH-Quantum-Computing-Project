#!/usr/bin/env python3
"""Validate public artifacts and safety guards without provider access."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data/processed/results_20260623T223649Z.csv"
REQUIRED = (
    "README.md", "LICENSE", "CITATION.cff", "pyproject.toml", ".env.example",
    "docs/INSTALLATION.md", "docs/RUNNING_THE_PROJECT.md", "docs/GLOSSARY.md",
    "docs/SOCIETAL_IMPACT.md", "config/experiments.yaml",
)


def run(*command: str) -> str:
    result = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("Missing required files: " + ", ".join(missing))

    with BASELINE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 63:
        raise SystemExit(f"Verified baseline has {len(rows)} rows; expected 63")

    tracked = set(run("git", "ls-files").splitlines())
    unsafe = sorted(path for path in tracked if Path(path).name in {".env", ".env.ibm", ".env.quantinuum"})
    if unsafe:
        raise SystemExit("Credential files are tracked: " + ", ".join(unsafe))

    for filename in ("submit_ibm_extended_validation.py", "submit_quantinuum_validation.py"):
        source = (ROOT / "scripts" / filename).read_text(encoding="utf-8")
        for flag in ("--dry-run", "--confirm-submit"):
            if flag not in source:
                raise SystemExit(f"{filename} lacks safety flag {flag}")

    print(run(sys.executable, "-m", "pytest", "-q"))
    print("Repository validation passed (no provider jobs were submitted).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
