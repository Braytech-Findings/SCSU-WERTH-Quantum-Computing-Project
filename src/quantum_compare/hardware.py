from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from qiskit import QuantumCircuit, qasm2

from quantum_compare.circuits import (
    build_bell_state,
    build_ghz_state,
    build_grover_search,
    build_qft,
)


SUPPORTED_PROVIDER_NAMES = ("ibm", "quantinuum")


def build_named_logical_circuit(family: str, size: int) -> QuantumCircuit:
    """Build one of the same starting circuits used by the comparison suite."""
    if family == "bell":
        return build_bell_state()
    if family == "ghz":
        return build_ghz_state(size)
    if family == "qft":
        return build_qft(size)
    if family == "grover":
        return build_grover_search(size)
    raise ValueError(f"Unknown circuit family '{family}'.")


def export_logical_circuit_qasm(
    family: str, size: int, output_dir: str | Path = "hardware_exports"
) -> Path:
    """Export a circuit file for humans or provider tools to inspect.

    This only writes a local file. It does not connect to IBM, Quantinuum, qBraid, or any
    other provider, and it does not submit a job.
    """
    circuit = build_named_logical_circuit(family, size)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"{family}_{size}_logical.qasm"
    qasm2.dump(circuit, path)
    return path


def hardware_readiness_text(provider: str = "all") -> str:
    """Return safe hardware preparation guidance without credentials or submission."""
    provider = provider.lower()
    if provider not in (*SUPPORTED_PROVIDER_NAMES, "all"):
        raise ValueError("Provider must be 'ibm', 'quantinuum', or 'all'.")

    sections: list[str] = [
        dedent(
            """
            Hardware readiness note
            -----------------------
            This project does not submit hardware jobs by default. Use the offline proxy
            workflow first, then export one small logical circuit for provider-specific
            testing. Submit only after you have checked provider pricing, quotas, queue
            status, and account permissions.
            """
        ).strip()
    ]

    if provider in ("ibm", "all"):
        sections.append(
            dedent(
                """
                IBM Quantum route
                -----------------
                1. Install IBM Runtime support in a separate environment:
                   python -m pip install qiskit-ibm-runtime
                2. Configure an IBM Quantum Platform account and service instance.
                3. Load one exported OpenQASM circuit or rebuild the same circuit from
                   quantum_compare.circuits.
                4. Use QiskitRuntimeService, choose an operational non-simulator backend,
                   transpile to that backend's ISA circuit, and run with Sampler only after
                   explicitly deciding to spend any required credits.
                5. Record backend name, job id, shot count, date, and any provider-reported
                   calibration or mitigation metadata. Do not replace unavailable values with
                   zeros; use null when a measurement or metadata value is not available.

                Official docs checked for this guidance:
                - https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit
                - https://quantum.cloud.ibm.com/docs/en/guides/cloud-setup
                - https://quantum.cloud.ibm.com/docs/en/guides/get-started-with-primitives
                """
            ).strip()
        )

    if provider in ("quantinuum", "all"):
        sections.append(
            dedent(
                """
                Quantinuum route
                ----------------
                1. Install the Nexus/Qiskit bridge packages in a separate environment:
                   python -m pip install pytket-qiskit pytket qnexus
                2. Configure Quantinuum Nexus access and select a project.
                3. Convert the same Qiskit QuantumCircuit to TKET with qiskit_to_tk, upload
                   it to Nexus, and compile for the selected Quantinuum target.
                4. Request a cost estimate before execution. Submit to hardware only after
                   explicitly deciding to spend HQCs or other account quota.
                5. Record target name, job id, shot count, date, and downloaded measurement
                   distribution. Keep the offline proxy rows separate from official
                   Quantinuum emulator or hardware rows.

                Official docs checked for this guidance:
                - https://docs.quantinuum.com/
                - https://docs.quantinuum.com/nexus/trainings/getting_started.html
                - https://docs.quantinuum.com/systems/trainings/alternate_pathways/qiskit_h2.html
                """
            ).strip()
        )

    sections.append(
        dedent(
            """
            Measurement bitstrings
            ----------------------
            The exported circuits measure qubit i into classical bit i. Qiskit displays
            count keys with the highest classical bit on the left, so document any provider
            conversion step before comparing hardware counts with saved proxy results.
            """
        ).strip()
    )
    return "\n\n".join(sections)
