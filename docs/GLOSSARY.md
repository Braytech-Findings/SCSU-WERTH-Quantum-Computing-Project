# Glossary

| Term | Simple definition | Technical definition | Why it matters here |
|---|---|---|---|
| Quantum computer | A machine that uses unusual rules of very small things | A processor that controls and measures quantum states | It is the kind of machine whose architectures are compared. |
| Qubit | A quantum version of a bit | A normalized two-level quantum state | Circuit width counts qubits. |
| Quantum circuit | A recipe for qubits | An ordered sequence of state preparations, operations, and measurements | The same logical recipes enter both proxy pipelines. |
| Quantum gate | One instruction in the recipe | A unitary operation, or a broader channel in noisy models | Architectures support different native gates. |
| Measurement | Reading a qubit to get ordinary data | A quantum measurement producing classical outcomes probabilistically | Counts from provider runs summarize repeated shots. |
| Noise | Small mistakes and disturbances | Decoherence, control error, readout error, and other nonideal processes | Proxy success values are estimates, not measured calibration noise. |
| Simulator | Software that computes circuit behavior | A classical numerical model of quantum evolution or sampling | Ideal baselines help check logic. |
| Emulator | Software made to imitate a target machine | A provider or local model incorporating target-specific behavior | Quantinuum emulator evidence is not physical-QPU evidence. |
| Real hardware | A physical quantum processor | A QPU executing operations on physical qubits | Saved IBM artifacts are real-hardware evidence. |
| Superconducting qubit | A tiny electrical circuit acting like an artificial atom | A Josephson-junction-based quantum degree of freedom | The IBM-style proxy uses line-limited connectivity. |
| Trapped-ion qubit | A charged atom held and controlled with fields and lasers | An internal ionic state with entanglement mediated by collective motion | The Quantinuum-style proxy uses all-to-all connectivity. |
| Connectivity | Which qubits can directly work together | The coupling graph allowed for two-qubit operations | Limited connectivity can require routing SWAPs. |
| Circuit depth | Number of layers of work | Length of the critical path under parallel gate scheduling | It measures compilation overhead, not wall-clock time by itself. |
| Fidelity | How close an operation or state is to its target | A state/process similarity measure with context-specific definitions | This project reports a proxy success estimate, not live fidelity. |
| Native gate | An instruction the target directly supports | An operation in the backend basis set | Logical gates are decomposed into native gates. |
| Routing | Moving logical interactions onto allowed connections | Placement and SWAP insertion over a coupling graph | It explains much of the proxy difference. |
