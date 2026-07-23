# Limitations

> [!IMPORTANT]
> IBM evidence in this repository is physical `ibm_kingston` QPU data. Quantinuum evidence is Nexus emulator execution and compile-only workflow validation. No physical Quantinuum QPU result is stored.

- The main architecture comparison is an offline proxy-model study, not a direct benchmark of physical IBM or Quantinuum hardware.
- The IBM hardware artifacts show what one physical backend returned for specific submitted jobs. They do not represent every IBM processor, calibration period, or workload.
- The completed Quantinuum executions used the Nexus-hosted `H2-1LE` and `H2-Emulator` emulator targets.
- `H2-1E` and `H2-2E` accepted compilation but did not authorize execution for the account at the time of testing.
- The repository contains no physical Quantinuum trapped-ion QPU measurements.
- The IBM and Quantinuum provider evidence is not matched by circuit suite, shots, repetitions, compiler settings, scoring rules, or calibration window.
- The project therefore cannot support a direct physical IBM-versus-Quantinuum provider ranking.
- The IBM proxy is a line-coupled Qiskit `GenericBackendV2`-style model, not a live calibrated backend snapshot.
- The Quantinuum proxy is an all-to-all H-series-style RZZ model, not an official physical QPU execution or a substitute for official pytket hardware compilation.
- Estimated native execution duration depends on declared proxy timing assumptions. It is not experimentally measured runtime.
- Estimated success probability depends on declared proxy error assumptions. It is not measured hardware fidelity.
- Bell and the current two-qubit Grover circuit are too small to support broad architecture conclusions.
- Only 3- and 5-qubit QFT and 3-, 5-, and 7-qubit GHZ cases are configured in the controlled suite.
- Optional qBraid simulator checks are platform sanity checks, not provider hardware measurements.
- Provider artifacts must remain separate from proxy-model rows and must retain their evidence labels.

The supported conclusion is limited to algorithm-hardware fit under the tested models and workloads. The evidence does not prove that one provider, architecture, or qubit technology is universally superior.
