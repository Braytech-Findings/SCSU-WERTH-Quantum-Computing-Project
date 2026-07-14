#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(readr)
  library(tidyr)
})

final_dir <- "results/final_figures"
dir.create(final_dir, recursive = TRUE, showWarnings = FALSE)

provider_labels <- c(
  ibm = "Superconducting proxy",
  quantinuum = "Trapped-ion proxy"
)

provider_colors <- c(
  "Superconducting proxy" = "#0072B2",
  "Trapped-ion proxy" = "#D55E00"
)

hardware_colors <- c(
  "IBM ibm_kingston hardware" = "#0072B2",
  "H2-1LE Nexus emulator" = "#009E73",
  "H2-Emulator Nexus emulator" = "#CC79A7"
)

provider_shapes <- c(
  "Superconducting proxy" = 16,
  "Trapped-ion proxy" = 17
)

provider_linetypes <- c(
  "Superconducting proxy" = "solid",
  "Trapped-ion proxy" = "longdash"
)

theme_final <- function(base_size = 13) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", size = base_size + 5, margin = margin(b = 7)),
      plot.subtitle = element_text(color = "#333333", size = base_size + 1, margin = margin(b = 12)),
      plot.caption = element_text(color = "#333333", hjust = 0, size = base_size - 2, lineheight = 1.18),
      axis.title = element_text(face = "bold", size = base_size),
      axis.text = element_text(color = "#222222", size = base_size - 1),
      panel.grid.major = element_line(color = "#E6E6E6", linewidth = 0.35),
      panel.grid.minor = element_blank(),
      strip.text = element_text(face = "bold", size = base_size),
      legend.position = "bottom",
      legend.title = element_blank(),
      legend.text = element_text(size = base_size - 1),
      plot.margin = margin(16, 22, 18, 18)
    )
}

caption_block <- function(simple_explanation, evidence_label, warning) {
  paste0(
    paste(strwrap(paste("What this means:", simple_explanation), width = 118), collapse = "\n"),
    "\n",
    paste(strwrap(paste("Evidence:", evidence_label), width = 118), collapse = "\n"),
    "\n",
    paste(strwrap(paste("Scientific warning:", warning), width = 118), collapse = "\n")
  )
}

save_plot <- function(plot, filename, width = 11, height = 7.4) {
  path <- file.path(final_dir, filename)
  ggsave(path, plot, width = width, height = height, dpi = 320, bg = "white")
  message("Wrote ", path)
}

grouped <- read_csv("results/tables/qubit_grouped_statistics.csv", show_col_types = FALSE) %>%
  mutate(
    provider_label = recode(provider, !!!provider_labels),
    circuit_family = factor(
      circuit_family,
      levels = c("bell", "ghz", "qft", "qaoa", "grover"),
      labels = c("Bell", "GHZ", "QFT", "QAOA", "Grover")
    )
  )

architecture <- read_csv("results/tables/architecture_validation_table.csv", show_col_types = FALSE) %>%
  mutate(
    provider_label = recode(provider, !!!provider_labels),
    circuit_family = factor(
      circuit_family,
      levels = c("bell", "ghz", "qft", "qaoa", "grover"),
      labels = c("Bell", "GHZ", "QFT", "QAOA", "Grover")
    )
  )

success_rows <- grouped %>%
  filter(metric == "estimated_success_probability_from_proxy_error_model")

success_line_rows <- success_rows %>%
  group_by(circuit_family, provider_label) %>%
  filter(n() > 1) %>%
  ungroup()

success_plot <- ggplot(
  success_rows,
  aes(
    x = qubit_count,
    y = mean,
    color = provider_label,
    shape = provider_label,
    linetype = provider_label,
    group = provider_label
  )
) +
  geom_line(data = success_line_rows, linewidth = 1.05) +
  geom_point(size = 2.9, stroke = 0.8) +
  facet_wrap(~ circuit_family, scales = "free_x") +
  scale_color_manual(values = provider_colors) +
  scale_shape_manual(values = provider_shapes) +
  scale_linetype_manual(values = provider_linetypes) +
  scale_x_continuous(breaks = sort(unique(success_rows$qubit_count))) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "Simulated Architecture Result: Estimated Success Probability",
    subtitle = "Controlled proxy model - not measured hardware performance",
    x = "Qubits in logical circuit",
    y = "Estimated success probability",
    caption = caption_block(
      "Higher points mean the model predicts the circuit is more likely to finish correctly. The biggest differences appear for larger GHZ and QFT circuits.",
      "offline_proxy",
      "These are model estimates, not live calibration values."
    )
  ) +
  theme_final()

