from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FormatStrFormatter
import numpy as np
import pandas as pd

ARCHITECTURE_LABELS = {
    "ibm": "IBM proxy",
    "quantinuum": "Quantinuum proxy",
}
ARCHITECTURE_FULL_NAMES = {
    "ibm": "IBM GenericBackendV2 line proxy",
    "quantinuum": "Quantinuum H-series RZZ proxy",
}
ARCHITECTURE_ORDER = ["ibm", "quantinuum"]
SENSITIVITY_SCENARIOS = {
    "optimistic": {"duration_multiplier": 0.75, "error_multiplier": 0.5},
    "baseline": {"duration_multiplier": 1.0, "error_multiplier": 1.0},
    "pessimistic": {"duration_multiplier": 1.25, "error_multiplier": 2.0},
}


def _prepare_plot_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()
    if "is_baseline" in cleaned.columns:
        cleaned = cleaned[~cleaned["is_baseline"].astype(bool)]
    cleaned = cleaned[cleaned["provider"].isin(ARCHITECTURE_ORDER)]
    if "error_message" in cleaned.columns:
        cleaned = cleaned[cleaned["error_message"].isna()]
    return cleaned


def generate_visualizations(results_path: str | Path, output_dir: str | Path) -> list[Path]:
    """Create statistically grouped plots, tables, and report artifacts."""
    results_path = Path(results_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    dataframe = pd.read_csv(results_path)
    created_files: list[Path] = []
    if dataframe.empty:
        return created_files

    cleaned = _prepare_plot_frame(dataframe)
    if cleaned.empty:
        return created_files

    tables_dir = output_dir.parent / "tables"
    reports_dir = output_dir.parent / "reports"
    tables_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    table_files = _write_tables(cleaned, tables_dir)
    created_files.extend(table_files)
    created_files.extend(_plot_key_metric_summary(cleaned, output_dir))
    created_files.extend(_plot_main_scaling(cleaned, output_dir))
    created_files.extend(_plot_logical_baseline(cleaned, output_dir))
    report_path = reports_dir / "summary_report.md"
    _write_report(cleaned, report_path, results_path, tables_dir, output_dir)
    created_files.append(report_path)
    return created_files


def _write_tables(cleaned: pd.DataFrame, tables_dir: Path) -> list[Path]:
    validation = cleaned.copy()
    validation["native_depth_over_logical_depth"] = (
        validation["native_compiled_depth"] / validation["logical_depth"]
    )
    validation["additional_native_entangling_gates"] = (
        validation["native_entangling_gate_count"] - validation["logical_two_qubit_gate_count"]
    )
    validation["estimated_native_execution_duration_us"] = (
        validation["estimated_native_execution_duration_ns"] / 1000.0
    )

    files: list[Path] = []
    validation_path = tables_dir / "architecture_validation_table.csv"
    validation[_validation_columns()].sort_values(
        ["circuit_family", "qubit_count", "provider", "repetition"]
    ).to_csv(validation_path, index=False)
    files.append(validation_path)

    grouped_stats_path = tables_dir / "qubit_grouped_statistics.csv"
    _grouped_stats(validation).to_csv(grouped_stats_path, index=False)
    files.append(grouped_stats_path)

    matched_path = tables_dir / "matched_size_architecture_comparison.csv"
    _matched_size_comparisons(validation).to_csv(matched_path, index=False)
    files.append(matched_path)

    assumptions_path = tables_dir / "proxy_assumptions_table.csv"
    _assumptions_table(validation).to_csv(assumptions_path, index=False)
    files.append(assumptions_path)

    sensitivity = _sensitivity_rows(validation)
    sensitivity_path = tables_dir / "model_sensitivity_analysis.csv"
    sensitivity.to_csv(sensitivity_path, index=False)
    files.append(sensitivity_path)

    ordering_path = tables_dir / "model_sensitivity_ordering.csv"
    _sensitivity_ordering(sensitivity).to_csv(ordering_path, index=False)
    files.append(ordering_path)

    interpretation_path = tables_dir / "results_interpretation_table.csv"
    _interpretation_table(validation).to_csv(interpretation_path, index=False)
    files.append(interpretation_path)

    raw_rows_path = tables_dir / "native_depth_bar_raw_rows.csv"
    validation[
        [
            "circuit_family",
            "provider",
            "target_model",
            "qubit_count",
            "repetition",
            "logical_depth",
            "routed_depth",
            "native_compiled_depth",
            "routing_swap_count",
            "native_entangling_gate_count",
            "unsupported_operation_count",
            "equivalence_passed",
            "native_operation_counts",
            "native_operation_sequence",
        ]
    ].sort_values(["circuit_family", "provider", "qubit_count", "repetition"]).to_csv(
        raw_rows_path, index=False
    )
    files.append(raw_rows_path)

    summary_path = tables_dir / "native_depth_bar_summary.csv"
    _grouped_metric_stats(validation, "native_compiled_depth").to_csv(summary_path, index=False)
    files.append(summary_path)

    appendix_path = tables_dir / "appendix_family_mean_summary.csv"
    _appendix_family_means(validation).to_csv(appendix_path, index=False)
    files.append(appendix_path)

    grover_path = tables_dir / "grover_diagnostic_report.csv"
    grover = validation[validation["circuit_family"].astype(str) == "grover"]
    grover[
        [
            "provider",
            "target_model",
            "qubit_count",
            "repetition",
            "logical_operation_counts",
            "routed_operation_counts",
            "native_operation_counts",
            "logical_depth",
            "routed_depth",
            "native_compiled_depth",
            "routing_swap_count",
            "native_entangling_gate_count",
            "unsupported_operation_count",
            "equivalence_passed",
            "routed_operation_sequence",
            "native_operation_sequence",
        ]
    ].sort_values(["provider", "qubit_count", "repetition"]).to_csv(grover_path, index=False)
    files.append(grover_path)

    return files


def _validation_columns() -> list[str]:
    return [
        "circuit_family",
        "provider",
        "target_model",
        "qubit_count",
        "repetition",
        "logical_depth",
        "routed_depth",
        "native_compiled_depth",
        "native_depth_over_logical_depth",
        "logical_gate_count",
        "routed_gate_count",
        "native_compiled_gate_count",
        "native_one_qubit_gate_count",
        "logical_two_qubit_gate_count",
        "routed_two_qubit_gate_count",
        "native_entangling_gate_count",
        "additional_native_entangling_gates",
        "routing_swap_count",
        "native_measurement_count",
        "estimated_native_execution_duration_ns",
        "estimated_native_execution_duration_us",
        "estimated_success_probability_from_proxy_error_model",
        "success_probability_one_qubit_contribution",
        "success_probability_entangling_contribution",
        "success_probability_measurement_contribution",
        "unsupported_operation_count",
        "equivalence_passed",
        "equivalence_validation_method",
        "equivalence_tolerance",
        "duration_source",
        "error_model_source",
        "target_metadata",
        "logical_operation_counts",
        "routed_operation_counts",
        "native_operation_counts",
    ]


def _grouped_stats(validation: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "logical_depth",
        "routed_depth",
        "native_compiled_depth",
        "routing_swap_count",
        "native_entangling_gate_count",
        "estimated_native_execution_duration_ns",
        "estimated_native_execution_duration_us",
        "estimated_success_probability_from_proxy_error_model",
    ]
    frames = [_grouped_metric_stats(validation, metric) for metric in metrics]
    return pd.concat(frames, ignore_index=True)


def _grouped_metric_stats(validation: pd.DataFrame, metric: str) -> pd.DataFrame:
    grouped = (
        validation.groupby(
            ["circuit_family", "provider", "target_model", "qubit_count"], dropna=False
        )[metric]
        .agg(["count", "mean", "std", "min", "max", "nunique"])
        .reset_index()
    )
    grouped = grouped.rename(
        columns={
            "count": "n_repetitions",
            "mean": "mean",
            "std": "std_across_repetitions",
            "min": "min",
            "max": "max",
            "nunique": "distinct_values",
        }
    )
    grouped["metric"] = metric
    grouped["std_across_repetitions"] = grouped["std_across_repetitions"].fillna(0.0)
    grouped["show_uncertainty"] = grouped["distinct_values"] > 1
    columns = [
        "metric",
        "circuit_family",
        "provider",
        "target_model",
        "qubit_count",
        "n_repetitions",
        "distinct_values",
        "mean",
        "std_across_repetitions",
        "min",
        "max",
        "show_uncertainty",
    ]
    return grouped[columns].sort_values(["metric", "circuit_family", "qubit_count", "provider"])


def _matched_size_comparisons(validation: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "logical_depth",
        "routed_depth",
        "native_compiled_depth",
        "routing_swap_count",
        "native_entangling_gate_count",
        "estimated_native_execution_duration_ns",
        "estimated_native_execution_duration_us",
        "estimated_success_probability_from_proxy_error_model",
    ]
    rows: list[dict[str, Any]] = []
    columns = [
        "circuit_family",
        "qubit_count",
        "repetition",
        "ibm_target_model",
        "quantinuum_target_model",
        "metric",
        "ibm_value",
        "quantinuum_value",
        "quantinuum_minus_ibm",
        "percent_difference_vs_ibm",
    ]
    keys = ["circuit_family", "qubit_count", "repetition"]
    for key_values, group in validation.groupby(keys, dropna=False):
        providers = {row.provider: row for row in group.itertuples()}
        if not all(provider in providers for provider in ARCHITECTURE_ORDER):
            continue
        ibm = providers["ibm"]
        quantinuum = providers["quantinuum"]
        base: dict[str, Any] = dict(zip(keys, key_values, strict=True))
        base["ibm_target_model"] = ibm.target_model
        base["quantinuum_target_model"] = quantinuum.target_model
        for metric in metrics:
            ibm_value = getattr(ibm, metric)
            quantinuum_value = getattr(quantinuum, metric)
            absolute_difference = quantinuum_value - ibm_value
            percent_difference_vs_ibm = (
                None if ibm_value == 0 else absolute_difference / ibm_value * 100.0
            )
            rows.append(
                {
                    **base,
                    "metric": metric,
                    "ibm_value": ibm_value,
                    "quantinuum_value": quantinuum_value,
                    "quantinuum_minus_ibm": absolute_difference,
                    "percent_difference_vs_ibm": percent_difference_vs_ibm,
                }
            )
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["circuit_family", "qubit_count", "repetition", "metric"]
    )


