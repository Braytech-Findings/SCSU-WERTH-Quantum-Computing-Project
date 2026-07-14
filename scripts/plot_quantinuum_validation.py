#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path

_CACHE_ROOT = Path(tempfile.gettempdir()) / "quantum-architecture-comparison-cache"
_MPL_CACHE = _CACHE_ROOT / "matplotlib"
_XDG_CACHE = _CACHE_ROOT / "xdg"
_MPL_CACHE.mkdir(parents=True, exist_ok=True)
_XDG_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
os.environ.setdefault("XDG_CACHE_HOME", str(_XDG_CACHE))

# Matplotlib reads cache locations during import, so cache env vars must be set first.
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


SUMMARY_FILES = [
    Path("results/hardware/quantinuum_job_H2-1LE_20260714T173914Z_summary.csv"),
    Path("results/hardware/quantinuum_job_H2-Emulator_20260714T175518Z_summary.csv"),
]
CIRCUIT_LABELS = {
    0: "Bell",
    1: "GHZ-3",
    2: "Grover-2",
}
OUTPUT_DIR = Path("results/figures")
TABLE_DIR = Path("results/tables")


def main() -> int:
    rows = load_rows(SUMMARY_FILES)
    if not rows:
        print("No Quantinuum validation summary rows found.")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table_path = TABLE_DIR / "quantinuum_validation_plot_rows.csv"
    figure_path = OUTPUT_DIR / "quantinuum_validation_expected_state_probability.png"
    write_plot_table(rows, table_path)
    plot_rows(rows, figure_path)
    print(f"Wrote Quantinuum validation plot table to {table_path}")
    print(f"Wrote Quantinuum validation figure to {figure_path}")
    return 0


def load_rows(paths: list[Path]) -> list[dict[str, str | float | int]]:
    rows: list[dict[str, str | float | int]] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                result_index = int(row["result_index"])
                rows.append(
                    {
                        "target": row["target"],
                        "circuit": CIRCUIT_LABELS.get(result_index, f"Result {result_index}"),
                        "result_index": result_index,
                        "shots": int(row["shots"]),
                        "all_zero_or_all_one_probability": float(
                            row["all_zero_or_all_one_probability"]
                        ),
                        "distinct_outcomes": int(row["distinct_outcomes"]),
                    }
                )
    return rows


def write_plot_table(rows: list[dict[str, str | float | int]], path: Path) -> None:
    fieldnames = [
        "target",
        "circuit",
        "result_index",
        "shots",
        "all_zero_or_all_one_probability",
        "distinct_outcomes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, str | float | int]], path: Path) -> None:
    circuits = ["Bell", "GHZ-3", "Grover-2"]
    targets = ["H2-1LE", "H2-Emulator"]
    values = {
        (str(row["target"]), str(row["circuit"])): float(row["all_zero_or_all_one_probability"])
        for row in rows
    }

    x_positions = range(len(circuits))
    bar_width = 0.34
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    colors = {"H2-1LE": "#2f6f9f", "H2-Emulator": "#d67b32"}

    for offset_index, target in enumerate(targets):
        offset = (offset_index - 0.5) * bar_width
        heights = [values.get((target, circuit), 0.0) for circuit in circuits]
        bars = ax.bar(
            [position + offset for position in x_positions],
            heights,
            width=bar_width,
            label=target,
            color=colors[target],
        )
        for bar, value in zip(bars, heights, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                min(value + 0.015, 1.03),
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_title("Quantinuum Nexus Validation: Expected-State Probability")
    ax.set_ylabel("All-zero/all-one probability")
    ax.set_xlabel("Circuit")
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(circuits)
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.6)
    ax.legend(title="Nexus target")
    ax.text(
        0.5,
        -0.22,
        "100 shots per circuit. Results are Nexus emulator outputs, not physical H2 hardware measurements.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
