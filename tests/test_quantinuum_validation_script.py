from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_quantinuum_validation_script_writes_dry_run_plan(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/submit_quantinuum_validation.py",
            "--target",
            "H2-1E",
            "--suite",
            "small",
            "--shots",
            "100",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    plan_path = tmp_path / "quantinuum_validation_plan.json"
    assert plan_path.exists()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["provider"] == "quantinuum"
    assert plan["target"] == "H2-1E"
    assert plan["circuit_count"] == 3
    assert plan["total_requested_shots"] == 300
    assert "Dry run only" in result.stdout