def _assumptions_table(validation: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in validation.drop_duplicates("provider").itertuples():
        metadata = _loads_json(row.target_metadata)
        durations = metadata.get("operation_duration_ns", {})
        errors = metadata.get("operation_error_rates", {})
        one_qubit_gates = metadata.get("native_one_qubit_gates", [])
        entangling_gates = metadata.get("native_entangling_gates", [])
        rows.append(
            {
                "proxy_target_name": metadata.get("target_model"),
                "provider": metadata.get("provider"),
                "connectivity_model": metadata.get("connectivity"),
                "native_operation_set": json.dumps(
                    [*one_qubit_gates, *entangling_gates], sort_keys=True
                ),
                "one_qubit_operation_durations_ns": json.dumps(
                    {gate: durations.get(gate) for gate in one_qubit_gates}, sort_keys=True
                ),
                "entangling_operation_durations_ns": json.dumps(
                    {gate: durations.get(gate) for gate in entangling_gates}, sort_keys=True
                ),
                "measurement_duration_ns": durations.get("measure"),
                "one_qubit_proxy_error_rates": json.dumps(
                    {gate: errors.get(gate) for gate in one_qubit_gates}, sort_keys=True
                ),
                "entangling_proxy_error_rates": json.dumps(
                    {gate: errors.get(gate) for gate in entangling_gates}, sort_keys=True
                ),
                "measurement_proxy_error_rate": errors.get("measure"),
                "source_or_rationale": (
                    f"{metadata.get('duration_source')}; {metadata.get('error_source')}"
                ),
                "assumption_version_date": metadata.get("assumptions_date"),
                "not_live_device_calibration": True,
            }
        )
    return pd.DataFrame(rows).sort_values("provider")


def _sensitivity_rows(validation: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in validation.itertuples():
        metadata = _loads_json(row.target_metadata)
        operation_counts = _loads_json(row.native_operation_counts)
        baseline_durations = metadata.get("operation_duration_ns", {})
        baseline_errors = metadata.get("operation_error_rates", {})
        for scenario, multipliers in SENSITIVITY_SCENARIOS.items():
            duration = 0.0
            success = 1.0
            for operation, count in operation_counts.items():
                duration += (
                    float(baseline_durations.get(operation, 0.0))
                    * multipliers["duration_multiplier"]
                    * int(count)
                )
                error_rate = min(
                    0.999999,
                    float(baseline_errors.get(operation, 0.0)) * multipliers["error_multiplier"],
                )
                success *= (1.0 - error_rate) ** int(count)
            rows.append(
                {
                    "scenario": scenario,
                    "duration_multiplier": multipliers["duration_multiplier"],
                    "error_multiplier": multipliers["error_multiplier"],
                    "circuit_family": row.circuit_family,
                    "provider": row.provider,
                    "target_model": row.target_model,
                    "qubit_count": row.qubit_count,
                    "repetition": row.repetition,
                    "estimated_native_execution_duration_from_proxy_timing_model_ns": round(
                        duration, 6
                    ),
                    "estimated_native_execution_duration_from_proxy_timing_model_us": round(
                        duration / 1000.0, 6
                    ),
                    "estimated_success_probability_from_proxy_error_model": round(success, 6),
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["scenario", "circuit_family", "qubit_count", "repetition", "provider"]
    )


def _sensitivity_ordering(sensitivity: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    columns = [
        "scenario",
        "circuit_family",
        "qubit_count",
        "repetition",
        "faster_duration_provider",
        "higher_success_provider",
        "ibm_duration_ns",
        "quantinuum_duration_ns",
        "ibm_success",
        "quantinuum_success",
        "duration_ordering_stable",
        "success_ordering_stable",
    ]
    keys = ["scenario", "circuit_family", "qubit_count", "repetition"]
    duration_col = "estimated_native_execution_duration_from_proxy_timing_model_ns"
    success_col = "estimated_success_probability_from_proxy_error_model"
    for key_values, group in sensitivity.groupby(keys, dropna=False):
        providers = {row.provider: row for row in group.itertuples()}
        if not all(provider in providers for provider in ARCHITECTURE_ORDER):
            continue
        ibm = providers["ibm"]
        quantinuum = providers["quantinuum"]
        rows.append(
            {
                **dict(zip(keys, key_values, strict=True)),
                "faster_duration_provider": "ibm"
                if getattr(ibm, duration_col) < getattr(quantinuum, duration_col)
                else "quantinuum"
                if getattr(quantinuum, duration_col) < getattr(ibm, duration_col)
                else "tie",
                "higher_success_provider": "ibm"
                if getattr(ibm, success_col) > getattr(quantinuum, success_col)
                else "quantinuum"
                if getattr(quantinuum, success_col) > getattr(ibm, success_col)
                else "tie",
                "ibm_duration_ns": getattr(ibm, duration_col),
                "quantinuum_duration_ns": getattr(quantinuum, duration_col),
                "ibm_success": getattr(ibm, success_col),
                "quantinuum_success": getattr(quantinuum, success_col),
            }
        )
    ordering = pd.DataFrame(rows)
    if ordering.empty:
        return pd.DataFrame(columns=columns)
    stability = (
        ordering.groupby(["circuit_family", "qubit_count", "repetition"], dropna=False)
        .agg(
            duration_ordering_stable=(
                "faster_duration_provider",
                lambda values: values.nunique() == 1,
            ),
            success_ordering_stable=(
                "higher_success_provider",
                lambda values: values.nunique() == 1,
            ),
        )
        .reset_index()
    )
    return ordering.merge(stability, on=["circuit_family", "qubit_count", "repetition"])[columns]


def _interpretation_table(validation: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "Circuit family": "bell",
            "Connectivity demand": "Two-qubit nearest-neighbor-sized circuit.",
            "IBM proxy behavior": "No routing SWAPs; native decomposition adds basis-gate layers.",
            "Quantinuum proxy behavior": "No routing SWAPs; all-to-all connectivity is not meaningfully exercised.",
            "Supported conclusion": "Too small to expose meaningful topology differences.",
            "Important limitation": "Only a two-qubit case is present.",
        },
        {
            "Circuit family": "ghz",
            "Connectivity demand": "Fan-out from one qubit to many others.",
            "IBM proxy behavior": "Line connectivity creates routing SWAPs and more native CX operations as qubit count grows.",
            "Quantinuum proxy behavior": "All-to-all routing avoids SWAP insertion; native RZZ decomposition still adds basis layers.",
            "Supported conclusion": "Restricted connectivity creates routing and native-gate overhead as qubit count grows.",
            "Important limitation": "Targets are proxies, not calibrated devices.",
        },
        {
            "Circuit family": "grover",
            "Connectivity demand": "Current implementation is only the two-qubit search circuit.",
            "IBM proxy behavior": "No routing SWAPs; CZ/H/X are decomposed into RZ/SX/CX basis.",
            "Quantinuum proxy behavior": "No routing SWAPs; CZ/H/X are decomposed into RZ/RX/RZZ proxy basis.",
            "Supported conclusion": "Current small-size evidence is insufficient for a broad architecture conclusion.",
            "Important limitation": "No 3-5 qubit Grover circuits are implemented here.",
        },
        {
            "Circuit family": "qft",
            "Connectivity demand": "Many long-range controlled-phase interactions.",
            "IBM proxy behavior": "Line connectivity and SWAP decomposition produce large native-depth and entangling-gate overhead.",
            "Quantinuum proxy behavior": "All-to-all routing avoids SWAP insertion; native decomposition still increases depth.",
            "Supported conclusion": "Long-range interactions strongly expose the difference between line connectivity and all-to-all connectivity.",
            "Important limitation": "Only 3- and 5-qubit QFT cases are configured.",
        },
    ]
    present = set(validation["circuit_family"].astype(str).unique())
    return pd.DataFrame([row for row in rows if row["Circuit family"] in present])


def _plot_main_scaling(cleaned: pd.DataFrame, output_dir: Path) -> list[Path]:
    plotting = cleaned.copy()
    plotting["estimated_native_execution_duration_us"] = (
        plotting["estimated_native_execution_duration_ns"] / 1000.0
    )
    specs = [
        ("routed_depth", "Routed Depth", "routed_depth_scaling_by_family.png"),
        ("native_compiled_depth", "Native-Compiled Depth", "native_depth_scaling_by_family.png"),
        ("routing_swap_count", "Routing SWAP Count", "routing_swap_count_scaling_by_family.png"),
        (
            "native_entangling_gate_count",
            "Native Entangling-Gate Count",
            "native_entangling_gate_count_scaling_by_family.png",
        ),
        (
            "estimated_native_execution_duration_us",
            "Estimated Native Execution Duration (us)",
            "estimated_native_duration_scaling_by_family.png",
        ),
        (
            "estimated_success_probability_from_proxy_error_model",
            "Estimated Success Probability from Proxy Error Model",
            "estimated_proxy_success_scaling_by_family.png",
        ),
    ]
    files: list[Path] = []
    for metric, ylabel, filename in specs:
        path = output_dir / filename
        _plot_metric_by_family(plotting, metric, ylabel, path)
        files.append(path)
    return files


def _plot_key_metric_summary(cleaned: pd.DataFrame, output_dir: Path) -> list[Path]:
    plotting = cleaned.copy()
    plotting["estimated_native_execution_duration_us"] = (
        plotting["estimated_native_execution_duration_ns"] / 1000.0
    )
    specs = [
        ("native_compiled_depth", "Native-Compiled Depth", "lower is less overhead"),
        ("routing_swap_count", "Routing SWAP Count", "lower is less routing overhead"),
        (
            "estimated_native_execution_duration_us",
            "Estimated Native Execution Duration (us)",
            "lower under this timing model",
        ),
        (
            "estimated_success_probability_from_proxy_error_model",
            "Estimated Success Probability",
            "higher under this error model",
        ),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), squeeze=False)
    colors = {"ibm": "#1f77b4", "quantinuum": "#ff7f0e"}
    for ax, (metric, ylabel, note) in zip(axes.flatten(), specs, strict=True):
        aggregate = (
            plotting.groupby("provider", dropna=False)[metric]
            .mean()
            .reindex(ARCHITECTURE_ORDER)
        )
        x_positions = np.arange(len(ARCHITECTURE_ORDER))
        values = aggregate.to_numpy(dtype=float)
        bars = ax.bar(
            x_positions,
            values,
            color=[colors[provider] for provider in ARCHITECTURE_ORDER],
            width=0.55,
        )
        ax.set_xticks(x_positions)
        ax.set_xticklabels([ARCHITECTURE_LABELS[provider] for provider in ARCHITECTURE_ORDER])
        ax.set_ylabel(ylabel)
        ax.set_title(note, fontsize=10)
        _set_metric_ylim(ax, metric, [float(value) for value in values if not pd.isna(value)])
        ax.grid(axis="y", alpha=0.3)
        for bar, value in zip(bars, values, strict=True):
            if pd.isna(value):
                continue
            ax.annotate(
                _format_metric_value(metric, float(value)),
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    fig.suptitle("Key Metric Summary", y=0.98)
    fig.text(
        0.5,
        0.93,
        "Means across configured matched architecture rows. Detailed scaling plots show size-specific behavior; these proxy estimates are not hardware benchmarks.",
        ha="center",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    path = output_dir / "key_metric_summary.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return [path]


def _plot_metric_by_family(
    dataframe: pd.DataFrame, metric: str, ylabel: str, output_path: Path
) -> None:
    families = sorted(dataframe["circuit_family"].astype(str).unique())
    fig, axes = plt.subplots(
        len(families), 1, figsize=(8.4, max(3.0, 2.35 * len(families))), squeeze=False
    )
    stats = _grouped_metric_stats(dataframe, metric)
    for ax, family in zip(axes.flatten(), families, strict=True):
        subset = stats[stats["circuit_family"] == family]
        metric_values: list[float] = []
        for provider_index, provider in enumerate(ARCHITECTURE_ORDER):
            provider_subset = subset[subset["provider"] == provider].sort_values("qubit_count")
            if provider_subset.empty:
                continue
            yerr = provider_subset["std_across_repetitions"].where(
                provider_subset["show_uncertainty"], 0.0
            )
            ax.errorbar(
                provider_subset["qubit_count"],
                provider_subset["mean"],
                yerr=yerr,
                marker="o",
                capsize=3,
                label=ARCHITECTURE_LABELS[provider],
            )
            metric_values.extend(provider_subset["mean"].astype(float).tolist())
            _annotate_points(
                ax,
                provider_subset["qubit_count"].tolist(),
                provider_subset["mean"].tolist(),
                metric,
                provider_index,
            )
        ax.set_title(family, loc="left", fontsize=10)
        ax.set_xlabel("Qubit count")
        ax.set_ylabel("")
        qubit_counts = sorted(subset["qubit_count"].dropna().unique())
        ax.xaxis.set_major_locator(FixedLocator(qubit_counts))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%d"))
        _set_metric_ylim(ax, metric, metric_values)
        ax.grid(alpha=0.3)
        if len(subset["provider"].unique()) > 1:
            ax.legend(loc="best", fontsize=8)
    fig.suptitle(ylabel, y=0.995)
    fig.text(
        0.5,
        0.965,
        "IBM: line-coupled GenericBackendV2 basis; Quantinuum: all-to-all H-series RZZ basis.\n"
        "Error bars show repetition variation at fixed qubit count.",
        ha="center",
        va="top",
        fontsize=8,
    )
    fig.supylabel(ylabel, x=0.015)
    fig.tight_layout(rect=(0.035, 0, 1, 0.89))
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def _plot_logical_baseline(cleaned: pd.DataFrame, output_dir: Path) -> list[Path]:
    logical = cleaned[
        ["circuit_family", "qubit_count", "repetition", "logical_depth"]
    ].drop_duplicates()
    stats = (
        logical.groupby(["circuit_family", "qubit_count"], dropna=False)["logical_depth"]
        .agg(["mean", "std", "count", "nunique"])
        .reset_index()
    )
    families = sorted(stats["circuit_family"].astype(str).unique())
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for family in families:
        subset = stats[stats["circuit_family"] == family].sort_values("qubit_count")
        yerr = subset["std"].fillna(0.0).where(subset["nunique"] > 1, 0.0)
        ax.errorbar(
            subset["qubit_count"], subset["mean"], yerr=yerr, marker="o", capsize=3, label=family
        )
        _annotate_points(
            ax,
            subset["qubit_count"].tolist(),
            subset["mean"].tolist(),
            "logical_depth",
            0,
        )
    qubit_counts = sorted(stats["qubit_count"].dropna().unique())
    ax.xaxis.set_major_locator(FixedLocator(qubit_counts))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%d"))
    ax.set_xlabel("Qubit count")
    ax.set_ylabel("Logical Depth")
    ax.set_title("Logical Baseline Depth", pad=24)
    ax.text(
        0.5,
        1.01,
        "One architecture-independent baseline: both proxy pipelines start from the exact same logical circuit.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8,
    )
    ax.grid(alpha=0.3)
    _set_metric_ylim(ax, "logical_depth", stats["mean"].astype(float).tolist())
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = output_dir / "logical_depth_baseline.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return [path]


def _annotate_points(
    ax: plt.Axes,
    x_values: list[float],
    y_values: list[float],
    metric: str,
    provider_index: int,
) -> None:
    y_offset = 7 + provider_index * 10
    for x_value, y_value in zip(x_values, y_values, strict=True):
        if pd.isna(y_value):
            continue
        ax.annotate(
            _format_metric_value(metric, float(y_value)),
            xy=(x_value, y_value),
            xytext=(0, y_offset),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7,
        )


def _format_metric_value(metric: str, value: float) -> str:
    if "success_probability" in metric:
        return f"{value:.3f}"
    if "duration" in metric:
        return f"{value:.2f}"
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.2f}"


def _set_metric_ylim(ax: plt.Axes, metric: str, values: list[float]) -> None:
    clean_values = [value for value in values if not pd.isna(value)]
    if not clean_values:
        return
    if "success_probability" in metric:
        ax.set_ylim(0, 1.05)
        return
    if min(clean_values) >= 0:
        upper = max(clean_values)
        if upper == 0:
            upper = 1.0
        ax.set_ylim(0, upper * 1.2)


def _appendix_family_means(validation: pd.DataFrame) -> pd.DataFrame:
    metrics = ["native_compiled_depth", "native_depth_over_logical_depth"]
    rows: list[pd.DataFrame] = []
    for metric in metrics:
        grouped = (
            validation.groupby(["circuit_family", "provider", "target_model"], dropna=False)[metric]
            .mean()
            .reset_index()
        )
        grouped["metric"] = metric
        grouped = grouped.rename(columns={metric: "family_mean"})
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True)


def _write_report(
    cleaned: pd.DataFrame,
    report_path: Path,
    results_path: Path,
    tables_dir: Path,
    figures_dir: Path,
) -> None:
    grouped_stats = pd.read_csv(tables_dir / "qubit_grouped_statistics.csv")
    assumptions_path = tables_dir / "proxy_assumptions_table.csv"
    matched_path = tables_dir / "matched_size_architecture_comparison.csv"
    sensitivity_path = tables_dir / "model_sensitivity_analysis.csv"
    ordering_path = tables_dir / "model_sensitivity_ordering.csv"
    interpretation = pd.read_csv(tables_dir / "results_interpretation_table.csv")
    unsupported_total = int(cleaned["unsupported_operation_count"].fillna(0).sum())
    equivalence_failures = int((cleaned["equivalence_passed"] != True).sum())  # noqa: E712
    duration_label = "estimated_native_execution_duration_from_proxy_timing_model"
    success_label = "estimated_success_probability_from_proxy_error_model"

    lines = [
        "# Quantum Architecture Comparison Report",
        "",
        "This report summarizes the architecture-proxy comparison tables. Those tables separate",
        "algorithmic logical circuits, topology-routed circuits, and final native-basis circuits.",
        "They are not real-hardware benchmarks and do not report measured IBM or Quantinuum",
        "hardware performance, physical fidelity, or experimentally measured execution time.",
        "The repository now also includes separate real IBM Quantum hardware validation artifacts",
        "and Quantinuum Nexus emulator validation artifacts under `results/hardware/`.",
        "",
        "## How To Read This Report",
        "",
        "- Logical means the starting circuit before any architecture-specific rewriting.",
        "- Routed means the circuit after the code adds movement needed by a layout.",
        "- Native-compiled means the circuit after it is rewritten into the gate set for one",
        "  architecture proxy.",
        "- Lower depth, fewer SWAPs, and fewer entangling gates usually mean less extra work.",
        "- The duration and success values are estimates from proxy assumptions, not live machine",
        "  measurements.",
        "",
        "## Targets and Assumptions",
        "",
        "- IBM proxy: Qiskit GenericBackendV2-compatible line-coupled proxy with `rz`, `sx`, `x`, and `cx`.",
        "- Quantinuum proxy: H-series-style all-to-all proxy with `rz`, `rx`, and Qiskit `rzz` as the ZZ-type entangling proxy.",
        "",
        f"Assumption table: `{_display_path(assumptions_path)}`. These values are not live-device calibration values.",
        "",
        "Duration metric name: `" + duration_label + "`.",
        "Success metric name: `" + success_label + "`.",
        "",
        "## Statistical Handling",
        "",
        "Uncertainty is calculated only within matched circuit family, architecture, and qubit-count",
        "groups across repetitions. Variation across qubit counts is shown as scaling, not as an",
        "experimental error bar.",
        "",
        f"Grouped statistics table: `{_display_path(tables_dir / 'qubit_grouped_statistics.csv')}`",
        f"Matched-size comparison table: `{_display_path(matched_path)}`",
        "",
        "## Native-Basis Validation",
        "",
        f"Unsupported-operation count across successful native circuits: `{unsupported_total}`.",
        f"Logical/native equivalence failures: `{equivalence_failures}`.",
        "Routing SWAPs are recorded on the routed circuit before SWAP decomposition. Native",
        "entangling-gate counts are recorded after final native-basis decomposition.",
        "",
        "## Main Figures",
        "",
        f"- `{_display_path(figures_dir / 'key_metric_summary.png')}`",
        f"- `{_display_path(figures_dir / 'routed_depth_scaling_by_family.png')}`",
        f"- `{_display_path(figures_dir / 'native_depth_scaling_by_family.png')}`",
        f"- `{_display_path(figures_dir / 'routing_swap_count_scaling_by_family.png')}`",
        f"- `{_display_path(figures_dir / 'native_entangling_gate_count_scaling_by_family.png')}`",
        f"- `{_display_path(figures_dir / 'estimated_native_duration_scaling_by_family.png')}`",
        f"- `{_display_path(figures_dir / 'estimated_proxy_success_scaling_by_family.png')}`",
        f"- `{_display_path(figures_dir / 'logical_depth_baseline.png')}`",
        "",
        "## Plain-Language Interpretation",
        "",
        "| Circuit family | Connectivity demand | IBM proxy behavior | Quantinuum proxy behavior | Supported conclusion | Important limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in interpretation.to_dict("records"):
        lines.append(
            f"| {row['Circuit family']} | {row['Connectivity demand']} | "
            f"{row['IBM proxy behavior']} | {row['Quantinuum proxy behavior']} | "
            f"{row['Supported conclusion']} | {row['Important limitation']} |"
        )

    lines.extend(
        [
            "",
            "## Sensitivity Analysis",
            "",
            "Duration and success probability were recomputed from the final native operation counts",
            "under optimistic, baseline, and pessimistic proxy assumptions without recompiling circuits.",
            "",
            f"Sensitivity rows: `{_display_path(sensitivity_path)}`",
            f"Sensitivity ordering: `{_display_path(ordering_path)}`",
        ]
    )
    ordering = pd.read_csv(ordering_path)
    if not ordering.empty:
        duration_stable = bool(ordering["duration_ordering_stable"].all())
        success_stable = bool(ordering["success_ordering_stable"].all())
        lines.append(f"Duration ordering stable across scenarios: `{duration_stable}`.")
        lines.append(f"Success-probability ordering stable across scenarios: `{success_stable}`.")

    lines.extend(
        [
            "",
            "## Provenance",
            "",
            f"Raw processed results: `{_display_path(results_path)}`",
            f"Validation table: `{_display_path(tables_dir / 'architecture_validation_table.csv')}`",
            f"Native-depth raw rows: `{_display_path(tables_dir / 'native_depth_bar_raw_rows.csv')}`",
            f"Grover diagnostics: `{_display_path(tables_dir / 'grover_diagnostic_report.csv')}`",
            "",
            "## Optional Real-Hardware Preparation",
            "",
            "This report still summarizes the proxy-model tables. The repository also contains",
            "finished IBM hardware validation results and a finished Quantinuum Nexus emulator",
            "validation result. To prepare another small provider test without submitting a job, run:",
            "",
            "```bash",
            "python -m quantum_compare.cli hardware-guide --provider all --export-family bell --export-size 2",
            "```",
            "",
            "That command exports the same measured logical Bell circuit and prints IBM Quantum and",
            "Quantinuum Nexus setup notes. Any real hardware or official emulator results should be",
            "saved separately from these proxy rows, with backend name, job id, shot count, date,",
            "measurement counts, and unavailable values recorded as `null`.",
            "",
            "Two IBM Quantum hardware jobs are recorded separately in",
            "`docs/IBM_HARDWARE_VALIDATION.md`. The first job, `d8up2d1ropqc738b44pg`, finished on",
            "backend `ibm_kingston` with 90 pub results and 4096 shots per pub result. The longer",
            "extended validation job, `d95vhvd2su3c739gc080`, also finished on `ibm_kingston` with 115",
            "pub results and 471,040 total retrieved shots. Sanitized artifacts are stored in",
            "`results/hardware/ibm_job_d8up2d1ropqc738b44pg.json`,",
            "`results/hardware/ibm_job_d8up2d1ropqc738b44pg_summary.csv`,",
            "`results/hardware/ibm_job_d95vhvd2su3c739gc080.json`, and",
            "`results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv`. These hardware jobs are not",
            "used in the proxy-model conclusions.",
            "",
            "A Quantinuum Nexus emulator validation is recorded separately in",
            "`docs/QUANTINUUM_HARDWARE_VALIDATION.md`. The `H2-1E` target accepted compilation but",
            "rejected execution for this account. The Nexus-hosted `H2-1LE` emulator target completed",
            "execution with 3 small circuits and 100 shots per circuit. Sanitized artifacts are stored",
            "in `results/hardware/quantinuum_submission_H2-1LE_20260714T173914Z.json`,",
            "`results/hardware/quantinuum_job_H2-1LE_20260714T173914Z.json`, and",
            "`results/hardware/quantinuum_job_H2-1LE_20260714T173914Z_summary.csv`. This emulator",
            "validation is not used in the proxy-model conclusions.",
            "",
            "## Remaining Scientific Limitations",
            "",
            "- The comparison-table targets are offline proxies, not current calibrated hardware",
            "  snapshots.",
            "- The separate IBM hardware validation artifacts are real machine results, but they are",
            "  not broad hardware benchmarks.",
            "- The separate Quantinuum Nexus artifacts are real provider emulator results, but they",
            "  are not physical H2 hardware measurements.",
            "- Quantinuum compilation uses a Qiskit RZZ proxy rather than pytket Quantinuum passes.",
            "- Duration and error values are proxy assumptions; they are not hardware metadata.",
            "- Lower duration or higher success estimates under these assumptions do not prove universal architecture superiority.",
            "- Grover has only one supported qubit count, so its ordering remains inconclusive.",
            "- Repetitions are deterministic and do not sample compiler stochasticity unless seeds are varied in future runs.",
        ]
    )

    # Keep this read live so missing grouped-stat artifacts fail report generation.
    _ = grouped_stats
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _display_path(path: str | Path) -> str:
    display = Path(path)
    if not display.is_absolute():
        return str(display)
    try:
        return str(display.relative_to(Path.cwd()))
    except ValueError:
        return str(display)


def _loads_json(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return {}
    return json.loads(str(value))
