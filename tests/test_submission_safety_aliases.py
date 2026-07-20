from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ibm_common_safety_aliases() -> None:
    module = load_script("submit_ibm_extended_validation.py")
    preview = module.build_parser().parse_args(["--dry-run"])
    submit = module.build_parser().parse_args(["--confirm-submit"])
    assert preview.dry_run is True
    assert preview.submit_hardware is False
    assert submit.submit_hardware is True


def test_quantinuum_common_safety_aliases() -> None:
    module = load_script("submit_quantinuum_validation.py")
    preview = module.build_parser().parse_args(["--dry-run"])
    submit = module.build_parser().parse_args(["--confirm-submit"])
    assert preview.dry_run is True
    assert preview.execute_nexus is False
    assert submit.execute_nexus is True
