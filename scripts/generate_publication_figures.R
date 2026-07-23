#!/usr/bin/env Rscript

if (!nzchar(Sys.getenv("XDG_CACHE_HOME"))) {
  Sys.setenv(XDG_CACHE_HOME = tempdir())
}

suppressPackageStartupMessages({
  library(cowplot)
  library(dplyr)
  library(ggplot2)
  library(readr)
  library(scales)
  library(tidyr)
})

output_dir <- "results/final_figures/publication"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

blue <- "#0072B2"
vermillion <- "#D55E00"
green <- "#009E73"
charcoal <- "#20252B"
light_grid <- "#D9DEE3"
proxy_colors <- c("Superconducting proxy" = blue, "Trapped-ion proxy" = vermillion)
emulator_colors <- c("H2-1LE" = blue, "H2-Emulator" = vermillion)
circuit_levels <- c("Bell-2", "GHZ-3", "GHZ-5", "GHZ-7", "Grover-2", "QFT-3", "QFT-5")

theme_publication <- function(base_size = 13) {
  theme_minimal(base_size = base_size) +
    theme(
      text = element_text(family = "sans", color = charcoal),
      plot.title = element_text(face = "bold", size = base_size + 6, margin = margin(b = 5)),
      plot.subtitle = element_text(size = base_size, color = "#454B52", margin = margin(b = 12)),
      plot.caption = element_text(size = base_size - 3, color = "#555B61", hjust = 0),
      axis.title = element_text(face = "bold"),
      axis.text = element_text(color = charcoal),
      panel.grid.major = element_line(color = light_grid, linewidth = 0.35),
      panel.grid.minor = element_blank(),
      strip.text = element_text(face = "bold", size = base_size),
      strip.background = element_rect(fill = "#F2F4F6", color = NA),
      legend.position = "top",
      legend.title = element_blank(),
      legend.text = element_text(size = base_size - 1),
      plot.margin = margin(14, 18, 8, 14)
    )
}

note_band <- function(lines, source) {
  wrapped_lines <- vapply(
    lines,
    function(line) paste(strwrap(paste0("• ", line), width = 112), collapse = "\n   "),
    character(1)
  )
  text <- paste0(
    paste(wrapped_lines, collapse = "\n"),
    "\n\nSource: ", source
  )
  ggdraw() +
    draw_label(
      text,
      x = 0.018,
      y = 0.96,
      hjust = 0,
      vjust = 1,
      size = 9.7,
      color = charcoal,
      lineheight = 1.2
    ) +
    theme(plot.background = element_rect(fill = "#F6F8FA", color = "#CDD3D8", linewidth = 0.6))
}

assemble <- function(plot, notes, source, note_height = 0.20) {
  plot_grid(
    plot,
    note_band(notes, source),
    ncol = 1,
    rel_heights = c(1 - note_height, note_height)
  )
}

save_publication <- function(plot, stem, width = 13, height = 9) {
  png_path <- file.path(output_dir, paste0(stem, ".png"))
  pdf_path <- file.path(output_dir, paste0(stem, ".pdf"))
  ggsave(png_path, plot, width = width, height = height, dpi = 400, bg = "white")
  ggsave(pdf_path, plot, width = width, height = height, device = cairo_pdf, bg = "white")
  message("Wrote ", png_path, " and ", pdf_path)
}

architecture <- read_csv(
  "results/tables/architecture_validation_table.csv",
  show_col_types = FALSE
) %>%
  mutate(
    architecture = recode(
      provider,
      ibm = "Superconducting proxy",
      quantinuum = "Trapped-ion proxy"
    ),
    circuit = case_when(
      circuit_family == "bell" ~ "Bell-2",
      circuit_family == "grover" ~ "Grover-2",
      TRUE ~ paste0(toupper(circuit_family), "-", qubit_count)
    ),
    circuit = factor(circuit, levels = circuit_levels)
  )

