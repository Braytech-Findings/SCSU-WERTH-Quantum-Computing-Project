# Final Status

> [!IMPORTANT]
> **IBM evidence:** physical `ibm_kingston` QPU measurements. **Quantinuum evidence:** Nexus emulator execution and compile-only checks. This release is not a completed matched physical IBM-versus-Quantinuum hardware benchmark.

## Release

- Public title: `Different Roads to the Same Circuit: Quantum Architecture Comparison`
- Release-preparation version: `1.0.0`
- Authoritative evidence statement: `EVIDENCE_STATUS.md`
- Project classification: controlled algorithm-hardware-fit study with offline proxies, IBM physical-hardware evidence, and Quantinuum emulator validation

The project name is retained. Every public description must state the evidence type so the title is not mistaken for a completed physical multi-provider benchmark.

## Evidence Inventory

### Phase I: controlled offline architecture proxies

- Authoritative CSV: `data/processed/results_20260623T223649Z.csv`
- Total rows: `63`
- Architecture-proxy rows: `42`
- Ideal baseline rows: `21`
- Circuit families: Bell, GHZ, QFT, and Grover
- IBM-style proxy: nearest-neighbor line connectivity
- Quantinuum-style proxy: all-to-all connectivity with an offline RZZ entangling proxy
- Unsupported native-operation count: `0`
- Logical-to-native equivalence failures: `0`

These are controlled model results, not live provider measurements.

### Phase II: IBM physical hardware

#### IBM experiment A: original GHZ stress study

- Backend: `ibm_kingston`
- Job ID: `d8up2d1ropqc738b44pg`
- Results: `90` circuits
- Conditions: `30`
- Shots per circuit: `4096`
- Total shots: `368640`
- Manuscript Pearson association: `r = -0.911`
- Artifact: `results/hardware/ibm_job_d8up2d1ropqc738b44pg.json`

#### IBM experiment B: expanded validation

- Backend: `ibm_kingston`
- Job ID: `d95vhvd2su3c739gc080`
- Results: `115`
- Shots per result: `4096`
- Total shots: `471040`
- Artifact: `results/hardware/ibm_job_d95vhvd2su3c739gc080.json`

These are physical IBM QPU results. They support IBM-specific workload observations, not a broad provider ranking.

### Phase III: Quantinuum Nexus emulator validation

- `H2-1LE`: 3 small circuits, 100 shots each, execution completed
- `H2-Emulator`: 3 small circuits, 100 shots each, execution completed
- `H2-1E`: compilation completed; direct execution returned a machine-access error
- `H2-2E`: compilation completed; direct execution returned a machine-access error
- Completed emulator circuits: Bell-2, GHZ-3, and Grover-2
- Documentation: `docs/QUANTINUUM_HARDWARE_VALIDATION.md`

These are real Quantinuum Nexus provider outputs from emulator targets. They are not physical Quantinuum trapped-ion QPU measurements.

## What Is Complete

- Offline proxy-model comparison
- qBraid reproducibility validation
- IBM Kingston physical-hardware result retrieval and analysis
- Quantinuum Nexus small-suite emulator execution
- Public figures, reports, tests, and sanitized result artifacts

## What Is Pending

- Physical Quantinuum QPU execution
- Full matched standardized suite on physical IBM and physical Quantinuum targets
- Matched shot counts, repetitions, compiler objectives, scoring rules, and calibration windows
- Any defensible direct physical provider ranking

## Validation Checks

The release-preparation audit recorded successful report generation, Ruff checks, mypy checks, pytest, CLI checks, artifact comparison, and a local secret scan with no provider credential matches. See the commit history and CI workflow for the current post-edit status.

## Final Supported Conclusion

Connectivity and native-gate structure affect circuit families differently. The proxy results show that connection-heavy GHZ and QFT circuits are more sensitive to routing constraints than the tested Bell and small Grover circuits. Physical IBM data support the expectation that added two-qubit work makes GHZ distributions harder to preserve. Quantinuum emulator data validate the small-circuit Nexus workflow. The current evidence does not establish that IBM or Quantinuum is universally superior on physical hardware.
