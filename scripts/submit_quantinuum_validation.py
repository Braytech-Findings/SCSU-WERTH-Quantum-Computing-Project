#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from quantum_compare.circuits import (
    build_bell_state,
    build_ghz_state,
    build_grover_search,
    build_qft,
)

LOCAL_ENV_PATH = Path(".env.quantinuum")
EXECUTABLE_EMULATORS = frozenset({"H2-1LE", "H2-Emulator"})
COMPILE_ONLY_TARGETS = frozenset({"H2-1E", "H2-2E"})
SYNTAX_CHECKERS = frozenset({"H2-1SC", "H2-2SC"})
CLAIM_BOUNDARY = (
    "Quantinuum Nexus emulator execution validates the standardized workflow and output "
    "distributions on emulator targets. It does not constitute physical Quantinuum "
    "trapped-ion QPU evidence and does not complete a matched physical IBM-versus-Quantinuum "
    "benchmark."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate circuits on Quantinuum Nexus emulators.")
    parser.add_argument("--target", default=os.getenv("QUANTINUUM_TARGET", "H2-1LE"))
    parser.add_argument(
        "--project", default=os.getenv("QUANTINUUM_NEXUS_PROJECT", "SCSU WERTH Quantum Validation")
    )
    parser.add_argument("--shots", type=int, default=1000)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--suite", choices=("small", "matched"), default="matched")
    parser.add_argument("--use-nexus", action="store_true")
    parser.add_argument("--estimate-cost", action="store_true")
    parser.add_argument(
        "--execute-nexus", "--confirm-submit", dest="execute_nexus", action="store_true"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--optimization-level", type=int, default=0)
    parser.add_argument("--output-dir", default="results/hardware")
    parser.add_argument("--i-understand-this-may-use-hqcs-or-quota", action="store_true")
    return parser


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_validation_suite(suite: str) -> list[QuantumCircuit]:
    if suite == "small":
        return [build_bell_state(), build_ghz_state(3), build_grover_search(2)]
    if suite == "matched":
        return [
            build_bell_state(),
            build_ghz_state(3),
            build_ghz_state(5),
            build_ghz_state(7),
            build_grover_search(2),
            build_qft(3),
            build_qft(5),
        ]
    raise ValueError(f"Unknown suite '{suite}'.")


def ideal_distribution(circuit: QuantumCircuit) -> dict[str, float]:
    """Return Qiskit's displayed classical-bit order (highest classical bit leftmost)."""
    logical = circuit.remove_final_measurements(inplace=False)
    probabilities = Statevector.from_instruction(logical).probabilities_dict()
    return {
        str(bitstring).zfill(circuit.num_qubits): float(probability)
        for bitstring, probability in probabilities.items()
        if probability > 1e-14
    }


def circuit_manifest(circuits: list[QuantumCircuit]) -> list[dict[str, Any]]:
    rows = []
    for index, circuit in enumerate(circuits):
        circuit_id = circuit.name
        if circuit_id == "bell_state":
            display, family, kind, note = (
                "Bell-2",
                "Bell",
                "two_outcome_entangled",
                "All-zero/all-one support is a meaningful secondary metric.",
            )
        elif circuit_id.startswith("ghz_"):
            display, family, kind, note = (
                f"GHZ-{circuit.num_qubits}",
                "GHZ",
                "two_outcome_entangled",
                "All-zero/all-one support is a meaningful secondary metric.",
            )
        elif circuit_id.startswith("grover_"):
            display, family, kind, note = (
                "Grover-2",
                "Grover",
                "marked_state",
                "Marked-state probability for 11 is a meaningful secondary metric.",
            )
        else:
            display, family, kind, note = (
                f"QFT-{circuit.num_qubits}",
                "QFT",
                "exact_logical_distribution",
                "Distribution fidelity tests measured probabilities, not the complete phase state.",
            )
        rows.append(
            {
                "circuit_index": index,
                "circuit_id": circuit_id,
                "display_name": display,
                "algorithm_family": family,
                "qubit_count": circuit.num_qubits,
                "expected_distribution_type": kind,
                "scoring_note": note,
                "logical_depth": circuit.depth(),
                "logical_operation_counts": dict(sorted(circuit.count_ops().items())),
                "ideal_distribution": ideal_distribution(circuit),
            }
        )
    return rows


def normalize_bitstring(key: Any, bit_width: int) -> str:
    """Normalize Nexus/pytket keys to Qiskit's displayed classical-bit order."""
    if isinstance(key, tuple):
        value = "".join(str(int(bit)) for bit in key)
    elif hasattr(key, "to_readouts"):
        readouts = key.to_readouts()
        value = "".join(str(int(bit)) for bit in readouts[0])
    else:
        value = re.sub(r"[\s_]", "", str(key))
    if value.startswith("0x"):
        value = f"{int(value, 16):0{bit_width}b}"
    if not value or any(bit not in "01" for bit in value):
        raise ValueError(f"Malformed count key: {key!r}")
    if len(value) > bit_width:
        raise ValueError(f"Count key {value!r} exceeds expected width {bit_width}.")
    return value.zfill(bit_width)


def normalize_counts(counts: Any, bit_width: int) -> dict[str, int]:
    if not isinstance(counts, dict) or not counts:
        raise ValueError("Counts are missing or malformed.")
    normalized: dict[str, int] = {}
    for key, raw_count in counts.items():
        if isinstance(raw_count, bool) or not isinstance(raw_count, (int, float)):
            raise ValueError(f"Malformed count for {key!r}: {raw_count!r}")
        count = int(raw_count)
        if count != raw_count or count < 0:
            raise ValueError(f"Count must be a non-negative integer: {raw_count!r}")
        bitstring = normalize_bitstring(key, bit_width)
        normalized[bitstring] = normalized.get(bitstring, 0) + count
    if sum(normalized.values()) <= 0:
        raise ValueError("Counts contain no retrieved shots.")
    return dict(sorted(normalized.items()))


def score_counts(
    counts: Any, manifest_row: dict[str, Any], requested_shots: int | None = None
) -> dict[str, Any]:
    width = int(manifest_row["qubit_count"])
    normalized = normalize_counts(counts, width)
    shots = sum(normalized.values())
    if requested_shots is not None and shots != requested_shots:
        raise ValueError(f"Retrieved {shots} shots; expected {requested_shots}.")
    observed = {key: value / shots for key, value in normalized.items()}
    ideal = {str(key): float(value) for key, value in manifest_row["ideal_distribution"].items()}
    support = set(ideal) | set(observed)
    fidelity = sum(math.sqrt(ideal.get(key, 0.0) * observed.get(key, 0.0)) for key in support) ** 2
    tvd = 0.5 * sum(abs(ideal.get(key, 0.0) - observed.get(key, 0.0)) for key in support)
    family = manifest_row["algorithm_family"]
    all_support = None
    marked = None
    if family in {"Bell", "GHZ"}:
        all_support = (normalized.get("0" * width, 0) + normalized.get("1" * width, 0)) / shots
    elif family == "Grover":
        marked = normalized.get("1" * width, 0) / shots
    return {
        "counts": normalized,
        "shots_retrieved": shots,
        "distribution_fidelity": round(fidelity, 12),
        "total_variation_distance": round(tvd, 12),
        "all_zero_or_all_one_probability": None if all_support is None else round(all_support, 12),
        "marked_state_probability": None if marked is None else round(marked, 12),
        "distinct_outcomes": len(normalized),
    }


def classify_target(target: str) -> str:
    if target in EXECUTABLE_EMULATORS:
        return "emulator"
    if target in COMPILE_ONLY_TARGETS:
        return "compile_only_access_restricted"
    if target in SYNTAX_CHECKERS:
        return "syntax_checker"
    if re.fullmatch(r"H\d+-\d+", target, re.IGNORECASE):
        return "physical_qpu_refused"
    return "unknown_refused"


def _device_snapshot(device: Any) -> dict[str, Any]:
    info = getattr(device, "stored_backend_info", None)
    misc = getattr(info, "misc", {}) if info is not None else {}
    return {
        "backend_name": getattr(device, "backend_name", None),
        "device_name": getattr(device, "device_name", None),
        "nexus_hosted": getattr(device, "nexus_hosted", None),
        "system_type": misc.get("system_type") if isinstance(misc, dict) else None,
        "simulator": misc.get("simulator") if isinstance(misc, dict) else None,
        "quota_type": misc.get("quota_type") if isinstance(misc, dict) else None,
    }


def inspect_live_target(qnx: Any, target: str) -> dict[str, Any]:
    devices = list(qnx.devices.get_all())
    matches = [item for item in devices if getattr(item, "device_name", None) == target]
    snapshot = _device_snapshot(matches[0]) if len(matches) == 1 else None
    text = json.dumps(snapshot, sort_keys=True).lower() if snapshot else ""
    emulator_proof = target in EXECUTABLE_EMULATORS and (
        bool(snapshot and snapshot.get("nexus_hosted")) or "emulat" in text or "simulat" in text
    )
    return {
        "target": target,
        "static_classification": classify_target(target),
        "catalog_match_count": len(matches),
        "catalog_metadata": snapshot,
        "catalog_confirms_emulator": emulator_proof,
    }


def execution_is_safe(
    target_review: dict[str, Any], cost_estimates: list[dict[str, Any]], quota_message: str | None
) -> tuple[bool, str]:
    if target_review["static_classification"] != "emulator":
        return False, "Target is not on the executable-emulator allowlist."
    if not target_review["catalog_confirms_emulator"]:
        return False, "Live Nexus catalog metadata does not confirm an emulator."
    costs = [item.get("reported_cost") for item in cost_estimates]
    if any(isinstance(cost, (int, float)) and cost > 0 for cost in costs):
        return False, "A non-zero cost was reported."
    errors = " ".join(str(item.get("error") or "") for item in cost_estimates).lower()
    combined = f"{errors} {quota_message or ''}".lower()
    if any(term in combined for term in ("monetary", "overage", "credit card", "payment")):
        return False, "A monetary charge or paid-overage message was reported."
    if not quota_message:
        return False, "No institutional simulator quota message was recorded."
    return True, "Catalog-confirmed emulator with no monetary cost and recorded simulator quota."


def build_plan(args: argparse.Namespace, circuits: list[QuantumCircuit], stamp: str) -> dict[str, Any]:
    manifest = circuit_manifest(circuits)
    return {
        "run_id": stamp,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider": "quantinuum",
        "route": "Quantinuum Nexus",
        "target": args.target,
        "target_classification": classify_target(args.target),
        "evidence_type": "emulator" if args.target in EXECUTABLE_EMULATORS else None,
        "suite": args.suite,
        "shots_per_circuit": args.shots,
        "repetitions": args.repetitions,
        "circuit_count": len(circuits),
        "result_count_planned": len(circuits) * args.repetitions,
        "total_requested_shots": len(circuits) * args.shots * args.repetitions,
        "optimization_level": args.optimization_level,
        "execute_requested": args.execute_nexus,
        "circuit_manifest": manifest,
        "bit_ordering": "Qiskit display order: highest-index classical bit at left.",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _write_json_new(path: Path, payload: Any) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _maybe_call(obj: Any, method_name: str) -> Any:
    method = getattr(obj, method_name, None)
    if not callable(method):
        return None
    try:
        return method()
    except Exception:  # noqa: BLE001
        return None


def extract_counts(result: Any) -> Any:
    return _maybe_call(result, "get_counts")


def estimate_costs(qnx: Any, refs: list[Any], target: str, shots: int) -> list[dict[str, Any]]:
    config = qnx.QuantinuumConfig(device_name=target)
    rows = []
    for index, ref in enumerate(refs):
        try:
            cost = qnx.client.circuits.cost(ref, n_shots=shots, backend_config=config)
        except Exception as exc:  # noqa: BLE001
            rows.append({"circuit_index": index, "reported_cost": None, "error": str(exc)})
        else:
            rows.append({"circuit_index": index, "reported_cost": cost, "error": None})
    return rows


def _rows_to_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        return
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_result_artifacts(payload: dict[str, Any], base: Path) -> None:
    _write_json_new(base.with_suffix(".json"), payload)
    flat = []
    for row in payload["results"]:
        flat.append({key: value for key, value in row.items() if key not in {"counts", "ideal_distribution"}})
    _rows_to_csv(flat, base.with_name(base.name + "_compact.csv"))


def aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["target"], row["circuit_id"]), []).append(row)
    output = []
    for (target, circuit_id), values in grouped.items():
        fidelities = [float(item["distribution_fidelity"]) for item in values]
        tvds = [float(item["total_variation_distance"]) for item in values]
        output.append(
            {
                "target": target,
                "circuit_id": circuit_id,
                "display_name": values[0]["display_name"],
                "successful_repetitions": len(values),
                "shots_retrieved": sum(int(item["shots_retrieved"]) for item in values),
                "mean_distribution_fidelity": statistics.mean(fidelities),
                "sd_distribution_fidelity": statistics.stdev(fidelities) if len(values) > 1 else None,
                "min_distribution_fidelity": min(fidelities),
                "max_distribution_fidelity": max(fidelities),
                "mean_tvd": statistics.mean(tvds),
                "sd_tvd": statistics.stdev(tvds) if len(values) > 1 else None,
            }
        )
    return output


def run_nexus_workflow(
    args: argparse.Namespace, circuits: list[QuantumCircuit], plan: dict[str, Any], output_dir: Path
) -> int:
    import qnexus as qnx
    from pytket.extensions.qiskit import qiskit_to_tk

    stamp = plan["run_id"]
    review = inspect_live_target(qnx, args.target)
    review_path = output_dir / f"quantinuum_target_review_{args.target}_{stamp}.json"
    _write_json_new(review_path, review)
    if classify_target(args.target) in {"physical_qpu_refused", "unknown_refused", "syntax_checker"}:
        print(f"Refusing Nexus execution/compilation: {classify_target(args.target)}")
        return 2

    project = qnx.projects.get_or_create(args.project)
    qnx.context.set_active_project(project)
    config = qnx.QuantinuumConfig(device_name=args.target)
    refs = [
        qnx.circuits.upload(qiskit_to_tk(circuit), name=f"{circuit.name}-{stamp}")
        for circuit in circuits
    ]
    compile_name = f"compile-{args.target}-matched-{stamp}"
    compile_job = qnx.start_compile_job(
        programs=refs,
        optimisation_level=args.optimization_level,
        backend_config=config,
        name=compile_name,
    )
    qnx.jobs.wait_for(compile_job)
    compile_results: Any = qnx.jobs.results(compile_job)
    compiled = [item.get_output() for item in compile_results]
    costs = estimate_costs(qnx, compiled, args.target, args.shots) if args.estimate_cost else []
    quota_message = os.getenv("QUANTINUUM_SIMULATOR_QUOTA_MESSAGE")
    safe, safety_reason = execution_is_safe(review, costs, quota_message)
    submission: dict[str, Any] = {
        "target": args.target,
        "target_classification": "emulator" if args.target in EXECUTABLE_EMULATORS else classify_target(args.target),
        "evidence_type": "emulator" if args.target in EXECUTABLE_EMULATORS else None,
        "compile_job_name": compile_name,
        "execute_job_names": [],
        "cost_estimates": costs,
        "quota_message": quota_message,
        "execution_safety_approved": safe,
        "execution_safety_reason": safety_reason,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    submission_path = output_dir / f"quantinuum_submission_{args.target}_{stamp}.json"
    if not args.execute_nexus:
        _write_json_new(submission_path, submission)
        print(f"Compile complete: {compile_name}; no execution requested.")
        return 0
    if not safe:
        _write_json_new(submission_path, submission)
        print(f"Execution refused: {safety_reason}")
        return 2

    all_rows = []
    manifest = plan["circuit_manifest"]
    for repetition in range(1, args.repetitions + 1):
        execute_name = f"execute-{args.target}-matched-r{repetition}-{stamp}"
        job = qnx.start_execute_job(
            programs=compiled,
            backend_config=config,
            n_shots=[args.shots] * len(compiled),
            name=execute_name,
        )
        submission["execute_job_names"].append(execute_name)
        qnx.jobs.wait_for(job)
        result_refs: Any = qnx.jobs.results(job)
        if len(result_refs) != len(manifest):
            raise RuntimeError(f"Retrieved {len(result_refs)} results; expected {len(manifest)}.")
        run_rows = []
        for index, (result_ref, identity) in enumerate(zip(result_refs, manifest, strict=True)):
            scored = score_counts(extract_counts(result_ref.download_result()), identity, args.shots)
            row = {
                "target": args.target,
                "target_classification": "emulator",
                "evidence_type": "emulator",
                "repetition": repetition,
                "execute_job_name": execute_name,
                "circuit_index": index,
                "circuit_id": identity["circuit_id"],
                "display_name": identity["display_name"],
                "algorithm_family": identity["algorithm_family"],
                "shots_requested": args.shots,
                "ideal_distribution": identity["ideal_distribution"],
                **scored,
            }
            run_rows.append(row)
        all_rows.extend(run_rows)
        write_result_artifacts(
            {"run_id": stamp, "target": args.target, "repetition": repetition, "results": run_rows},
            output_dir / f"quantinuum_full_suite_{args.target}_{stamp}_r{repetition}",
        )
    _write_json_new(submission_path, submission)
    _rows_to_csv(all_rows, output_dir / f"quantinuum_full_suite_{args.target}_{stamp}_raw.csv")
    _rows_to_csv(
        aggregate_rows(all_rows), output_dir / f"quantinuum_full_suite_{args.target}_{stamp}_aggregate.csv"
    )
    return 0


def main() -> int:
    load_dotenv(LOCAL_ENV_PATH)
    args = build_parser().parse_args()
    if args.shots <= 0 or args.repetitions <= 0:
        print("--shots and --repetitions must be positive.")
        return 2
    if args.dry_run and (args.use_nexus or args.execute_nexus):
        print("--dry-run cannot be combined with --use-nexus or --confirm-submit.")
        return 2
    if args.execute_nexus and not args.use_nexus:
        print("--confirm-submit requires --use-nexus.")
        return 2
    if args.execute_nexus and not args.i_understand_this_may_use_hqcs_or_quota:
        print("Refusing execution without the quota acknowledgement flag.")
        return 2
    circuits = build_validation_suite(args.suite)
    stamp = utc_stamp()
    plan = build_plan(args, circuits, stamp)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = output_dir / f"quantinuum_run_manifest_{args.target}_{stamp}.json"
    _write_json_new(plan_path, plan)
    print(f"Wrote immutable run manifest: {plan_path}")
    print(
        f"{len(circuits)} circuits x {args.shots} shots x {args.repetitions} repetitions "
        f"= {plan['total_requested_shots']} requested shots"
    )
    print("Circuit order: " + ", ".join(row["circuit_id"] for row in plan["circuit_manifest"]))
    if not args.use_nexus:
        print("Dry run only. No Nexus request was made.")
        return 0
    return run_nexus_workflow(args, circuits, plan, output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
