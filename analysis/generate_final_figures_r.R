#!/usr/bin/env Rscript

# Expanded R visualization workflow for the v1.0.0 research release.
# Run from the repository root:
# Rscript analysis/generate_final_figures_r.R

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(readr)
  library(scales)
  library(tidyr)
})

output_dir <- "results/final_figures/r_visualizations"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

proxy_table_path <- "results/tables/architecture_validation_table.csv"
grouped_table_path <- "results/tables/qubit_grouped_statistics.csv"
matched_table_path <- "results/tables/matched_size_architecture_comparison.csv"
ibm_summary_path <- "results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv"
quantinuum_summary_path <- "results/tables/quantinuum_validation_plot_rows.csv"

architecture_rows <- read_csv(proxy_table_path, show_col_types = FALSE)
grouped_rows <- read_csv(grouped_table_path, show_col_types = FALSE)
matched_rows <- read_csv(matched_table_path, show_col_types = FALSE)
ibm_rows <- read_csv(ibm_summary_path, show_col_types = FALSE)
quantinuum_rows <- read_csv(quantinuum_summary_path, show_col_types = FALSE)

provider_labels <- c(
  ibm = "Superconducting proxy",
  quantinuum = "Trapped-ion proxy"
)

family_labels <- c(
  bell = "Bell",
  ghz = "GHZ",
  qft = "QFT",
  grover = "Grover"
)

provider_palette <- c(
  "Superconducting proxy" = "#2364AA",
  "Trapped-ion proxy" = "#C75146"
)

hardware_palette <- c(
  "IBM ibm_kingston hardware" = "#2364AA",
  "H2-1LE Nexus emulator" = "#2A9D8F",
  "H2-Emulator Nexus emulator" = "#E9A23B"
)

theme_release <- function(base_size = 12) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", size = base_size + 3),
      plot.subtitle = element_text(color = "#333333"),
      plot.caption = element_text(color = "#555555", hjust = 0),
      panel.grid.minor = element_blank(),
      strip.text = element_text(face = "bold"),
      legend.position = "bottom"
    )
}

format_proxy_rows <- function(rows) {
  rows %>%
    mutate(
      architecture = recode(provider, !!!provider_labels),
      algorithm = factor(
        recode(circuit_family, !!!family_labels),
        levels = c("Bell", "GHZ", "QFT", "Grover")
      )
    )
}

save_release_plot <- function(plot, file_stem, width = 10, height = 6) {
  png_path <- file.path(output_dir, paste0(file_stem, ".png"))
  pdf_path <- file.path(output_dir, paste0(file_stem, ".pdf"))
  ggsave(png_path, plot, width = width, height = height, dpi = 320, bg = "white")
  ggsave(pdf_path, plot, width = width, height = height, bg = "white")
  message("Wrote ", png_path)
  message("Wrote ", pdf_path)
}

# Wilson score interval for binomial proportions.
# This avoids the simple normal approximation, which can be weak near 0 or 1.
wilson_interval <- function(successes, trials, z_value = 1.96) {
  proportion <- successes / trials
  denominator <- 1 + (z_value^2 / trials)
  center <- (proportion + (z_value^2 / (2 * trials))) / denominator
  half_width <- (
    z_value *
      sqrt((proportion * (1 - proportion) / trials) + (z_value^2 / (4 * trials^2)))
  ) / denominator
  data.frame(
    estimate = proportion,
    lower = pmax(0, center - half_width),
    upper = pmin(1, center + half_width)
  )
}

proxy_rows <- format_proxy_rows(architecture_rows)
grouped_proxy_rows <- format_proxy_rows(grouped_rows)

manifest_rows <- list()

add_manifest <- function(
  figure_number,
  filename,
  graph_type,
  research_question,
  data_source,
  evidence_type,
  main_metric,
  aggregation_used,
  sample_size,
  interpretation_warning
) {
  manifest_rows[[length(manifest_rows) + 1]] <<- data.frame(
    figure_number = figure_number,
    filename = filename,
    graph_type = graph_type,
    research_question = research_question,
    data_source = data_source,
    evidence_type = evidence_type,
    main_metric = main_metric,
    aggregation_used = aggregation_used,
    sample_size = sample_size,
    script = "analysis/generate_final_figures_r.R",
    interpretation_warning = interpretation_warning,
    stringsAsFactors = FALSE
  )
}

# R01: grouped bars answer a categorical comparison question.
r01_data <- proxy_rows %>%
  group_by(algorithm, architecture) %>%
  summarize(
    mean_native_depth = mean(native_compiled_depth),
    n_rows = n(),
    .groups = "drop"
  )