save_plot(success_plot, "01_simulated_success_probability.png")

swap_rows <- grouped %>%
  filter(metric == "routing_swap_count")

swap_line_rows <- swap_rows %>%
  group_by(circuit_family, provider_label) %>%
  filter(n() > 1) %>%
  ungroup()

swap_plot <- ggplot(
  swap_rows,
  aes(
    x = qubit_count,
    y = mean,
    color = provider_label,
    shape = provider_label,
    linetype = provider_label,
    group = provider_label
  )
) +
  geom_line(data = swap_line_rows, linewidth = 1.05) +
  geom_point(size = 2.9, stroke = 0.8) +
  facet_wrap(~ circuit_family, scales = "free_x") +
  scale_color_manual(values = provider_colors) +
  scale_shape_manual(values = provider_shapes) +
  scale_linetype_manual(values = provider_linetypes) +
  scale_x_continuous(breaks = sort(unique(swap_rows$qubit_count))) +
  labs(
    title = "Simulated Architecture Result: Routing SWAP Cost",
    subtitle = "Controlled proxy model - lower is usually better",
    x = "Qubits in logical circuit",
    y = "Mean routing SWAP count",
    caption = caption_block(
      "A SWAP is an extra move the computer must make when two qubits cannot connect directly. More SWAPs mean the circuit must take more detours.",
      "offline_proxy",
      "Routing SWAP count is a compiler/proxy metric, not a direct provider benchmark."
    )
  ) +
  theme_final()

save_plot(swap_plot, "02_simulated_routing_swap_cost.png")

tradeoff_rows <- architecture %>%
  group_by(circuit_family, provider_label, qubit_count) %>%
  summarize(
    duration_us = mean(estimated_native_execution_duration_us, na.rm = TRUE),
    success_probability = mean(estimated_success_probability_from_proxy_error_model, na.rm = TRUE),
    .groups = "drop"
  )

tradeoff_plot <- ggplot(
  tradeoff_rows,
  aes(
    x = duration_us,
    y = success_probability,
    color = provider_label,
    shape = provider_label,
    size = qubit_count
  )
) +
  geom_point(alpha = 0.86, stroke = 0.8) +
  facet_wrap(~ circuit_family, scales = "free_x") +
  scale_color_manual(values = provider_colors) +
  scale_shape_manual(values = provider_shapes) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  scale_size_continuous(range = c(2.6, 6.8)) +
  labs(
    title = "Simulated Architecture Result: Time vs. Reliability Tradeoff",
    subtitle = "Controlled model estimates - not provider speed measurements",
    x = "Estimated native execution duration (microseconds)",
    y = "Estimated success probability",
    size = "Qubits",
    caption = caption_block(
      "Points farther right take more estimated time. Points higher up have better estimated reliability, so the best area is usually toward the upper left.",
      "offline_proxy",
      "Runtime and success are both estimated from fixed documented assumptions."
    )
  ) +
  theme_final()

save_plot(tradeoff_plot, "03_simulated_time_reliability_tradeoff.png")

ibm_summary <- read_csv(
  "results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv",
  show_col_types = FALSE
) %>%
  mutate(
    bit_width = factor(bit_width),
    hardware_label = "IBM ibm_kingston hardware"
  )

ibm_shots_per_circuit <- unique(ibm_summary$shots)
if (length(ibm_shots_per_circuit) != 1 || ibm_shots_per_circuit != 4096) {
  stop("Unexpected IBM shot count in results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv")
}

ibm_plot <- ggplot(
  ibm_summary,
  aes(x = bit_width, y = all_zero_or_all_one_probability)
) +
  geom_boxplot(
    fill = "#DCEBF7",
    color = "#0072B2",
    width = 0.62,
    linewidth = 0.55,
    outlier.shape = NA
  ) +
  geom_jitter(
    aes(color = hardware_label),
    width = 0.16,
    height = 0,
    size = 2.1,
    alpha = 0.82
  ) +
  scale_color_manual(values = hardware_colors) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "IBM Kingston Hardware: All-Zero/All-One Probability by Bit Width",
    subtitle = "115 physical-hardware validation circuits, 4,096 shots per circuit",
    x = "Measured bit width",
    y = "All-zero/all-one probability",
    caption = caption_block(
      "Higher values mean the real IBM hardware measured all zeros or all ones more often. This measure is most useful for Bell and GHZ-style circuits and is not a score for every algorithm.",
      "physical_hardware",
      "Source: IBM job d95vhvd2su3c739gc080. This Bell/GHZ-style indicator is not a universal success metric for every circuit family."
    )
  ) +
  theme_final()

