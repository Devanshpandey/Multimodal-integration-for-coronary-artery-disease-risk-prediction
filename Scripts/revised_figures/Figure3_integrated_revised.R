###############################################
# Integrated Figure 3: Model Evaluation & Independence
# Revised: Panel c shows raw data (hexbin), standardized axes, stats in subtitle.
#          Panel e bar heights use true partial R2 (no post-hoc visual inflation).
###############################################
required_packages <- c("ggplot2", "dplyr", "gridExtra", "RColorBrewer",
                       "forcats", "grid", "gtable", "patchwork", "tidyr", "scales", "survival",
                       "hexbin")

for(pkg in required_packages){
  if(!require(pkg, quietly=TRUE)) {
    options(repos = c(CRAN = "https://cloud.r-project.org"))
    install.packages(pkg, quiet=TRUE)
    library(pkg, quietly=TRUE, character.only=TRUE)
  }
}

# Source survival utilities for imaging score generation
source("/Users/devanshpandey/Downloads/Revsisons/figure5_joint_survival_utility.R")
TIME_COL <- "time_at_risk"
EVENT_COL <- "event"

# Nature Medicine–style theme
theme_nm <- theme_bw(base_size = 12, base_family = "Helvetica") +
  theme(
    panel.border       = element_rect(color = "black", fill = NA, linewidth = 0.8),
    panel.grid.major   = element_line(color = "grey95", linewidth = 0.3),
    panel.grid.minor   = element_blank(),
    axis.line          = element_line(color = "black", linewidth = 0.8),
    axis.ticks         = element_line(color = "black", linewidth = 0.5),
    axis.text          = element_text(color = "black", size = 11),
    axis.title         = element_text(color = "black", face = "plain", size = 14),
    strip.text         = element_text(face = "bold", size = 11),
    strip.background   = element_blank(),
    legend.position    = "none",
    plot.title         = element_text(face = "bold", size = 14, hjust = 0.5),
    plot.tag           = element_text(face = "bold", size = 22)
  )

###############################################
# 1) TOP ROW: Individual R² (a) and LOO (b)
###############################################
loo_data <- data.frame(
  Feature_Group   = c("Baseline", "Metabolic", "PRS",
                      "Heart_LA-Imaging", "Liver-Imaging", "Pancreatic-Imaging",
                      "BP", "DXA-Imaging", "Heart_BF-Imaging", "Heart_AD-Imaging",
                      "ECG", "Diabetes", "Medication"),
  Relative_Change = c(-6.114735, -3.519219, -9.614460,
                      -13.929790, -0.238650, -0.330359,
                      -0.698111, -0.483912, -0.654914, -7.908534,
                      -2.277529, -1.858552, -10.613794),
  Error           = c(1.136187, 0.593196, 1.177457,
                      1.655146, 0.357481, 0.415335,
                      0.448801, 0.399405, 0.440654, 0.864088,
                      0.516222, 0.461390, 1.267530)
)

r2_data <- data.frame(
  Feature_Group = c("Baseline", "Metabolic", "PRS",
                    "Heart_LA-Imaging", "Liver-Imaging", "Pancreatic-Imaging",
                    "BP", "DXA-Imaging", "Heart_BF-Imaging", "Heart_AD-Imaging",
                    "ECG", "Diabetes", "Medication"),
  R2_Mean       = c(0.161890, 0.071645, 0.067548, 0.237157,
                    0.096386, 0.088265, 0.037717, 0.036446, 0.112434,
                    0.162828, 0.046793, 0.029889, 0.180086),
  CI_Low        = c(0.154059, 0.061942, 0.059718, 0.224244,
                    0.086184, 0.081059, 0.032452, 0.028236, 0.104154,
                    0.151797, 0.039797, 0.024769, 0.168960),
  CI_High       = c(0.173062, 0.079839, 0.075628, 0.248923,
                    0.104633, 0.095288, 0.042929, 0.043365, 0.121698,
                    0.171547, 0.053738, 0.035120, 0.191337)
)

# Panel a - Individual R² (arranged decreasing)
r2_plot_data <- r2_data %>%
  arrange(desc(R2_Mean)) %>%
  mutate(Feature_Group = factor(Feature_Group, levels = rev(Feature_Group)))

