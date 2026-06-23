from __future__ import annotations

from pathlib import Path

import yaml

from quantum_compare.models import ExperimentConfig


def load_config(path: str | Path) -> ExperimentConfig:
    """Load experiment config from a YAML file."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        values = yaml.safe_load(handle) or {}
    return ExperimentConfig.from_dict(values)


def save_config(path: str | Path, config: ExperimentConfig) -> None:
    """Save an experiment config to YAML."""
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config.__dict__, handle, sort_keys=False)
