# Final Research Answer

## Research Question

**How do the same logical circuits change after topology routing and native-basis
decomposition for superconducting-proxy and trapped-ion-proxy architectures?**

## Answer

The same logical circuit can become a very different compiled circuit because the two
architecture proxies connect qubits differently and use different native gates.

For Bell-2 and the current Grover-2 circuit, both proxies need zero routing SWAPs. These
circuits are too small to reveal a strong connectivity effect. For GHZ and QFT, the
effect grows with circuit size. The line-connected superconducting proxy must move
quantum information through extra SWAP operations so distant qubits can interact. The
all-to-all trapped-ion proxy can connect every required pair directly in these tests, so
it inserts zero routing SWAPs.

The added routing work carries forward into native compilation:

| Circuit | Superconducting proxy SWAPs | Trapped-ion proxy SWAPs | Superconducting native depth | Trapped-ion native depth | Superconducting entangling gates | Trapped-ion entangling gates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Bell-2 | 0 | 0 | 5 | 7 | 1 | 1 |
| GHZ-3 | 4 | 0 | 16 | 9 | 12 | 2 |
| GHZ-5 | 12 | 0 | 38 | 13 | 34 | 4 |
| GHZ-7 | 20 | 0 | 60 | 17 | 56 | 6 |
| Grover-2 | 0 | 0 | 12 | 10 | 2 | 2 |
| QFT-3 | 6 | 0 | 42 | 21 | 27 | 6 |
| QFT-5 | 30 | 0 | 106 | 29 | 116 | 16 |

The strongest tested example is QFT-5. Its superconducting proxy circuit uses 30 routing
SWAPs, reaches native depth 106, and contains 116 native entangling gates. The
trapped-ion proxy uses no routing SWAPs, reaches native depth 29, and contains 16 native
entangling gates.

Under the repository's fixed proxy timing and error assumptions, the trapped-ion proxy
also has lower estimated duration and higher estimated success for every tested matched
circuit. That result is a consequence of this controlled model. It is not measured
physical-device speed or fidelity and does not prove universal hardware superiority.

## Supporting Emulator Result

The later Quantinuum Nexus emulator experiment ran the complete seven-circuit suite on
`H2-1LE` and `H2-Emulator`, with 1,000 shots per circuit and three repetitions per
target. All 42,000 requested shots were retrieved. Every target/circuit mean classical
distribution fidelity exceeded 0.984. QFT-5 had the largest mean TVD on both targets:
0.0761 on `H2-1LE` and 0.0661 on `H2-Emulator`.

This validates the standardized workflow and measured output distributions on emulator
targets. It does not constitute physical Quantinuum trapped-ion QPU evidence. QFT
measurement-distribution fidelity also does not validate the complete quantum phase
state.

## Final Conclusion

**Quantum architecture changes how much work is required to implement the same
algorithm.** Circuits with long-range interactions, especially the tested GHZ and QFT
circuits, expose the largest difference between line and all-to-all connectivity.
Connectivity should therefore be considered alongside qubit count, native gates,
calibration, error, time, and cost when choosing a system for an experiment.

The evidence supports a structural architecture conclusion. It does not complete a
matched physical IBM-versus-Quantinuum QPU benchmark and must not be used as a direct
physical-provider ranking.

## Publication Figures

1. `results/final_figures/publication/01_research_question_answer.png`
2. `results/final_figures/publication/02_connectivity_scaling.png`
3. `results/final_figures/publication/03_modeled_time_reliability.png`
4. `results/final_figures/publication/04_quantinuum_emulator_validation.png`

Every figure has a matching vector PDF and includes five reading notes: the question,
how to read the graph, the result, why it matters, and the scientific boundary.
