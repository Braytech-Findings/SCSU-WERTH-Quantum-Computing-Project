#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


JOB_ID = "d8up2d1ropqc738b44pg"
LOCAL_ENV_PATH = Path(".env.ibm")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and sanitize an IBM Quantum job result.")
    parser.add_argument("--job-id", default=JOB_ID, help="IBM Runtime job ID to fetch")
    parser.add_argument(
        "--output-dir", default="results/hardware", help="Directory for sanitized artifacts"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(LOCAL_ENV_PATH)

    token = os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("QISKIT_IBM_TOKEN")
    instance = os.getenv("IBM_QUANTUM_INSTANCE")
    if not token or not instance:
        print("Missing IBM credentials.")
        print("Open .env.ibm and fill in IBM_QUANTUM_TOKEN and IBM_QUANTUM_INSTANCE.")
        print("That file is ignored by Git and must not be committed.")
        return 2

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except ImportError:
        print("Missing qiskit-ibm-runtime. Install it in your local environment:")
        print("python -m pip install qiskit-ibm-runtime")
        return 2

    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=token,
        instance=instance,
    )
    job = service.job(args.job_id)
    result = job.result()

    safe_payload = {
        "provider": "ibm",
        "job_id": args.job_id,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": _safe_string(job.status()),
        "backend": _backend_name(job),
        "creation_date": _safe_string(_maybe_call(job, "creation_date")),
        "result_type": type(result).__name__,
        "pub_results": _extract_pub_results(result),
        "notes": [
            "This file intentionally excludes IBM Quantum tokens, CRNs, and account identifiers.",
            "These data are separate from the offline proxy-model result tables.",
        ],
    }

    output_dir = Path(args.output_dir)
    output_path = output_dir / f"ibm_job_{args.job_id}.json"
    summary_path = output_dir / f"ibm_job_{args.job_id}_summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(safe_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary_csv(safe_payload, summary_path)
    print(f"Wrote sanitized IBM job data to {output_path}")
    print(f"Wrote compact IBM job summary to {summary_path}")
    return 0


def _backend_name(job: Any) -> str | None:
    backend = _maybe_call(job, "backend")
    if backend is None:
        return None
    name = getattr(backend, "name", None)
    if callable(name):
        try:
            return str(name())
        except Exception:  # noqa: BLE001
            return str(backend)
    if name is not None:
        return str(name)
    return str(backend)


def _extract_pub_results(result: Any) -> list[dict[str, Any]]:
    pub_results: list[dict[str, Any]] = []
    try:
        iterable = list(result)
    except TypeError:
        iterable = [result]

    for index, pub_result in enumerate(iterable):
        entry: dict[str, Any] = {
            "index": index,
            "type": type(pub_result).__name__,
            "classical_registers": [],
        }
        data = getattr(pub_result, "data", None)
        if data is not None:
            for register_name in dir(data):
                if register_name.startswith("_"):
                    continue
                register = getattr(data, register_name)
                get_counts = getattr(register, "get_counts", None)
                if callable(get_counts):
                    try:
                        counts = get_counts()
                    except Exception as exc:  # noqa: BLE001
                        counts = {"error": str(exc)}
                    entry["classical_registers"].append(
                        {"name": register_name, "counts": _json_safe(counts)}
                    )
        pub_results.append(entry)
    return pub_results


def _maybe_call(obj: Any, method_name: str) -> Any:
    method = getattr(obj, method_name, None)
    if not callable(method):
        return None
    try:
        return method()
    except Exception:  # noqa: BLE001
        return None


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


def _write_summary_csv(payload: dict[str, Any], path: Path) -> None:
    import csv

    fieldnames = [
        "provider",
        "backend",
        "job_id",
        "pub_index",
        "register_name",
        "bit_width",
        "shots",
        "all_zero_count",
        "all_one_count",
        "all_zero_or_all_one_count",
        "all_zero_or_all_one_probability",
        "distinct_outcomes",
    ]
    rows: list[dict[str, Any]] = []
    for pub_result in payload.get("pub_results", []):
        for register in pub_result.get("classical_registers", []):
            counts = register.get("counts", {})
            if not isinstance(counts, dict):
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
                    "backend": payload.get("backend"),
                    "job_id": payload.get("job_id"),
                    "pub_index": pub_result.get("index"),
                    "register_name": register.get("name"),
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

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
