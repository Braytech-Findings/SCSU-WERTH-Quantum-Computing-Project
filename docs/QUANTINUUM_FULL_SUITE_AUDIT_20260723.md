# Quantinuum Full-Suite Pre-Submission Audit

Date: 2026-07-23

This audit was completed before any new Quantinuum Nexus submission. The requested
evidence class is **Quantinuum Nexus emulator validation**. It is not physical
Quantinuum trapped-ion QPU evidence.

## Findings

- `build_validation_suite("matched")` contained six circuits, omitted `ghz_7`, and put
  `grover_search_2` after both QFT circuits. The manuscript order requires seven circuits:
  Bell-2, GHZ-3, GHZ-5, GHZ-7, Grover-2, QFT-3, and QFT-5.
- Nexus result artifacts associated outputs with numeric result indices only. That made
  circuit identity depend on remembering the submission order. Each new run needs an
  immutable circuit manifest and circuit-aware result rows.
- The legacy compact summary used all-zero/all-one probability for every circuit. That
  support metric is meaningful for Bell and GHZ circuits, and marked-state probability is
  meaningful for Grover, but neither is a universal QFT score. New analysis must use
  classical distribution fidelity and total variation distance against the exact noiseless
  logical-circuit distribution.
- Qiskit displays classical bitstrings with the highest-index classical bit on the left.
  Nexus key formats must be normalized to that convention and tested explicitly.
- Documentation correctly calls the July 14 results emulator evidence in many places, but
  some status and workflow text still discusses only the small suite or uses broad
  "hardware validation" wording. Full-suite completion must be stated only if all requested
  emulator executions and retrievals finish.

## Preserved Legacy Evidence

The July 14, 2026 small-suite files below are historical evidence and must not be renamed,
overwritten, or reinterpreted as full-suite results:

- `results/hardware/quantinuum_submission_H2-1LE_20260714T173914Z.json`
- `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z.json`
- `results/hardware/quantinuum_job_H2-1LE_20260714T173914Z_summary.csv`
- `results/hardware/quantinuum_submission_H2-Emulator_20260714T175518Z.json`
- `results/hardware/quantinuum_job_H2-Emulator_20260714T175518Z.json`
- `results/hardware/quantinuum_job_H2-Emulator_20260714T175518Z_summary.csv`
- the July 14 compile/access records for `H2-1E` and `H2-2E`

New artifacts will use timestamped, non-overwriting filenames. No execution will proceed
unless live catalog metadata confirms an executable emulator target and the account path
shows institutional simulator quota with no monetary charge or paid overage.

## Claim Boundary

> Quantinuum Nexus emulator execution validates the standardized workflow and output
> distributions on emulator targets. It does not constitute physical Quantinuum
> trapped-ion QPU evidence and does not complete a matched physical IBM-versus-Quantinuum
> benchmark.
