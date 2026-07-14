#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from qiskit import QuantumCircuit

from quantum_compare.circuits import (
    build_bell_state,
    build_ghz_state,
    build_grover_search,
    build_qft,
)


LOCAL_ENV_PATH = Path(".env.quantinuum")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare, compile, or execute a Quantinuum Nexus validation bundle."
    )
    parser.add_argument(
        "--target",
        default=os.getenv("QUANTINUUM_TARGET", "H2-1E"),
        help="Quantinuum Nexus target, for example H2-1E, H2-2E, H2-1SC, or H2-2SC.",
    )
    parser.add_argument(
        "--project",
        default=os.getenv("QUANTINUUM_NEXUS_PROJECT", "SCSU WERTH Quantum Validation"),
        help="Quantinuum Nexus project name to get or create.",
    )
    parser.add_argument("--shots", type=int, default=100, help="Shots per circuit.")
    parser.add_argument(
        "--suite",
        choices=("small", "matched"),
        default="small",
        help="Circuit bundle to prepare. Start with small before using matched.",
    )
    parser.add_argument(
        "--use-nexus",
        action="store_true",
        help="Upload and compile through Quantinuum Nexus. Omit for a local dry-run plan.",
    )
    parser.add_argument(
        "--estimate-cost",
        action="store_true",
        help="Ask Nexus for a cost estimate after compilation when the selected target supports it.",
    )
    parser.add_argument(
        "--execute-nexus",
        action="store_true",
        help="Execute the compiled circuits on the selected Nexus target.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for Nexus compile/execute jobs and download results when execution finishes.",
    )
    parser.add_argument(
        "--optimization-level",
        type=int,
        default=0,
        help="Quantinuum Nexus compile optimization level. Official examples use 0 to 2.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/hardware",
        help="Directory for sanitized Quantinuum plan, submission, and result artifacts.",
    )
    parser.add_argument(
        "--i-understand-this-may-use-hqcs-or-quota",
        action="store_true",
        help="Required with --execute-nexus because execution can consume HQCs or quota.",
    )
    return parser


def main() -> int:
    load_dotenv(LOCAL_ENV_PATH)
    args = build_parser().parse_args()

    circuits = build_validation_suite(args.suite)
    plan = build_plan(args, circuits)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = output_dir / "quantinuum_validation_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote Quantinuum validation plan to {plan_path}")
    print(f"Target: {args.target}")
    print(f"Circuits: {len(circuits)}")
    print(f"Shots per circuit: {args.shots}")
    print(f"Total requested shots: {len(circuits) * args.shots}")

    if not args.use_nexus:
        print("Dry run only. No Quantinuum Nexus job was created.")
        print("Next safe step: rerun with --use-nexus --wait to upload and compile only.")
        return 0

    if args.execute_nexus and not args.i_understand_this_may_use_hqcs_or_quota:
        print("Refusing to execute without --i-understand-this-may-use-hqcs-or-quota.")
        return 2

    return run_nexus_workflow(args, circuits, plan_path, output_dir)


def build_validation_suite(suite: str) -> list[QuantumCircuit]:
    if suite == "small":
        return [
            build_bell_state(),
            build_ghz_state(3),
            build_grover_search(2),
        ]
    if suite == "matched":
        return [
            build_bell_state(),
            build_ghz_state(3),
            build_ghz_state(5),
            build_qft(3),
            build_qft(5),
            build_grover_search(2),
        ]
    raise ValueError(f"Unknown suite '{suite}'.")


def build_plan(args: argparse.Namespace, circuits: list[QuantumCircuit]) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "quantinuum",
        "route": "Quantinuum Nexus",
        "target": args.target,
        "project": args.project,
        "suite": args.suite,
        "shots_per_circuit": args.shots,
        "circuit_count": len(circuits),
        "total_requested_shots": len(circuits) * args.shots,
        "optimization_level": args.optimization_level,
        "execute_requested": args.execute_nexus,
        "target_note": _target_note(args.target),
        "circuits": [
            {
                "index": index,
                "name": circuit.name,
                "qubits": circuit.num_qubits,
                "clbits": circuit.num_clbits,
                "depth": circuit.depth(),
                "operations": dict(sorted(circuit.count_ops().items())),
            }
            for index, circuit in enumerate(circuits)
        ],
        "safety_note": (
            "This is a Quantinuum Nexus validation plan. It is separate from offline "
            "proxy-model results. Execution can consume HQCs, simulator quota, or other "
            "account quota depending on the selected target."
        ),
    }


