# Beginner Guide

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

## Circuit depth
Circuit depth is roughly the number of layers of operations that must happen in sequence. Shorter depth can be beneficial, but the best circuit depends on the target hardware.

## Noise
Noise is anything that makes the output differ from the ideal mathematical expectation. Real hardware adds noise because of imperfect control and environmental interactions.

## Fidelity
Fidelity measures how close a measured probability distribution is to an ideal one. Higher fidelity is better.

## Why different physical qubits can behave differently
Different device technologies use different native gates, connectivity, and error rates. That means the same logical circuit can be compiled into a different sequence of instructions and therefore behave differently in practice.
