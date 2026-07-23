# Figure Interpretation Guide

## Definitive Publication Set

The four final figures are stored in `results/final_figures/publication/`. Every image
prints five notes beneath the graph: its question, how to read it, its result, why the
result matters, and the scientific boundary. The same notes are available as selectable
text in `results/final_figures/publication/README.md`.

1. `01_research_question_answer`: matched proxy bars for routing SWAPs, native depth,
   and native entangling gates. Lower means less compiled work.
2. `02_connectivity_scaling`: tested GHZ/QFT routing SWAP counts by qubit count. Lines
   join tested sizes and do not extrapolate beyond them.
3. `03_modeled_time_reliability`: proxy duration versus proxy success. Upper-left is
   better only within the documented fixed assumptions.
4. `04_quantinuum_emulator_validation`: mean exact-distribution fidelity and TVD for
   the completed seven-circuit Nexus emulator suite. This is not physical QPU evidence.

## Full-Suite Quantinuum Emulator Figures

The fidelity graph asks how closely each emulator's measured answer pattern matched the
exact ideal pattern. Circuits are on the x-axis; fidelity is on the y-axis, where 1 is a
perfect distribution match. Blue is `H2-1LE`, orange is `H2-Emulator`, points are
three-run means, and lines span the observed minimum to maximum. Every mean exceeded
0.984. This measurement test does not validate the complete QFT phase state.

The TVD graph asks how far measured probabilities were from ideal. Lower is better and 0
is perfect. Bars are target means; error bars show one repetition standard deviation.
QFT-5 had the largest mean TVD on both targets: 0.0761 and 0.0661.

The repetition graph shows every observation. Color identifies target and shape identifies
the repetition. Three runs describe spread but do not establish statistical significance.
All figures use 1,000 shots per circuit and three repetitions and are emulator evidence,
not physical Quantinuum QPU measurements.

Quantinuum Nexus emulator execution validates the standardized workflow and output
distributions on emulator targets. It does not constitute physical Quantinuum
trapped-ion QPU evidence and does not complete a matched physical IBM-versus-Quantinuum
benchmark.

This guide explains how to read the final figures without mixing evidence types. The
project uses three evidence categories:

- `offline_proxy`: compiled/model-estimated architecture comparison rows.
- `physical_hardware`: saved IBM `ibm_kingston` hardware counts.
- `emulator`: saved Quantinuum Nexus emulator counts.
- `syntax_checker`: compile-only provider workflow checks, when present.

No figure claims statistical significance. The figures are meant to communicate the
stored evidence clearly and conservatively.

## Relationship To Manuscript Figures

The July 2026 manuscript has its own Figure 1 through Figure 13 numbering. Repository
figures added after the manuscript keep separate labels so readers do not mistake a
supplemental graph for an original manuscript figure.

- Manuscript Figures 1-13: original paper figures and IBM GHZ stress analysis.
- Repository figures 01-03: curated proxy-model presentation figures.
- Repository supplemental figure H04: post-manuscript IBM 115-circuit validation graph.
- Repository supplemental figure Q01: Quantinuum Nexus emulator validation graph.
- Repository supplemental figures R01-R10: expanded R alternative visualizations.

The original manuscript IBM figures use distribution fidelity for the 90-circuit GHZ
stress study. The later IBM validation graphs use all-zero/all-one probability for the
115-circuit package; that metric is easiest to interpret for Bell/GHZ-style outcomes and
is not a universal algorithm success score.

## Original Final Figure Package

### 01 Simulated Success Probability

- File: `results/final_figures/01_simulated_success_probability.png`
- Graph type: faceted line/point graph.
- Evidence type: `offline_proxy`.
- Source script: `scripts/generate_final_figures.R`.
- Source data: `results/tables/qubit_grouped_statistics.csv`.
- Number of observations: 14 grouped proxy rows.
- Main research question: How does model-estimated success change by circuit family,
  qubit count, and architecture proxy?
- Why this graph type: qubit count is ordered, so lines can show how the proxy estimate
  changes as circuit size increases.
- X-axis: qubits in the logical circuit.
- Y-axis: estimated success probability from the proxy error model.
- Color/line: superconducting proxy versus trapped-ion proxy.
- Facets: algorithm family.
- Main result visible: GHZ and QFT show a larger separation between the two proxy models
  as size increases.
