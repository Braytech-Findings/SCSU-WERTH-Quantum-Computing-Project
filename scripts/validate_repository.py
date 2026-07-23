#!/usr/bin/env python3
"""Validate public artifacts and safety guards without provider access."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data/processed/results_20260623T223649Z.csv"
REQUIRED = (
    "README.md",
    "FINAL_RESEARCH_ANSWER.md",
    "LICENSE",
    "CITATION.cff",
    "pyproject.toml",
    ".env.example",
    "docs/INSTALLATION.md",
    "docs/RUNNING_THE_PROJECT.md",
    "docs/GLOSSARY.md",
    "docs/SOCIETAL_IMPACT.md",
    "config/experiments.yaml",
)
PUBLICATION_STEMS = (
    "01_research_question_answer",
    "02_connectivity_scaling",
    "03_modeled_time_reliability",
    "04_quantinuum_emulator_validation",
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

    publication_dir = ROOT / "results/final_figures/publication"
    publication_files = [
        publication_dir / f"{stem}.{extension}"
        for stem in PUBLICATION_STEMS
        for extension in ("png", "pdf")
    ]
    missing_publication = [str(path.relative_to(ROOT)) for path in publication_files if not path.is_file()]
    if missing_publication:
        raise SystemExit("Missing publication figures: " + ", ".join(missing_publication))
    if any(path.stat().st_size < 5_000 for path in publication_files):
        raise SystemExit("One or more publication figures are unexpectedly small.")

    manifest_path = publication_dir / "publication_figures_manifest.csv"
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        publication_manifest = list(csv.DictReader(handle))
    if [row["figure"] for row in publication_manifest] != list(PUBLICATION_STEMS):
        raise SystemExit("Publication figure manifest order or identity is invalid.")
    for row in publication_manifest:
        if not (ROOT / row["source_csv"]).is_file():
            raise SystemExit(f"Publication source is missing: {row['source_csv']}")

    full_suite_path = ROOT / "results/tables/quantinuum_full_suite_raw_results.csv"
    with full_suite_path.open(newline="", encoding="utf-8") as handle:
        full_suite_rows = list(csv.DictReader(handle))
    if len(full_suite_rows) != 42:
        raise SystemExit(f"Full emulator suite has {len(full_suite_rows)} rows; expected 42.")
    if sum(int(row["shots_retrieved"]) for row in full_suite_rows) != 42_000:
        raise SystemExit("Full emulator suite does not contain 42,000 retrieved shots.")
    if any(row["evidence_type"] != "emulator" for row in full_suite_rows):
        raise SystemExit("A full-suite row is not classified as emulator evidence.")
    if any(
        row["all_zero_or_all_one_probability"]
        for row in full_suite_rows
        if row["algorithm_family"] == "QFT"
    ):
        raise SystemExit("A QFT row incorrectly uses all-zero/all-one probability.")

    public_emulator_paths = list((ROOT / "results/hardware").glob("quantinuum_full_suite_*.json"))
    uuid_pattern = re.compile(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        re.IGNORECASE,
    )
    sensitive_keys = {"access_token", "refresh_token", "api_key", "password", "credential"}
    for path in public_emulator_paths:
        text = path.read_text(encoding="utf-8")
        if uuid_pattern.search(text):
            raise SystemExit(f"Internal UUID-shaped value found in {path.relative_to(ROOT)}")
        payload = json.loads(text)
        keys = {str(key).lower() for key in _walk_keys(payload)}
        found = sorted(keys & sensitive_keys)
        if found:
            raise SystemExit(f"Sensitive key names found in {path.relative_to(ROOT)}: {found}")

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


def _walk_keys(value: object) -> Iterator[Any]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


if __name__ == "__main__":
    raise SystemExit(main())