if (nrow(architecture) != 42) {
  stop("Expected 42 architecture-proxy rows; found ", nrow(architecture), ".")
}
if (!setequal(unique(architecture$architecture), names(proxy_colors))) {
  stop("Architecture labels do not match the publication palette.")
}

matched <- architecture %>%
  group_by(circuit, architecture) %>%
  summarize(
    routing_swaps = mean(routing_swap_count),
    native_depth = mean(native_compiled_depth),
    entangling_gates = mean(native_entangling_gate_count),
    duration_us = mean(estimated_native_execution_duration_us),
    success = mean(estimated_success_probability_from_proxy_error_model),
    .groups = "drop"
  )

answer_rows <- matched %>%
  select(circuit, architecture, routing_swaps, native_depth, entangling_gates) %>%
  pivot_longer(
    cols = c(routing_swaps, native_depth, entangling_gates),
    names_to = "metric",
    values_to = "value"
  ) %>%
  mutate(
    metric = factor(
      metric,
      levels = c("routing_swaps", "native_depth", "entangling_gates"),
      labels = c("Routing SWAPs", "Native-compiled depth", "Native entangling gates")
    )
  )

answer_plot <- ggplot(answer_rows, aes(circuit, value, fill = architecture)) +
  geom_col(position = position_dodge(width = 0.78), width = 0.68) +
  geom_text(
    aes(label = number(value, accuracy = 1)),
    position = position_dodge(width = 0.78),
    vjust = -0.25,
    size = 3.2,
    color = charcoal
  ) +
  facet_wrap(~metric, scales = "free_y", ncol = 1) +
  scale_fill_manual(values = proxy_colors) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  labs(
    title = "The Same Circuit Takes Different Roads",
    subtitle = "Controlled architecture proxies: identical logical circuits, different connectivity and native gates",
    x = NULL,
    y = "Count or depth (lower means less compiled work)",
    caption = "Evidence class: offline architecture proxy. These values are not physical-device measurements."
  ) +
  theme_publication() +
  theme(axis.text.x = element_text(angle = 25, hjust = 1))

answer_final <- assemble(
  answer_plot,
  c(
    "QUESTION — How do identical logical circuits change after routing and native-gate decomposition?",
    "READ — Compare the blue and orange bars within one circuit; shorter bars mean less compiled work.",
    "RESULT — GHZ and QFT expose the largest gap: line connectivity needs SWAP detours, while all-to-all connectivity needs none here.",
    "WHY IT MATTERS — Connectivity can change the practical circuit long before a quantum algorithm reaches a device.",
    "BOUNDARY — This answers the controlled proxy question; it does not rank physical IBM and Quantinuum QPUs."
  ),
  "results/tables/architecture_validation_table.csv",
  note_height = 0.23
)
save_publication(answer_final, "01_research_question_answer", height = 12.2)

scaling_rows <- architecture %>%
  filter(circuit_family %in% c("ghz", "qft")) %>%
  group_by(circuit_family, qubit_count, architecture) %>%
  summarize(routing_swaps = mean(routing_swap_count), .groups = "drop") %>%
  mutate(family = recode(circuit_family, ghz = "GHZ", qft = "QFT"))

scaling_plot <- ggplot(
  scaling_rows,
  aes(qubit_count, routing_swaps, color = architecture, shape = architecture, group = architecture)
) +
  geom_line(linewidth = 1.25) +
  geom_point(size = 3.8, stroke = 1) +
  geom_text(
    aes(label = number(routing_swaps, accuracy = 1)),
    vjust = -0.8,
    size = 3.6,
    show.legend = FALSE
  ) +
  facet_wrap(~family, scales = "free_x") +
  scale_color_manual(values = proxy_colors) +
  scale_shape_manual(values = c("Superconducting proxy" = 16, "Trapped-ion proxy" = 17)) +
  scale_x_continuous(breaks = c(3, 5, 7)) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  labs(
    title = "Long-Range Circuits Magnify the Connectivity Gap",
    subtitle = "Routing SWAPs grow with circuit size on the line-connected proxy",
    x = "Logical qubits",
    y = "Routing SWAP count (lower is better)",
    caption = "Evidence class: offline architecture proxy. Lines connect tested sizes; they are not extrapolations."
  ) +
  theme_publication()

