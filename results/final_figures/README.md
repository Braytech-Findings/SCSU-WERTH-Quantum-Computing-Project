# Final Figures

This folder contains the curated, presentation-ready figures for the project.

| File | What it shows |
| --- | --- |
| `01_simulated_success_probability.png` | Estimated success probability from the offline superconducting and trapped-ion proxy models. |
| `02_simulated_routing_swap_cost.png` | Routing overhead from the offline proxy models, focused on added SWAP operations. |
| `03_simulated_time_reliability_tradeoff.png` | Estimated runtime versus estimated success probability from the offline proxy models. |
| `04_ibm_hardware_expected_state_probability.png` | Real IBM `ibm_kingston` hardware validation counts from job `d95vhvd2su3c739gc080`. |
| `05_quantinuum_nexus_emulator_validation.png` | Quantinuum Nexus emulator validation counts from `H2-1LE` and `H2-Emulator`. |

The first three figures are simulated/proxy-model results. The IBM figure is real hardware output. The Quantinuum figure is provider emulator output, not physical H2 hardware output.

Expanded R visualizations are stored in:

`results/final_figures/r_visualizations/`

Those figures are documented in `docs/FIGURE_INTERPRETATION_GUIDE.md` and
`reports/R_VISUAL_ANALYSIS.md`.

Regenerate these files with:

```bash
Rscript scripts/generate_final_figures.R
```
