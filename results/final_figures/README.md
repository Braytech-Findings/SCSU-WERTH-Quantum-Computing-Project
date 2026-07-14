# Final Figures

This folder contains the curated, presentation-ready figures for the project.

| File | Evidence type | Simple explanation | Scientific warning |
| --- | --- | --- | --- |
| `01_simulated_success_probability.png` | `offline_proxy` | Higher points mean the model predicts the circuit is more likely to finish correctly. The biggest differences appear for larger GHZ and QFT circuits. | Proxy-estimated success is not measured hardware fidelity. |
| `02_simulated_routing_swap_cost.png` | `offline_proxy` | A SWAP is an extra move the computer must make when two qubits cannot connect directly. More SWAPs mean the circuit must take more detours. | Routing SWAP count is a compiler/proxy metric, not a direct provider benchmark. |
| `03_simulated_time_reliability_tradeoff.png` | `offline_proxy` | Points farther right take more estimated time. Points higher up have better estimated reliability, so the best area is usually toward the upper left. | Runtime and success are calculated from fixed assumptions, not measured hardware timing. |
| `04_ibm_hardware_expected_state_probability.png` | `physical_hardware` | Higher values mean the real IBM hardware measured all zeros or all ones more often. This measure is most useful for Bell and GHZ-style circuits and is not a score for every algorithm. | All-zero/all-one probability is not a universal algorithm success metric. |
| `05_quantinuum_nexus_emulator_validation.png` | `emulator` | Higher bars mean the emulator returned the expected answer pattern more often. These results came from a Quantinuum Nexus emulator, not a physical H2 quantum computer. | Nexus emulator results are not physical Quantinuum QPU measurements. |

The first three figures are simulated/proxy-model results. The IBM figure is real hardware output. The Quantinuum figure is provider emulator output, not physical Quantinuum QPU output.

Figure labels are separate from the manuscript's Figure 1-13 numbering. The IBM
validation graph is repository supplemental figure H04, and the Quantinuum emulator
graph is repository supplemental figure Q01.

Expanded R visualizations are stored in:

`results/final_figures/r_visualizations/`

Those figures are documented in `docs/FIGURE_INTERPRETATION_GUIDE.md` and
`reports/R_VISUAL_ANALYSIS.md`.

Regenerate these files with:

```bash
Rscript scripts/generate_final_figures.R
```
