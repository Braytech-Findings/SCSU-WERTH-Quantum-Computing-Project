# R Visual Analysis Report

## Research Question

How can the saved quantum-architecture comparison results be communicated with graph
types that match the structure of the data?

The visual analysis keeps three evidence types separate:

- `offline_proxy`: architecture-model compilation and proxy-estimate rows.
- `physical_hardware`: IBM `ibm_kingston` hardware counts.
- `emulator`: Quantinuum Nexus emulator counts.

## Data Sources

- `results/tables/architecture_validation_table.csv`
- `results/tables/qubit_grouped_statistics.csv`
- `results/tables/matched_size_architecture_comparison.csv`
- `results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv`
- `results/tables/quantinuum_validation_plot_rows.csv`

No new experiments or provider jobs are run by the R script.

## Data-Cleaning Steps

The script `analysis/generate_final_figures_r.R`:

1. Reads existing repository CSV files with relative paths.
2. Renames provider labels into plain language for display.
3. Converts circuit-family names into consistent display labels.
4. Aggregates means directly from stored rows when a figure needs an average.
5. Calculates Wilson 95% binomial intervals for the IBM hardware probability figure
   using saved counts and shot totals.
6. Writes high-resolution PNG and PDF files to
   `results/final_figures/r_visualizations/`.

## Variables Used

- Algorithm family: Bell, GHZ, QFT, and Grover.
- Architecture proxy: superconducting proxy and trapped-ion proxy.
- Circuit size: qubit count or measured bit width.
- Proxy metrics: native-compiled depth, native entangling-gate count, routing SWAP
  count, estimated native execution duration, and estimated success probability.
- Hardware/emulator metrics: all-zero/all-one counts and probability.

## Why Each Graph Type Was Used

- Grouped bar graphs compare separate algorithm or target categories.
- Box plots show the spread and middle of repeated stored observations.
- Scatter plots show whether two numerical proxy measurements appear related.
- Line graphs are used only when the x-axis is ordered by circuit size.
- Heat maps show matrix-style algorithm-by-architecture patterns.
- Slope graphs show paired changes for the same logical circuit across architecture
  proxies.
- Faceted small multiples prevent incompatible metrics from being squeezed into one
  crowded scale.
- Wilson interval plots are used for IBM hardware probabilities because shot counts are
  available.

## Major Visual Findings

- GHZ and QFT expose the largest architecture-proxy differences in routing SWAP count,
  native depth, and estimated success probability.
- Bell and the current 2-qubit Grover case are too small to support broad architecture
  conclusions.
- The IBM hardware validation figure shows real `ibm_kingston` counts, but the
  all-zero/all-one probability should be read most carefully for Bell/GHZ-style
  circuits.
- The Quantinuum Nexus figures are emulator validation evidence, not physical H2
  hardware benchmarking.
- The evidence-summary graph shows record counts only; it does not rank evidence
  quality.

## Important Cautions

- The offline proxy estimates are not live hardware calibration data.
- The IBM hardware results and Quantinuum emulator results answer different questions
  and should not be merged into one performance ranking.
- No statistical significance tests were performed.
- Wilson intervals are used only where saved binomial count data support them.
- The final supported conclusion is limited: connectivity and native-gate structure
  affect circuit families differently. The tested results do not establish that one
  hardware architecture is universally superior.

## Generated Figures

The manifest for the R figures is:

`results/final_figures/r_visualizations/r_visualizations_manifest.csv`

The generated R figures are:

- `results/final_figures/r_visualizations/r01_algorithm_architecture_grouped_bar.png`
- `results/final_figures/r_visualizations/r02_native_depth_distribution_boxplot.png`
- `results/final_figures/r_visualizations/r03_gate_count_vs_fidelity_scatter.png`
- `results/final_figures/r_visualizations/r04_scaling_by_qubit_count_line.png`
- `results/final_figures/r_visualizations/r05_algorithm_architecture_heatmap.png`
- `results/final_figures/r_visualizations/r06_matched_architecture_slopegraph.png`
- `results/final_figures/r_visualizations/r07_proxy_results_faceted.png`
- `results/final_figures/r_visualizations/r08_ibm_hardware_probability_ci.png`
- `results/final_figures/r_visualizations/r09_quantinuum_emulator_results.png`
- `results/final_figures/r_visualizations/r10_evidence_summary.png`

PDF versions are saved beside the PNG files.

## Reproduction Instructions

Install the required R packages if needed:

```r
install.packages(c(
  "ggplot2",
  "dplyr",
  "tidyr",
  "readr",
  "scales"
))
```

Run from the repository root:

```bash
Rscript analysis/generate_final_figures_r.R
```