def run_nexus_workflow(
    args: argparse.Namespace, circuits: list[QuantumCircuit], plan_path: Path, output_dir: Path
) -> int:
    try:
        import qnexus as qnx
        from pytket.extensions.qiskit import qiskit_to_tk
    except ImportError:
        print("Missing Quantinuum Nexus packages. Install them first:")
        print("python -m pip install pytket-qiskit pytket qnexus")
        return 2

    qnx_client: Any = qnx
    name_suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    project = qnx_client.projects.get_or_create(args.project)
    qnx_client.context.set_active_project(project)
    backend_config = qnx_client.QuantinuumConfig(device_name=args.target)

    uploaded_refs = []
    for circuit in circuits:
        tket_circuit = qiskit_to_tk(circuit)
        uploaded_refs.append(
            qnx_client.circuits.upload(
                circuit=tket_circuit,
                name=f"{circuit.name}-{name_suffix}",
            )
        )

    compile_job_name = f"compile-{args.target}-{name_suffix}"
    compile_job = qnx_client.start_compile_job(
        circuits=uploaded_refs,
        optimisation_level=args.optimization_level,
        backend_config=backend_config,
        name=compile_job_name,
    )
    print(f"Started Quantinuum compile job: {compile_job_name}")

    compiled_refs: list[Any] = []
    if args.wait or args.execute_nexus or args.estimate_cost:
        qnx_client.jobs.wait_for(compile_job)
        compiled_refs = [result.get_output() for result in qnx_client.jobs.results(compile_job)]
        print(f"Compiled circuits available: {len(compiled_refs)}")

    cost_estimates = []
    if args.estimate_cost and compiled_refs:
        cost_estimates = estimate_costs(qnx_client, compiled_refs, args.target, args.shots)

    execute_job_name = None
    execute_job = None
    execute_error = None
    downloaded_results: list[dict[str, Any]] = []
    if args.execute_nexus:
        if not compiled_refs:
            qnx_client.jobs.wait_for(compile_job)
            compiled_refs = [result.get_output() for result in qnx_client.jobs.results(compile_job)]
        execute_job_name = f"execute-{args.target}-{name_suffix}"
        execute_job = qnx_client.start_execute_job(
            circuits=compiled_refs,
            backend_config=backend_config,
            n_shots=[args.shots] * len(compiled_refs),
            name=execute_job_name,
        )
        print(f"Started Quantinuum execute job: {execute_job_name}")
        if args.wait:
            try:
                qnx_client.jobs.wait_for(execute_job)
            except Exception as exc:  # noqa: BLE001
                execute_error = str(exc)
                print(f"Quantinuum execute job failed: {execute_error}")
            else:
                result_refs = qnx_client.jobs.results(execute_job)
                downloaded_results = [
                    extract_quantinuum_result(index, result_ref.download_result())
                    for index, result_ref in enumerate(result_refs)
                ]

    submission = {
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "quantinuum",
        "route": "Quantinuum Nexus",
        "target": args.target,
        "project": args.project,
        "suite": args.suite,
        "shots_per_circuit": args.shots,
        "circuit_count": len(circuits),
        "plan_path": str(plan_path),
        "compile_job_name": compile_job_name,
        "execute_job_name": execute_job_name,
        "execute_error": execute_error,
        "cost_estimates": cost_estimates,
        "result_count": len(downloaded_results),
        "notes": [
            "This file intentionally excludes Quantinuum passwords, tokens, account secrets, and internal Nexus UUID refs.",
            "These data are separate from the offline proxy-model result tables.",
        ],
    }
    submission_path = output_dir / f"quantinuum_submission_{args.target}_{name_suffix}.json"
    submission_path.write_text(json.dumps(submission, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote Quantinuum submission record to {submission_path}")

    if downloaded_results:
        result_payload = {
            "provider": "quantinuum",
            "route": "Quantinuum Nexus",
            "target": args.target,
            "project": args.project,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "execute_job_name": execute_job_name,
            "shots_per_circuit": args.shots,
            "results": downloaded_results,
            "notes": [
                "This file intentionally excludes Quantinuum passwords, tokens, account secrets, and internal Nexus UUID refs.",
                "These data are separate from the offline proxy-model result tables.",
            ],
        }
        result_path = output_dir / f"quantinuum_job_{args.target}_{name_suffix}.json"
        summary_path = output_dir / f"quantinuum_job_{args.target}_{name_suffix}_summary.csv"
        result_path.write_text(
            json.dumps(result_payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        write_summary_csv(result_payload, summary_path)
        print(f"Wrote Quantinuum result data to {result_path}")
        print(f"Wrote Quantinuum compact summary to {summary_path}")

    if execute_error is not None:
        return 1
    return 0


def estimate_costs(
    qnx: Any, compiled_refs: list[Any], target: str, shots: int
) -> list[dict[str, Any]]:
    estimates = []
    backend_config = qnx.QuantinuumConfig(device_name=target)
    for index, ref in enumerate(compiled_refs):
        error: str | None
        try:
            cost = qnx.client.circuits.cost(ref, n_shots=shots, backend_config=backend_config)
        except Exception as exc:  # noqa: BLE001
            cost = None
            error = str(exc)
        else:
            error = None
        estimates.append({"circuit_index": index, "hqc_cost": cost, "error": error})
    return estimates


def extract_quantinuum_result(index: int, result: Any) -> dict[str, Any]:
    counts = _maybe_call(result, "get_counts")
    distribution = (
        _maybe_call(result, "get_empirical_distribution")
        or _maybe_call(result, "get_probability_distribution")
        or _maybe_call(result, "get_distribution")
    )
    return {
        "index": index,
        "result_type": type(result).__name__,
        "counts": _json_safe(_normalize_counts(counts)),
        "distribution": _json_safe(_normalize_distribution(distribution)),
    }


def write_summary_csv(payload: dict[str, Any], path: Path) -> None:
    fieldnames = [
        "provider",
        "target",
        "execute_job_name",
        "result_index",
        "bit_width",
        "shots",
        "all_zero_count",
        "all_one_count",
        "all_zero_or_all_one_count",
        "all_zero_or_all_one_probability",
        "distinct_outcomes",
    ]
    rows = []
    for result in payload.get("results", []):
        counts = result.get("counts")
        if not isinstance(counts, dict) or not counts:
            continue
        int_counts = {
            str(bitstring): int(count)
            for bitstring, count in counts.items()
            if isinstance(count, int)
        }
        if not int_counts:
            continue
        bit_width = max(len(bitstring) for bitstring in int_counts)
        shots = sum(int_counts.values())
        all_zero_count = int_counts.get("0" * bit_width, 0)
        all_one_count = int_counts.get("1" * bit_width, 0)
        all_zero_or_all_one_count = all_zero_count + all_one_count
        rows.append(
            {
                "provider": payload.get("provider"),
                "target": payload.get("target"),
                "execute_job_name": payload.get("execute_job_name"),
                "result_index": result.get("index"),
                "bit_width": bit_width,
                "shots": shots,
                "all_zero_count": all_zero_count,
                "all_one_count": all_one_count,
                "all_zero_or_all_one_count": all_zero_or_all_one_count,
                "all_zero_or_all_one_probability": round(all_zero_or_all_one_count / shots, 6)
                if shots
                else None,
                "distinct_outcomes": len(int_counts),
            }
        )

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _target_note(target: str) -> str:
    if target.endswith("SC"):
        return "Target name looks like a syntax checker. Use it before emulator or hardware runs."
    if target.endswith("E"):
        return "Target name looks like an emulator. It may use simulator quota rather than hardware HQCs."
    return "Target name does not end in E or SC. Confirm cost before execution."


def _maybe_call(obj: Any, method_name: str) -> Any:
    method = getattr(obj, method_name, None)
    if not callable(method):
        return None
    try:
        return method()
    except Exception:  # noqa: BLE001
        return None


def _normalize_counts(counts: Any) -> dict[str, int] | None:
    if counts is None:
        return None
    if not isinstance(counts, dict):
        return None
    normalized = {}
    for key, value in counts.items():
        normalized[_bitstring_from_key(key)] = int(value)
    return normalized


def _normalize_distribution(distribution: Any) -> dict[str, float] | None:
    if distribution is None:
        return None
    if not isinstance(distribution, dict):
        return None
    normalized = {}
    for key, value in distribution.items():
        normalized[_bitstring_from_key(key)] = float(value)
    return normalized


def _bitstring_from_key(key: Any) -> str:
    if isinstance(key, tuple):
        return "".join(str(bit) for bit in key)
    return str(key)


def _safe_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
