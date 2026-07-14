from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate


def _validate_qubit_count(size: int, minimum: int, name: str) -> None:
    if size < minimum:
        raise ValueError(f"{name} requires at least {minimum} qubits, received {size}.")


def build_bell_state() -> QuantumCircuit:
    """Build a two-qubit Bell circuit.

    Plain English: make two qubits act like a linked pair, then measure both of them.
    The measurement maps qubit 0 to classical bit 0 and qubit 1 to classical bit 1.
    """
    circuit = QuantumCircuit(2, 2, name="bell_state")
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    return circuit


def build_ghz_state(num_qubits: int) -> QuantumCircuit:
    """Build a GHZ circuit.

    Plain English: link several qubits so the ideal result is all zeros or all ones.
    """
    _validate_qubit_count(num_qubits, 3, "GHZ state")
    circuit = QuantumCircuit(num_qubits, num_qubits, name=f"ghz_{num_qubits}")
    circuit.h(0)
    for index in range(num_qubits - 1):
        circuit.cx(0, index + 1)
    circuit.measure(list(range(num_qubits)), list(range(num_qubits)))
    return circuit


def build_qft(num_qubits: int) -> QuantumCircuit:
    """Build a QFT circuit on the requested number of qubits.

    Plain English: QFT is a standard test circuit with many interactions, so it is useful
    for seeing how much work each architecture proxy has to do.
    """
    _validate_qubit_count(num_qubits, 3, "QFT")
    circuit = QuantumCircuit(num_qubits, num_qubits, name=f"qft_{num_qubits}")
    qft = QuantumCircuit(num_qubits)
    qft.append(QFTGate(num_qubits), range(num_qubits))
    qft = qft.decompose()
    circuit.compose(qft, inplace=True)
    circuit.measure(list(range(num_qubits)), list(range(num_qubits)))
    return circuit


def build_grover_search(num_qubits: int) -> QuantumCircuit:
    """Build a 2-qubit Grover iteration that amplifies the marked state |11>.

    The circuit prepares an equal superposition, applies a phase oracle that flips the
    sign of |11>, and then applies a diffuser so that |11> becomes the dominant output
    on an ideal simulator.
    """
    _validate_qubit_count(num_qubits, 2, "Grover search")
    if num_qubits != 2:
        raise ValueError("Grover search is currently implemented for 2 qubits only.")
    circuit = QuantumCircuit(num_qubits, num_qubits, name="grover_search_2")
    # The first Hadamards spread the starting state across all possible answers.
    circuit.h(range(num_qubits))
    # The CZ marks the answer this tiny Grover circuit is searching for: bitstring 11.
    circuit.cz(0, 1)
    # The remaining gates amplify the marked answer so it appears most often ideally.
    circuit.h(range(num_qubits))
    circuit.x(range(num_qubits))
    circuit.cz(0, 1)
    circuit.x(range(num_qubits))
    circuit.h(range(num_qubits))
    circuit.measure(list(range(num_qubits)), list(range(num_qubits)))
    return circuit
