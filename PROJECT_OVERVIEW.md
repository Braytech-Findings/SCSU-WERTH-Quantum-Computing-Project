# Project Overview

> [!IMPORTANT]
> **Evidence status:** The IBM results are physical `ibm_kingston` QPU measurements. The Quantinuum results are Nexus emulator measurements and compile-only checks. The project is not yet a matched physical IBM-versus-Quantinuum hardware benchmark.

## What Was Built

This project contains a reproducible comparison of the same logical quantum circuits across two controlled architecture proxy models, plus separate provider evidence. The proxy study compares a nearest-neighbor superconducting-style model with an all-to-all trapped-ion-style model. The provider evidence contains physical IBM Kingston QPU measurements and Quantinuum Nexus emulator measurements.

## Evidence Categories

1. **Offline proxy comparison:** Bell, GHZ, Grover, and QFT compilation and model metrics.
2. **IBM physical hardware:** saved results from `ibm_kingston`.
3. **Quantinuum emulator:** saved results from `H2-1LE` and `H2-Emulator`, plus compile-only checks for `H2-1E` and `H2-2E`.
4. **Pending future work:** a matched execution of the full standardized suite on a physical Quantinuum QPU.

## How the Comparison Works

Every configured circuit begins as the same logical recipe. The workflow measures logical depth, routed depth, routing SWAPs, native-compiled depth, native two-qubit work, model-estimated duration, and model-estimated success. The provider artifacts are stored separately and are never substituted for the proxy rows.

## What the Results Suggest

For the tested GHZ and QFT circuits, nearest-neighbor connectivity creates substantial routing overhead. The all-to-all model avoids routing SWAPs for those circuits under the selected assumptions. The IBM physical experiment separately shows that extra compiled two-qubit work is associated with lower GHZ distribution fidelity. The Quantinuum emulator runs confirm that the small validation suite can be compiled and executed through Nexus.

## What the Results Do Not Prove

The project does not yet compare physical IBM and physical Quantinuum QPUs under matched conditions. The Quantinuum results are emulator outputs, not physical trapped-ion hardware measurements. The evidence therefore does not prove that one provider, architecture, or qubit technology is universally superior.

## Independent Student Contribution

The student independently implemented the circuit suite, architecture-aware compilation, metrics, validation tables, figures, reports, tests, provider-result packaging, and qBraid validation workflow. The public repository is sanitized and excludes credentials and protected materials.