r01 <- ggplot(r01_data, aes(x = algorithm, y = mean_native_depth, fill = architecture)) +
  geom_col(position = position_dodge(width = 0.72), width = 0.64) +
  geom_text(
    aes(label = sprintf("%.1f", mean_native_depth)),
    position = position_dodge(width = 0.72),
    vjust = -0.35,
    size = 3.4
  ) +
  scale_fill_manual(values = provider_palette) +
  labs(
    title = "Mean Native-Compiled Depth by Algorithm Family",
    subtitle = "Grouped bars compare the two offline architecture proxy models.",
    x = "Algorithm family",
    y = "Mean native-compiled depth",
    fill = NULL,
    caption = "Source: architecture validation table. Bars are means across configured sizes and repetitions; evidence type: offline proxy."
  ) +
  theme_release()

save_release_plot(r01, "r01_algorithm_architecture_grouped_bar")
add_manifest(
  1,
  "r01_algorithm_architecture_grouped_bar.png / .pdf",
  "grouped_bar",
  "How does mean native-compiled depth differ by algorithm family and architecture proxy?",
  proxy_table_path,
  "offline_proxy",
  "native_compiled_depth",
  "Mean by algorithm family and proxy architecture.",
  nrow(proxy_rows),
  "Means combine configured sizes and deterministic repetitions; this is not physical hardware performance."
)

# R02: box plot uses repeated rows to show spread instead of only means.
r02 <- ggplot(proxy_rows, aes(x = architecture, y = native_compiled_depth, fill = architecture)) +
  geom_boxplot(width = 0.55, outlier.shape = NA, alpha = 0.58) +
  geom_jitter(aes(shape = algorithm), width = 0.14, height = 0, size = 2.2, alpha = 0.82) +
  scale_fill_manual(values = provider_palette) +
  labs(
    title = "Distribution of Native-Compiled Depth",
    subtitle = "Box plots show median, spread, and individual proxy observations.",
    x = "Architecture proxy",
    y = "Native-compiled depth",
    fill = NULL,
    shape = "Algorithm",
    caption = "Source: architecture validation table. Points are raw proxy rows; evidence type: offline proxy."
  ) +
  theme_release()

save_release_plot(r02, "r02_native_depth_distribution_boxplot")
add_manifest(
  2,
  "r02_native_depth_distribution_boxplot.png / .pdf",
  "boxplot_with_jitter",
  "How much spread exists in native-compiled depth within each architecture proxy?",
  proxy_table_path,
  "offline_proxy",
  "native_compiled_depth",
  "Raw rows shown; box summarizes median and quartiles by architecture proxy.",
  nrow(proxy_rows),
  "Repeated rows are deterministic repeats unless compiler settings change; spread mostly reflects circuit families and sizes."
)

# R03: scatter plot compares overhead and predicted performance.
r03 <- ggplot(
  proxy_rows,
  aes(
    x = native_entangling_gate_count,
    y = estimated_success_probability_from_proxy_error_model,
    color = architecture,
    shape = algorithm
  )
) +
  geom_point(size = 2.7, alpha = 0.86) +
  scale_color_manual(values = provider_palette) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "Entangling-Gate Count vs. Estimated Success",
    subtitle = "Scatter points ask whether greater native entangling overhead tracks lower proxy success estimates.",
    x = "Native entangling-gate count",
    y = "Estimated success probability",
    color = NULL,
    shape = "Algorithm",
    caption = "Source: architecture validation table. The plot shows association, not causation; evidence type: offline proxy."
  ) +
  theme_release()

save_release_plot(r03, "r03_gate_count_vs_fidelity_scatter")
add_manifest(
  3,
  "r03_gate_count_vs_fidelity_scatter.png / .pdf",
  "scatter",
  "Do circuits with more native entangling gates tend to have lower proxy-estimated success?",
  proxy_table_path,
  "offline_proxy",
  "native_entangling_gate_count and estimated_success_probability_from_proxy_error_model",
  "Raw architecture-proxy rows.",
  nrow(proxy_rows),
  "No statistical significance test is claimed; estimated success comes from a proxy error model."
)

# R04: line graph only uses ordered qubit count.
r04_data <- grouped_proxy_rows %>%
  filter(metric == "routing_swap_count")

r04_line_data <- r04_data %>%
  group_by(algorithm, architecture) %>%
  filter(n() > 1) %>%
  ungroup()