scaling_final <- assemble(
  scaling_plot,
  c(
    "QUESTION — What happens as GHZ and QFT circuits become larger?",
    "READ — Move left to right as qubit count grows; a rising line means routing overhead is increasing.",
    "RESULT — The superconducting line proxy reaches 20 SWAPs for GHZ-7 and 30 for QFT-5; the all-to-all proxy stays at 0 for these tests.",
    "WHY IT MATTERS — Algorithms with distant two-qubit interactions are especially sensitive to device connectivity.",
    "BOUNDARY — Only the configured 3–7 qubit cases were tested; the graph does not predict every larger circuit."
  ),
  "results/tables/qubit_grouped_statistics.csv",
  note_height = 0.20
)
save_publication(scaling_final, "02_connectivity_scaling", height = 8.8)

tradeoff_plot <- ggplot(
  matched,
  aes(duration_us, success, color = architecture, shape = architecture)
) +
  geom_point(size = 4, stroke = 1, alpha = 0.92) +
  geom_text(
    data = matched %>% filter(circuit %in% c("GHZ-5", "GHZ-7", "QFT-3", "QFT-5")),
    aes(label = circuit),
    size = 3.25,
    nudge_y = 0.025,
    show.legend = FALSE
  ) +
  scale_color_manual(values = proxy_colors) +
  scale_shape_manual(values = c("Superconducting proxy" = 16, "Trapped-ion proxy" = 17)) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0.2, 1.02)) +
  scale_x_continuous(labels = label_number(suffix = " µs")) +
  labs(
    title = "Modeled Time and Reliability Tell the Same Structural Story",
    subtitle = "Upper-left means shorter estimated duration and higher estimated success",
    x = "Estimated native duration",
    y = "Estimated success probability",
    caption = "Evidence class: offline proxy model using fixed timing and error assumptions; not measured device speed or fidelity."
  ) +
  theme_publication()

tradeoff_final <- assemble(
  tradeoff_plot,
  c(
    "QUESTION — Under the documented proxy assumptions, how do estimated time and success move together?",
    "READ — Better modeled outcomes sit toward the upper-left: less time and a higher success estimate.",
    "RESULT — The trapped-ion proxy is upper-left of the superconducting proxy for every tested matched circuit.",
    "WHY IT MATTERS — Routing overhead affects more than one count; it propagates into modeled duration and error exposure.",
    "BOUNDARY — These estimates depend on fixed proxy assumptions and are not calibration-based physical measurements."
  ),
  "results/tables/architecture_validation_table.csv",
  note_height = 0.27
)
save_publication(tradeoff_final, "03_modeled_time_reliability", height = 8.8)

emulator <- read_csv(
  "results/tables/quantinuum_full_suite_aggregate.csv",
  show_col_types = FALSE
) %>%
  mutate(display_name = factor(display_name, levels = circuit_levels))

if (nrow(emulator) != 14 || !setequal(unique(emulator$target), names(emulator_colors))) {
  stop("Expected seven aggregate rows for each of the two emulator targets.")
}
if (any(is.na(emulator$display_name)) || any(emulator$successful_repetitions != 3)) {
  stop("Emulator circuit identities or repetition totals failed validation.")
}
if (sum(emulator$shots_retrieved) != 42000) {
  stop("Expected 42,000 retrieved emulator shots.")
}

fidelity_panel <- ggplot(
  emulator,
  aes(display_name, mean_distribution_fidelity, color = target, group = target)
) +
  geom_errorbar(
    aes(ymin = min_distribution_fidelity, ymax = max_distribution_fidelity),
    position = position_dodge(width = 0.32),
    width = 0.12,
    linewidth = 0.7
  ) +
  geom_point(position = position_dodge(width = 0.32), size = 3.2) +
  scale_color_manual(values = emulator_colors) +
  scale_y_continuous(labels = percent_format(accuracy = 0.1), limits = c(0.975, 1.001)) +
  labs(
    title = "A. Distribution fidelity",
    x = NULL,
    y = "Mean fidelity (higher is better)"
  ) +
  theme_publication(11) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1), legend.position = "none")

