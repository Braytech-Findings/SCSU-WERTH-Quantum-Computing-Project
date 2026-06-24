# Project Overview

## What Was Built

This project builds a reproducible offline comparison of two quantum-computing
architecture proxy models. The IBM proxy represents a line-coupled superconducting
architecture. The Quantinuum proxy represents an all-to-all trapped-ion architecture
using an H-series-style RZZ entangling proxy. The same logical Qiskit circuits are sent
through both pipelines so their routed and native-compiled forms can be compared.

## Independent Student Contribution

The student independently implemented the circuit suite, architecture-aware proxy
compilation, metric extraction, validation tables, visualizations, reports, tests, and
qBraid validation workflow. The repository is sanitized for public review and excludes
confidential company information and nondisclosure-agreement materials.

## How The Comparison Works

Each configured circuit starts as one logical circuit. The workflow records logical
depth, routed depth, routing SWAP count, native-compiled depth, native entangling-gate
count, estimated native execution duration, and estimated success probability. The IBM
proxy models nearest-neighbor line connectivity, so long-range interactions require
routing. The Quantinuum proxy models all-to-all connectivity, so the tested circuits do
not require routing SWAP insertion.

## What The Results Suggest

For the tested GHZ and QFT circuits, line connectivity produces routing overhead in the
IBM proxy, which increases native-compiled depth and native entangling-gate count. The
Quantinuum proxy avoids routing SWAPs for these circuits and has lower estimated native
execution duration and higher estimated success probability under the selected proxy
assumptions.

## What The Results Do Not Prove

These results are not physical-hardware benchmarks. They do not measure IBM or
Quantinuum device performance, hardware fidelity, queue behavior, or calibration drift.
Estimated duration and estimated success probability depend on proxy timing and error
assumptions. The results do not prove that one architecture is universally superior.

## Possible Bioinformatics Extension

A later extension could use the same reproducible comparison framework for quantum
circuits motivated by bioinformatics, such as small sequence-alignment scoring
subroutines, graph-based protein interaction toy models, or optimization kernels for
genomic feature selection. The key next step would be to add domain-specific circuits
while preserving the same logical circuits across architecture-proxy pipelines.