r04 <- ggplot(r04_data, aes(x = qubit_count, y = mean, color = architecture, group = architecture)) +
  geom_line(data = r04_line_data, linewidth = 0.9) +
  geom_point(size = 2.4) +
  facet_wrap(~ algorithm, scales = "free_x") +
  scale_color_manual(values = provider_palette) +
  scale_x_continuous(breaks = sort(unique(r04_data$qubit_count))) +
  labs(
    title = "Routing SWAP Count as Circuit Size Increases",
    subtitle = "Lines are used only where qubit count forms an ordered size sequence.",
    x = "Qubits in logical circuit",
    y = "Mean routing SWAP count",
    color = NULL,
    caption = "Source: grouped proxy statistics. Points are means across repetitions; evidence type: offline proxy."
  ) +
  theme_release()

save_release_plot(r04, "r04_scaling_by_qubit_count_line")
add_manifest(
  4,
  "r04_scaling_by_qubit_count_line.png / .pdf",
  "line",
  "How does routing overhead change as configured circuit size increases?",
  grouped_table_path,
  "offline_proxy",
  "routing_swap_count",
  "Mean by algorithm, proxy architecture, and qubit count.",
  nrow(r04_data),
  "Lines are omitted for groups with only one size; line segments should not be read as continuous physical laws."
)

# R05: heat map gives a quick matrix view of raw mean SWAP overhead.
r05_data <- grouped_proxy_rows %>%
  filter(metric == "routing_swap_count") %>%
  group_by(algorithm, architecture) %>%
  summarize(
    mean_swap_count = mean(mean),
    n_size_groups = n(),
    .groups = "drop"
  )

r05 <- ggplot(r05_data, aes(x = architecture, y = algorithm, fill = mean_swap_count)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = sprintf("%.1f", mean_swap_count)), size = 3.7) +
  scale_fill_gradient(low = "#F7FBFF", high = "#2364AA") +
  labs(
    title = "Heat Map of Mean Routing SWAP Overhead",
    subtitle = "Darker cells indicate more routing work added by the proxy compiler.",
    x = "Architecture proxy",
    y = "Algorithm family",
    fill = "Mean SWAPs",
    caption = "Source: grouped proxy statistics. Values are raw means across configured sizes, not normalized scores; evidence type: offline proxy."
  ) +
  theme_release()

save_release_plot(r05, "r05_algorithm_architecture_heatmap")
add_manifest(
  5,
  "r05_algorithm_architecture_heatmap.png / .pdf",
  "heatmap",
  "Where is routing SWAP overhead concentrated across algorithms and architecture proxies?",
  grouped_table_path,
  "offline_proxy",
  "routing_swap_count",
  "Mean of size-level means by algorithm family and architecture proxy.",
  nrow(r05_data),
  "Only one compatible metric is shown, so color intensity should not be compared to timing or fidelity scales."
)

# R06: paired comparison uses matched circuits compiled for both architecture proxies.
r06_data <- matched_rows %>%
  filter(metric == "estimated_success_probability_from_proxy_error_model") %>%
  mutate(
    algorithm = factor(
      recode(circuit_family, !!!family_labels),
      levels = c("Bell", "GHZ", "QFT", "Grover")
    ),
    matched_circuit = paste(algorithm, qubit_count, "qubits")
  ) %>%
  group_by(algorithm, qubit_count, matched_circuit) %>%
  summarize(
    superconducting_proxy = mean(ibm_value),
    trapped_ion_proxy = mean(quantinuum_value),
    .groups = "drop"
  ) %>%
  pivot_longer(
    cols = c(superconducting_proxy, trapped_ion_proxy),
    names_to = "architecture_key",
    values_to = "estimated_success_probability"
  ) %>%
  mutate(
    architecture = recode(
      architecture_key,
      superconducting_proxy = "Superconducting proxy",
      trapped_ion_proxy = "Trapped-ion proxy"
    )
  )

r06 <- ggplot(
  r06_data,
  aes(x = architecture, y = estimated_success_probability, group = matched_circuit)
) +
  geom_line(aes(color = algorithm), linewidth = 0.8, alpha = 0.85) +
  geom_point(aes(color = algorithm, shape = algorithm), size = 2.5) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "Matched-Circuit Change in Estimated Success",
    subtitle = "Each line follows the same logical circuit from one architecture proxy to the other.",
    x = "Architecture proxy",
    y = "Estimated success probability",
    color = "Algorithm",
    shape = "Algorithm",
    caption = "Source: matched-size architecture comparison. Values are means across deterministic repetitions; evidence type: offline proxy."
  ) +
  theme_release()