- Plain-language explanation: Higher points mean the model predicts the circuit is more
  likely to finish correctly. The biggest differences appear for larger GHZ and QFT
  circuits.
- Scientific warning: Proxy-estimated success is not measured hardware fidelity.
- Presentation script: "This figure shows the modeled success probability for the same
  circuits after each architecture proxy compiles them. The main takeaway is that
  topology matters more for some circuit families than for others."

### 02 Simulated Routing SWAP Cost

- File: `results/final_figures/02_simulated_routing_swap_cost.png`
- Graph type: faceted line/point graph.
- Evidence type: `offline_proxy`.
- Source script: `scripts/generate_final_figures.R`.
- Source data: `results/tables/qubit_grouped_statistics.csv`.
- Number of observations: 14 grouped proxy rows.
- Main research question: How much routing detour work does each architecture proxy add?
- Why this graph type: routing SWAP count is tracked across ordered qubit counts.
- X-axis: qubits in the logical circuit.
- Y-axis: mean routing SWAP count.
- Color/line: superconducting proxy versus trapped-ion proxy.
- Facets: algorithm family.
- Main result visible: GHZ and QFT require added SWAPs on the line-connected
  superconducting proxy, while the all-to-all trapped-ion proxy avoids routing SWAPs in
  these tested cases.
- Plain-language explanation: A SWAP is an extra move the computer must make when two
  qubits cannot connect directly. More SWAPs mean the circuit must take more detours.
- Scientific warning: Routing SWAP count is a compiler/proxy metric, not a direct
  provider benchmark.
- Presentation script: "This graph shows why connectivity matters. When long-range
  interactions are needed, the line-connected model has to add routing moves."

### 03 Simulated Time Reliability Tradeoff

- File: `results/final_figures/03_simulated_time_reliability_tradeoff.png`
- Graph type: faceted scatter plot.
- Evidence type: `offline_proxy`.
- Source script: `scripts/generate_final_figures.R`.
- Source data: `results/tables/qubit_grouped_statistics.csv`.
- Number of observations: 14 grouped proxy rows.
- Main research question: How do model-estimated runtime and model-estimated reliability
  move together?
- Why this graph type: it compares two numerical model outputs at the same time.
- X-axis: estimated native execution duration in microseconds.
- Y-axis: estimated success probability.
- Color: architecture proxy.
- Point size: qubit count.
- Facets: algorithm family.
- Main result visible: the proxy models separate most strongly for GHZ and QFT.
- Plain-language explanation: Points farther right take more estimated time. Points
  higher up have better estimated reliability, so the best area is usually toward the
  upper left.
- Scientific warning: Runtime and success are calculated from fixed assumptions, not
  measured hardware timing.
- Presentation script: "This plot puts speed and reliability estimates on the same
  page. It shows that the main conclusion depends on the circuit family, not one single
  winner across everything."

### 04 IBM Hardware Probability By Bit Width

- File: `results/final_figures/04_ibm_hardware_expected_state_probability.png`
- Repository label: supplemental figure H04.
- Manuscript correspondence: post-manuscript validation figure; it is not Manuscript
  Figure 9, 10, 11, or 12.
- Graph type: box plot with visible observations.
- Evidence type: `physical_hardware`.
- Source script: `scripts/generate_final_figures.R`.
- Source data: `results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv`.
- Number of observations: 115 physical-hardware validation circuits.
- Main research question: What all-zero/all-one probability did the later IBM Kingston
  validation package return by bit width?
- Why this graph type: the IBM job has multiple pub results per measured bit-width
  group, so a box plot shows spread and individual observations.
- X-axis: measured bit width.
- Y-axis: all-zero/all-one probability.
- Color: IBM `ibm_kingston` hardware.
- Main result visible: the all-zero/all-one probability generally declines and spreads
  across wider mixed validation circuits.
- Plain-language explanation: Higher values mean the real IBM hardware measured all
  zeros or all ones more often. This measure is most useful for Bell and GHZ-style
  circuits and is not a score for every algorithm.
- Scientific warning: All-zero/all-one probability is most direct for Bell/GHZ-style
  circuits and is not a universal algorithm success metric.
- Dataset: later 115-circuit IBM validation package, job `d95vhvd2su3c739gc080`.
- Presentation script: "This is the real IBM hardware validation. It is separate from
  the proxy-model tables, and the metric is easiest to interpret for Bell and GHZ-style
  circuits."