pA <- ggplot(r2_plot_data, aes(x = R2_Mean, y = Feature_Group)) +
  geom_point(size = 3, color = "#66c2a5") +
  geom_errorbarh(aes(xmin = CI_Low, xmax = CI_High), height = 0.2) +
  labs(title = "Individual Feature Group R²", x = expression(bold(R^2~mean)), y = NULL, tag = "a") +
  theme_nm +
  theme(axis.title.x = element_text(size = 16, face = "bold"))

# Panel b - Leave-One-Out (custom order)
custom_order_b <- c(
  "Heart_LA-Imaging", "Medication", "PRS", "Heart_AD-Imaging",
  "Baseline", "Metabolic", "ECG", "Diabetes",
  "BP", "Heart_BF-Imaging", "DXA-Imaging",
  "Pancreatic-Imaging", "Liver-Imaging"
)

loo_plot_data <- loo_data %>%
  mutate(Feature_Group = factor(Feature_Group, levels = rev(custom_order_b)))

pB <- ggplot(loo_plot_data, aes(x = Relative_Change, y = Feature_Group)) +
  geom_point(size = 3, color = "#fc8d62") +
  geom_errorbarh(aes(xmin = Relative_Change - Error, xmax = Relative_Change + Error), height = 0.2) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "grey50") +
  labs(title = "Leave-One-Out R²", x = "Relative Change in R² (%)", y = NULL, tag = "b") +
  theme_nm +
  theme(axis.text.y = element_text(size = 11),
        axis.title.x = element_text(size = 16, face = "bold"))

###############################################
# 2) MIDDLE ROW: Scatter (c) and Variance Dec (d)
###############################################
train_df <- read.csv("revision_train_imbalanced_true.csv")
prs_col <- "PRS"
img_col <- "imaging_score_cf"

# Generate imaging_score_cf natively to ensure it exists
imaging_pc_cols <- grep("^pca_embedding", names(train_df), value = TRUE)
cat("Generating cross-fit imaging score for Panel C/D...\n")
train_df <- make_crossfit_imaging_score(
  df              = train_df,
  time_col        = TIME_COL,
  event_col       = EVENT_COL,
  imaging_pc_cols = imaging_pc_cols,
  n_splits        = 5
)

# -- Standardize both axes to SD (z-scores) so units match the "(SD)" axis labels.
train_df$PRS_z <- as.numeric(scale(train_df[[prs_col]]))
train_df$IMG_z <- as.numeric(scale(train_df[[img_col]]))

# Statistics for Panel C (correlation is scale-invariant; unchanged by standardization)
res_p  <- cor(train_df$PRS_z, train_df$IMG_z, method = "pearson",  use = "complete.obs")
res_s  <- cor(train_df$PRS_z, train_df$IMG_z, method = "spearman", use = "complete.obs")
r2_val <- summary(lm(IMG_z ~ PRS_z, data = train_df))$r.squared
n_obs  <- sum(complete.cases(train_df$PRS_z, train_df$IMG_z))

stats_label <- sprintf("r = %.3f    rho = %.3f    R² = %.3f    n = %s",
                       res_p, res_s, r2_val, format(n_obs, big.mark = ","))

# Panel 3c: PRS vs Imaging — RAW DATA as hexbin, standardized axes, stats in subtitle
#           (addresses reviewer comment: "show the raw data ... feel we are hiding the data/fit")
ax_lim <- 4   # show +/- 4 SD; trims a few extreme hexes visually, all data still used in the fit
pC <- ggplot(train_df, aes(x = PRS_z, y = IMG_z)) +
  geom_hex(bins = 60) +
  scale_fill_gradient(low = "grey88", high = "#2C5F8A",
                      trans = "log10", name = "Count") +
  geom_smooth(method = "lm", color = "darkred", linewidth = 1.2, se = TRUE) +
  coord_cartesian(xlim = c(-ax_lim, ax_lim), ylim = c(-ax_lim, ax_lim)) +
  labs(title = "Genetic vs Imaging Risk",
       subtitle = stats_label,
       x = "Polygenic Risk Score (SD)", y = "Imaging Risk Score (SD)", tag = "c") +
  theme_nm +
  theme(legend.position = "right",
        plot.subtitle = element_text(size = 11, hjust = 0.5, face = "plain"),
        legend.key.height = unit(0.8, "cm"),
        legend.key.width  = unit(0.35, "cm"))

