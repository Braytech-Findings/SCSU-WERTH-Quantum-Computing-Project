# Quantinuum Nexus Full-Suite Emulator Validation

## Run Summary

- Evidence: Quantinuum Nexus emulator validation, not physical QPU evidence.
- Targets: `H2-1LE` and `H2-Emulator`, live-catalog-confirmed local H2 emulators.
- Suite: Bell-2, GHZ-3, GHZ-5, GHZ-7, Grover-2, QFT-3, and QFT-5.
- Design: 1,000 shots per circuit, 3 independent repetitions, 42,000 requested and
  42,000 retrieved shots.
- Provider-reported execution cost: `null` for all six jobs.
- Quota: Nexus reported simulation CPU usage with `No quota set for user`; no monetary
  charge or paid-overage prompt appeared.

## Main Result

All 42 circuit results passed shot-total validation. Mean classical distribution fidelity
ranged from 0.9844 (H2-Emulator,
GHZ-7) to 1.0000
(H2-1LE, Grover-2). QFT-5 had the largest mean TVD on both targets:
0.0761 on H2-1LE and 0.0661 on H2-Emulator. Three repetitions show run-to-run spread but
are not enough to claim statistical significance.

Classical distribution fidelity compares measured output probabilities with the exact
noiseless logical-circuit distribution. QFT measurement fidelity does not validate the
complete quantum phase state.

## Claim Boundary

Quantinuum Nexus emulator execution validates the standardized workflow and output
distributions on emulator targets. It does not constitute physical Quantinuum trapped-ion
QPU evidence and does not complete a matched physical IBM-versus-Quantinuum benchmark.
