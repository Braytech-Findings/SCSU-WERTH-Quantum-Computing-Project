#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


JOB_ID = "d8up2d1ropqc738b44pg"
LOCAL_ENV_PATH = Path(".env.ibm")
OUTPUT_PATH = Path("results/hardware/ibm_job_d8up2d1ropqc738b44pg.json")


def main() -> int:
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
    job = service.job(JOB_ID)
    result = job.result()

    safe_payload = {
        "provider": "ibm",
        "job_id": JOB_ID,
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

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(safe_payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote sanitized IBM job data to {OUTPUT_PATH}")
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


if __name__ == "__main__":
    raise SystemExit(main())