tvd_panel <- ggplot(emulator, aes(display_name, mean_tvd, fill = target)) +
  geom_col(position = position_dodge(width = 0.78), width = 0.66) +
  geom_errorbar(
    aes(ymin = pmax(0, mean_tvd - sd_tvd), ymax = mean_tvd + sd_tvd),
    position = position_dodge(width = 0.78),
    width = 0.14,
    linewidth = 0.65
  ) +
  scale_fill_manual(values = emulator_colors) +
  scale_y_continuous(labels = percent_format(accuracy = 1), expand = expansion(mult = c(0, 0.12))) +
  labs(
    title = "B. Total variation distance",
    x = NULL,
    y = "Mean TVD (lower is better)"
  ) +
  theme_publication(11) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1), legend.position = "none")

emulator_header <- ggdraw() +
  draw_label(
    "Quantinuum Nexus Full-Suite Emulator Validation",
    x = 0.01,
    hjust = 0,
    fontface = "bold",
    size = 19,
    color = charcoal
  ) +
  draw_label(
    "1,000 shots per circuit × 3 repetitions per target; error bars show observed range (A) or ±1 SD (B)",
    x = 0.01,
    y = 0.2,
    hjust = 0,
    size = 11.5,
    color = "#454B52"
  )

legend <- get_legend(
  fidelity_panel +
    theme(legend.position = "top") +
    labs(color = "Nexus emulator target")
)

emulator_graph <- plot_grid(
  emulator_header,
  legend,
  plot_grid(fidelity_panel, tvd_panel, nrow = 1, rel_widths = c(1, 1)),
  ncol = 1,
  rel_heights = c(0.13, 0.09, 0.78)
)

emulator_final <- assemble(
  emulator_graph,
  c(
    "QUESTION — Did the complete seven-circuit workflow return output distributions close to the exact ideal distributions?",
    "READ — Fidelity should be near 100%; TVD should be near 0%. Compare targets only within the same circuit.",
    "RESULT — Every target/circuit mean fidelity exceeded 98.4%; QFT-5 had the largest mean TVD on both targets.",
    "WHY IT MATTERS — The full workflow, circuit identity mapping, bit order, retrieval, and distribution scoring all worked end to end.",
    "BOUNDARY — These are emulator measurements, not physical trapped-ion QPU results; QFT measurement fidelity does not test the complete phase state."
  ),
  "results/tables/quantinuum_full_suite_aggregate.csv",
  note_height = 0.28
)
save_publication(emulator_final, "04_quantinuum_emulator_validation", height = 9.4)

manifest <- tibble::tribble(
  ~figure, ~question, ~evidence_type, ~source_csv, ~primary_metric, ~claim_boundary,
  "01_research_question_answer", "How do identical logical circuits change after routing and native decomposition?", "offline_proxy", "results/tables/architecture_validation_table.csv", "routing SWAPs; native depth; native entangling gates", "Controlled proxy comparison; not physical-provider ranking.",
  "02_connectivity_scaling", "How does routing overhead change as GHZ and QFT grow?", "offline_proxy", "results/tables/qubit_grouped_statistics.csv", "routing SWAP count", "Tested sizes only; no extrapolation.",
  "03_modeled_time_reliability", "How do modeled duration and success move together?", "offline_proxy", "results/tables/architecture_validation_table.csv", "proxy duration and proxy success", "Assumption-dependent estimates; not measured speed or fidelity.",
  "04_quantinuum_emulator_validation", "Did the full Nexus emulator workflow match exact ideal output distributions?", "emulator", "results/tables/quantinuum_full_suite_aggregate.csv", "classical distribution fidelity and TVD", "Nexus emulator evidence; not physical Quantinuum QPU measurements."
)
write_csv(manifest, file.path(output_dir, "publication_figures_manifest.csv"))