# Panel 3e: Variance Decomposition (Partial R2)
# Partition into: Demographics (Age, Sex), Risk Factors (rest), Genetics (PRS)
clinical_cols <- c("age", "sex", "bmi", "ldl", "trig", "total_cholestrol",
                   "smoking", "bp_dia", "bp_sys", "pulse_rate",
                   "lipid_med", "bp_med", "insulin")
# Filter available cols
clinical_cols <- intersect(clinical_cols, names(train_df))
demo_cols <- intersect(clinical_cols, c("age", "sex"))
rf_cols   <- setdiff(clinical_cols, demo_cols)

d_lm <- train_df %>% dplyr::select(all_of(c(prs_col, img_col, clinical_cols))) %>% tidyr::drop_na()

fit_demo <- lm(reformulate(demo_cols, response = img_col), data = d_lm)
fit_clin <- lm(reformulate(clinical_cols, response = img_col), data = d_lm)
fit_full <- lm(reformulate(c(clinical_cols, prs_col), response = img_col), data = d_lm)

r2_demo <- summary(fit_demo)$r.squared
r2_clin <- summary(fit_clin)$r.squared
r2_full <- summary(fit_full)$r.squared

# Incremental (Partial) R2 contributions
part_r2_demo <- r2_demo
part_r2_rf   <- (r2_clin - r2_demo) / (1 - r2_demo)
part_r2_prs  <- (r2_full - r2_clin) / (1 - r2_clin)

# Colour palette (consistent with Figure 4)
col_clinical <- "#5B9E6F"   # green
col_prs      <- "#4A7FB5"   # blue
col_rf       <- "#7570B3"   # purple

# NOTE: bar heights now use the TRUE partial R2 (no post-hoc visual inflation).
# The genetics bar is genuinely tiny — that IS the finding ("<1%"). The printed label
# and y-axis floor keep it readable without distorting the height.
r2_long <- tibble(
  Category = factor(c("Demographics", "Clinical Risk Factors", "Genetics (PRS)"),
                    levels = c("Demographics", "Clinical Risk Factors", "Genetics (PRS)")),
  true_value = c(part_r2_demo, part_r2_rf, part_r2_prs),
  fill_col = c(col_clinical, col_rf, col_prs)
)

pD <- ggplot(r2_long, aes(x = Category, y = true_value, fill = fill_col)) +
  geom_col(width = 0.6, color = "white", linewidth = 0.5, show.legend = FALSE) +
  geom_text(aes(label = sprintf("%.2f%%", 100 * true_value)),
            vjust = -0.5, size = 4, fontface = "bold") +
  scale_fill_identity() +
  scale_y_continuous(
    limits = c(0, max(0.12, max(r2_long$true_value) * 1.5)),
    labels = scales::percent_format(accuracy = 1),
    expand = expansion(mult = c(0, 0.15))
  ) +
  labs(title = "Variance Decomposition (Partial R2)", x = NULL, y = "Partial R2", tag = "e") +
  theme_nm +
  theme(axis.text.x = element_text(size = 13, angle = 20, hjust = 1))

# Panel 3d: PRS Independence (Boxplot by Imaging Quintile)
train_df$img_q <- factor(ntile(train_df[[img_col]], 5), labels = paste0("Q", 1:5))

pD_box <- ggplot(train_df, aes(x = img_q, y = .data[[prs_col]])) +
  geom_boxplot(alpha = 0.7, outlier.size = 0.5, fill = "#a1d99b") +
  labs(title = "Genetic Risk Independence", x = "Imaging Risk Quintile", y = "PRS (SD)", tag = "d") +
  theme_nm +
  theme(legend.position = "none")

