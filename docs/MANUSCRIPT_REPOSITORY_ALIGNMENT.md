# Manuscript and Repository Alignment

> [!IMPORTANT]
> The manuscript correctly treats the IBM Kingston experiment as physical hardware. The repository later added Quantinuum Nexus emulator validation, not physical Quantinuum QPU evidence. The project is still not a matched physical IBM-versus-Quantinuum benchmark.

This document audits the July 2026 manuscript against the current public repository. The manuscript remains the foundation of the research narrative. Later repository evidence is supplemental and must remain separated by evidence type.

## Evidence Inventory

| Package | Target or model | Evidence type | Workload | Size |
| --- | --- | --- | --- | --- |
| Controlled architecture comparison | nearest-neighbor superconducting-style and all-to-all trapped-ion-style models | `offline_proxy` | Bell, GHZ, Grover, QFT | 42 proxy rows plus 21 ideal rows |
| IBM experiment A | `ibm_kingston` | `physical_hardware` | GHZ stress study | 90 circuits, 368,640 shots |
| IBM experiment B | `ibm_kingston` | `physical_hardware` | expanded validation | 115 results, 471,040 shots |
| Quantinuum check A | `H2-1E` | `compile_only` | Bell-2, GHZ-3, Grover-2 | 3 compile requests |
| Quantinuum check B | `H2-2E` | `compile_only` | Bell-2, GHZ-3, Grover-2 | 3 compile requests |
| Quantinuum execution A | `H2-1LE` | `emulator` | Bell-2, GHZ-3, Grover-2 | 300 shots total |
| Quantinuum execution B | `H2-Emulator` | `emulator` | Bell-2, GHZ-3, Grover-2 | 300 shots total |

## Manuscript Statements and Current Qualification

| Manuscript location | Original status | Current repository status | Required wording |
| --- | --- | --- | --- |
| Cover and study status | Proxy comparison and IBM GHZ experiment complete; matched trapped-ion QPU pending | Quantinuum emulator validation was later completed | State that emulator validation is complete while matched physical Quantinuum QPU execution remains pending |
| Abstract | Covers proxy study and IBM physical experiment | Supplemental IBM and Quantinuum emulator packages now exist | Add only a supplemental qualification; do not present emulator results as physical trapped-ion data |
| Evidence streams | Proxy study and IBM real hardware | Repository now has proxy, IBM physical hardware, Quantinuum emulator, and compile-only evidence | Keep all categories separate |
| Study phases | Two manuscript phases | Public repository documents a third emulator-validation phase | Preserve manuscript history and add Phase III as supplemental evidence |
| qBraid checks | 26 of 26 historical checks | Later local test suite contains more tests | Report each validation count in its own context |
| IBM GHZ statistics | 90 circuits, 30 conditions, 4,096 shots each | Stored job supports those values | Do not overwrite the original analysis with the later 115-result package |
| Technology comparison | Matched real-device execution required | Still required | Quantinuum emulator validation supports workflow portability only |
| Future work | Full standardized suite on both technologies | IBM hardware exists; physical Quantinuum matched run does not | Focus future work on a matched physical Quantinuum QPU run and repeated calibration windows |

## Public Description to Use

> This project combines a controlled architecture-proxy comparison, physical IBM Kingston QPU evidence, and Quantinuum Nexus emulator validation. It has not yet completed a matched physical IBM-versus-Quantinuum QPU benchmark.

## Final Conclusion to Preserve

Connectivity and native-gate structure affect circuit families differently. The available evidence does not establish that one architecture, provider, or qubit technology is universally superior.
