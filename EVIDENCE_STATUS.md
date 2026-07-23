# Evidence Status

> [!IMPORTANT]
> **IBM evidence:** physical `ibm_kingston` QPU measurements. **Quantinuum evidence:** Nexus emulator execution on `H2-1LE` and `H2-Emulator`, plus compile-only checks. This project is **not yet a matched physical IBM-versus-Quantinuum hardware benchmark**. A full matched physical Quantinuum QPU run remains future work.

## What is complete

- The controlled offline architecture-proxy comparison is complete for Bell, GHZ, Grover, and QFT circuits.
- IBM physical-hardware evidence is complete for the saved `ibm_kingston` jobs, including the original 90-circuit GHZ stress study and the later 115-result validation package.
- Quantinuum Nexus emulator validation is complete for the saved small suite on `H2-1LE` and `H2-Emulator`.
- Quantinuum `H2-1E` and `H2-2E` compile-only checks are preserved as workflow evidence; direct execution was not authorized for the account at the time of testing.

## What is not complete

- No physical Quantinuum QPU result is stored in this repository.
- The full standardized suite has not been run as a matched physical IBM-versus-Quantinuum QPU experiment.
- Provider-level claims about which company or physical platform is better are therefore unsupported.

## Correct public description

This is a controlled algorithm-hardware-fit study with offline architecture proxies, real IBM Kingston hardware evidence, and Quantinuum Nexus emulator validation. It is not yet a complete matched physical multi-provider hardware benchmark.

## Future completion rule

A matched physical comparison requires the same logical circuits, circuit sizes, compiler objective, shot counts, repetitions, scoring rules, and documented calibration windows on both physical platforms. Until those data exist, IBM hardware and Quantinuum emulator results must remain separate evidence categories.