### 05 Quantinuum Nexus Emulator Validation

- File: `results/final_figures/05_quantinuum_nexus_emulator_validation.png`
- Repository label: supplemental figure Q01.
- Manuscript correspondence: post-manuscript emulator validation figure.
- Graph type: grouped bar graph.
- Evidence type: `emulator`.
- Source script: `scripts/generate_final_figures.R`.
- Source data: `results/tables/quantinuum_validation_plot_rows.csv`.
- Number of observations: 6 emulator result rows.
- Main research question: What did the Quantinuum Nexus emulator return for the stored
  small validation circuits?
- Why this graph type: there are a few named validation circuits and two emulator
  targets, which makes category comparison appropriate.
- X-axis: validation circuit.
- Y-axis: all-zero/all-one probability.
- Fill color: Nexus emulator target.
- Main result visible: the small emulator validation circuits returned the expected
  answer pattern near 99-100%.
- Plain-language explanation: Higher bars mean the emulator returned the expected answer
  pattern more often. These results came from a Quantinuum Nexus emulator, not a
  physical H2 quantum computer.
- Scientific warning: Nexus emulator results are not physical Quantinuum QPU
  measurements.
- Presentation script: "This shows the Quantinuum Nexus emulator validation only. It
  confirms the workflow and small circuit behavior, but it is not physical Quantinuum
  QPU evidence."

## Expanded R Visualization Package

### R01 Algorithm Architecture Grouped Bar

- File: `results/final_figures/r_visualizations/r01_algorithm_architecture_grouped_bar.png`
- Graph type: grouped bar graph.
- Why this graph type: bar graphs compare separate categories clearly.
- X-axis: algorithm family.
- Y-axis: mean native-compiled depth.
- Fill color: architecture proxy.
- Main result visible: QFT and GHZ show much larger native-depth differences than Bell
  or the current small Grover circuit.
- What it does not prove: means across configured sizes are not hardware measurements.
- Evidence type: `offline_proxy`.
- Presentation script: "This bar graph shows which circuit families became deeper after
  compilation for each architecture model."

### R02 Native Depth Distribution Boxplot

- File: `results/final_figures/r_visualizations/r02_native_depth_distribution_boxplot.png`
- Graph type: box plot with jittered observations.
- Why this graph type: it shows both spread and individual rows.
- X-axis: architecture proxy.
- Y-axis: native-compiled depth.
- Shape: algorithm family.
- Main result visible: the superconducting proxy has a wider spread because some tested
  circuit families require more routing and decomposition.
- What it does not prove: deterministic repetitions should not be interpreted as random
  experimental trials.
- Evidence type: `offline_proxy`.
- Presentation script: "The box plot helps show not just an average, but how varied the
  compiled depth is across the saved proxy rows."

### R03 Gate Count Vs Fidelity Scatter

- File: `results/final_figures/r_visualizations/r03_gate_count_vs_fidelity_scatter.png`
- Graph type: scatter plot.
- Why this graph type: scatter plots show possible relationships between two numerical
  measurements.
- X-axis: native entangling-gate count.
- Y-axis: estimated success probability.
- Color: architecture proxy.
- Shape: algorithm family.
- Main result visible: rows with more native entangling gates generally sit lower in
  proxy-estimated success.
- What it does not prove: no causation or statistical significance test is claimed.
- Evidence type: `offline_proxy`.
- Presentation script: "This scatter plot checks whether more entangling work tends to
  line up with lower modeled success probability."

### R04 Scaling By Qubit Count Line

- File: `results/final_figures/r_visualizations/r04_scaling_by_qubit_count_line.png`
- Graph type: faceted line/point graph.
- Why this graph type: qubit count is ordered.
- X-axis: qubits in the logical circuit.
- Y-axis: mean routing SWAP count.
- Color/line: architecture proxy.
- Facets: algorithm family.
- Main result visible: routing overhead grows for GHZ and QFT on the superconducting
  proxy but stays at zero on the trapped-ion proxy for these tested cases.
- What it does not prove: line segments are not continuous physical laws.
- Evidence type: `offline_proxy`.
- Presentation script: "This line graph shows how routing overhead scales as the
  configured circuit size grows."

### R05 Algorithm Architecture Heatmap

