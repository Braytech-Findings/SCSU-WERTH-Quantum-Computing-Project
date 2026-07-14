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
    title = "IBM Hardware Validation: Expected-State Probability by Bit Width",
    subtitle = "The extended IBM validation job produced real ibm_kingston counts across 115 pub results.",
    x = "Measured bit width",
    y = "All-zero/all-one probability",
    color = NULL,
    caption = "Source: IBM job d95vhvd2su3c739gc080. Mixed circuit families are shown together; this hardware result is separate from the offline proxy comparison."
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
    caption = "Source: Quantinuum Nexus emulator artifacts. These are not physical H2 hardware measurements."
  ) +
  theme_final()

save_plot(quantinuum_plot, "05_quantinuum_nexus_emulator_validation.png")

manifest <- tibble::tribble(
  ~file, ~plain_english_meaning,
  "01_simulated_success_probability.png", "Proxy-model estimate of success probability for superconducting and trapped-ion architectures.",
  "02_simulated_routing_swap_cost.png", "Proxy-model routing overhead, showing where limited connectivity adds SWAP operations.",
  "03_simulated_time_reliability_tradeoff.png", "Proxy-model tradeoff between estimated runtime and estimated success probability.",
  "04_ibm_hardware_expected_state_probability.png", "Real IBM ibm_kingston hardware validation counts summarized by measured bit width.",
  "05_quantinuum_nexus_emulator_validation.png", "Quantinuum Nexus emulator validation counts for Bell, GHZ-3, and Grover-2."
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
  "The first three figures are simulated/proxy-model results. The IBM figure is real hardware output. The Quantinuum figure is provider emulator output, not physical H2 hardware output.",
  "",
  "Regenerate these files with:",
  "",
  "```bash",
  "Rscript scripts/generate_final_figures.R",
  "```"
)

writeLines(readme_lines, file.path(final_dir, "README.md"))