########################################################################################
# 3) BOTTOM ROW: UNIQUE VARIANCE (f)
###############################################
other_data <- data.frame(
  Imaging_Group           = rep(c("Heart_LA-Imaging","Heart_AD-Imaging",
                                  "Liver-Imaging","Pancreatic-Imaging",
                                  "DXA-Imaging","Heart_BF-Imaging"), each = 4),
  Combination             = rep(c("Alone","+ Baseline","+ Metabolic","+ ECG"), 6),
  Commonality_Coefficient = c(
    0.237157, -0.138022, -0.044970, -0.031519,
    0.162828, -0.107761, -0.043829, -0.021407,
    0.096386, -0.091256, -0.037964, -0.013733,
    0.088265, -0.080601, -0.026097, -0.009255,
    0.036446, -0.032364, -0.015078, -0.006277,
    0.112434, -0.091996, -0.035764, -0.018972
  )
)
PRS_data <- data.frame(
  Imaging_Group           = rep("PRS", 10),
  Combination             = c("Alone","+ Baseline","+ Metabolic","+ ECG",
                              "+ Heart LA","+ Heart AD","+ Heart BF",
                              "+ Liver","+ Pancreas","+ DXA"),
  Commonality_Coefficient = c(0.067548, -0.016412, -0.014596, -0.005333,
                              -0.034255, -0.025101, -0.016107,
                              -0.016314, -0.011693, -0.004394)
)
commonality_data <- bind_rows(other_data, PRS_data)
commonality_data$Imaging_Group <- factor(
  commonality_data$Imaging_Group,
  levels = c("Heart_LA-Imaging","Heart_AD-Imaging","Liver-Imaging",
             "Pancreatic-Imaging","DXA-Imaging","Heart_BF-Imaging","PRS")
)

commonality_processed <- commonality_data %>%
  group_by(Imaging_Group) %>%
  mutate(
    Alone_Value          = Commonality_Coefficient[Combination == "Alone"],
    Unique_Variance_Left = ifelse(Combination == "Alone",
                                   Commonality_Coefficient,
                                   Alone_Value + Commonality_Coefficient),
    Combination_ordered  = factor(Combination,
                                   levels = Combination[order(Unique_Variance_Left, decreasing = TRUE)])
  ) %>%
  ungroup()

unique_variance_plot <- ggplot(commonality_processed,
                               aes(x = Combination_ordered, y = Unique_Variance_Left)) +
  geom_bar(stat = "identity", fill = "#8da0cb") +
  facet_wrap(~ Imaging_Group, ncol = 7, scales = "free_x") +
  labs(
    title = "Unique Variance Explained",
    x     = "Feature Combination",
    y     = "Unique Variance",
    tag   = "f"
  ) +
  theme_nm +
  theme(axis.text.x = element_text(angle = 90, hjust = 1, size = 10),
        axis.title = element_text(face = "bold"))

# Adjust PRS facet width
g_F <- ggplotGrob(unique_variance_plot)
panels <- g_F$layout[grepl("panel", g_F$layout$name), ]
panel_cols <- unique(panels$l)
new_widths <- g_F$widths
for (i in seq_along(panel_cols)) {
  new_widths[panel_cols[i]] <- if (i == 7) unit(2, "null") else unit(0.8, "null")
}
g_F$widths <- new_widths

###############################################
# 4) ASSEMBLE (6-panel grid)
###############################################
# Column 1: A / B
# Column 2: C / D / E
# Bottom: F (Full Width)

col1 <- gridExtra::arrangeGrob(pA, pB, ncol = 1, heights = c(1, 1))
col2 <- gridExtra::arrangeGrob(pC, pD_box, pD, ncol = 1, heights = c(1, 1, 1))

# Row 1-2 combined
row12 <- gridExtra::arrangeGrob(col1, col2, ncol = 2, widths = c(1.8, 1))

# Full assembly
final_fig <- gridExtra::grid.arrange(
  row12,
  g_F,
  nrow = 2,
  heights = c(2.4, 1)
)

ggsave("Figure3_integrated.png", final_fig, width = 16, height = 20, dpi = 300, bg = "white")
ggsave("Figure3_integrated.pdf", final_fig, width = 16, height = 20, bg = "white")

cat("Figure 3 Integrated (revised Panels c & e) generated successfully.\n")
