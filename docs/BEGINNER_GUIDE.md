# Beginner Guide

## What this project is doing
This project compares two different ways a quantum computer might be built. It uses the
same small quantum circuits for both sides. Then it asks how much each hardware style has
to change the circuit before it is ready for that style.

Most of the architecture comparison is an offline model. That means the code runs on a
normal computer and uses clear assumptions instead of live hardware calibration data. The
repository also includes separate IBM Quantum hardware validation files and Quantinuum
Nexus emulator validation files from jobs that were actually run through provider tools.

## Classical bits
A classical bit can be either 0 or 1. It is like a light switch that is either off or on.

## Qubits
A qubit can be in a superposition of 0 and 1. The analogy is useful but not exact, because a qubit is not a coin that is simply hiding its face.

## Superposition
A qubit in superposition has a probability amplitude for 0 and a probability amplitude for 1. When we measure the qubit, we get one definite outcome.

## Measurement
Measurement is the moment when the quantum state collapses to a classical outcome. The raw probabilities are what matter for comparison.

## Entanglement
Entanglement links qubits so that their measurement outcomes are correlated in ways that cannot be explained by independent classical bits.

## Quantum gates
Gates change the quantum state. A Hadamard gate creates superposition, and controlled-NOT gates create entanglement.

## Quantum circuits
A quantum circuit is a list of gates in order. It is like a recipe: do this gate first,
then this gate, then measure the answer at the end.

## Logical circuit
The logical circuit is the starting recipe. It describes what the algorithm should do
without worrying too much about the shape of a specific machine.

## Routing
Routing is the step where the code checks whether two qubits can talk directly. If they
cannot, the code may add SWAP gates to move the qubit information closer together.

## Native gates
Native gates are the gates a hardware style is assumed to understand directly. If a
circuit uses a different gate, the compiler rewrites that gate into native gates.

## Circuit depth
Circuit depth is roughly the number of layers of operations that must happen in sequence. Shorter depth can be beneficial, but the best circuit depends on the target hardware.

## SWAP gates
A SWAP gate trades the quantum information held by two qubits. SWAPs can be useful, but
extra SWAPs usually mean extra work for the hardware.

## Noise
Noise is anything that makes the output differ from the ideal mathematical expectation. Real hardware adds noise because of imperfect control and environmental interactions.

## Fidelity
Fidelity measures how close a measured probability distribution is to an ideal one. Higher fidelity is better.

## Proxy model
A proxy model is a careful stand-in. It is not the real machine. It is a simplified model
that lets us compare architecture ideas without claiming live hardware results.

## Why `null` appears in result files
`null` means "not available." The project uses `null` instead of writing zero when a
number was not actually measured or does not apply.

## Why different physical qubits can behave differently
Different device technologies use different native gates, connectivity, and error rates. That means the same logical circuit can be compiled into a different sequence of instructions and therefore behave differently in practice.
