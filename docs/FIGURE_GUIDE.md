# Figure Guide

The authoritative per-figure explanations are in [FIGURE_INTERPRETATION_GUIDE.md](FIGURE_INTERPRETATION_GUIDE.md). That guide identifies what each main figure asks, the source table, what beginners and technical readers should notice, and the relevant limitation. The final-figure directories also contain manifests that bind images to their generated data:

- `results/final_figures/final_figures_manifest.csv`
- `results/final_figures/r_visualizations/r_visualizations_manifest.csv`
- `results/final_figures/README.md`
- `results/final_figures/r_visualizations/README.md`

## Regeneration

```bash
python -m quantum_compare.cli report
Rscript scripts/generate_final_figures.R
Rscript analysis/generate_final_figures_r.R
```

The first command regenerates the Python report assets. The R commands regenerate the two committed final-figure collections when R and their documented packages are installed. Inspect titles, axes, legends, evidence labels, and the manifests after regeneration. Proxy estimates, IBM physical-hardware measurements, and Quantinuum emulator measurements must remain visibly distinct.

## Reading rules

- Blue denotes the superconducting/IBM-style route; gold denotes trapped-ion/Quantinuum-style results.
- Gray denotes ideal or neutral comparison data, and green marks provider validation evidence.
- Color is reinforced by labels, facets, shapes, or captions; never infer evidence type from color alone.
- Duration and success probability in proxy figures are model-dependent estimates, not live device measurements.
- IBM and Quantinuum provider plots are not a matched physical-QPU comparison.
