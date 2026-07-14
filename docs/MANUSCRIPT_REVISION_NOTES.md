# Manuscript Revision Notes

The repository does not contain an editable manuscript source or a documented manuscript
build workflow. A PDF and `.docx` copy were found outside the repository in the local
Downloads folder, but they are not part of version-controlled project source. For that
reason, this file provides ready-to-paste conservative revision text instead of editing
or overwriting the manuscript PDF.

## Cover Study Status

Replace the study-status paragraph with:

> Completed: a controlled comparison of the same standardized Bell, GHZ, Grover, and
> QFT circuits across two hardware-inspired architecture models; a 90-circuit IBM
> Kingston GHZ stress experiment; a separate expanded IBM Kingston validation package;
> and Quantinuum Nexus emulator validation for the stored small-circuit suite. Pending:
> matched execution of the complete standardized suite on a physical trapped-ion QPU.
> The study asks which hardware features fit which algorithm structures; it does not
> claim one company or qubit technology is best at everything.

## Abstract

Keep the original abstract and add this final sentence:

> Subsequent repository validation added a separate 115-circuit IBM Kingston hardware
> package and small-circuit Quantinuum Nexus emulator executions. These supplemental
> results broaden workflow validation but do not constitute a matched physical
> comparison between superconducting and trapped-ion QPUs. A complete matched
> multi-QPU physical-hardware study remains future work.

## Section 1.3 Evidence Categories

Replace the final evidence-category sentence with:

> The architecture comparison is a controlled offline proxy study. The IBM Kingston
> jobs are physical-hardware evidence. The Quantinuum Nexus results now stored in the
> repository are emulator and syntax-checker workflow evidence, not physical Quantinuum QPU
> measurements. These evidence streams are kept separate so model assumptions,
> emulator outputs, syntax checks, and physical-hardware measurements are never
> presented as the same kind of result.

## Section 5.1 Overall Study Design

Replace the first paragraph with:

> The project is now best described in three evidence phases. Phase I held the logical
> algorithm constant and changed the hardware-inspired target. This directly tested
> whether standardized algorithms respond differently to architecture. Phase II used
> IBM Kingston physical hardware to test a supporting mechanism: whether added
> two-qubit work makes a GHZ result harder to preserve. Phase III added Quantinuum
> Nexus emulator validation for a stored small-circuit suite. Model outputs, emulator
> results, syntax-checker records, and physical-hardware measurements were saved and
> reported separately.

## Section 5.3 Software Verification

Add after the 26/26 paragraph:

> The 26/26 result refers to the historical qBraid reproduction checklist used for the
> manuscript. During v1.0.0 repository preparation, the current local pytest suite
> contained 28 passing tests. These numbers describe different validation moments and
> should not be collapsed into one test count.

## Sections 5.4-6.12 IBM GHZ Analysis

Do not replace the original IBM GHZ values. Preserve:

- 90 circuits.
- 30 qubit-count-by-stress conditions.
- 3 transpiler-seed repetitions per condition.
- 4096 shots per circuit.
- 368640 total shots.
- Job identifier `d8up2d1ropqc738b44pg`.
- Pearson `r = -0.911`, Spearman `rho = -0.876`, reported slope, and `R^2`.

If adding a supplement, use:

> A later repository validation package used IBM Kingston again, but it was a separate
> 115-circuit validation job with job identifier `d95vhvd2su3c739gc080`. It is not the
> dataset used for the manuscript's GHZ stress statistics.

## Section 6.14 Interpretation

Add to the end of the section:

> Later Quantinuum Nexus emulator results support small-circuit workflow validation and
> provider-platform portability, but they do not establish physical trapped-ion QPU
> performance and do not complete a direct IBM-versus-Quantinuum physical-hardware
> comparison.

## Section 7 Timeline

Replace the "Matched Quantinuum run" row with two rows:

| Stage | Status | What happened |
| --- | --- | --- |
| Quantinuum Nexus emulator validation | Complete | Ran the stored small-circuit validation suite on Nexus emulator targets and saved sanitized counts. |
| Matched physical Quantinuum QPU comparison | Pending | Needed to turn the architecture-model comparison into a matched physical trapped-ion QPU comparison. |

## Section 8 Summary

Add these bullets after the original IBM Kingston bullet:

> A separate later IBM Kingston validation package stored 115 physical-hardware pub
> results with 4096 shots per circuit. It is supplemental validation evidence and is
> not merged with the original 90-circuit GHZ statistical analysis.

> Quantinuum Nexus emulator validation was completed for the stored small-circuit
> suite. These executions provide provider-platform emulator evidence, not physical Quantinuum QPU
> QPU measurements.

## Section 9 Future Work

Replace the first future-work bullet with:

> Run the complete standardized Bell, GHZ, Grover, and QFT suite on a physical
> trapped-ion QPU using matched circuit definitions, sizes, shots, repeats, compiler
> goals, dates, and scoring rules. Repeat physical-hardware runs across calibration
> windows before making provider-level or technology-level comparisons.

## Appendix D Reproducibility Record

Replace the final evidence-category paragraph with:

> The project keeps evidence categories separate: (1) offline proxy results, (2) IBM
> physical-hardware results, (3) Quantinuum Nexus emulator results, (4)
> syntax-checker/compiler-validation records where present, and (5) future matched
> physical trapped-ion QPU results. Missing future hardware values are not filled with
> estimates. This separation is part of the research-integrity design.