save_release_plot(r06, "r06_matched_architecture_slopegraph")
add_manifest(
  6,
  "r06_matched_architecture_slopegraph.png / .pdf",
  "slopegraph",
  "How does the same logical circuit's estimated success change between architecture proxies?",
  matched_table_path,
  "offline_proxy",
  "estimated_success_probability_from_proxy_error_model",
  "Mean by matched algorithm family and qubit count.",
  length(unique(r06_data$matched_circuit)),
  "The paired change is a proxy-model comparison, not a measured hardware fidelity comparison."
)

# R07: faceted small multiples keep several metrics readable.
r07_data <- grouped_proxy_rows %>%
  filter(
    metric %in% c(
      "native_compiled_depth",
      "native_entangling_gate_count",
      "routing_swap_count",
      "estimated_native_execution_duration_us"
    )
  ) %>%
  mutate(
    metric_label = recode(
      metric,
      native_compiled_depth = "Native depth",
      native_entangling_gate_count = "Entangling gates",
      routing_swap_count = "Routing SWAPs",
      estimated_native_execution_duration_us = "Duration (microseconds)"
    )
  )

r07 <- ggplot(
  r07_data,
  aes(x = qubit_count, y = mean, color = architecture, group = architecture)
) +
  geom_point(size = 2.1) +
  facet_grid(metric_label ~ algorithm, scales = "free_y") +
  scale_color_manual(values = provider_palette) +
  scale_x_continuous(breaks = sort(unique(r07_data$qubit_count))) +
  labs(
    title = "Proxy Results as Faceted Small Multiples",
    subtitle = "Facets separate metrics so incompatible units are not forced onto one scale.",
    x = "Qubits in logical circuit",
    y = "Mean value",
    color = NULL,
    caption = "Source: grouped proxy statistics. Each panel uses its own y-axis; evidence type: offline proxy."
  ) +
  theme_release(base_size = 10)

save_release_plot(r07, "r07_proxy_results_faceted", width = 12, height = 8)
add_manifest(
  7,
  "r07_proxy_results_faceted.png / .pdf",
  "faceted_small_multiple",
  "How do several proxy metrics vary by algorithm, size, and architecture without mixing units?",
  grouped_table_path,
  "offline_proxy",
  "native depth, entangling gates, routing SWAPs, and duration",
  "Mean by metric, algorithm, architecture proxy, and qubit count.",
  nrow(r07_data),
  "Facet y-axes differ because the metrics use different units; do not compare heights across rows."
)

# R08: IBM physical-hardware probability with Wilson confidence intervals.
ibm_ci <- ibm_rows %>%
  group_by(bit_width) %>%
  summarize(
    successes = sum(all_zero_or_all_one_count),
    trials = sum(shots),
    pub_results = n(),
    .groups = "drop"
  )

ibm_ci_values <- wilson_interval(ibm_ci$successes, ibm_ci$trials)
ibm_ci <- bind_cols(ibm_ci, ibm_ci_values) %>%
  mutate(bit_width = factor(bit_width))

r08 <- ggplot(ibm_ci, aes(x = bit_width, y = estimate)) +
  geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.18, color = "#2364AA") +
  geom_point(
    aes(size = pub_results, color = "IBM ibm_kingston hardware"),
    alpha = 0.9
  ) +
  scale_color_manual(values = hardware_palette) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  labs(
    title = "IBM Hardware: All-Zero/All-One Probability with Wilson Intervals",
    subtitle = "Intervals aggregate mixed validation circuits by measured bit width.",
    x = "Measured bit width",
    y = "All-zero/all-one probability",
    color = NULL,
    size = "Pub results",
    caption = "Source: IBM job d95vhvd2su3c739gc080. Wilson 95% binomial intervals; this Bell/GHZ-style indicator is not universal."
  ) +
  theme_release()

save_release_plot(r08, "r08_ibm_hardware_probability_ci")
add_manifest(
  8,
  "r08_ibm_hardware_probability_ci.png / .pdf",
  "dot_plot_with_wilson_confidence_intervals",
  "What all-zero/all-one probability did the IBM hardware job return by measured bit width?",
  ibm_summary_path,
  "physical_hardware",
  "all_zero_or_all_one_probability",
  "Counts summed by bit width; Wilson 95% binomial interval calculated from summed successes and shots.",
  nrow(ibm_rows),
  "The metric is most meaningful for Bell/GHZ-style circuits and should not be treated as universal algorithm accuracy."
)

