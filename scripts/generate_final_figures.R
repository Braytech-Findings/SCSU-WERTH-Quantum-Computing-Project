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
  "Superconducting proxy" = "#2364AA",
  "Trapped-ion proxy" = "#C75146"
)

hardware_colors <- c(
  "IBM ibm_kingston hardware" = "#2364AA",
  "H2-1LE Nexus emulator" = "#2A9D8F",
  "H2-Emulator Nexus emulator" = "#E9A23B"
)

theme_final <- function(base_size = 12) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", size = base_size + 4),
      plot.subtitle = element_text(color = "#333333"),
      plot.caption = element_text(color = "#555555", hjust = 0),
      panel.grid.minor = element_blank(),
      strip.text = element_text(face = "bold"),
      legend.position = "bottom"
    )
}

save_plot <- function(plot, filename, width = 10, height = 6) {
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
  aes(x = qubit_count, y = mean, color = provider_label, group = provider_label)
) +
  geom_line(data = success_line_rows, linewidth = 0.9) +
  geom_point(size = 2.3) +
  facet_wrap(~ circuit_family, scales = "free_x") +
  scale_color_manual(values = provider_colors) +
  scale_x_continuous(breaks = sort(unique(success_rows$qubit_count))) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "Simulated Architecture Result: Estimated Success Probability",
    subtitle = "The proxy model compares a superconducting line-connected target with a trapped-ion all-to-all target.",
    x = "Qubits in logical circuit",
    y = "Estimated success probability",
    color = NULL,
    caption = "Source: offline proxy tables. These are model estimates, not live calibration values."
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
  aes(x = qubit_count, y = mean, color = provider_label, group = provider_label)
) +
  geom_line(data = swap_line_rows, linewidth = 0.9) +
  geom_point(size = 2.3) +
  facet_wrap(~ circuit_family, scales = "free_x") +
  scale_color_manual(values = provider_colors) +
  scale_x_continuous(breaks = sort(unique(swap_rows$qubit_count))) +
  labs(
    title = "Simulated Architecture Result: Routing SWAP Cost",
    subtitle = "Connectivity-heavy circuits need more routing work on the line-connected superconducting proxy.",
    x = "Qubits in logical circuit",
    y = "Mean routing SWAP count",
    color = NULL,
    caption = "Source: offline proxy tables. Lower SWAP count means less extra routing work was added."
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
    size = qubit_count
  )
) +
  geom_point(alpha = 0.82) +
  facet_wrap(~ circuit_family, scales = "free_x") +
  scale_color_manual(values = provider_colors) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  scale_size_continuous(range = c(2, 6)) +
  labs(
    title = "Simulated Architecture Result: Time vs. Reliability Tradeoff",
    subtitle = "The clearest story is not one metric alone, but how runtime and estimated success move together.",
    x = "Estimated native execution duration (microseconds)",
    y = "Estimated success probability",
    color = NULL,
    size = "Qubits",
    caption = "Source: offline proxy tables. Runtime and success are both estimated from fixed documented assumptions."
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

ibm_plot <- ggplot(
  ibm_summary,
  aes(x = bit_width, y = all_zero_or_all_one_probability)
) +
  geom_boxplot(
    fill = "#D8E8F7",
    color = "#2364AA",
    width = 0.62,
    outlier.shape = NA
  ) +
  geom_jitter(
    aes(color = hardware_label),
    width = 0.16,
    height = 0,
    size = 1.9,
    alpha = 0.78
  ) +
  scale_color_manual(values = hardware_colors) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "IBM Hardware Validation: All-Zero/All-One Probability by Bit Width",
    subtitle = paste0(
      "Mixed validation circuits from ",
      nrow(ibm_summary),
      " real ibm_kingston hardware results"
    ),
    x = "Measured bit width",
    y = "All-zero/all-one probability",
    color = NULL,
    caption = "Source: IBM job d95vhvd2su3c739gc080. This Bell/GHZ-style indicator is not a universal success metric for every circuit family."
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
    size = 3.7
  ) +
  scale_fill_manual(values = hardware_colors) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, 1.08)) +
  labs(
    title = "Quantinuum Nexus Validation: Emulator Results",
    subtitle = "Both Nexus emulator targets returned the expected states for the small validation circuits.",
    x = "Validation circuit",
    y = "All-zero/all-one probability",
    fill = NULL,
    caption = "Source: Quantinuum Nexus emulator artifacts. These are not physical Quantinuum QPU measurements."
  ) +
  theme_final()

