#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from qiskit import QuantumCircuit


LOCAL_ENV_PATH = Path(".env.ibm")
OUTPUT_DIR = Path("results/hardware")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare or submit an extended IBM Quantum hardware validation suite."
    )
    parser.add_argument("--backend", default="ibm_kingston", help="IBM backend name")
    parser.add_argument("--shots", type=int, default=4096, help="Shots per circuit")
    parser.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="How many times to repeat each circuit in the submitted bundle",
    )
    parser.add_argument(
        "--max-qubits",
        type=int,
        default=16,
        help="Largest GHZ-style circuit width to include",
    )
    parser.add_argument(
        "--submit-hardware",
        action="store_true",
        help="Actually submit to IBM hardware. Omit this for a dry-run plan.",
    )
    parser.add_argument(
        "--i-understand-this-may-use-credits",
        action="store_true",
        help="Required together with --submit-hardware.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    circuits = build_extended_suite(args.max_qubits, args.repetitions)
    plan = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": args.backend,
        "shots_per_circuit": args.shots,
        "repetitions": args.repetitions,
        "max_qubits": args.max_qubits,
        "circuit_count": len(circuits),
        "total_requested_shots": len(circuits) * args.shots,
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
            "This is a real-hardware validation plan. It is separate from offline "
            "proxy-model results and may use IBM Quantum quota or credits if submitted."
        ),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plan_path = OUTPUT_DIR / "ibm_extended_validation_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote extended validation plan to {plan_path}")
    print(f"Circuits: {len(circuits)}")
    print(f"Shots per circuit: {args.shots}")
    print(f"Total requested shots: {len(circuits) * args.shots}")

    if not args.submit_hardware:
        print("Dry run only. No IBM job was submitted.")
        print(
            "To submit, rerun with --submit-hardware "
            "--i-understand-this-may-use-credits after reviewing the plan."
        )
        return 0

    if not args.i_understand_this_may_use_credits:
        print("Refusing to submit without --i-understand-this-may-use-credits.")
        return 2

    return submit_to_ibm(circuits, args.backend, args.shots, plan_path)


def build_extended_suite(max_qubits: int, repetitions: int) -> list[QuantumCircuit]:
    if max_qubits < 2:
        raise ValueError("--max-qubits must be at least 2.")
    if repetitions < 1:
        raise ValueError("--repetitions must be at least 1.")

    base_circuits: list[QuantumCircuit] = []
    for width in range(2, max_qubits + 1, 2):
        base_circuits.append(build_ghz_like(width))
        base_circuits.append(build_reverse_ladder(width))
        if width >= 4:
            base_circuits.append(build_ring_entangler(width))

    circuits: list[QuantumCircuit] = []
    for repetition in range(repetitions):
        for circuit in base_circuits:
            copied = circuit.copy()
            copied.name = f"{circuit.name}_rep_{repetition + 1}"
            circuits.append(copied)
    return circuits


def build_ghz_like(width: int) -> QuantumCircuit:
    circuit = QuantumCircuit(width, width, name=f"ghz_like_{width}")
    circuit.h(0)
    for target in range(1, width):
        circuit.cx(0, target)
    circuit.measure(range(width), range(width))
    return circuit


def build_reverse_ladder(width: int) -> QuantumCircuit:
    circuit = QuantumCircuit(width, width, name=f"reverse_ladder_{width}")
    for qubit in range(width):
        circuit.h(qubit)
    for left in range(width - 1):
        circuit.cx(left, left + 1)
    for right in range(width - 1, 0, -1):
        circuit.cx(right, right - 1)
    circuit.measure(range(width), range(width))
    return circuit


def build_ring_entangler(width: int) -> QuantumCircuit:
    circuit = QuantumCircuit(width, width, name=f"ring_entangler_{width}")
    for qubit in range(width):
        circuit.h(qubit)
    for qubit in range(width):
        circuit.cx(qubit, (qubit + 1) % width)
    for qubit in range(width):
        circuit.rz(0.125 * (qubit + 1), qubit)
    circuit.measure(range(width), range(width))
    return circuit


def submit_to_ibm(
    circuits: list[QuantumCircuit], backend_name: str, shots: int, plan_path: Path
) -> int:
    load_dotenv(LOCAL_ENV_PATH)
    token = os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("QISKIT_IBM_TOKEN")
    instance = os.getenv("IBM_QUANTUM_INSTANCE")
    if not token or not instance:
        print("Missing IBM credentials in .env.ibm.")
        return 2

    try:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    except ImportError:
        print("Missing qiskit-ibm-runtime. Install it first:")
        print("python -m pip install qiskit-ibm-runtime")
        return 2

    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=token,
        instance=instance,
    )
    backend = service.backend(backend_name)
    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_circuits = [pass_manager.run(circuit) for circuit in circuits]
    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa_circuits, shots=shots)
    submission = {
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": backend_name,
        "job_id": job.job_id(),
        "shots_per_circuit": shots,
        "circuit_count": len(circuits),
        "plan_path": str(plan_path),
        "notes": [
            "This file intentionally excludes IBM Quantum tokens, CRNs, and account identifiers.",
            "Fetch results later with scripts/fetch_ibm_hardware_job.py or a job-specific retrieval script.",
        ],
    }
    submission_path = OUTPUT_DIR / f"ibm_extended_validation_submission_{job.job_id()}.json"
    submission_path.write_text(json.dumps(submission, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Submitted IBM job: {job.job_id()}")
    print(f"Wrote submission record to {submission_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
