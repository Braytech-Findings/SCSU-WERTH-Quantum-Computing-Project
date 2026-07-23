library(ggplot2)
library(readr)

aggregate <- read_csv("results/tables/quantinuum_full_suite_aggregate.csv", show_col_types = FALSE)
raw <- read_csv("results/tables/quantinuum_full_suite_raw_results.csv", show_col_types = FALSE)
aggregate$display_name <- factor(aggregate$display_name, levels = c("Bell-2", "GHZ-3", "GHZ-5", "GHZ-7", "Grover-2", "QFT-3", "QFT-5"))
raw$display_name <- factor(raw$display_name, levels = levels(aggregate$display_name))
palette <- c("H2-1LE" = "#0072B2", "H2-Emulator" = "#D55E00")
caption <- "Quantinuum Nexus emulator; 1,000 shots/circuit; 3 repetitions. Not physical Quantinuum QPU measurements. Source: results/tables/quantinuum_full_suite_aggregate.csv"

save_both <- function(plot, name) {
  ggsave(paste0("results/final_figures/", name, ".png"), plot, width = 10, height = 6, dpi = 320)
  ggsave(paste0("results/final_figures/", name, ".pdf"), plot, width = 10, height = 6)
}

theme_final <- theme_minimal(base_size = 12) + theme(legend.position = "top", panel.grid.minor = element_blank())

fidelity <- ggplot(aggregate, aes(display_name, mean_distribution_fidelity, color = target, group = target)) +
  geom_errorbar(aes(ymin = min_distribution_fidelity, ymax = max_distribution_fidelity), position = position_dodge(width = .25), width = .12) +
  geom_point(position = position_dodge(width = .25), size = 3) +
  scale_color_manual(values = palette) + coord_cartesian(ylim = c(.97, 1.002)) +
  labs(title = "Full-Suite Classical Distribution Fidelity", x = "Circuit", y = "Mean fidelity (higher is better)", color = "Emulator target", caption = caption) + theme_final
save_both(fidelity, "quantinuum_full_suite_distribution_fidelity")

tvd <- ggplot(aggregate, aes(display_name, mean_tvd, fill = target)) +
  geom_col(position = position_dodge(width = .8), width = .72) +
  geom_errorbar(aes(ymin = pmax(0, mean_tvd - sd_tvd), ymax = mean_tvd + sd_tvd), position = position_dodge(width = .8), width = .18) +
  scale_fill_manual(values = palette) +
  labs(title = "Full-Suite Total Variation Distance", x = "Circuit", y = "Mean TVD (lower is better)", fill = "Emulator target", caption = caption) + theme_final
save_both(tvd, "quantinuum_full_suite_tvd")

repetitions <- ggplot(raw, aes(display_name, distribution_fidelity, color = target, shape = factor(repetition))) +
  geom_point(position = position_jitterdodge(jitter.width = .06, dodge.width = .35), size = 2.6) +
  scale_color_manual(values = palette) +
  labs(title = "Emulator Repetition-Level Results", x = "Circuit", y = "Classical distribution fidelity", color = "Emulator target", shape = "Repetition", caption = gsub("aggregate", "raw_results", caption)) + theme_final
save_both(repetitions, "quantinuum_emulator_repetition_results")
