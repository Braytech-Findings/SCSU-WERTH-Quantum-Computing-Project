from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from typing import Any

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator

ALLOWED_NON_UNITARY_OPERATIONS = frozenset({"measure", "reset", "barrier", "delay"})
TRANSPILER_NON_UNITARY_BASIS = ("measure", "reset", "delay")
EQUIVALENCE_TOLERANCE = 1e-8


@dataclass(frozen=True)
class NativeCompileResult:
    """Store the three versions of a circuit.

    Logical is the starting recipe. Routed is after qubits are moved as needed. Native is
    after the circuit is rewritten into the gate set for one architecture proxy.
    """

    logical: QuantumCircuit
    routed: QuantumCircuit
    native_compiled: QuantumCircuit
    target_metadata: dict[str, Any]
    routing_swap_count: int
    unsupported_operation_count: int
    equivalence_method: str
    equivalence_tolerance: float
    equivalence_passed: bool


class ArchitectureModel:
    """Base class for reproducible offline architecture targets.

    A target is a simplified stand-in for a hardware style. It lets the project compare
    architecture effects without claiming that live hardware was used.
    """

    def __init__(
        self,
        *,
        provider: str,
        target_model: str,
        connectivity: str,
        native_one_qubit_gates: tuple[str, ...],
        native_entangling_gates: tuple[str, ...],
        operation_duration_ns: dict[str, float | None],
        operation_error_rates: dict[str, float | None],
        duration_source: str,
        error_source: str,
        assumptions_date: str | None = None,
    ) -> None:
        self.provider = provider
        self.target_model = target_model
        self.connectivity = connectivity
        self.native_one_qubit_gates = native_one_qubit_gates
        self.native_entangling_gates = native_entangling_gates
        self.operation_duration_ns = operation_duration_ns
        self.operation_error_rates = operation_error_rates
        self.duration_source = duration_source
        self.error_source = error_source
        self.assumptions_date = assumptions_date or date.today().isoformat()

    @property
    def native_unitary_gates(self) -> tuple[str, ...]:
        return self.native_one_qubit_gates + self.native_entangling_gates

    @property
    def allowed_operations(self) -> frozenset[str]:
        return frozenset(self.native_unitary_gates) | ALLOWED_NON_UNITARY_OPERATIONS

    def compile(self, circuit: QuantumCircuit) -> NativeCompileResult:
        """Route, translate, and validate one circuit for this architecture proxy."""
        logical = circuit.copy()
        # Step 1: place or move qubits so required two-qubit gates can happen.
        routed = self.route(logical)
        # Step 2: rewrite the circuit into the gate "alphabet" this proxy accepts.
        native = self.to_native(routed)
        unsupported = self.unsupported_operations(native)
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise ValueError(
                f"{self.target_model} native circuit contains unsupported operations: {names}"
            )
        # Step 3: make sure the rewrite did not change the intended quantum operation.
        equivalence_passed = self.equivalent_to_logical(logical, native)
        if not equivalence_passed:
            raise ValueError(f"{self.target_model} native compilation changed circuit behavior.")
        return NativeCompileResult(
            logical=logical,
            routed=routed,
            native_compiled=native,
            target_metadata=self.target_metadata(),
            routing_swap_count=int(routed.metadata.get("routing_swap_count", 0)),
            unsupported_operation_count=0,
            equivalence_method="unitary_up_to_global_phase_after_removing_final_measurements",
            equivalence_tolerance=EQUIVALENCE_TOLERANCE,
            equivalence_passed=True,
        )

    def route(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Return a routed circuit. The base model does not need to move anything."""
        return circuit.copy()

    def to_native(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Ask Qiskit to rewrite the circuit using this proxy's allowed gate names."""
        return transpile(
            circuit,
            basis_gates=[*self.native_unitary_gates, *TRANSPILER_NON_UNITARY_BASIS],
            optimization_level=1,
        )

    def summarize(self, result: NativeCompileResult) -> dict[str, Any]:
        """Turn compiled circuits into numbers that can be saved in tables."""
        logical = result.logical
        routed = result.routed
        native = result.native_compiled
        native_operation_counts = Counter(instruction.operation.name for instruction in native.data)
        routed_operation_counts = Counter(instruction.operation.name for instruction in routed.data)
        native_one_qubit_count = sum(
            1
            for instruction in native.data
            if instruction.operation.num_qubits == 1
            and instruction.operation.name in self.native_one_qubit_gates
        )
        native_entangling_count = sum(
            1
            for instruction in native.data
            if instruction.operation.name in self.native_entangling_gates
        )
        measurement_count = sum(
            1 for instruction in native.data if instruction.operation.name == "measure"
        )
        duration = self.estimate_duration(native)
        success_parts = self.estimate_success_probability(native)
        return {
            "circuit_level": "native_compiled",
            "logical_depth": logical.depth(),
            "logical_gate_count": logical.size(),
            "logical_two_qubit_gate_count": logical.num_nonlocal_gates(),
            "logical_operation_counts": dict(sorted(logical.count_ops().items())),
            "routed_depth": routed.depth(),
            "routed_gate_count": routed.size(),
            "routed_two_qubit_gate_count": routed.num_nonlocal_gates(),
            "routed_operation_counts": dict(sorted(routed_operation_counts.items())),
            "routing_swap_count": result.routing_swap_count,
            "native_compiled_depth": native.depth(),
            "native_compiled_gate_count": native.size(),
            "native_one_qubit_gate_count": native_one_qubit_count,
            "native_entangling_gate_count": native_entangling_count,
            "native_measurement_count": measurement_count,
            "native_operation_names": sorted(native_operation_counts),
            "native_operation_counts": dict(sorted(native_operation_counts.items())),
            "unsupported_operation_count": result.unsupported_operation_count,
            "estimated_native_execution_duration_ns": duration,
            "duration_source": self.duration_source,
            "duration_unit": "ns",
            "estimated_success_probability_from_proxy_error_model": success_parts["total"],
            "success_probability_one_qubit_contribution": success_parts["one_qubit"],
            "success_probability_entangling_contribution": success_parts["entangling"],
            "success_probability_measurement_contribution": success_parts["measurement"],
            "error_model_source": self.error_source,
            "equivalence_validation_method": result.equivalence_method,
            "equivalence_tolerance": result.equivalence_tolerance,
            "equivalence_passed": result.equivalence_passed,
            "connectivity": self.connectivity,
            "target_metadata": result.target_metadata,
        }

    def unsupported_operations(self, circuit: QuantumCircuit) -> Counter[str]:
        return Counter(
            instruction.operation.name
            for instruction in circuit.data
            if instruction.operation.name not in self.allowed_operations
        )

    def equivalent_to_logical(self, logical: QuantumCircuit, native: QuantumCircuit) -> bool:
        logical_unitary = self._unitary_circuit(logical)
        native_unitary = self._unitary_circuit(native)
        return bool(
            Operator(logical_unitary).equiv(Operator(native_unitary), rtol=EQUIVALENCE_TOLERANCE)
        )

    def estimate_duration(self, circuit: QuantumCircuit) -> float | None:
        """Add up assumed operation times. Return None if any time is unavailable."""
        total = 0.0
        for instruction in circuit.data:
            name = instruction.operation.name
            duration = self.operation_duration_ns.get(name)
            if duration is None:
                return None
            total += duration
        return round(total, 6)

    def estimate_success_probability(self, circuit: QuantumCircuit) -> dict[str, float | None]:
        """Multiply simple proxy success factors for each operation in the circuit."""
        one_qubit = 1.0
        entangling = 1.0
        measurement = 1.0
        for instruction in circuit.data:
            name = instruction.operation.name
            error_rate = self.operation_error_rates.get(name)
            if error_rate is None:
                return {"one_qubit": None, "entangling": None, "measurement": None, "total": None}
            factor = 1.0 - error_rate
            if name in self.native_one_qubit_gates:
                one_qubit *= factor
            elif name in self.native_entangling_gates:
                entangling *= factor
            elif name == "measure":
                measurement *= factor
        return {
            "one_qubit": round(one_qubit, 6),
            "entangling": round(entangling, 6),
            "measurement": round(measurement, 6),
            "total": round(one_qubit * entangling * measurement, 6),
        }

    def target_metadata(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "target_model": self.target_model,
            "connectivity": self.connectivity,
            "native_one_qubit_gates": list(self.native_one_qubit_gates),
            "native_entangling_gates": list(self.native_entangling_gates),
            "allowed_non_unitary_operations": sorted(ALLOWED_NON_UNITARY_OPERATIONS),
            "operation_duration_ns": self.operation_duration_ns,
            "operation_error_rates": self.operation_error_rates,
            "duration_source": self.duration_source,
            "error_source": self.error_source,
            "assumptions_date": self.assumptions_date,
        }

    def _unitary_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Remove final measurements so two circuits can be compared mathematically."""
        unitary_circuit = circuit.remove_final_measurements(inplace=False)
        for instruction in unitary_circuit.data:
            if instruction.operation.name in ALLOWED_NON_UNITARY_OPERATIONS:
                raise ValueError(
                    "Equivalence validation only supports final measurement/reset/barrier removal."
                )
        return unitary_circuit


class IBMArchitectureModel(ArchitectureModel):
    """IBM superconducting proxy target with Qiskit native basis and line coupling."""

    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        settings = settings or {}
        super().__init__(
            provider="ibm",
            target_model=settings.get("target_model", "qiskit-generic-backend-v2-line-proxy"),
            connectivity=settings.get("connectivity", "line/nearest-neighbor"),
            native_one_qubit_gates=tuple(settings.get("native_one_qubit_gates", ("rz", "sx", "x"))),
            native_entangling_gates=tuple(settings.get("native_entangling_gates", ("cx",))),
            operation_duration_ns=settings.get(
                "operation_duration_ns",
                {"rz": 0.0, "sx": 80.0, "x": 160.0, "cx": 300.0, "measure": 120.0},
            ),
            operation_error_rates=settings.get(
                "operation_error_rates",
                {"rz": 0.0, "sx": 0.001, "x": 0.001, "cx": 0.01, "measure": 0.02},
            ),
            duration_source=settings.get(
                "duration_source",
                "offline proxy assumptions; not provider metadata or hardware calibration",
            ),
            error_source=settings.get(
                "error_source",
                "offline proxy error assumptions; not hardware fidelity",
            ),
        )

    def route(self, circuit: QuantumCircuit) -> QuantumCircuit:
        if circuit.num_qubits <= 2:
            routed = circuit.copy()
            routed.metadata["routing_swap_count"] = 0
            routed.metadata["coupling_map"] = self.coupling_map(circuit.num_qubits)
            return routed

        routed = QuantumCircuit(circuit.num_qubits, circuit.num_clbits, name=circuit.name)
        # layout[position] tells us which original logical qubit is currently sitting at
        # that physical line position. The IBM proxy uses a simple nearest-neighbor line.
        layout = list(range(circuit.num_qubits))
        swap_count = 0
        deferred_measurements: list[tuple[int, int]] = []

        for instruction in circuit.data:
            operation = instruction.operation
            qarg_indices = [circuit.qubits.index(q) for q in instruction.qubits]
            if operation.name == "measure":
                deferred_measurements.append(
                    (qarg_indices[0], circuit.clbits.index(instruction.clbits[0]))
                )
                continue
            if operation.num_qubits == 2 and len(qarg_indices) == 2:
                left_logical, right_logical = qarg_indices
                # If two logical qubits are not neighbors on the line, add SWAPs until
                # they become neighbors. Each SWAP is counted as routing overhead.
                while abs(layout.index(left_logical) - layout.index(right_logical)) > 1:
                    left_position = layout.index(left_logical)
                    right_position = layout.index(right_logical)
                    if left_position < right_position:
                        first_position = left_position
                        second_position = left_position + 1
                    else:
                        first_position = left_position
                        second_position = left_position - 1
                    self._append_swap(routed, layout, first_position, second_position)
                    swap_count += 1
                mapped_qargs = [routed.qubits[layout.index(qarg)] for qarg in qarg_indices]
                routed.append(operation, mapped_qargs)
            else:
                mapped_qargs = [routed.qubits[layout.index(qarg)] for qarg in qarg_indices]
                routed.append(operation, mapped_qargs)

        # Move qubits back to their original measurement positions before measuring.
        for physical_position, logical_qubit in enumerate(list(layout)):
            while logical_qubit != physical_position:
                target_position = layout.index(physical_position)
                step = 1 if target_position > physical_position else -1
                self._append_swap(routed, layout, target_position, target_position - step)
                swap_count += 1
                logical_qubit = layout[physical_position]

        for logical_qubit, clbit in deferred_measurements:
            routed.measure(routed.qubits[logical_qubit], routed.clbits[clbit])

        routed.metadata["routing_swap_count"] = swap_count
        routed.metadata["coupling_map"] = self.coupling_map(circuit.num_qubits)
        return routed

    def to_native(self, circuit: QuantumCircuit) -> QuantumCircuit:
        native = transpile(
            circuit,
            basis_gates=[*self.native_unitary_gates, *TRANSPILER_NON_UNITARY_BASIS],
            coupling_map=self.coupling_map(circuit.num_qubits),
            optimization_level=1,
            seed_transpiler=42,
        )
        native.metadata.update(circuit.metadata)
        return native

    def target_metadata(self) -> dict[str, Any]:
        metadata = super().target_metadata()
        metadata["proxy_name"] = "Qiskit GenericBackendV2 line-coupled superconducting proxy"
        metadata["coupling_map_rule"] = "bidirectional nearest-neighbor line over active qubits"
        metadata["qiskit_target_basis_source"] = "Qiskit GenericBackendV2-compatible basis"
        return metadata

    def coupling_map(self, num_qubits: int) -> list[list[int]]:
        edges: list[list[int]] = []
        for index in range(num_qubits - 1):
            edges.append([index, index + 1])
            edges.append([index + 1, index])
        return edges

    def _append_swap(
        self, circuit: QuantumCircuit, layout: list[int], first_position: int, second_position: int
    ) -> None:
        first_logical = layout[first_position]
        second_logical = layout[second_position]
        circuit.swap(circuit.qubits[first_position], circuit.qubits[second_position])
        layout[first_position], layout[second_position] = second_logical, first_logical


class QuantinuumArchitectureModel(ArchitectureModel):
    """Offline Quantinuum H-series-style proxy with all-to-all RZZ entangling basis."""

    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        settings = settings or {}
        super().__init__(
            provider="quantinuum",
            target_model=settings.get("target_model", "quantinuum-h-series-rzz-offline-proxy"),
            connectivity=settings.get("connectivity", "all-to-all"),
            native_one_qubit_gates=tuple(settings.get("native_one_qubit_gates", ("rz", "rx"))),
            native_entangling_gates=tuple(settings.get("native_entangling_gates", ("rzz",))),
            operation_duration_ns=settings.get(
                "operation_duration_ns",
                {"rz": 0.0, "rx": 40.0, "rzz": 150.0, "measure": 90.0},
            ),
            operation_error_rates=settings.get(
                "operation_error_rates",
                {"rz": 0.0, "rx": 0.0005, "rzz": 0.005, "measure": 0.01},
            ),
            duration_source=settings.get(
                "duration_source",
                "offline H-series-style proxy assumptions; not provider metadata or hardware calibration",
            ),
            error_source=settings.get(
                "error_source",
                "offline proxy error assumptions; not hardware fidelity",
            ),
        )

    def route(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """All-to-all connectivity means this proxy does not need routing SWAPs."""
        routed = circuit.copy()
        routed.metadata["routing_swap_count"] = 0
        routed.metadata["coupling_map"] = "all-to-all"
        return routed

    def to_native(self, circuit: QuantumCircuit) -> QuantumCircuit:
        native = transpile(
            circuit,
            basis_gates=[*self.native_unitary_gates, *TRANSPILER_NON_UNITARY_BASIS],
            optimization_level=1,
            seed_transpiler=42,
        )
        native.metadata.update(circuit.metadata)
        return native

    def target_metadata(self) -> dict[str, Any]:
        metadata = super().target_metadata()
        metadata["proxy_name"] = "Quantinuum H-series-style all-to-all RZZ offline proxy"
        metadata["coupling_map_rule"] = "all-to-all"
        metadata["native_basis_note"] = (
            "Qiskit RZZ is used as the offline parameterized ZZ-type entangling proxy."
        )
        return metadata
