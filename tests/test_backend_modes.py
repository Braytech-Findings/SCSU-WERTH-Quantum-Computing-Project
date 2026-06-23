from __future__ import annotations

from quantum_compare.backends.ibm_superconducting import IBMBackend
from quantum_compare.backends.quantinuum_trapped_ion import QuantinuumBackend


def test_ibm_backend_reports_unavailable_mode() -> None:
    backend = IBMBackend()
    result = backend.execute(None, shots=10)
    assert result["job_status"] == "dry_run"
    assert result["counts"] is None


def test_quantinuum_backend_reports_unavailable_mode() -> None:
    backend = QuantinuumBackend()
    result = backend.execute(None, shots=10)
    assert result["job_status"] == "dry_run"
    assert result["counts"] is None