- File: `results/final_figures/r_visualizations/r05_algorithm_architecture_heatmap.png`
- Graph type: heat map.
- Why this graph type: heat maps make matrix-style patterns quick to see.
- X-axis: architecture proxy.
- Y-axis: algorithm family.
- Fill color: raw mean routing SWAP count.
- Main result visible: the routing overhead is concentrated in the superconducting proxy
  for GHZ and QFT.
- What it does not prove: color intensity only represents SWAP count, not runtime,
  fidelity, or overall quality.
- Evidence type: `offline_proxy`.
- Presentation script: "The heat map is a quick visual summary of where routing overhead
  appears in the study."

### R06 Matched Architecture Slopegraph

- File: `results/final_figures/r_visualizations/r06_matched_architecture_slopegraph.png`
- Graph type: slope graph.
- Why this graph type: the same logical circuit is paired across two architecture
  proxies.
- X-axis: architecture proxy.
- Y-axis: estimated success probability.
- Color/shape: algorithm family.
- Main result visible: many matched circuits have higher estimated success under the
  trapped-ion proxy assumptions.
- What it does not prove: it does not compare measured IBM hardware to measured
  Quantinuum hardware.
- Evidence type: `offline_proxy`.
- Presentation script: "Each line follows one matched circuit from one model to the
  other, so the reader can see the change directly."

### R07 Proxy Results Faceted

- File: `results/final_figures/r_visualizations/r07_proxy_results_faceted.png`
- Graph type: faceted small-multiple graph.
- Why this graph type: facets prevent incompatible units from being forced onto one
  crowded axis.
- X-axis: qubits in the logical circuit.
- Y-axis: mean value for the metric in that row of facets.
- Color: architecture proxy.
- Facets: metric and algorithm family.
- Main result visible: the same architecture difference appears through several
  metrics, especially for GHZ and QFT.
- What it does not prove: y-axis scales differ by metric row, so heights across rows
  should not be compared directly.
- Evidence type: `offline_proxy`.
- Presentation script: "This small-multiple graph lets us compare several metrics
  without pretending they share the same unit."

### R08 IBM Hardware Probability CI

- File: `results/final_figures/r_visualizations/r08_ibm_hardware_probability_ci.png`
- Repository label: supplemental figure R08.
- Manuscript correspondence: post-manuscript validation figure; it is not one of the
  manuscript's IBM GHZ distribution-fidelity figures.
- Graph type: dot plot with Wilson confidence intervals.
- Why this graph type: shot counts support binomial intervals after aggregating by bit
  width.
- X-axis: measured bit width.
- Y-axis: all-zero/all-one probability.
- Point size: number of pub results in the bit-width group.
- Main result visible: the aggregated IBM probability is highest for 2-bit results and
  lower for wider mixed validation circuits.
- What it does not prove: this all-zero/all-one metric is not universal algorithm
  accuracy.
- Evidence type: `physical_hardware`.
- Dataset: later 115-circuit IBM validation package, not the original 90-circuit GHZ
  stress study.
- Presentation script: "This IBM hardware plot adds uncertainty intervals from the
  saved shot counts, while keeping the interpretation limited to this specific metric."

### R09 Quantinuum Emulator Results

- File: `results/final_figures/r_visualizations/r09_quantinuum_emulator_results.png`
- Graph type: grouped bar graph.
- Why this graph type: it compares a small set of categories.
- X-axis: validation circuit.
- Y-axis: all-zero/all-one probability.
- Fill color: Nexus emulator target.
- Main result visible: both emulator targets returned near-ideal small-circuit results.
- What it does not prove: it is not physical Quantinuum QPU evidence.
- Evidence type: `emulator`.
- Presentation script: "This figure is intentionally labeled as emulator validation,
  because it should not be mistaken for physical Quantinuum QPU evidence."

### R10 Evidence Summary

- File: `results/final_figures/r_visualizations/r10_evidence_summary.png`
- Graph type: bar graph.
- Why this graph type: it compares record counts across evidence categories.
- X-axis: evidence category.
- Y-axis: stored result records.
- Fill color: evidence type.
- Main result visible: the repository preserves proxy rows, IBM hardware pub results,
  and Quantinuum emulator rows as separate evidence categories.
- What it does not prove: more records do not mean better or stronger evidence.
- Evidence type: mixed summary.
- Presentation script: "This is not a performance graph; it simply shows what kinds of
  evidence are saved in the repository."