save_plot(ibm_plot, "04_ibm_hardware_expected_state_probability.png")

quantinuum_rows <- read_csv(
  "results/tables/quantinuum_validation_plot_rows.csv",
  show_col_types = FALSE
) %>%
  mutate(
    target_label = recode(
      target,
      "H2-1LE" = "H2-1LE Nexus emulator",
      "H2-Emulator" = "H2-Emulator Nexus emulator"
    ),
    circuit = factor(circuit, levels = c("Bell", "GHZ-3", "Grover-2"))
  )

quantinuum_plot <- ggplot(
  quantinuum_rows,
  aes(x = circuit, y = all_zero_or_all_one_probability, fill = target_label)
) +
  geom_col(position = position_dodge(width = 0.7), width = 0.62) +
  geom_text(
    aes(label = sprintf("%.0f%%", 100 * all_zero_or_all_one_probability)),
    position = position_dodge(width = 0.7),
    vjust = -0.35,
    size = 4.1,
    fontface = "bold"
  ) +
  scale_fill_manual(values = hardware_colors) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1.08)) +
  labs(
    title = "Quantinuum Nexus Validation: Emulator Results",
    subtitle = "Quantinuum Nexus emulator evidence",
    x = "Validation circuit",
    y = "All-zero/all-one probability",
    fill = NULL,
    caption = caption_block(
      "Higher bars mean the emulator returned the expected answer pattern more often. These results came from a Quantinuum Nexus emulator, not a physical H2 quantum computer.",
      "emulator",
      "Source: Quantinuum Nexus emulator artifacts. These are not physical Quantinuum QPU measurements."
    )
  ) +
  theme_final()

save_plot(quantinuum_plot, "05_quantinuum_nexus_emulator_validation.png")

manifest <- tibble::tribble(
  ~repository_filename,
  ~repository_figure_label,
  ~manuscript_figure_number,
  ~figure_type,
  ~main_research_question,
  ~dataset,
  ~evidence_type,
  ~number_of_observations,
  ~metric,
  ~statistical_summary,
  ~plain_language_explanation,
  ~release_context,
  ~source_script,
  ~interpretation_warning,
  "01_simulated_success_probability.png",
  "Repository figure 01",
  "",
  "faceted line/point graph",
  "How does model-estimated success change by circuit family, qubit count, and architecture proxy?",
  "results/tables/qubit_grouped_statistics.csv",
  "offline_proxy",
  nrow(success_rows),
  "estimated_success_probability_from_proxy_error_model",
  "Mean by circuit family, architecture proxy, and qubit count.",
  "Higher points mean the model predicts the circuit is more likely to finish correctly. The biggest differences appear for larger GHZ and QFT circuits.",
  "post-manuscript curated proxy figure",
  "scripts/generate_final_figures.R",
  "Proxy-estimated success is not measured hardware fidelity.",
  "02_simulated_routing_swap_cost.png",
  "Repository figure 02",
  "",
  "faceted line/point graph",
  "How much routing detour work does each architecture proxy add?",
  "results/tables/qubit_grouped_statistics.csv",
  "offline_proxy",
  nrow(swap_rows),
  "routing_swap_count",
  "Mean by circuit family, architecture proxy, and qubit count.",
  "A SWAP is an extra move the computer must make when two qubits cannot connect directly. More SWAPs mean the circuit must take more detours.",
  "post-manuscript curated proxy figure",
  "scripts/generate_final_figures.R",
  "Routing SWAP count is a compiler/proxy metric, not a direct provider benchmark.",
  "03_simulated_time_reliability_tradeoff.png",
  "Repository figure 03",
  "",
  "faceted scatter plot",
  "How do model-estimated runtime and model-estimated reliability move together?",
  "results/tables/qubit_grouped_statistics.csv",
  "offline_proxy",
  nrow(tradeoff_rows),
  "estimated_native_execution_duration_ns and estimated_success_probability_from_proxy_error_model",
  "Mean by circuit family, architecture proxy, and qubit count.",
  "Points farther right take more estimated time. Points higher up have better estimated reliability, so the best area is usually toward the upper left.",
  "post-manuscript curated proxy figure",
  "scripts/generate_final_figures.R",
  "Runtime and success are calculated from fixed assumptions, not measured hardware timing.",
  "04_ibm_hardware_expected_state_probability.png",
  "Repository supplemental figure H04",
  "",
  "box plot with visible observations",
  "What all-zero/all-one probability did the later IBM Kingston validation package return by bit width?",
  "results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv",
  "physical_hardware",
  nrow(ibm_summary),
  "all_zero_or_all_one_probability",
  "Raw pub-result observations grouped by measured bit width.",
  "Higher values mean the real IBM hardware measured all zeros or all ones more often. This measure is most useful for Bell and GHZ-style circuits and is not a score for every algorithm.",
  "post-manuscript IBM validation figure",
  "scripts/generate_final_figures.R",
  "All-zero/all-one probability is most direct for Bell/GHZ-style circuits and is not a universal algorithm success metric.",
  "05_quantinuum_nexus_emulator_validation.png",
  "Repository supplemental figure Q01",
  "",
  "grouped bar graph",
  "What did the Quantinuum Nexus emulator return for the stored small validation circuits?",
  "results/tables/quantinuum_validation_plot_rows.csv",
  "emulator",
  nrow(quantinuum_rows),
  "all_zero_or_all_one_probability",
  "Raw row per emulator target and validation circuit.",
  "Higher bars mean the emulator returned the expected answer pattern more often. These results came from a Quantinuum Nexus emulator, not a physical H2 quantum computer.",
  "post-manuscript Quantinuum emulator figure",
  "scripts/generate_final_figures.R",
  "Nexus emulator results are not physical Quantinuum QPU measurements."
)