save_plot(quantinuum_plot, "05_quantinuum_nexus_emulator_validation.png")

manifest <- tibble::tribble(
  ~repository_filename,
  ~repository_figure_label,
  ~manuscript_figure_number,
  ~figure_type,
  ~dataset,
  ~evidence_type,
  ~number_of_observations,
  ~metric,
  ~statistical_summary,
  ~release_context,
  ~interpretation_warning,
  "01_simulated_success_probability.png",
  "Repository figure 01",
  "",
  "faceted line/point graph",
  "results/tables/qubit_grouped_statistics.csv",
  "offline_proxy",
  nrow(grouped),
  "estimated_success_probability_from_proxy_error_model",
  "Mean by circuit family, architecture proxy, and qubit count.",
  "post-manuscript curated proxy figure",
  "Proxy-estimated success is not measured hardware fidelity.",
  "02_simulated_routing_swap_cost.png",
  "Repository figure 02",
  "",
  "faceted line/point graph",
  "results/tables/qubit_grouped_statistics.csv",
  "offline_proxy",
  nrow(grouped),
  "routing_swap_count",
  "Mean by circuit family, architecture proxy, and qubit count.",
  "post-manuscript curated proxy figure",
  "Routing SWAP count is a compiler/proxy metric, not a direct provider benchmark.",
  "03_simulated_time_reliability_tradeoff.png",
  "Repository figure 03",
  "",
  "faceted scatter plot",
  "results/tables/qubit_grouped_statistics.csv",
  "offline_proxy",
  nrow(grouped),
  "estimated_native_execution_duration_ns and estimated_success_probability_from_proxy_error_model",
  "Mean by circuit family, architecture proxy, and qubit count.",
  "post-manuscript curated proxy figure",
  "Runtime and success are calculated from fixed assumptions, not measured hardware timing.",
  "04_ibm_hardware_expected_state_probability.png",
  "Repository supplemental figure H04",
  "",
  "box plot with visible observations",
  "results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv",
  "physical_hardware",
  nrow(ibm_summary),
  "all_zero_or_all_one_probability",
  "Raw pub-result observations grouped by measured bit width.",
  "post-manuscript IBM validation figure",
  "All-zero/all-one probability is most direct for Bell/GHZ-style circuits and is not a universal algorithm success metric.",
  "05_quantinuum_nexus_emulator_validation.png",
  "Repository supplemental figure Q01",
  "",
  "grouped bar graph",
  "results/tables/quantinuum_validation_plot_rows.csv",
  "emulator",
  nrow(quantinuum_rows),
  "all_zero_or_all_one_probability",
  "Raw row per emulator target and validation circuit.",
  "post-manuscript Quantinuum emulator figure",
  "Nexus emulator results are not physical Quantinuum QPU measurements."
)

write_csv(manifest, file.path(final_dir, "final_figures_manifest.csv"))

readme_lines <- c(
  "# Final Figures",
  "",
  "This folder contains the curated, presentation-ready figures for the project.",
  "",
  "| File | What it shows |",
  "| --- | --- |",
  "| `01_simulated_success_probability.png` | Estimated success probability from the offline superconducting and trapped-ion proxy models. |",
  "| `02_simulated_routing_swap_cost.png` | Routing overhead from the offline proxy models, focused on added SWAP operations. |",
  "| `03_simulated_time_reliability_tradeoff.png` | Estimated runtime versus estimated success probability from the offline proxy models. |",
  "| `04_ibm_hardware_expected_state_probability.png` | Real IBM `ibm_kingston` hardware validation counts from job `d95vhvd2su3c739gc080`. |",
  "| `05_quantinuum_nexus_emulator_validation.png` | Quantinuum Nexus emulator validation counts from `H2-1LE` and `H2-Emulator`. |",
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