# R09: Quantinuum Nexus emulator-only validation.
quantinuum_plot_rows <- quantinuum_rows %>%
  mutate(
    target_label = recode(
      target,
      "H2-1LE" = "H2-1LE Nexus emulator",
      "H2-Emulator" = "H2-Emulator Nexus emulator"
    ),
    circuit = factor(circuit, levels = c("Bell", "GHZ-3", "Grover-2"))
  )

r09 <- ggplot(
  quantinuum_plot_rows,
  aes(x = circuit, y = all_zero_or_all_one_probability, fill = target_label)
) +
  geom_col(position = position_dodge(width = 0.72), width = 0.62) +
  geom_text(
    aes(label = percent(all_zero_or_all_one_probability, accuracy = 1)),
    position = position_dodge(width = 0.72),
    vjust = -0.32,
    size = 3.5
  ) +
  scale_fill_manual(values = hardware_palette) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1.08)) +
  labs(
    title = "Quantinuum Nexus Emulator Validation",
    subtitle = "Small validation circuits executed on Nexus emulator targets only.",
    x = "Validation circuit",
    y = "All-zero/all-one probability",
    fill = NULL,
    caption = "Source: Quantinuum Nexus emulator artifacts. These are emulator results, not physical H2 hardware measurements."
  ) +
  theme_release()

save_release_plot(r09, "r09_quantinuum_emulator_results")
add_manifest(
  9,
  "r09_quantinuum_emulator_results.png / .pdf",
  "grouped_bar",
  "What did the stored Quantinuum Nexus emulator validation return for the small circuits?",
  quantinuum_summary_path,
  "emulator",
  "all_zero_or_all_one_probability",
  "Raw row per target and validation circuit.",
  nrow(quantinuum_rows),
  "These are Nexus emulator results and must not be described as physical H2 hardware measurements."
)

# R10: evidence summary counts records by evidence type without implying quality.
evidence_summary <- data.frame(
  evidence_type = c("offline_proxy", "physical_hardware", "emulator"),
  record_count = c(nrow(proxy_rows), nrow(ibm_rows), nrow(quantinuum_rows)),
  label = c("Architecture-proxy rows", "IBM pub results", "Quantinuum emulator rows"),
  evidence_label = c("Offline proxy", "Physical hardware", "Emulator")
)

r10 <- ggplot(evidence_summary, aes(x = label, y = record_count, fill = evidence_label)) +
  geom_col(width = 0.62) +
  geom_text(aes(label = record_count), vjust = -0.35, size = 3.8) +
  scale_fill_manual(
    values = c(
      "Offline proxy" = "#6C757D",
      "Physical hardware" = "#2364AA",
      "Emulator" = "#2A9D8F"
    )
  ) +
  labs(
    title = "Evidence Records Preserved in the Repository",
    subtitle = "Counts show quantity of stored records, not evidence quality or importance.",
    x = "Evidence category",
    y = "Stored result records",
    fill = "Evidence type",
    caption = "Source: stored proxy, IBM hardware, and Quantinuum emulator result tables."
  ) +
  theme_release()

save_release_plot(r10, "r10_evidence_summary")
add_manifest(
  10,
  "r10_evidence_summary.png / .pdf",
  "bar",
  "How many stored records exist in each evidence category?",
  paste(proxy_table_path, ibm_summary_path, quantinuum_summary_path, sep = "; "),
  "mixed_summary",
  "record_count",
  "Rows counted separately by evidence category.",
  sum(evidence_summary$record_count),
  "Record count is not a measure of evidence quality and does not combine the evidence types analytically."
)

manifest <- bind_rows(manifest_rows)
write_csv(manifest, file.path(output_dir, "r_visualizations_manifest.csv"))

readme_lines <- c(
  "# R Visualizations",
  "",
  "These figures were generated with `analysis/generate_final_figures_r.R`.",
  "",
  "The R figures use several graph types because each graph answers a different kind of",
  "research question. They do not combine proxy, emulator, and physical-hardware evidence",
  "as if those evidence types were equivalent.",
  "",
  "Use the manifest for details about data source, evidence type, aggregation, sample size,",
  "and interpretation warnings:",
  "",
  "- `r_visualizations_manifest.csv`",
  "",
  "Regenerate from the repository root with:",
  "",
  "```bash",
  "Rscript analysis/generate_final_figures_r.R",
  "```"
)

writeLines(readme_lines, file.path(output_dir, "README.md"))