write_csv(manifest, file.path(final_dir, "final_figures_manifest.csv"))

readme_lines <- c(
  "# Final Figures",
  "",
  "This folder contains the curated, presentation-ready figures for the project.",
  "",
  "| File | Evidence type | Simple explanation | Scientific warning |",
  "| --- | --- | --- | --- |",
  "| `01_simulated_success_probability.png` | `offline_proxy` | Higher points mean the model predicts the circuit is more likely to finish correctly. The biggest differences appear for larger GHZ and QFT circuits. | Proxy-estimated success is not measured hardware fidelity. |",
  "| `02_simulated_routing_swap_cost.png` | `offline_proxy` | A SWAP is an extra move the computer must make when two qubits cannot connect directly. More SWAPs mean the circuit must take more detours. | Routing SWAP count is a compiler/proxy metric, not a direct provider benchmark. |",
  "| `03_simulated_time_reliability_tradeoff.png` | `offline_proxy` | Points farther right take more estimated time. Points higher up have better estimated reliability, so the best area is usually toward the upper left. | Runtime and success are calculated from fixed assumptions, not measured hardware timing. |",
  "| `04_ibm_hardware_expected_state_probability.png` | `physical_hardware` | Higher values mean the real IBM hardware measured all zeros or all ones more often. This measure is most useful for Bell and GHZ-style circuits and is not a score for every algorithm. | All-zero/all-one probability is not a universal algorithm success metric. |",
  "| `05_quantinuum_nexus_emulator_validation.png` | `emulator` | Higher bars mean the emulator returned the expected answer pattern more often. These results came from a Quantinuum Nexus emulator, not a physical H2 quantum computer. | Nexus emulator results are not physical Quantinuum QPU measurements. |",
  "",
  "The first three figures are simulated/proxy-model results. The IBM figure is real hardware output. The Quantinuum figure is provider emulator output, not physical Quantinuum QPU output.",
  "",
  "Figure labels are separate from the manuscript's Figure 1-13 numbering. The IBM",
  "validation graph is repository supplemental figure H04, and the Quantinuum emulator",
  "graph is repository supplemental figure Q01.",
  "",
  "Expanded R visualizations are stored in:",
  "",
  "`results/final_figures/r_visualizations/`",
  "",
  "Those figures are documented in `docs/FIGURE_INTERPRETATION_GUIDE.md` and",
  "`reports/R_VISUAL_ANALYSIS.md`.",
  "",
  "Regenerate these files with:",
  "",
  "```bash",
  "Rscript scripts/generate_final_figures.R",
  "```"
)

writeLines(readme_lines, file.path(final_dir, "README.md"))
